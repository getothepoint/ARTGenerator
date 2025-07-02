from dotenv import load_dotenv
import os

load_dotenv()
stable_horde_key = os.getenv("STABLE_HORDE_KEY")
STABLE_HORDE_ENDPOINT = "https://stablehorde.net/api/v2/generate/async"
STABLE_HORDE_STATUS_ENDPOINT = "https://stablehorde.net/api/v2/generate/status"
if not stable_horde_key: 
    raise ValueError("Stable Horde key not found in environment variables")
HEADERS = {
    "Content-Type": "application/json",
    "Accept":"application/json",
    "apikey": f"{stable_horde_key}"
    }

print("API Key:", "1")