import os
from dotenv import load_dotenv
load_dotenv()


class Settings:
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://genailab.tcs.in")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-VDOkoWDmc8LxJK7zXfzKGQ")
    LLM_MODEL = os.getenv("LLM_MODEL", "azure_ai/genailab-maas-DeepSeek-V3-0324")


settings = Settings()
