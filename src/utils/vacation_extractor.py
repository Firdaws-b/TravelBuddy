import os
import re
import json
from dateparser import parse as parse_date
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
OPEN_AI_KEY = os.getenv('OPENAI_API_KEY_OTHER')
client = OpenAI(api_key=OPEN_AI_KEY)


def rule_extract(text: str):

    extracted = {}

    # Cities
    city_match = re.findall(r"(?:in|to|from)\s+([A-Za-z\s]+)", text)
    if city_match:
        extracted["cities"] = list({c.strip() for c in city_match})

    # Dates
    date_matches = re.findall(r"(\b\w+\s+\d{1,2}(?:,\s*\d{4})?)", text)
    if date_matches:
        parsed = []
        for d in date_matches:
            dt = parse_date(d)
            if dt:
                parsed.append(dt.date().isoformat())
        extracted["dates"] = parsed

    # Travelers
    adults = re.search(r"(\d+)\s+adults?", text)
    if adults:
        extracted["adults"] = int(adults.group(1))

    children = re.search(r"(\d+)\s+children", text)
    if children:
        extracted["children"] = int(children.group(1))

    return extracted


def llm_complete(user_input: str, partial: dict, schema_name: str):
    prompt = f"""
    You are a strict information extractor.

    User query:
    "{user_input}"

    Partially extracted JSON:
    {partial}

    Fill ONLY the missing fields required for a valid '{schema_name}' object.
    

    SCHEMA:
    - trip:
        destination (string)
        budget (number)
        duration (int)
        number_of_travelers (int)
        date (YYYY-MM-DD)

    - flight:
        departure_airport (string)
        arrival_airport (string)
        departure_date (YYYY-MM-DD)
        cabin_class (string)
        adults (int)
        children (int)
        infants (int)

    - hotel:
        destination (string)
        check_in (YYYY-MM-DD)
        check_out (YYYY-MM-DD)
        guests (int)
    
    
    The following are some examples: 
    Example 1:
    User query: "I want to travel to Los Angeles for 5 days with a budget of 2000 CAD for 2 people, fly from Montreal to Los Angeles on 2025-01-01 in economy, and book a hotel from 2025-01-01 to 2025-01-05 for 2 guests"
    Output:
    {{
    "trip": {{"destination": "Los Angeles", "budget": 2000, "duration": 5, "number_of_travelers": 2, "date": "2025-01-01"}},
    "flight": {{"departure_airport": "Montreal", "arrival_airport": "Los Angeles", "departure_date": "2025-01-01", "cabin_class": "Economy", "adults": 2, "children": 0, "infants": 0}},
    "hotel": {{"destination": "Los Angeles", "check_in": "2025-01-01", "check_out": "2025-01-05", "guests": 2}}
    }}
    Example 2:
    User query: "Plan a short 3-day trip to Kyoto for 1 traveler with a 1000 CAD budget, flight from YUL to KIX on 2025-10-05 in business class, and hotel stay from 2025-10-05 to 2025-10-08"
    Output:
    {{
    "trip": {{"destination": "Kyoto", "budget": 1000, "duration": 3, "number_of_travelers": 1, "date": "2025-10-05"}},
    "flight": {{"departure_airport": "YUL", "arrival_airport": "KIX", "departure_date": "2025-10-05", "cabin_class": "Business", "adults": 1, "children": 0, "infants": 0}},
    "hotel": {{"destination": "Kyoto", "check_in": "2025-10-05", "check_out": "2025-10-08", "guests": 1}}
    }}
    Example 3:
    User query: "I want a family trip to Rio de Janeiro, 5 days for 2 adults and 1 child, flying from YUL to GIG on 2025-11-20 in economy, and staying in a hotel from 2025-11-20 to 2025-11-25"
    Output:
    {{
    "trip": {{"destination": "Rio de Janeiro", "budget": 3000, "duration": 5, "number_of_travelers": 3, "date": "2025-11-20"}},
    "flight": {{"departure_airport": "YUL", "arrival_airport": "GIG", "departure_date": "2025-11-20", "cabin_class": "Economy", "adults": 2, "children": 1, "infants": 0}},
    "hotel": {{"destination": "Rio de Janeiro", "check_in": "2025-11-20", "check_out": "2025-11-25", "guests": 3}}
    }}

    Example 4:
    User query: "Book a trip to London for 7 days for 2 adults and 2 children, with a budget of 4000 CAD, flight from Montreal to LHR on 2025-06-15 in economy, and a hotel from 2025-06-15 to 2025-06-22 for 4 guests"
    Output:
    {{
    "trip": {{"destination": "London", "budget": 4000, "duration": 7, "number_of_travelers": 4, "date": "2025-06-15"}},
    "flight": {{"departure_airport": "Montreal", "arrival_airport": "LHR", "departure_date": "2025-06-15", "cabin_class": "Economy", "adults": 2, "children": 2, "infants": 0}},
    "hotel": {{"destination": "London", "check_in": "2025-06-15", "check_out": "2025-06-22", "guests": 4}}
    }}

    Example 5:
    User query: "I want to travel to Paris for 7 days with a budget of 3500 CAD for 3 people, fly from YUL to CDG on 2025-06-15 in business class, and reserve a hotel from 2025-06-15 to 2025-06-22 for 3 guests"
    Output:
    {{
    "trip": {{"destination": "Paris", "budget": 3500, "duration": 7, "number_of_travelers": 3, "date": "2025-06-15"}},
    "flight": {{"departure_airport": "YUL", "arrival_airport": "CDG", "departure_date": "2025-06-15", "cabin_class": "Business", "adults": 3, "children": 0, "infants": 0}},
    "hotel": {{"destination": "Paris", "check_in": "2025-06-15", "check_out": "2025-06-22", "guests": 3}}
    }}

    Output MUST be valid JSON. No extra text.
    """



    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content.strip())


def hybrid_extract(user_input: str, schema_name: str):
    rules = rule_extract(user_input)  # Step 1: rule-based
    llm_filled = llm_complete(user_input, rules, schema_name)  # Step 2: LLM completes
    return llm_filled
