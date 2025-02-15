import dspy

# Load environment variables from .env file.
dspy.load_dotenv()

class Settings:
    OPENAI_API_KEY = dspy.getenv("OPENAI_API_KEY")
    SUPABASE_URL = dspy.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = dspy.getenv("SUPABASE_SERVICE_KEY")
    DEFAULT_MODEL = dspy.getenv("DEFAULT_MODEL", "openai-gpt4")
    MODEL_PROVIDER = dspy.getenv("MODEL_PROVIDER", "openai")
    ADMIN_TOKEN = dspy.getenv("ADMIN_TOKEN", "change-this-for-production")
    MAX_CORRECTION_ATTEMPTS = dspy.getenv("MAX_CORRECTION_ATTEMPTS", 3)

settings = Settings()
