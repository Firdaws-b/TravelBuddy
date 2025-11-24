import os
import re
import json
from typing import Dict
from dotenv import load_dotenv
from sympy.physics.units import temperature
from openai import OpenAI

from src.models import FlightsListSearchRequest, FlightInfoRequest

load_dotenv()
open_ai_key = os.getenv("OPENAI_CLIENT_ID")

class FlightQueryParser:
    def __init__(self):
        # Use OpenAI model
        self.client = OpenAI(api_key=open_ai_key)
        self.model = "gpt-4o-mini"

    def parse_query_flights_list(self, query: str) -> FlightsListSearchRequest:
        prompt = f"""
        Extract the following flight search parameters from the user query and return a valid JSON object.

        The JSON must always include these keys:
        departure_airport, arrival_airport, departure_date (YYYY-MM-DD), cabin_class, currency, adults, children, infants, airline.

        ### RULES
        - The date can appear in many forms (e.g., "January 2nd 2026", "02/01/2026", "2026-01-02"). 
          Convert it to the format **YYYY-MM-DD**.
        - Convert numbers from text to integers (e.g., two -> 2, one -> 1, three->3, four->4..etc). 
        - Convert airline names to their IATA ailine code (e.g. air canada -> AC, air france -> AF, air algerie -> AH, qatar airways -> QR)
        - If the user doesn’t specify a field, use defaults:
          - currency: "CAD"
          - cabin_class: "Economy"
          - adults: 1
          - children: 0
          - infants: 0
          - airline: ""
        - Output must be valid JSON — no extra text, no explanations.

        ### Example:
        Query: I want to fly from Toronto to New York on 25th December 2023 in Business class for two adults and one child with air canada.
        Output:
        {{"departure_airport": "YYZ", "arrival_airport": "JFK", "departure_date": "2023-12-25", "cabin_class": "Business", "currency": "CAD", "adults": 2, "children": 1, "infants": 0, "airline":"AC"}}

        Now parse this query:
        {query}

        Output a valid JSON object only:
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", "content": "You are a precise data extraction model that outputs valid JSON only"
                },
                {
                    "role": "user", "content": prompt
                },

            ],
            temperature=0,
        )


        result = response.choices[0].message.content.strip()
        print("Model output", result)

        # Fix the output to ensure it's a valid JSON
        result_fixed = re.sub(r'"\s+"', '", "', result)  # Remove spaces between quotes
        result_fixed = result.replace(';', ',')  # Replace semicolons with commas
        if not result_fixed.startswith('{'):
            result_fixed = "{" + result_fixed
        if not result_fixed.endswith('}'):
            result_fixed = result_fixed + "}"
        print("Fixed output", result_fixed)

        # Parse the output JSON
        try:
            data_json = json.loads(result_fixed)
        except json.JSONDecodeError:
            # Default values in case parsing fails
            data_json = {
                "departure_airport": "",
                "arrival_airport": "",
                "departure_date": "%Y-%m-%d",
                "cabin_class": "Economy",
                "currency": "CAD",
                "adults": 1,
                "children": 0,
                "infants": 0,
                "airline": "",
            }

        return FlightsListSearchRequest(
            departure_airport=data_json.get("departure_airport", ""),
            arrival_airport=data_json.get("arrival_airport", ""),
            departure_date= data_json.get("departure_date", ""),
            cabin_class=data_json.get("cabin_class", "Economy").upper().replace(" ", "_"),
            currency=data_json.get("currency", "CAD"),
            adults=data_json.get("adults", "1"),
            children=data_json.get("children", "0"),
            infants=data_json.get("infants", "0"),
            airline=data_json.get("airline", ""),
        )
    # this function extracts inputs from the query related to flights info.
    def parse_query_flight_info(self, query: str)-> FlightInfoRequest:
        prompt = f"""
        Extract the following flight search parameters from the user query and return a valid JSON object.
        The JSON must always include these keys:
        - flight_number (eg. 33, 839, 2500)
        - airline (eg. AC, AF, AH, QR)
        - departure_date (YYYY-MM-DD)
        ### RULES TO FOLLOW: 
        - The date can appear in many forms (e.g., "January 2nd 2026", "02/01/2026", "2026-01-02"). 
          Convert it to the format **YYYY-MM-DD**.
        - Output must be valid JSON — no extra text, no explanations.
        - If flight_number and airline are attached, detach the flight number from the airline such as AC33 
        should be flight_number: "33" and airline: "air canada".
        
        ### Example: 
        Query: Show me flight AC33 on December 3rd, 2025
        Output:
        {{ "airline": "AC", "flight_number":33, "departure_date": "2025-12-03"}}
        
        Now parse this query:
        {query}
        Output a valid JSON object only:
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", "content": "You are a precise data extraction model that outputs valid JSON only"
                },
                {
                    "role": "user", "content": prompt
                },

            ],
            temperature=0,
        )
        result = response.choices[0].message.content.strip()
        print("Model output", result)
        # Now let's parse the output JSON
        try:
            data_json = json.loads(result)
        except json.JSONDecodeError:
        # Default values in case the parsing fails
            data_json = {
                "airline": "",
                "flight_number": "",
                "departure_date": ""
            }
        return FlightInfoRequest(
            flight_number=str(data_json.get("flight_number", "")),
            airline=data_json.get("airline", ""),
            departure_date=data_json.get("departure_date", ""),
        )

    # parser to extract booking id from the query
    def parse_query_booking_id(self, query: str) -> str:
        prompt = f"""
        Extract the booking_id from the user query and return a valid JSON object.
        The JSON must always include this key:
        - booking_id (eg. a UUID string like "123e4567-e89b-12d3-a456-426614174000")
        
        ### RULES TO FOLLOW: 
        - Output must be valid string
        
        ### Example: 
        Query: I want to cancel my booking with id 123e4567-e89b-12d3-a456-426614174000
        Output:
        {{ "booking_id": "123e4567-e89b-12d3-a456-426614174000"}}
        
        Now parse this query:
        {query}
        Output a valid JSON object only:
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", "content": "You are a precise data extraction model that outputs valid JSON only"
                },
                {
                    "role": "user", "content": prompt
                },

            ],
            temperature=0,
        )
        result = response.choices[0].message.content.strip()
        print("Model output", result)
        # Now let's parse the output JSON
        try:
            data_json = json.loads(result)
            booking_id = data_json.get("booking_id", "")
        except json.JSONDecodeError:
            booking_id = ""
        return booking_id