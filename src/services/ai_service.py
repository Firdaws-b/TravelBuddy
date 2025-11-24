# Handle AI integration: gpt and langchain
import json
import os

from src.models.trip_model import ItineraryDayModel

OPEN_AI_KEY = os.getenv('OPENAI_API_KEY')
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


async def generate_itinerary(destination: str, duration:float, number_of_travelers: int, budget: int):
    template = """
    You are a professional travel planner. 
    Create a detailed day-by-day travel itinerary for a trip to {destination} lasting {duration} days.
    for {number_of_travelers} people, with a total budget of ${budget}.
    Include morning, afternoon and evening activities each day. Do not include hotels or restaurants recommendations. 
    Only list of activities to do along their cost per traveler. You should strictly follow this format. 
    Do not deviate. Similar to this 
 

    Output the result as a valid JSON with the following JSON format:
     
        "destination": "{destination}",
        "duration": {duration},
        "number_of_travelers": {number_of_travelers},
        "budget": {budget},
        "itinerary": [
            
                "day": 1,
                "activities": ["...", "..."]
        ]
    
    """

    prompt = PromptTemplate.from_template(template)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o",temperature=0)

    # Create chain
    chain = prompt | llm

    response = chain.invoke({"destination":destination,
                           "duration":duration,
                           "number_of_travelers":number_of_travelers,
                           "budget":budget})
    output = response.content.replace("```json","")
    output = output.replace("```","")
    data = json.loads(output)
    print(data)
    itinerary = validate_response_str(data)
    itinerary_model = [ItineraryDayModel(**item) for item in itinerary]
    return itinerary_model



def validate_response_str(data):
    validation_keys = ['destination', 'duration', 'number_of_travelers','budget', 'itinerary']
    day_keys = ["day", "activities"]
    # if not isinstance(data, str):
    #     return False
    for key in validation_keys:
        if key not in data:
            if key == "itinerary":
                data[key] = []
            else:
                data[key] = locals()[key]
    if not isinstance(data['itinerary'], list):
        data["itinerary"] = [{"day": 1, "activities": [str(data["itinerary"])]}]

    # Fix Each day entry
    fixed_itinerary = []
    for i, day_entry in enumerate(data['itinerary'], start=1):
        if not isinstance(day_entry, dict):
            day_entry = {"day": i, "activities": [str(day_entry)]}
        else:
            for key in day_keys:
                if key not in day_entry:
                    if key == "day":
                        day_entry[key] = i
                    else:
                        day_entry[key] = []
        fixed_itinerary.append(day_entry)
    data['itinerary'] = fixed_itinerary
    print(data['itinerary'])
    return data['itinerary']

# regeneration function for generated itinerary based on user's feedback
async def regenerate_itinerary(previous_trip, user_feedback: str):
    destination = previous_trip['destination']
    duration = previous_trip['duration']
    number_of_travelers = previous_trip['number_of_travelers']
    overall_budget = previous_trip['overall_cost']

    template = """
    You are a professional travel planner. The user previously asked you to generate a day-by-day itinerary, 
    but they did not like it. Your task is to modify or regenerate the itinerary based on their feedback.

    -------------------------
    PREVIOUS ITINERARY
    {previous_trip}
    -------------------------

    USER FEEDBACK
    {user_feedback}
    -------------------------

    TRIP DETAILS
    Destination: {destination}
    Duration: {duration} days
    Number of travelers: {number_of_travelers}
    Total budget: ${overall_budget}
    -------------------------

    INSTRUCTIONS
    - Modify or regenerate the itinerary so that it addresses the user’s feedback.
    - You MUST respect the trip details (destination, duration, travelers, budget).
    - Do NOT include hotels or restaurants.
    - For each day, include morning, afternoon, and evening activities.
    - Each activity MUST include a cost per traveler.
    - Make sure the new itinerary is meaningfully different from the previous one.


    OUTPUT FORMAT
    Output the result as a valid JSON with the following JSON format:
     
        "destination": "{destination}",
        "duration": {duration},
        "number_of_travelers": {number_of_travelers},
        "budget": {overall_budget},
        "itinerary": [
            
                "day": 1,
                "activities": ["...", "..."]
        ]
    

    Only produce JSON. No explanations, no commentary.
    """

    prompt = PromptTemplate.from_template(template)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Create chain
    chain = prompt | llm

    response = chain.invoke({"destination": destination,
                             "duration": duration,
                             "number_of_travelers": number_of_travelers,
                             "overall_budget": overall_budget,
                            "previous_trip": previous_trip,
                             "user_feedback": user_feedback})
    output = response.content.replace("```json", "")
    output = output.replace("```", "")
    data = json.loads(output)
    print(data)
    itinerary = validate_response_str(data)
    itinerary_model = [ItineraryDayModel(**item) for item in itinerary]
    return itinerary_model


    # # check itinerary structure
    # itinerary = data['itinerary']
    # if not isinstance(itinerary, list):
    #     print("Invalid response from OpenAI, itinerary must be a list")
    #     return False
    #
    # for day_entry in itinerary:
    #     if not isinstance(day_entry, dict):
    #         print("Invalid response from OpenAI, day entry must be a dict")
    #         return False
    #     for key in day_keys:
    #         if key not in day_entry:
    #             print("Invalid response from OpenAI, key '{}' must be a dict".format(key))
    #             return False
    #         if not isinstance(day_entry["activities"], list):
    #             print("Invalid response from OpenAI, key '{}' must be a list".format(key))
    #             return False


















