import ast
import os
import re
import json
from typing import Dict
from dotenv import load_dotenv
from sympy.physics.units import temperature
from openai import OpenAI

from src.models.flights_model import FlightsListSearchRequest, FlightInfoRequest

load_dotenv()
OPEN_AI_KEY = os.getenv('OPENAI_API_KEY_OTHER')

class FlightQueryParser:
    def __init__(self):
        # Use OpenAI model
        self.client = OpenAI(api_key=OPEN_AI_KEY)
        self.model = "gpt-4o-mini"

    def normalize_flight_input(self, raw_fields: dict) -> FlightsListSearchRequest:
        prompt = f"""
        You are a flight input normalization model. Reformat these flight search parameters for a valid Amadeus API input parameters.
        {raw_fields}

        ### RULES
        - The date can appear in many forms (e.g., "January 2nd 2026", "02/01/2026", "2026-01-02"). 
          Convert it to the format YYYY-MM-DD.
        - Map city names to their IATA airport codes (e.g. Toronto -> YYZ, New York -> JFK, Paris -> CDG, Algiers -> ALG, Doha -> DOH)
        - Convert airline names to their IATA airline code (e.g. air canada -> AC, air france -> AF, air algerie -> AH, qatar airways -> QR)
        - If the user doesn’t specify a field, use defaults:
          - currency: "CAD"
          - cabin_class: "Economy"
          - adults: 1
          - children: 0
          - infants: 0
          - airline: ""
        - Output must be valid JSON ONLY — no Python dict, no extra text.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise flight input normalizer"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )

        result = response.choices[0].message.content.strip()
        print("Model output", result)

        try:
            result_dict = json.loads(result)
        except json.JSONDecodeError:
            print("Error parsing flight input, falling back to defaults")
            result_dict = {}

        normalized_result_dict = {
            "departure_airport": result_dict.get('departureAirport', raw_fields.get('departure_airport', '')).upper(),
            "arrival_airport": result_dict.get('arrivalAirport', raw_fields.get('arrival_airport', '')).upper(),
            "departure_date": result_dict.get('departureDate', raw_fields.get('departure_date', '')).replace(" ", "-"),
            "cabin_class": result_dict.get('cabinClass', raw_fields.get('cabin_class', 'Economy')),
            "currency": result_dict.get('currency', raw_fields.get('currency', 'CAD')).upper(),
            "adults": int(result_dict.get('adults', raw_fields.get('adults', 1))),
            "children": int(result_dict.get('children', raw_fields.get('children', 0))),
            "infants": int(result_dict.get('infants', raw_fields.get('infants', 0))),
            "airline": result_dict.get('airline', raw_fields.get('airline', ''))
        }

        return FlightsListSearchRequest(**normalized_result_dict)



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