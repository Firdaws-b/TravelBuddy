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
    """
    prompt = f"""
    Transform the user request into a JSON that I can use to compute exact hotel search parameters.

    You may use the following time references when interpreting the user's dates:
    - TODAY: today's date ({datetime.today().date().isoformat()})
    - TOMORROW: tomorrow's date
    - NEXT_WEEK: 7 days after today
    - END_OF_MONTH: last day of the current month
    - MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY: days of the upcoming week
    - CHECKIN: explicitly provided check-in date (if any)
    - CHECKOUT: explicitly provided check-out date (if any)

    If the user sentence mentions a stay duration or window, return:
        {{"start": check-in, "end": check-out}}

    If the sentence mentions only specific dates, return:
        {{"list": [dates]}}

    All dates MUST use the format YYYY-MM-DD.

    If you cannot compute the exact date, express it using the simplest arithmetic formula based on the above references.
    Use a unit of one day. Consider a week = 7 days.

    If no valid city or dates are detected, return:
        {{"error": true}}

    Today's date: {datetime.today().date().isoformat()}.

    Now extract the hotel search parameters strictly following this structure:

    {{
        "q": "city name",
        "check_in_date": "YYYY-MM-DD or relative reference",
        "check_out_date": "YYYY-MM-DD or relative reference",
        "adults": number (default 2),
        "children": number (default 0),
        "currency": "CAD",
        "gl": "us",
        "hl": "en"
    }}

    Input sentence:
    \"""{user_input}\"""
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

    # --- Current date to verify is user inputted a past date ---
    today = datetime.today().date()

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
    
    check_in = normalize_date(data.get("check_in_date"), None)
    check_out = normalize_date(data.get("check_out_date"), None)

    # if check_out == None:
    #     check_out = check_in + timedelta(days=1)

    # Ensure checkout is after checkin if checkout date not mentioned
    if check_out <= check_in:
        check_out = check_in + timedelta(days=1)

    # Write back normalized ISO strings
    data["check_in_date"] = check_in.isoformat()
    data["check_out_date"] = check_out.isoformat()

    # Other safe defaults
    data["adults"] = data.get("adults")
    data["children"] = data.get("children")
    data["currency"] = data.get("currency", "CAD")
    data["gl"] = data.get("gl", "us")
    data["hl"] = data.get("hl", "en")

    return data
