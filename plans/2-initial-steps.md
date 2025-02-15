# Initial Setup Steps

## Phase 1: Project Setup and Repository Structure

### Prerequisites
- Python 3.9+ installed
- Access to OpenAI API (API key)
- Access to Supabase project (URL and service key)
- (Optional) Google AI credentials for Gemini integration

### Directory Structure Setup
```
app/
├── main.py              # FastAPI instance and route definitions
├── agent.py            # OmegaAgent class and related logic
├── model_provider.py   # LLM API integration functions
├── db.py              # Database (Supabase) connection and functions
├── routes/            # Route modules directory
│   ├── omega_routes.py
│   ├── human_to_omega_routes.py
│   ├── omega_to_human_routes.py
│   ├── reasoning_routes.py
│   ├── agent_routes.py
│   └── logs_routes.py
└── config.py          # Configuration loader
tests/                 # Test directory
docs/                 # Documentation directory
```

### Step-by-Step Setup Tasks

1. **Environment Setup**
   - Create virtual environment: `python3 -m venv venv`
   - Activate environment: `source venv/bin/activate`
   - Install initial dependencies:
     ```bash
     pip install --upgrade pip
     pip install fastapi uvicorn supabase openai python-dotenv
     ```

2. **Configuration Setup**
   - Create `.env` file with required variables:
     ```env
     OPENAI_API_KEY="sk-..."
     SUPABASE_URL="https://xyz.supabase.co"
     SUPABASE_SERVICE_KEY="your-supabase-service-role-key"
     MODEL_PROVIDER="openai"
     DEFAULT_MODEL="gpt-4"
     ```

3. **Initial Code Setup**
   - Create minimal `main.py` with health check endpoint
   - Set up FastAPI application instance
   - Configure logging (basic setup)
   - Implement basic error handling structure

4. **Database Setup**
   - Create Supabase project
   - Set up `query_logs` table with schema:
     ```sql
     CREATE TABLE IF NOT EXISTS public.query_logs (
         id BIGSERIAL PRIMARY KEY,
         prompt TEXT NOT NULL,
         response TEXT NOT NULL,
         model VARCHAR(50) NOT NULL,
         created_at TIMESTAMPTZ DEFAULT now()
     );
     ```

5. **Verification Steps**
   - Run server: `uvicorn app.main:app --reload`
   - Test health endpoint: `curl http://localhost:8000/health`
   - Verify OpenAPI docs: Visit `http://localhost:8000/docs`
   - Test Supabase connection

### Initial Implementation Checklist

- [ ] Project directory structure created
- [ ] Virtual environment set up
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] Basic FastAPI app running
- [ ] Health check endpoint working
- [ ] Supabase table created
- [ ] Basic logging configured
- [ ] Documentation structure in place

### Next Steps
After completing the initial setup:
1. Define Pydantic models for requests/responses
2. Implement the core Omega endpoint structure
3. Set up the LLM integration layer
4. Begin implementing the OmegaAgent class

This setup phase establishes the foundation for the entire project, ensuring all necessary components are in place before beginning the core implementation.