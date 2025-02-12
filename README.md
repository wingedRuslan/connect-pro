## ConnectPro

ConnectPro is an intelligent networking assistant that analyzes LinkedIn profiles to generate personalized conversation starters and insights. It crafts more meaningful and engaging networking interactions by providing tailored discussion points based on a person's story and professional background. 

### Features

- :mag: Smart LinkedIn profile search using name, company, or position
- :bar_chart: In-depth profile analysis using OpenAI LLM
- :bulb: Generation of professional insights and conversation starters 
- :sparkles: Simple UI React frontend
- :zap: Fast and reliable FastAPI backend 


### Tech Stack

#### Frontend:
- React
- Modern CSS with responsive design
- Real-time profile analysis interface

#### Backend:
- FastAPI (Python 3.13)
- LangChain for AI orchestration
- Integration with OpenAI, Proxycurl (Linkedin Scraper), and Tavily APIs (Search Tool)


### Run Locally

Clone the project
```
git clone https://github.com/yourusername/connect-pro.git
cd connect-pro
```

Backend Setup

1. Set up Python environment with Poetry
```
poetry install
poetry shell
```

2. Create .env file in project root: 

`.env.example` provides the detailed overview of the env vars needed to run the project.

```
OPENAI_API_KEY=your_openai_key
PROXYCURL_API_KEY=your_proxycurl_key
TAVILY_API_KEY=your_tavily_key
OPENAI_MODEL_NAME=gpt-4-turbo-preview  # or your preferred model
```

3. Start the backend server
```
cd src
uvicorn connect_pro.app:app --reload --port 8000
```

Frontend Setup

1. Install dependencies
```
cd frontend
npm install
```

2. Start the development server
```
npm start
```
The app will be available at http://localhost:3000.

### API Reference

Analyze Profile
POST /api/analyze

| Parameter | Type | Description |
|---|---|---|
| query | string | Search query (e.g., "John Smith Software Engineer Google") |

### Environment Variables

The following environment variables are required:
| Variable | Description |
|---|---|
| OPENAI_API_KEY | Your OpenAI API key |
| PROXYCURL_API_KEY | Your Proxycurl API key for LinkedIn data access |
| TAVILY_API_KEY | Your Tavily API key for web search |
| OPENAI_MODEL_NAME | OpenAI model to use (default: gpt-4-turbo-preview) |


### Development
The project uses several development tools:

- Black for code formatting
- isort for import sorting
- mypy for type checking
- pytest for testing

