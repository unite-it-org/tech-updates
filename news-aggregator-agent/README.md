# News Aggregator Agent

A specialized AI agent that fetches, filters, and formats news from NewsAPI into HTML templates.

## Overview

This agent follows the specifications in `agent_news_aggregator.md` from the parent directory. It:
- Fetches news from newsapi.org for categories: AI, Automotive, Information Technology, Science, Art
- Filters content for family-friendly articles (removes adult content, violence, profanity)
- Formats articles into HTML using the `month_template_year.html` template
- Outputs HTML files with naming convention `MONTH-YEAR.html` (e.g., `Apr-26.html`)

## Project Structure

```
news-aggregator-agent/
├── agent.py          # Core agent implementation
├── server.py         # HTTP server wrapper (FastAPI)
├── requirements.txt  # Python dependencies
├── .env              # Environment configuration
├── .vscode/
│   ├── launch.json   # Debug configurations
│   └── tasks.json    # Build tasks
└── README.md         # This file
```

## Setup

### 1. Create Virtual Environment

```bash
cd news-aggregator-agent
python3 -m venv venv
```

### 2. Install Dependencies

```bash
./venv/bin/pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env` and add your **Gemini API key** (OpenAI-compatible format):

```
GEMINI_API_KEY=your-gemini-api-key-here
```

> **Note**: Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey). The agent uses the OpenAI-compatible Gemini API endpoint.

## Usage

### Run as HTTP Server (Production)

```bash
./venv/bin/python -m uvicorn server:app --reload --port 8000
```

Then access:
- `http://localhost:8000/` - Root endpoint
- `http://localhost:8000/health` - Health check
- `http://localhost:8000/news` - Fetch all categories
- `http://localhost:8000/news/AI` - Fetch specific category

### Run as CLI (One-time fetch)

```bash
./venv/bin/python agent.py
```

This will fetch news and save to `Apr-26.html` (current month-year).

### Debug in VSCode

Press `F5` to start debugging. Choose from:
- **Python: Server** - Debug the HTTP server
- **Python: Agent (Debug)** - Debug the agent directly

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/news` | Fetch all categories |
| GET | `/news/{category}` | Fetch specific category |

### Request/Response Examples

**POST /news**
```json
{
  "category": "AI"
}
```

**Response**
```json
{
  "success": true,
  "html": "<a href=\"...\">...</a>",
  "filename": "Apr-26.html",
  "article_count": 15
}
```

## Agent Tool

The agent provides a `get_tech_news` tool that can be called with:
- `category`: Optional category (AI, Automotive, IT, Science, Art)

Example usage in agent conversation:
```
User: Get me the latest AI news
Agent: [calls get_tech_news with category="AI"]
```

## Output Files

Generated HTML files are saved to the `news-aggregator-agent/` directory:
- `Apr-26.html` - April 2026
- `Apr-26-v1.html` - Version 1 if file exists

## Safety Filtering

The agent automatically filters out articles containing:
- NSFW/Adult content
- Explicit violence
- Profanity
- Clickbait patterns

## Requirements

- Python 3.10+
- OpenAI API key (for agent functionality)
- NewsAPI key (pre-configured)

## Next Steps

1. **Add Tracing**: Use `aitk-get_tracing_code_gen_best_practices` to add monitoring
2. **Deploy to Foundry**: Use VSCode Command "Microsoft Foundry: Deploy Hosted Agent"
3. **Customize Categories**: Edit `CATEGORIES` in `server.py`
4. **Adjust Filters**: Modify `BLOCKED_KEYWORDS` in `server.py`