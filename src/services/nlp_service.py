import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
from dateparser import parse as parse_date

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_hotel_search_params(user_input: str):
    """
    Extracts hotel search parameters using OpenAI + dateparser.
    Handles relative phrases like 'tomorrow', 'next weekend', etc.
    """
    prompt = f"""
    Extract hotel search parameters from this text:
    "{user_input}"

    Respond ONLY with valid JSON in this structure:
    {{
      "q": "city",
      "check_in_date": "string (may be a relative expression like 'tomorrow')",
      "check_out_date": "string (may be a relative expression like 'next week')",
      "adults": number,
      "children": number,
      "currency": "USD",
      "gl": "us",
      "hl": "en"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You extract structured hotel search data and return only JSON."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        data = {}

    # --- Date handling ---
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    def normalize_date(date_value, fallback):
        """Converts various formats or relative phrases into YYYY-MM-DD."""
        if not date_value:
            return fallback
        # Try to parse absolute or relative date
        parsed = parse_date(str(date_value), settings={"RELATIVE_BASE": datetime.now()})
        if parsed:
            parsed_date = parsed.date()
            # avoid past dates
            if parsed_date < today:
                parsed_date = today
            return parsed_date
        return fallback

    # Try to parse using model output or user text
    check_in = normalize_date(data.get("check_in_date") or user_input, today)
    check_out = normalize_date(data.get("check_out_date") or user_input, check_in + timedelta(days=1))

    # Ensure checkout is after checkin
    if check_out <= check_in:
        check_out = check_in + timedelta(days=1)

    # Write back normalized ISO strings
    data["check_in_date"] = check_in.isoformat()
    data["check_out_date"] = check_out.isoformat()

    # Other safe defaults
    data["adults"] = data.get("adults", 2)
    data["children"] = data.get("children", 0)
    data["currency"] = data.get("currency", "USD")
    data["gl"] = data.get("gl", "us")
    data["hl"] = data.get("hl", "en")

    return data
