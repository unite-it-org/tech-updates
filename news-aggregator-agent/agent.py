"""
News Aggregator Agent
Fetches, filters, and formats news from NewsAPI into HTML templates.
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Annotated, Optional
import httpx
from dateutil.relativedelta import relativedelta

# Agent Framework imports
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient


# Configuration from agent_news_aggregator.md
NEWS_API_KEY = "1ca9068869d14e7285a539bb0a7c7cf4"
NEWS_API_BASE_URL = "https://newsapi.org/v2"
CATEGORIES = ["Artificial Intelligence", "AUTOMOTIVE", "INFORMATION TECHNOLOGY", "SCIENCE", "ART"]
ARTICLE_COUNT = 15
LANGUAGE = "en"

# Template paths
STATIC_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "month_template_year.html")
CONTENT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "news_content.html")
OUTPUT_DIR = os.path.dirname(__file__)

# Safety filter keywords
BLOCKED_KEYWORDS = ["NSFW", "Adult", "adult", "nsfw", "explicit", "violence", "profanity"]


def get_current_month_year() -> tuple[str, str]:
    """Get current month (3-letter) and year (2-digit)."""
    now = datetime.now()
    month = now.strftime("%b")  # Jan, Feb, Mar, etc.
    year = now.strftime("%y")   # 25, 26, 27
    return month, year


def is_safe_article(article: dict) -> bool:
    """Check if article is family-friendly."""
    title = article.get("title", "") or ""
    description = article.get("description", "") or ""
    content = article.get("content", "") or ""
    
    combined_text = f"{title} {description} {content}".lower()
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in combined_text:
            return False
    
    # Check for suggestive clickbait patterns
    clickbait_patterns = ["clickbait", "shocking", "you won't believe"]
    for pattern in clickbait_patterns:
        if pattern in combined_text:
            return False
    
    return True


def load_static_template() -> str:
    """Load the static HTML template (month_template_year.html)."""
    with open(STATIC_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_content_template() -> str:
    """Load the dynamic content template (news_content.html)."""
    with open(CONTENT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_output_filename(month: str, year: str) -> str:
    """Generate output filename with version handling."""
    base_filename = f"{month}-{year}.html"
    filepath = os.path.join(OUTPUT_DIR, base_filename)
    
    if not os.path.exists(filepath):
        return base_filename
    
    # Find next available version
    version = 1
    while True:
        versioned_filename = f"{month}-{year}-v{version}.html"
        filepath = os.path.join(OUTPUT_DIR, versioned_filename)
        if not os.path.exists(filepath):
            return versioned_filename
        version += 1


def format_article_in_content_template(article: dict) -> str:
    """Replace template placeholders in news_content.html with article data."""
    title = article.get("title", "No Title")
    author = article.get("author") or "Unknown"
    source = article.get("source", {}).get("name", "Unknown Source")
    description = article.get("description") or "No description available."
    url_to_image = article.get("urlToImage") or ""
    url = article.get("url", "#")
    published_at = article.get("publishedAt", "")
    
    # Format date
    try:
        date_obj = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        formatted_date = date_obj.strftime("%b %d, %Y")
    except:
        formatted_date = published_at
    
    # Load content template for each article
    content_template = load_content_template()
    
    replacements = {
        "{{TITLE}}": title,
        "{{AUTHOR}}": author,
        "{{SOURCE}}": source,
        "{{SUMMARY}}": description,
        "{{IMAGE_URL}}": url_to_image,
        "{{LINK}}": url,
        "{{DATE}}": formatted_date,
    }
    
    result = content_template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    
    return result


def format_static_template(news_content: str, month: str, year: str) -> str:
    """Replace placeholders in month_template_year.html with content and metadata."""
    static_template = load_static_template()
    
    replacements = {
        "{{NEWS_CONTENT}}": news_content,
        "{{CURRENT_MONTH}}": month,
        "{{CURRENT_YEAR}}": year,
    }
    
    result = static_template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    
    return result


async def fetch_news(category: str) -> list[dict]:
    """Fetch news for a specific category from NewsAPI."""
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Use 'everything' endpoint which properly supports search queries
    params = {
        "apiKey": NEWS_API_KEY,
        "q": category,
        "language": LANGUAGE,
        "sortBy": "publishedAt",
        "pageSize": 10,
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{NEWS_API_BASE_URL}/everything",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])
            else:
                print(f"Error fetching {category}: {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception fetching {category}: {e}")
            return []


async def fetch_all_news() -> list[dict]:
    """Fetch news from all categories."""
    tasks = [fetch_news(cat) for cat in CATEGORIES]
    results = await asyncio.gather(*tasks)
    
    # Flatten and deduplicate
    all_articles = []
    seen_urls = set()
    
    for articles in results:
        for article in articles:
            url = article.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(article)
    
    return all_articles


def filter_articles(articles: list[dict]) -> list[dict]:
    """Filter articles for family-friendly content."""
    return [article for article in articles if is_safe_article(article)]


async def generate_news_html() -> str:
    """Main function to fetch, filter, and generate HTML."""
    print("Fetching news from NewsAPI...")
    articles = await fetch_all_news()
    
    print(f"Fetched {len(articles)} articles, filtering for family-friendly content...")
    filtered_articles = filter_articles(articles)
    
    # Take the top articles (up to ARTICLE_COUNT)
    selected_articles = filtered_articles[:ARTICLE_COUNT]
    print(f"Selected {len(selected_articles)} safe articles")
    
    if not selected_articles:
        return "<p>No articles available at this time.</p>"
    
    # Get current month/year
    month, year = get_current_month_year()
    
    # Generate HTML content for each article using news_content.html
    html_blocks = []
    for article in selected_articles:
        html_block = format_article_in_content_template(article)
        html_blocks.append(html_block)
    
    # Join all article content blocks
    news_content = "\n\n".join(html_blocks)
    
    # Insert into static template (month_template_year.html)
    final_html = format_static_template(news_content, month, year)
    
    return final_html


async def run_news_aggregator() -> None:
    """Run the news aggregator and save output."""
    html_content = await generate_news_html()
    
    # Generate output filename
    month, year = get_current_month_year()
    filename = generate_output_filename(month, year)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"News aggregated successfully! Output saved to: {filename}")


# Tool function for the agent
async def get_tech_news(
    category: Annotated[str, "The news category to fetch (AI, Automotive, IT, Science, Art)"] = "AI"
) -> str:
    """
    Fetch technology news from NewsAPI for a specific category.
    Returns formatted HTML with family-friendly articles.
    """
    global CATEGORIES
    original_categories = CATEGORIES.copy()
    CATEGORIES = [category]
    
    try:
        html_content = await generate_news_html()
        return html_content
    finally:
        CATEGORIES = original_categories


# Agent instructions
AGENT_INSTRUCTIONS = """You are a specialized News Curation Agent. Your goal is to fetch the latest high-quality news from newsapi.org, filter it for family-friendly content, and format it into a specific HTML structure.

When asked for a news update:
1. Use the get_tech_news tool to fetch news
2. The tool automatically applies safety filters (removes adult content, violence, profanity)
3. Returns HTML formatted articles ready for display

You can specify a category: AI, AUTOMOTIVE, INFORMATION TECHNOLOGY, SCIENCE, or ART.
If no category is specified, it fetches from all categories."""


async def create_agent():
    """Create and return the news aggregator agent using OpenAI SDK with Gemini API."""
    # Use OpenAI client with Gemini API endpoint
    client = OpenAIChatClient(
        api_key=os.environ.get("GEMINI_API_KEY", ""),
        model="gemini-2.0-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    agent = Agent(
        client=client,
        instructions=AGENT_INSTRUCTIONS,
        tools=[get_tech_news],
    )
    
    return agent


async def main():
    """Main entry point for CLI usage."""
    # Run the news aggregator directly
    await run_news_aggregator()


if __name__ == "__main__":
    asyncio.run(main())