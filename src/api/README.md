# BioAI-Lab API

FastAPI-based backend service for BioAI-Lab platform.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
api/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── api/              # API routes
│   ├── core/             # Core logic
│   └── ai/               # AI models
├── tests/                # Tests
└── requirements.txt      # Dependencies
```

## Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/bioai
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
DEBUG=true
```
