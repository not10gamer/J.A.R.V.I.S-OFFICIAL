import os
from googleapiclient.discovery import build
from langchain_core.tools import tool

@tool
def google_custom_search(query: str) -> str:
    """
    Performs a web search using Google Custom Search API and returns the results.
    This tool is useful for finding current information on the internet.
    Requires GOOGLE_API_KEY and GOOGLE_CSE_ID to be set in environment variables.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        return "Error: GOOGLE_API_KEY or GOOGLE_CSE_ID not found. Please set the environment variables."

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id).execute()
        
        search_results = []
        if 'items' in res:
            for item in res['items']:
                search_results.append({
                    "title": item.get('title'),
                    "link": item.get('link'),
                    "snippet": item.get('snippet')
                })
        
        return str(search_results)
    except Exception as e:
        return f"An error occurred during Google Custom Search: {e}"
