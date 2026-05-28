import httpx
from langchain_openai import ChatOpenAI
from ..config import settings
http_client = httpx.Client(verify=False)
def get_llm(temperature=0.3):
    return ChatOpenAI(
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        http_client=http_client,
        temperature=temperature,
    )
