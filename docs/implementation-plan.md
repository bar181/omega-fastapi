
# Implementation_Plan.md

This section outlines a step-by-step implementation plan for building the Omega-AGI FastAPI system. It breaks the development process into milestones, lists the tasks needed for each milestone, and discusses testing strategies to ensure each part works as intended. Following this plan will help a developer implement the system in a systematic, verifiable way.

## Phase 1: Project Setup and Repository Structure
**Milestone 1:** Establish the project skeleton and configuration.
- **Tasks:**
  1. Initialize a new Python project (e.g., using `pip` or `poetry` for dependencies). Create a virtual environment.
  2. Create a Git repository (if not already) and set up a basic README (which will later be replaced by the full README.md content).
  3. Create the directory structure:
     - `app/` for the application code.
     - Inside `app/`, create `main.py` (to hold FastAPI instance and route definitions).
     - `app/agent.py` for the OmegaAgent class and related logic.
     - `app/model_provider.py` for LLM API integration functions.
     - `app/db.py` for database (Supabase) connection and functions.
     - `tests/` for test code.
     - `docs/` for the documentation (we will place the .md files there).
  4. Install FastAPI and Uvicorn: `pip install fastapi uvicorn`.
  5. Install any other necessary libraries (OpenAI SDK, supabase-py) that we know will be used.
  6. Set up environment variable loading. Possibly use Pydantic BaseSettings as shown or `python-dotenv` to load a `.env` file.
  7. Write a minimal `main.py` that creates a FastAPI app and includes a simple health-check endpoint (`/health`) returning "ok". This is to verify the server runs.
  8. Configure logging (optional at this stage). It might help to log requests or errors for debugging.
- **Testing:**
  - Run `uvicorn app.main:app --reload` and call the `/health` endpoint via browser or curl to confirm the setup.
  - Run `pytest` (even if no tests yet) to ensure the environment is ready for testing.

## Phase 2: Define Pydantic Models and API Endpoints
**Milestone 2:** Define the input/output data models and set up the API routes according to the specification.
- **Tasks:**
  1. Create the Pydantic models `OmegaRequest` and `OmegaResponse` in a `app/models.py` (or in `main.py` for simplicity initially).
  2. In `main.py`, define the POST `/api/v1/omega` route. It should accept `OmegaRequest` as input (FastAPI will handle parsing into the model).
  3. For now, implement the `/api/v1/omega` handler with a stub that returns a dummy `OmegaResponse(result="Not implemented yet")`. This allows testing the request/response cycle.
  4. Add the health check endpoint if not already.
  5. If planning the validate and logs endpoints:
     - Define a `validate` function (can be part of agent or separate) and a corresponding route `/api/v1/omega/validate`. Initially, this can just call a stub in the agent that always returns valid.
     - Define a logs retrieval route `/api/v1/logs` (admin only). Implement it later once DB is ready.
  6. Ensure that the OpenAPI docs reflect these models (start the server and check `/docs`).
- **Testing:**
  - Use `curl` or the interactive docs to POST to `/api/v1/omega` with a sample JSON (e.g., `{ "omega": "TEST", "model": "openai-gpt4" }`). It should return the dummy response with 200 status.
  - Test input validation: send a request without "omega" field, should get a 422 error from FastAPI.
  - If `validate` endpoint is added, test it similarly with a dummy Omega string.
  - This phase ensures the basic API contract is in place.

## Phase 3: Integrate LLM Provider (OpenAI, etc.)
**Milestone 3:** Implement the model integration layer to allow calling an LLM (OpenAI's API to start).
- **Tasks:**
  1. Install the OpenAI Python SDK: `pip install openai`. Also ensure you have an OpenAI API key in your environment.
  2. In `app/model_provider.py`, write a function `generate_text(prompt: str, model_name: str) -> str`. Inside:
     - Use `openai.api_key` from env.
     - Map `model_name` to an OpenAI model identifier (e.g., "openai-gpt4" -> `model="gpt-4"` for the API call).
     - Use `openai.ChatCompletion.create` or `openai.Completion.create` depending on whether using chat format or not. Likely use Chat with a system message including Omega instructions and a user message with prompt.
     - For initial testing, you might use a simpler model (like GPT-3.5) to reduce cost.
     - Return the text of the completion (e.g., `response['choices'][0]['message']['content']`).
  3. Add error handling around the OpenAI call (catch exceptions, etc., maybe translate them to a unified error type).
  4. In the `/api/v1/omega` endpoint, instead of returning a dummy response, call `generate_text(request.omega, request.model or default_model)`.
     - For now, we may not use the OmegaAgent logic, just directly feed the whole Omega script to the LLM and return the result. This is a baseline functionality (the agent orchestration will come next).
     - Possibly prepend a system message explaining how to interpret Omega (e.g., "You are an expert AI that can interpret Omega-AGI instructions..."). This prompt engineering is important but we can iteratively refine it.
  5. Test the integrated call with a simple Omega prompt like one asking a basic question. Note: Without the agent splitting tasks, the LLM might or might not understand the Omega format. We might find we need at least a simple explanation.
- **Testing:**
  - Put a very basic Omega prompt (maybe just a single `WR_SECT` without all overhead) and see if GPT-3.5 or GPT-4 returns a result. If it does, check if format is followed. If not, adjust prompt.
  - Test model switching by sending `model: "openai-gpt3.5"` vs `"openai-gpt4"` (assuming you have access).
  - Simulate an API error by using an invalid API key or model name to see if error handling works (should return an HTTP 502/500 with an appropriate message).
  - At this stage, we have an end-to-end path: request hits API -> goes to OpenAI -> returns answer.

## Phase 4: Implement the Omega Agent Logic
**Milestone 4:** Develop the OmegaAgent class to properly parse and handle the Omega-AGI structure instead of one-shot prompting.
- **Tasks:**
  1. Outline the OmegaAgent class in `app/agent.py` as per pseudocode (methods: validate_script, parse components, run, etc.).
  2. Start with a minimal approach:
     - Implement `validate_script` with some regex checks for the presence of "DEFINE_SYMBOLS" and "WR_SECT". If fail, raise `OmegaValidationError("Invalid Omega script: missing ...")`.
     - Implement `extract_sections` by finding all occurrences of `WR_SECT(` in the script and capturing the symbol and description inside. For example, use a regex like `WR_SECT\(([^,]+),\s*d="([^"]+)"` to grab symbol and description text. This doesn't handle all cases (like if there are quotes inside description, etc.), but it's a start.
     - Implement `extract_symbols` similarly by capturing text inside `DEFINE_SYMBOLS{...}` and splitting by `,`. Create a dict of symbol->meaning. (The meaning might not be heavily used by code, but could be used for logging or debugging or giving context to LLM.)
     - You can skip actually parsing memory graph for now if it's complex; just note if present.
     - For now, ignore conditional and neural block intricacies.
  3. Implement `run()` in a simple way:
     - Perhaps do not yet break into multiple LLM calls; instead, build a single prompt string that includes everything. But that is what we had earlier, so to improve:
     - Possibly attempt a two-step: 
       a) If reflection requested (detect `∇`), we could do one call to get an outline or plan.
       b) Then do another call to get final output.
       This might be complicated; maybe skip reflection handling for first iteration of agent.
     - Focus on multi-section: we want to try generating section by section.
       For each section found by `extract_sections`, call `model_provider.generate_text` with a prompt focusing on that section.
       But the model might need context of previous sections for consistency or to not repeat. This is tricky: 
       We can include all previously generated sections as context for the next call (like a running transcript).
       Or we generate independently, but risk inconsistency.
       A compromise: still do one call but having the agent's understanding allows at least verification.
       Actually, perhaps skip splitting the call in first version of agent logic. Instead, use the agent to validate and then call LLM once with the entire prompt, as we did, but now within the structured agent.
     - In summary, for initial agent.run: do validate, then directly call LLM with the whole script.
  4. Integrate the agent in the endpoint:
     - Instead of calling `generate_text` directly, do:
       ```python
       agent = OmegaAgent(request.omega, model=request.model or default)
       result_text = agent.run()
       return OmegaResponse(result=result_text)
       ```
     - The agent then internally calls `model_provider.generate_text` possibly multiple times if implemented.
  5. Test stepwise:
     - With a well-formed Omega prompt, ensure agent.validate doesn't throw incorrectly.
     - If the agent splits into multiple calls, test with a simpler prompt (like one define and one section) to see if it still returns something sensible.
     - At this point, we might find the output from LLM could be worse if we split calls poorly. We need to fine-tune how we prompt the LLM for partial tasks.
     - Possibly refine `generate_text` usage: e.g., for each section, prepend a system message with symbol definitions (so the LLM knows what `++` means, etc.).
     - This might require iteration: adjusting how we communicate context to LLM for each section.

- **Testing:**
  - Create a variety of Omega prompts for testing:
    * Minimal prompt: just a define and one section that says something simple.
    * Prompt with multiple sections but no memory graph (the LLM should produce something for each).
    * Improper prompt to test validation (remove DEFINE_SYMBOLS and see if it errors).
  - Write unit tests for agent parsing functions with example strings to ensure they extract what we expect (e.g., feed a snippet and assert that symbols dict or sections list contains expected values).
  - If an Omega prompt is complex, manually verify if the output has corresponding parts. Since we may still be doing one-call execution, this step might not change output much from Phase 3. The main difference now is we can detect errors and possibly structure for future steps.

## Phase 5: Logging Integration
**Milestone 5:** Connect to Supabase and implement logging of each request.
- **Tasks:**
  1. Install supabase Python client: `pip install supabase`.
  2. In `app/db.py`, use `create_client(SUPABASE_URL, SUPABASE_KEY)` to get a client.
  3. Write a function `log_interaction(prompt: str, response: str, model: str)` that inserts a row into `query_logs`.
     - This might be as simple as `supabase.table("query_logs").insert({...}).execute()`.
     - Use the service key to ensure it can insert.
     - Call this function at the end of the `/api/v1/omega` handler (or within agent.run after getting result, but better at the API layer after agent returns).
     - Ensure that logging failure doesn't crash the app: wrap in try/except and maybe print warning.
  4. If not done, create the table in Supabase (via web UI or supabase SQL). Use the provided schema from Data_Specs. If possible, write a SQL script and mention it in README or docs for others to replicate.
  5. Optionally, implement the GET `/api/v1/logs` route:
     - This route in `main.py` can use `supabase.table("query_logs").select(...).execute()` to fetch data. Or better, have a function in `app/db.py` to fetch last N logs.
     - Only enable it if some authentication or at least a simple token is provided. If skipping auth for now (since it's not external), maybe just not document it in public.
  6. Add any needed environment variables (service key, etc.) to .env and ensure they are loaded.
- **Testing:**
  - After running a few requests, query the `query_logs` table directly (via Supabase dashboard or CLI) to see if records are inserted correctly (prompt and response should match what was sent/received, model correct, timestamp present).
  - Test what happens on logging failure: e.g., provide a wrong supabase URL and see that the API still returns the result to client (and maybe logs an error message on server).
  - If the logs endpoint is implemented, call it and verify it returns data in expected format.

## Phase 6: Advanced Features & Refinement
**Milestone 6:** Implement remaining features like the `/validate` endpoint more robustly, error handling improvements, and model selection enhancements.
- **Tasks:**
  1. Flesh out `/api/v1/omega/validate`: Now that agent can parse, use `agent.validate_script()` to actually validate without calling the LLM. Return results accordingly.
     - If valid, maybe even return a summary like "Valid Omega script with X sections" or simply `{valid: true}`.
     - If invalid, include error message from exception.
  2. Add more validation rules to agent.validate (undefined symbol check, etc., as per Omega_Specs).
  3. Implement a simple authentication for the logs endpoint, if desired (could be a hardcoded token in env, to supply as query param or header).
  4. Review error messages: ensure they are not leaking anything sensitive and are clear. Possibly implement a global exception handler using `app.add_exception_handler` for HTTPException to unify error format.
  5. Performance test small scale: measure a single request time. If slow, consider setting `async` on our endpoints and making OpenAI calls in an async manner (the openai library now supports asyncio via `aiohttp` if configured). This can be an improvement but may require switching to `httpx` for example.
  6. If Google Gemini or other provider integration is desired at this stage: 
     - This might require a separate implementation using Google's API (if available). Possibly use a placeholder if not yet released.
     - Abstract the model provider further: e.g., `if model starts with "openai", use openai provider; if "google-", use google provider`.
     - Ensure environment keys for Google are handled (maybe `GOOGLE_API_KEY` etc.).
     - Without actual Gemini access, document how one would plug it in once available.
  7. Documentation cross-verification: As features shape up, update the docs (the content we have prepared) to match reality if there were any deviations.
- **Testing:**
  - Write a test for the validate endpoint: feed it a known bad script and expect a specific error message or valid flag.
  - Intentionally break part of Omega script and see if agent catches it vs the LLM just working around it.
  - If multi-model is integrated and if there's any stub for Gemini, test switching to it (even if it returns a dummy message like "Gemini not available", just to confirm the code path).
  - Run concurrent requests (if possible simulate 5-10 at once using async or a tool like `ab` ApacheBench) to see if any race conditions or performance bottlenecks (with real LLM calls this might be slow and expensive, so maybe stub out `generate_text` for this test).
  - Ensure that for each request a separate OmegaAgent is created and there's no leakage of data between them (this should be fine if coded properly).

## Phase 7: Deployment and Further Testing
**Milestone 7:** Final preparations for deployment (if needed) and comprehensive testing.
- **Tasks:**
  1. Containerization (optional): Write a Dockerfile if we plan to containerize deployment. Ensure to include environment variables in container config.
  2. Deployment environment: If deploying to a platform, test there (maybe a staging environment).
  3. Load testing with a stubbed model: One strategy is to temporarily replace actual LLM calls with a dummy function that returns a canned response quickly, then hammer the API to see how it holds up (this tests FastAPI, our logic, and DB I/O under load without incurring API costs).
  4. Documentation packaging: Make sure the `/docs` folder with all markdown files is included in the repository and perhaps mention in README how they relate (some might put an index in README linking to others).
  5. Code quality: run `flake8` or similar linters, ensure no major warnings. Format code with `black` (if used).
  6. Security review: as per Technical_Specs, ensure no secrets in code, and ideally implement at least a simple API key check if going public (maybe not full OAuth due to time).
- **Testing:**
  - Full integration test: run through a realistic scenario such as "Use Omega to produce a short report on a topic" and see it all working (and log it).
  - If possible, test with GPT-4 (since the format understanding might be better) and compare output to GPT-3.5 to ensure the system works with both.
  - Test the error flows:
    * Provide an input that triggers an OpenAI content filter (like ask a disallowed question) and see how our system responds (OpenAI might return an error or a safe completion; our system should handle that gracefully).
    * Stop the network (or point to wrong OpenAI domain) to simulate LLM downtime and ensure user gets a clear error without crash.
    * Remove Supabase credentials and ensure it doesn't break the main functionality (just logs error on insert).
  - If authentication added: test accessing protected endpoints with and without creds.

## Phase 8: Future Roadmap (Beyond initial implementation)
Although not part of initial coding, it's good to outline tasks for features we deferred:
- Implement complete Omega parsing using a parsing library.
- Reflection and evaluation loops fully.
- Multi-agent or tool integration capabilities.
- These would be separate projects or major tasks and can be logged as GitHub issues or in a FUTURE.md document.

Throughout the implementation, maintain frequent commits and possibly use version control branching (e.g., a branch for each milestone) to manage development. After each milestone, one could have a review or run a set of tests to ensure the system is stable before moving to the next.

Finally, after Phase 7, the system should be ready for use and the documentation should serve as a comprehensive guide to it. 

By following this plan, a developer can incrementally build and verify the Omega-AGI system, reducing the chance of major issues and ensuring that at each stage, there's a working, testable component.

---

# Using dspy

This section describes how dspy is integrated into the Omega-AGI system. dspy is used primarily for configuration management. It loads environment variables from a `.env` file and provides a centralized, secure, and flexible way to configure system settings. The following subsections detail its use in various parts of the application.

---

## 1. Configuration Loading at Startup

### Purpose

dspy is used to load essential environment variables such as API keys, model settings, and database credentials. This ensures that sensitive information is managed outside of the source code and allows for dynamic reconfiguration.

### Code Example

```python
# config.py
import dspy  # dspy is assumed to be our lightweight dependency for .env management

# Load environment variables from the .env file
# This is executed at application startup.
dspy.load_dotenv()  # Loads variables into os.environ

# Define our configuration class (could also use Pydantic BaseSettings)
class Settings:
    # Environment variables are read directly via dspy/os.environ
    OPENAI_API_KEY = dspy.getenv("OPENAI_API_KEY")
    SUPABASE_URL = dspy.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = dspy.getenv("SUPABASE_SERVICE_KEY")
    DEFAULT_MODEL = dspy.getenv("DEFAULT_MODEL", "openai-gpt4")
    MODEL_PROVIDER = dspy.getenv("MODEL_PROVIDER", "openai")
    ADMIN_TOKEN = dspy.getenv("ADMIN_TOKEN", "change-this-for-production")

# Instantiate settings for use in the application
settings = Settings()

# Verbose comment:
# dspy.load_dotenv() automatically searches for a .env file in the project root and loads
# each line as an environment variable. This allows us to keep our API keys and configuration
# separate from our codebase. All modules that require configuration (e.g., for LLM calls,
# database connections, or agent behavior) reference these settings.
```

### Explanation

- **dspy.load_dotenv():** This function scans the project directory for a `.env` file and loads all the key-value pairs into `os.environ`.
- **Configuration Class:** We define a simple `Settings` class that reads variables via `dspy.getenv()`, which provides an easy interface to access these variables.
- **Usage:** Other modules (like our model provider or agent modules) import the `settings` object to access configuration values.

---

## 2. Configuring LLM Calls

### Purpose

dspy is used to set LLM-specific configuration such as API keys and default model parameters. This ensures that functions handling LLM calls (e.g., `call_translator_llm_human_to_omega`, `call_translator_llm_omega_to_human`, and `call_translator_llm_correction`) can easily retrieve the necessary keys and settings.

### Code Example

```python
# model_provider.py
import openai
from config import settings

# Initialize OpenAI with API key from dspy configuration
openai.api_key = settings.OPENAI_API_KEY

# Function to call the LLM for human-to-Omega translation
async def call_translator_llm_human_to_omega(prompt: str) -> str:
    # Verbose comment:
    # This function sends a prompt to the LLM to translate a natural language instruction into a valid Omega script.
    messages = [
        {
            "role": "system", 
            "content": "You are an expert in Omega-AGI symbolic language. Convert natural language instructions into a valid Omega prompt following best practices."
        },
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",  # Could use settings.DEFAULT_MODEL here as well
        messages=messages,
        temperature=0.2
    )
    # Return the generated Omega text
    return response['choices'][0]['message']['content']

# Function to call the LLM for Omega-to-human translation
async def call_translator_llm_omega_to_human(prompt: str) -> str:
    # Verbose comment:
    # This function instructs the LLM to convert an Omega script into plain English.
    messages = [
        {
            "role": "system", 
            "content": "You are an expert in interpreting Omega-AGI scripts. Translate the following Omega script into plain, natural language."
        },
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",  # Alternatively, use a specific model setting from dspy if needed
        messages=messages,
        temperature=0.0
    )
    return response['choices'][0]['message']['content']

# Function for correction/improvement of Omega scripts
async def call_translator_llm_correction(prompt: str) -> str:
    # Verbose comment:
    # This function is used to correct or improve an Omega script based on feedback.
    messages = [
        {
            "role": "system", 
            "content": "You are an expert in Omega-AGI. Correct and improve the following Omega script based on the given instructions."
        },
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",  # You can choose to lower the temperature for determinism
        messages=messages,
        temperature=0.1
    )
    return response['choices'][0]['message']['content']
```

### Explanation

- **Initialization:** `openai.api_key` is set using the value loaded by dspy.
- **Dynamic Model Settings:** You could further use settings (like `settings.DEFAULT_MODEL`) to choose a model dynamically.
- **Translator Functions:** Each function creates a system message and sends a prompt to the LLM, returning the result. The API key and model parameters come from our configuration via dspy.

---

## 3. Configuring Agents

### Purpose

dspy settings influence how agents behave (e.g., the number of reflection iterations, timeouts, and retry policies). All agents use the same configuration to ensure consistency.

### Code Example in Agent Module

```python
# agent.py
from config import settings

class OmegaAgent:
    def __init__(self, omega_script: str, model: str):
        self.omega_script = omega_script
        self.model = model
        # Configuration values from dspy can be used to set thresholds, max attempts, etc.
        self.max_correction_attempts = int(settings.__dict__.get("MAX_CORRECTION_ATTEMPTS", 3))
        # More configuration can be loaded here as needed, e.g., timeout settings
        # For example: self.llm_timeout = int(settings.__dict__.get("LLM_TIMEOUT", 60))
    
    def validate_script(self):
        # Verbose comment:
        # Validate that the omega_script contains mandatory parts.
        if "DEFINE_SYMBOLS" not in self.omega_script:
            raise OmegaValidationError("Missing DEFINE_SYMBOLS block.")
        if "WR_SECT" not in self.omega_script:
            raise OmegaValidationError("Missing WR_SECT command.")
        # Additional checks can be implemented here.
    
    async def run(self) -> str:
        # Verbose comment:
        # Main method to execute the Omega script.
        self.validate_script()  # Ensure script is valid before execution.
        # Here you could add additional reflection and evaluation steps.
        # For example, if reflection is enabled (check for ∇), perform a reflection call:
        if "∇" in self.omega_script:
            reflection_prompt = f"Evaluate the following Omega script for structure and quality:\n{self.omega_script}"
            reflection_result = await call_reflection_llm(reflection_prompt)
            # Optionally process the reflection_result (not shown).
        # For now, simply pass the script to the LLM:
        from model_provider import call_translator_llm_correction  # For demonstration
        result = await call_translator_llm_correction(self.omega_script)
        return result
```

### Explanation

- **Dynamic Parameters:** The agent reads configuration values (e.g., `MAX_CORRECTION_ATTEMPTS`) from the settings loaded by dspy.
- **Validation and Execution:** The agent validates the script and then, if needed, calls reflection functions. All configuration-driven behavior is centralized via dspy-loaded settings.

---

## 4. Summary

dspy plays a vital role in our Omega-AGI system by:
- Loading configuration variables from a `.env` file at startup.
- Ensuring that all modules (LLM calls, agent behavior, database configuration, etc.) have access to the necessary parameters.
- Allowing dynamic reconfiguration without changing the source code, as all changes are applied via the `.env` file and then loaded through dspy.

By centralizing configuration management using dspy, our system is more secure, maintainable, and flexible. Developers can modify settings (such as API keys, model parameters, and agent thresholds) without modifying code, simply by updating the `.env` file. This approach improves overall system reliability and ease of deployment.

---
