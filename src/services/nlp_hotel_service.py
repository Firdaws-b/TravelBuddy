import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
from dateparser import parse as parse_date
from fastapi import HTTPException

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_OTHER"))


def extract_hotel_search_params(user_input: str):
    """
    Extracts structured hotel search parameters using GPT,
    then validates and corrects dates to ensure they are always
    valid future ISO dates for the external hotel search API.
    """

    # -----------------------------
    # Prompt for GPT
    # -----------------------------
    prompt = f"""
    You are a deterministic hotel-search extractor.

    STRICT OUTPUT RULES:
    - Return ONLY valid JSON, no explanation or text.
    - All dates MUST be ISO format YYYY-MM-DD if you can determine them.
    - If a date cannot be determined, output null.
    - Required keys: q, check_in_date, check_out_date, adults, children, currency, gl, hl.
    - currency="CAD", gl="us", hl="en".

    EXAMPLES:
    Input: "Find hotels in Paris from March 10 to March 15 for 2 adults"
    Output: {{"q":"Paris","check_in_date":"2025-03-10","check_out_date":"2025-03-15","adults":2,"children":0,"currency":"CAD","gl":"us","hl":"en"}}

    Input: "Hotels in Tokyo from July 4 to July 8 for 1 adult and 1 child"
    Output: {{"q":"Tokyo","check_in_date":"2025-07-04","check_out_date":"2025-07-08","adults":1,"children":1,"currency":"CAD","gl":"us","hl":"en"}}

    YOUR TURN.
    Input: "{user_input}"
    """

    # -----------------------------
    # 1. GPT CALL
    # -----------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return ONLY JSON. No explanation."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    # -----------------------------
    # 2. Parse JSON
    # -----------------------------
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError(f"GPT returned invalid JSON:\n{raw_output}")

    # -----------------------------
    # 3. Strict key validation
    # -----------------------------
    required_keys = [
        "q", "check_in_date", "check_out_date",
        "adults", "children", "currency", "gl", "hl"
    ]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key: {key}\nOutput: {raw_output}")

    # -----------------------------
    # 4. Strict ISO parser
    # -----------------------------
    def rigid_parse(date_string):
        if date_string is None:
            return None
        if isinstance(date_string, str) and len(date_string) == 10:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d").date()
            except:
                return None
        return None

    check_in = rigid_parse(data["check_in_date"])
    check_out = rigid_parse(data["check_out_date"])

    # -----------------------------
    # 5. Fallback using dateparser
    # -----------------------------
    if not check_in and data["check_in_date"]:
        parsed = parse_date(data["check_in_date"])
        if parsed:
            check_in = parsed.date()

    if not check_out and data["check_out_date"]:
        parsed = parse_date(data["check_out_date"])
        if parsed:
            check_out = parsed.date()

    # -----------------------------
    # 6. If both dates missing → reject input
    # -----------------------------
    if not check_in and not check_out:
        raise HTTPException(
            status_code=400,
            detail="No valid dates found in user input."
        )

    # -----------------------------
    # 7. If only one date given → infer the other
    # -----------------------------
    if check_in and not check_out:
        check_out = check_in + timedelta(days=1)

    if check_out and not check_in:
        check_in = check_out - timedelta(days=1)

    # -----------------------------
    # 8. Future-date enforcement logic
    # -----------------------------
    today = datetime.now().date()

    def ensure_future(date_obj):
        """
        If the extracted date is in the past, roll it into the future.
        Example:
        Today = 2025-11-24
        "Dec 31" → 2025-12-31
        "Jan 2" → 2026-01-02
        """
        # if parsed date has no year or is incorrect, dateparser may give past years
        if date_obj < today:
            # first try setting the year to the current one
            updated = date_obj.replace(year=today.year)
            if updated < today:
                # otherwise bump to next year
                updated = date_obj.replace(year=today.year + 1)
            return updated
        return date_obj

    check_in = ensure_future(check_in)
    check_out = ensure_future(check_out)

    # -----------------------------
    # 9. Guarantee valid range
    # -----------------------------
    if check_out < check_in:
        check_out = check_in + timedelta(days=1)

    # -----------------------------
    # 10. Save cleaned values
    # -----------------------------
    data["check_in_date"] = check_in.isoformat()
    data["check_out_date"] = check_out.isoformat()

    return data
