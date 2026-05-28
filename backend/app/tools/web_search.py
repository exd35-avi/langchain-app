from langchain.tools import tool
import requests
@tool
def web_search(query: str) -> str:
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data['query']['search']:
                title = data['query']['search'][0]['title']
                return f"Web search result for '{query}': Found '{title}' on Wikipedia. For details, check industry sources."
        return f"I searched the web for '{query}' but found no inventory-related information."
    except Exception as e:
        return f"Web search unavailable: {e}. Could not find info on '{query}'."
