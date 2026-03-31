from dotenv import load_dotenv
import os

from settings import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set")

