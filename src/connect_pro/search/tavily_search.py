from typing import Dict, List, Optional
from tavily import TavilyClient
from connect_pro.config.settings import settings


def get_profile_data_search_tavily(search_query: str) -> Optional[List[Dict]]:
    """
    Search for a LinkedIn profile URL using Tavily's search API.
    
    Args:
        search_query: search query incl. name of the person to search for
    
    Returns:
        Optional[List[Dict]]: LinkedIn profile URLs if found, None otherwise
    """
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    try:
        search_query = f"{search_query} linkedin profile"
        raw_results = client.search(
            query=search_query,
            search_depth="basic",
            max_results=5
        )

        # Filter and keep only LinkedIn profile URLs with their titles
        search_results = [
            {
                "url": result.get("url", "").strip(),
                "title": result.get("title", "").strip()
            }
            for result in raw_results.get("results", [])
            if "linkedin.com/in/" in result.get("url", "")
        ]
        return search_results
    
    except Exception as e:
        print(f"Error searching Tavily: {e}")
        return None
