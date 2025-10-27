# Handle AI integration: gpt and langchain
import json
import os
OPEN_AI_KEY = os.getenv('OPENAI_API_KEY')
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


async def generate_itinerary(destination: str, duration:float, number_of_travelers: int, budget: int):
    template = f"""
    You are a professional travel planner. 
    Create a detailed day-by-day travel itinerary for a trip to {destination} lasting {duration} days.
    for {number_of_travelers} people, with a total budget of ${budget}.
    Include morning, afternoon and evening activities each day. Do not include hotels or restaurants recommendations. 
    Only list of activities to do along their cost per traveler. 
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

    print("Planned trip ",response.text())








