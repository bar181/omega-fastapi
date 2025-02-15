from supabase import create_client
from app.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def log_interaction(prompt: str, response: str, model: str):
    try:
        data = {"prompt": prompt, "response": response, "model": model}
        supabase.table("query_logs").insert(data).execute()
    except Exception as e:
        print("Warning: Logging to Supabase failed:", e)
