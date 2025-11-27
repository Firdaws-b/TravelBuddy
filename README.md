## 🧳 TravelBuddy
## **Description**: 
TravelBuddy is a cloud-based, AI-driven travel planning SaaS that helps users generate complete trip itineraries, search flights, hotels, transportation, and activities through a unified microservices architecture.
The platform uses OpenAI models, LangChain, distributed orchestration, and modern DevOps practices to deliver consistent, scalable, real-time travel planning.

## **Microservices**
TravelBuddy is built on a modular service architecture:
Trips Service – create, update, and store trips
Flights Service – flight search via Amadeus API
Hotels Service – hotel search using RapidAPI
Activities Service – location-based activities & points of interest
Vacation aka Orchestrator Service (optional coordinator) – orchestrates workflows across services

## **Cloud & DevOps**
- ☁️ Full cloud deployment on AWS EC2
- 🐳 Dockerized services
- 🔄 GitHub Actions CI/CD pipeline (automatic build & deployment)
- 🔐 Encrypted service-level API keys (per service

## ⚙️ Tech Stack
Backend
- Python, FastAPI
- LangChain + OpenAI (GPT-4o/4o mini)
- httpx (async client)
- MongoDB (NoSQL)
   
Frontend: 
- SwaggerHub: Deployed SaaS: http://3.19.14.187:8000/docs 
   
Cloud:
- AWS EC2
- Docker
- Github Actions
   
## Setup Instructions: 
## 1. Create and Activate a Virtual Environment

It’s recommended to use a virtual environment to isolate project dependencies.

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

## 2. Install Dependencies

### Runtime Dependencies
```bash
pip install -r requirements.txt
```

### Testing Dependencies
```bash
pip install -r test-requirements.txt
```

## Run the FastAPI App
```bash
uvicorn main:app --reload
```

## Swagger UI

Access the interactive API documentation at:

```
http://127.0.0.1:8000/docs
```

## Run Tests
```bash
pytest -v
```


