
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


