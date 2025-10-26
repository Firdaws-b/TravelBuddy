from datetime import datetime
import torch
import json

from pydantic.v1.datetime_parse import parse_date
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from src.schemas import FlightSearchRequest

# Load a pre-trained model from Hugging Face
model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def parse_input(query: str) -> FlightSearchRequest:
    prompt = (
        "Extract the following search parameters from the user query "
        "and return them as a JSON object matching the FlightSearchRequest schema: "
        "departure_airport, arrival_airport, departure_date (YYYY-MM-DD), cabin_class, currency, "
        "adults, children, infants.\n\n"
        "Use the example below as a reference for airport codes and formatting. "
        "Toronto -> YYZ \n"
        "New York -> JFK \n"
        "Los Angeles -> LAX \n"
        "London -> LHR \n"
        "Paris -> CDG \n"
        "Montreal -> YUL \n"
        "Algiers -> ALG \n"
        "Follow this example format:\n"
        "Query: I want to fly from Toronto to New York on 2023-12-25 in Business class for 2 adults and 1 child.\n"
        "Output: {\"departure_airport\": \"YYZ\", \"arrival_airport\": \"JFK\", "
        "\"departure_date\": \"2023-12-25\", \"cabin_class\": \"Business\", \"currency\": \"CAD\", "
        "\"adults\": 2, \"children\": 1, \"infants\": 0}\n\n"
        f"Now, parse this query: {query}\n"
        "Output:"
    )

    # Tokenize the input
    tokenized_input = tokenizer(prompt, return_tensors="pt")

    # Generate output
    output_text = model.generate(**tokenized_input, max_length=512)
    result = tokenizer.decode(output_text[0], skip_special_tokens=True)
    print("Model output", result)
    # Parse the output JSON
    try:
        data_json = json.loads(result)
    except json.JSONDecodeError:
        # Default values in case parsing fails
        data_json = {
            "departure_airport": "",
            "arrival_airport": "",
            "departure_date": datetime.today().strftime("%Y-%m-%d"),
            "cabin_class": "Economy",
            "currency": "CAD",
            "adults": 1,
            "children": 0,
            "infants": 0,
        }

    # Parse the date safely
    dep_date = data_json.get("departure_date")
    try:
        if dep_date:
            dep_date = parse_date(dep_date).date()
        else:
            dep_date = datetime.today().date()
    except Exception:
        dep_date = datetime.today().date()

    return FlightSearchRequest(
        departure_airport=data_json.get("departure_airport", ""),
        arrival_airport=data_json.get("arrival_airport", ""),
        departure_date=dep_date,
        cabin_class=data_json.get("cabin_class", "Economy"),
        currency=data_json.get("currency", "CAD"),
        adults=data_json.get("adults", 1),
        children=data_json.get("children", 0),
        infants=data_json.get("infants", 0),
    )
