I will now prepare the full documentation set, ensuring clarity and completeness so a developer can begin implementation without additional support. This will include:

- **8 Markdown documents** covering project setup, technical specifications, endpoints, data structures, Omega-AGI details, agent coordination, implementation plan, and a README.
- **1 shell script (`setup.sh`)** to automate initial project setup.
- **Integration of OpenAI 40-mini, OpenAI 03, and Google Gemini**, with an option for later enhancement using LiteLLM for more dynamic LLM selection.
- **A simple Supabase schema**, primarily for development logging and monitoring.
- **Detailed pseudocode for agents**, covering initialization, processing, error handling, and output management.

I will let you know once the documents are ready for review.

# README.md

## Overview
**Omega-AGI FastAPI System** is a web API that leverages the Omega-AGI symbolic language to interact with Large Language Models (LLMs) in a structured and deterministic way. Omega-AGI provides a standardized format for communicating instructions to an AI, aiming to eliminate ambiguity and improve consistency ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=language%2C%20which%20can%20be%20ambiguous,method%20for%20conveying%20complex%20instructions)). By using this format, the system ensures that complex tasks are broken down into clear, machine-readable directives, enabling reliable execution of multi-step AI workflows. The FastAPI framework is used to expose these capabilities via HTTP endpoints, allowing developers to integrate advanced AI agent behaviors into applications through a simple API.

In this system, users compose prompts in the **Omega-AGI format** (a concise, symbolic instruction language for AGI). The API receives these prompts, processes them through an **Agent** component that interprets and orchestrates the instructions, and queries an LLM (such as OpenAI's GPT series or Google's Gemini) to generate responses. The design emphasizes determinism and efficiency – by structuring prompts with Omega-AGI, responses become more predictable and information-dense ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,reliable%20and%20efficient%20processing%2C%20and)). This approach is particularly useful for complex tasks like multi-section reports, chain-of-thought reasoning, and self-evaluating answers, which Omega-AGI natively supports.

## Architecture Summary
The Omega-AGI FastAPI System is composed of several key components working together:
- **FastAPI Application** – Manages HTTP API endpoints for interacting with the agent. It handles request routing, input validation, and response serialization.
- **Omega Agent Engine** – The core module that interprets Omega-AGI instructions and coordinates the LLM's actions. It breaks down the Omega script into steps, invokes the LLM for generating content or reflections, and assembles the final output.
- **LLM Integration Layer** – A modular interface to connect with different language models. By default, it supports OpenAI GPT models (e.g., GPT-4 and GPT-3.5) and is designed to integrate with Google Gemini when available. This layer abstracts the specifics of each provider, allowing the agent to call `generate_text` uniformly whether using OpenAI's API or another model.
- **Supabase Logging Database** – A cloud Postgres (Supabase) database for logging queries and results. Each request and its response are recorded for auditing, debugging, and performance tracking. The system uses Supabase's RESTful interface (or client library) to insert log records asynchronously, so as not to block the user request.

The architecture follows a straightforward request-response flow: a client makes an HTTP request to a FastAPI endpoint, the request data (Omega script and parameters) is validated and passed to the Omega agent, the agent executes the script by making one or multiple calls to the LLM as needed, and the final result is returned as a JSON response. The entire interaction is stateless (each request is handled independently), but the Omega format allows the prompt to include a "memory" or context if needed via its symbolic structure ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,%E2%A7%89)). This design ensures **modularity** (components can be updated independently), **scalability** (the FastAPI app can be run with multiple workers or replicated across servers), and **maintainability** (clear separation of concerns between API handling, agent logic, and data logging).

## Setup Instructions
To set up the Omega-AGI system on your local machine or server, follow these steps:

1. **Prerequisites**: Ensure you have **Python 3.9+** installed. You'll also need access to an LLM API (e.g., an OpenAI API key) and a Supabase project (with its URL and service key) for logging. Sign up for accounts if you haven't:
   - OpenAI API key (for GPT-4/GPT-3.5) if using OpenAI.
   - (Optional) Google AI credentials or API access for Gemini (if available).
   - Supabase project URL and Service (secret) API key for the database.
2. **Project Setup**: Clone the project repository or create a new directory and copy the provided source code. Ensure the directory contains the `app` folder (with the FastAPI application code), the `docs` folder (with this documentation), and the `setup.sh` script.
3. **Create Virtual Environment**: Open a terminal in the project directory and create a virtual environment:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   This creates and activates an isolated environment for the project's dependencies.
4. **Install Dependencies**: Run the setup script or install manually. For manual installation, use:
   ```bash
   pip install --upgrade pip 
   pip install -r requirements.txt
   ``` 
   (If a `requirements.txt` is not provided, use `pip install fastapi uvicorn supabase openai` to get the main libraries.)
5. **Configuration**: Create a file named `.env` in the project root (or use environment variables in your deployment system) and add the necessary configuration values:
   ```env
   OPENAI_API_KEY="sk-..."        # Your OpenAI API key
   SUPABASE_URL="https://xyz.supabase.co"   # Your Supabase project URL
   SUPABASE_SERVICE_KEY="your-supabase-service-role-key"
   MODEL_PROVIDER="openai"        # Default LLM provider (e.g., "openai" or "google")
   DEFAULT_MODEL="gpt-4"          # Default model name (e.g., "gpt-4", "gpt-3.5-turbo")
   ```
   Replace the placeholder values with your actual keys and preferences. The `SUPABASE_SERVICE_KEY` should be the secure service role key (kept secret on server side), which allows inserting logs. Never expose this in client-side code.
6. **Database Setup**: In your Supabase project, create the required table for logging (see **Data_Specs.md** for the schema). You can execute the SQL provided or use the Supabase dashboard to create a table named `query_logs` with appropriate columns (id, prompt, response, model, created_at). Ensure the table is **public** or that appropriate Row Level Security (RLS) policies are added to allow inserts with your service key.
7. **Run the Application**: Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   This will launch the server at `http://localhost:8000` (the `--reload` flag auto-restarts on code changes, useful in development). You should see console output indicating the server is running.

## Quick Start Guide
Once the server is up, you can interact with the Omega-AGI API. Here’s a quick example to ensure everything is working:

- **Using cURL:** Open a new terminal and send a test request:
  ```bash
  curl -X POST "http://localhost:8000/api/v1/omega" \
       -H "Content-Type: application/json" \
       -d '{"omega": "Ω=>δ(ts=\"opt\");DEFINE_SYMBOLS{@=\"Question\" /*What is the capital of France?*/}; → AGI_Rpt WR_SECT(@, d=\"Provide a detailed answer to the question.\");"}'
  ```
  In this example, we send a simple Omega script that defines a question and instructs the agent to write a section answering it. The API should respond with a JSON containing the result. For instance, a successful response might look like:
  ```json
  {
    "result": "The capital of France is Paris. Paris has been the political, cultural, and economic center of France for centuries..."
  }
  ```
  The exact wording will vary since it’s generated by the LLM, but it should correctly answer the question in a detailed manner.

- **Using Python (requests):** You can also test the endpoint with a short Python snippet:
  ```python
  import requests
  url = "http://localhost:8000/api/v1/omega"
  omega_script = 'Ω=>δ(ts="opt");DEFINE_SYMBOLS{@="Task" /*sum of 2 and 3*/}; → AGI_Rpt WR_SECT(@, d="Compute the result of the arithmetic task.");'
  resp = requests.post(url, json={"omega": omega_script, "model": "openai-gpt3.5"})
  print(resp.json())
  ```
  This will send an Omega script asking the agent to compute *the sum of 2 and 3*. The printed result should be the answer (e.g., "5") explained in the style dictated by Omega (in this case, a straightforward computation).

- **API Documentation:** Visit `http://localhost:8000/docs` in a browser to view the interactive API documentation (provided by FastAPI's Swagger UI). Here you can see the available endpoints, their request/response formats, and even execute calls from the web interface. For details on each endpoint beyond the quick start, see **Endpoints.md** in this documentation set.

If the above steps are successful, your Omega-AGI system is working correctly. You can now craft more elaborate Omega-AGI prompts and send them via the API to perform complex tasks. For example, you could ask the agent to generate a multi-section report or to evaluate its own answers using the Omega format features (reflection, evaluation loops, etc.). Refer to **Omega_Specs.md** for guidance on writing Omega-AGI instructions.

## Future Enhancements
This project provides a foundation for an Omega-AGI driven AI agent. Looking ahead, several enhancements and extensions are planned:

- **Full Omega Parsing & Execution**: Implement a complete parser for the Omega-AGI language, enabling the system to understand and execute each Omega command natively (rather than relying solely on the LLM to interpret). This would allow for features like conditional branching and loop constructs (`IF...THEN`, `FOR...DO`) to be handled with actual code logic, improving determinism.
- **Advanced Multi-Agent Coordination**: Extend the architecture to support multiple agents or specialized sub-agents. For instance, one agent could handle knowledge retrieval while another focuses on reasoning. Omega-AGI’s standardized language can facilitate communication between these agents. A future version might allow an Omega script to spawn or coordinate multiple AI agents (e.g., a planning agent and an execution agent working together).
- **Enhanced LLM Support**: Integrate additional model providers. Google’s **Gemini** (once available) will be added alongside OpenAI. The system could dynamically select models based on task requirements (e.g., use a faster model for simple tasks and a more powerful model for complex or creative tasks). There are also plans to support local or open-source LLMs for offline or self-hosted scenarios by abstracting the LLM API layer further.
- **Streaming Responses**: For lengthy outputs (like large reports or real-time analyses), enable streaming of results. This means the API could return partial results as they are generated (using HTTP streaming or WebSockets). This would improve responsiveness for the client during long-running tasks.
- **Web Interface & Visualization**: Develop a simple frontend or dashboard to interact with the Omega-AGI system. This could visualize the **Memory Graph** relationships, show the chain-of-thought steps as the agent works through the Omega script, and allow users to input Omega instructions without writing raw JSON or curl commands.
- **Robust Error Recovery and Self-Improvement**: Leverage Omega-AGI’s reflection capabilities by implementing automated self-correction loops. In future versions, if the agent detects an error or suboptimal section in its output, it could automatically re-invoke the LLM with a refined prompt (perhaps using the `∇` or `EVAL_SECT` instructions) to correct or improve that part of the answer.
- **Security & Auth**: Add authentication and rate limiting to the API. This will be important when exposing the service to multiple users or production use. Options include API keys or OAuth2 tokens for clients, as well as per-user request quotas to control costs and prevent abuse.
- **Logging & Analytics**: Expand the logging to capture more metrics, such as token usage per request, response time, and quality ratings. Provide analytics tools or queries to analyze this data (e.g., identify what types of prompts lead to longer responses or errors). This can guide prompt engineering improvements and cost optimizations.
- **Omega Language Enhancements**: As Omega-AGI evolves (reference the master Omega document for planned updates), update the system to support new syntax or features. For example, if a future Omega version introduces new reflection operators or memory management features, incorporate them into the agent’s parsing and execution logic.

Each of these enhancements will increase the power and usability of the Omega-AGI system. The project is structured to accommodate growth: new modules can be added for new features, and the documentation (this set of files) will be kept up-to-date with design changes. For now, developers can build on the current system to create highly structured AI-driven applications, confident that future updates will further expand what’s possible with Omega-AGI.

---

# Technical_Specs.md

## System Architecture
The Omega-AGI FastAPI system follows a modular architecture that cleanly separates the API layer, the agent logic, external AI model integration, and data persistence. Below is a high-level overview of the architecture and its components:

- **FastAPI Web API**: Acts as the entry point for all requests. It defines the RESTful endpoints (see **Endpoints.md** for details) and uses Pydantic models for request/response validation. FastAPI's asynchronous capabilities allow handling multiple requests concurrently, which is crucial when some requests may involve long LLM processing times.
- **Omega Agent**: This is the core engine that interprets Omega-AGI instructions. Implemented as a Python module/class (e.g., `OmegaAgent`), it encapsulates the logic to:
  - Parse or at least identify components of the Omega script (preamble, symbol definitions, sections, etc.).
  - Manage the execution flow dictated by the script (for example, ensuring sections are generated in order, handling any `IF` conditions or loops if present).
  - Interact with the LLM through the model integration layer to generate content for each section or perform reflection/evaluation steps.
  - Aggregate the outputs and return a final result.
- **Model Integration Layer**: Abstracts away the details of connecting to various LLM providers. This could be a simple utility module (e.g., `model_providers.py`) with functions like `generate_text(prompt, model_name)` that internally call OpenAI’s API or Google’s API. By using an abstraction, the agent doesn’t need to know if the response is coming from OpenAI GPT-4, GPT-3.5, or Google Gemini – it just requests text generation. New providers can be integrated by adding their API calls in this layer. For instance, using OpenAI’s Python SDK for GPT models, and Google’s SDK or HTTP calls for Gemini (once available).
- **Supabase Database (Logging)**: A Postgres database hosted by Supabase that stores logs of interactions. The system uses the Supabase Python client or HTTP API to insert a new record for each request, recording details like timestamp, the Omega script (prompt), chosen model, and the LLM’s response. This component is not on the critical path of generating a response (to avoid slowing down the API call); logging can be done asynchronously or after sending the response to the client.
- **Configuration & Utilities**: Supporting modules for configuration (loading environment variables, setting up API keys) and utility functions (e.g., formatting outputs, validating Omega syntax). For example, a config module might read the environment to determine which model provider to use by default and provide that to the agent.

**Data Flow**: When a request comes in, the sequence is as follows (this is the typical **endpoint flow**):
1. **Request Reception** – The FastAPI app receives a request on an endpoint (e.g., `POST /api/v1/omega`). It immediately uses a Pydantic model to validate the JSON body. If the body is missing required fields or has incorrect types, FastAPI returns a 422/400 error automatically without invoking the agent ([How to secure APIs built with FastAPI: A complete guide](https://escape.tech/blog/how-to-secure-fastapi-api/#:~:text=In%20FastAPI%2C%20handling%20and%20validating,of%20data%20in%20each%20request)).
2. **Agent Invocation** – If validation passes, FastAPI calls the Omega Agent module (for example, `agent = OmegaAgent(request.omega, request.model)` followed by `result = agent.run()`). This call is typically `await`ed since it may involve async operations (calling external APIs).
3. **Omega Script Processing** – Inside the agent, the Omega script is processed:
   - Basic validation of the Omega format structure (if implemented) to ensure it includes necessary components.
   - The agent might split the script into segments (preamble, definitions, sections, etc.) for internal handling.
   - The agent prepares a **system prompt** or initial message for the LLM that explains how to interpret the Omega commands, ensuring the LLM understands the symbolic instructions. (In early implementations, this could be a predefined prompt that includes a brief summary of Omega syntax or a one-shot example.)
   - The agent then either makes a **single call** to the LLM with the entire Omega prompt (letting the LLM execute it in one go), or **multiple calls** for a stepwise execution:
     - For example, the agent may call the LLM to generate each section (`WR_SECT`) separately, which can help manage long outputs or handle evaluation loops by checking each section as it's produced.
     - If the Omega script includes reflection (`∇`) or evaluation (`EVAL_SECT`), the agent might first ask the LLM to perform those meta-steps (e.g., "evaluate the draft output of section X") and then adjust prompts accordingly for another generation round.
4. **LLM Generation** – The model integration layer formats the prompts and parameters for the specified model. It injects API keys and model names as needed. For OpenAI, this might use `openai.ChatCompletion.create(...)` with the prompt; for others, it might use REST calls. The call is asynchronous if possible. Upon completion, it returns the generated text.
5. **Assembling Response** – The agent takes the raw output from the LLM (which could be the full answer or parts of it) and post-processes it:
   - If multiple pieces (sections) were generated, they are concatenated or combined into the final structured output.
   - If the Omega format dictates a certain output structure (like a report with sections), the agent ensures the final output respects that structure (e.g., by adding section headings or numbering if required – although ideally the LLM already did that as instructed by the Omega prompt).
   - Performs any final sanitization or formatting (for example, ensure the output is plain text or JSON as needed by the endpoint contract).
6. **Sending Response** – The FastAPI endpoint returns a JSON response to the client, containing the result (and possibly additional metadata like status or any warnings).
7. **Logging** – In parallel or just after sending the response, the system logs the interaction to Supabase:
   - The log includes the prompt (Omega script), the resulting output, the model used, and a timestamp. 
   - If an error occurred or the agent had to retry, those events could also be logged (possibly in separate log tables or with status fields).

This architecture ensures that each concern is handled in isolation, making the system easier to maintain and extend. For example, to support a new LLM provider, one would primarily add a new function in the model integration layer and adjust configuration – the agent logic and API do not need major changes. Similarly, if the Omega language specification is updated, the changes would be made in the agent’s parsing/execution logic, without affecting the API endpoints.

## Endpoint Flows
Each API endpoint in the system has a defined flow of execution from request to response. Here we describe the flow for the primary endpoint (`/api/v1/omega`) and any ancillary endpoints like health checks. (Detailed request/response schemas for each endpoint are in **Endpoints.md**.)

- **Health Check Endpoint Flow**: A GET request to `/health` is a simple flow:
  1. FastAPI receives the GET request on `/health`.
  2. It invokes the corresponding path operation function, which likely just returns a static message or status code (for example, a JSON `{"status": "ok"}` with HTTP 200).
  3. There is no agent or external call; this is just to verify that the service is running. The response is sent immediately.
  4. Minimal logging might be done (could be omitted due to high frequency and low value of health checks).
  5. The entire flow should complete in a few milliseconds.

- **Omega Execution Endpoint Flow (`POST /api/v1/omega`)**: This is the main and more complex flow:
  1. **Request Intake**: User sends a JSON body containing at least the Omega script (`omega`) and optionally a model specification. FastAPI matches this to the `/api/v1/omega` POST endpoint and begins processing.
  2. **Pydantic Validation**: The request body is validated against a Pydantic model, e.g., `OmegaRequest` with fields `omega: str` and `model: Optional[str]`. If validation fails (missing `omega` or wrong types), FastAPI short-circuits and returns an error response (400 Bad Request or 422 Unprocessable Entity) with details about what was expected ([How to secure APIs built with FastAPI: A complete guide](https://escape.tech/blog/how-to-secure-fastapi-api/#:~:text=In%20FastAPI%2C%20handling%20and%20validating,of%20data%20in%20each%20request)). The endpoint function is not executed in this case.
  3. **Agent Call**: If validation passes, the endpoint function creates an OmegaAgent instance and calls its execution method. This could be an `async def` function call (ensuring other requests can still be handled while waiting on the LLM).
  4. **Omega Script Execution**: Inside the agent, as described earlier, the script is executed. If this involves multiple LLM calls (for example, one per section or an initial reflection then a final answer), the agent will orchestrate these calls sequentially or in a controlled manner. The internal flow might look like:
     - Initialize context (read symbols, set up memory graph).
     - Loop through each instruction or section in the Omega script:
       * If it's a content generation instruction (like `WR_SECT`), prepare a prompt and call the LLM to get that section’s text.
       * If it's a reflection instruction (`∇`), possibly call the LLM to reflect (or adjust some internal state).
       * If it's a conditional (`IF...THEN`), decide based on stored memory whether to execute the block or skip.
       * If it's an evaluation loop (`EVAL_SECT`), after generating content, call the LLM to evaluate quality and possibly loop back to improve the content.
     - Collect results from each relevant step.
  5. **Handle LLM Response**: Each call to the LLM returns some text. The agent may need to parse or clean these outputs. For example, if the LLM returns the entire report including sections, the agent can pass it through; if the LLM returns one section at a time, the agent accumulates them.
  6. **Agent Result**: The agent finishes processing and returns the final output (likely as a string) to the FastAPI endpoint function.
  7. **Formulate HTTP Response**: The FastAPI endpoint then wraps this result in the response model (e.g., `OmegaResponse` with field `result: str`). It sets the appropriate HTTP status (200 for success, or 500 if something went wrong internally that wasn’t caught as a specific exception).
  8. **Return to Client**: The JSON is sent back to the client. Example:
     ```json
     { "result": "<final output text>" }
     ```
  9. **Logging**: In the background (or immediately after forming the response), the code logs to Supabase:
     * It calls the Supabase client to insert a row into `query_logs` with the prompt, result, model, and timestamp. This might be done in a background task using FastAPI's `BackgroundTasks` feature to avoid delaying the response, or right after sending the response (since inserts are usually quick).
     * If the logging fails (e.g., network issue connecting to Supabase), the error is caught and maybe logged to console, but it does not affect the client’s response.

- **Error Flow**: If at any point during the agent execution an error occurs (exception thrown):
  - If it's a known error (for instance, the agent detects an invalid Omega script structure), the agent could raise a custom exception which the FastAPI endpoint catches and translates to a 400 response with a message explaining the validation issue.
  - If it's an unexpected error (like a crash in the code, or the LLM API is unreachable), the exception might propagate. We implement an exception handler to catch unhandled exceptions at the app level to return a generic error message ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=%40app,)), ensuring the stack trace or internal details are not exposed (important for security).
  - The error is also logged (both to console and potentially to Supabase with a flag indicating failure). The client would receive an error JSON like `{"detail": "Internal error processing the request"}` with a 500 status.

This flow covers the full cycle of an API call. The **Endpoints.md** file provides a list of all endpoints and their expected inputs/outputs, which aligns with these flows. In summary, the system is designed to handle each request methodically: validate early, process through the Omega agent with careful orchestration of the LLM, and respond quickly while logging for transparency.

## Error Handling Strategies
A robust error handling strategy is critical for a production-quality AI system. In the Omega-AGI FastAPI system, errors can occur in various stages (input validation, processing, external API, etc.). Our approach is to catch and handle errors at the appropriate level, providing informative yet secure feedback to the client and ensuring the system remains stable.

**1. Input Validation Errors (Client Errors)**: These are errors due to bad inputs from the client (malformed JSON, missing fields, invalid values).
- FastAPI with Pydantic automatically handles many of these. If the JSON is not parseable or required fields are missing, the client receives a 422 Unprocessable Entity or 400 Bad Request with details. For example, if `omega` field is missing, the error will clearly indicate that.
- For Omega script validation beyond basic JSON structure (e.g., the script text not following Omega format), the agent performs checks. If the script is found invalid (like missing a `DEFINE_SYMBOLS` section when required), the agent will raise a `ValueError` or custom `OmegaValidationError`. The FastAPI endpoint catches this and returns a 400 status with a message like `"Invalid Omega script structure: <description>"`.
- We avoid deeply analyzing the Omega script on the API side (to not duplicate logic), but a lightweight check (like ensuring the string contains certain key tokens such as `DEFINE_SYMBOLS{` and `WR_SECT`) can be done to give immediate feedback for completely malformed scripts.

**2. LLM API Errors**: These occur when calling the external model API (OpenAI or others):
- Potential issues include network timeouts, authentication errors (invalid API key), model not available, or rate limiting by the provider.
- The model integration layer wraps API calls in try/except. If an exception (like `openai.error.APIError` or a request timeout) is caught, the agent can implement a **retry logic** for transient errors. For example, if a call times out or returns a 500 from OpenAI, we might wait briefly and retry once or twice.
- If the error persists or is not retryable (like invalid API key or a model name error), the agent raises an error up to the API layer. The FastAPI endpoint then returns a 502 Bad Gateway or 503 Service Unavailable, indicating the upstream model failed. The response message might be generic ("LLM service error, please try again later") to avoid exposing internal details or API keys.
- All such errors are logged with context (including maybe the portion of the Omega script that was being processed, to help debugging later).

**3. Agent Logic Errors**: These are bugs or unforeseen issues in our agent implementation:
- For example, attempting to parse the Omega script might raise an exception if the format is unexpected, or maybe a division by zero in some hypothetical calculation.
- We will use Python’s exception handling around major blocks of the agent (like a general try/except in the `agent.run()` method). If something truly unexpected happens, we catch it and prevent it from crashing the server.
- Using FastAPI’s exception handling mechanism, we can define a global exception handler that catches any exception not already handled, and returns a generic internal error message ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=%40app,)). This ensures even if we miss something, the client never sees a raw stack trace or 500 HTML page – they get a clean JSON error.
- During development and testing, these exceptions would be printed to the console or logs so developers can fix the underlying issue. In production, one might integrate an error monitoring service (like Sentry) to capture the stack traces for offline analysis, without leaking them to users.

**4. Omega Script Execution Errors**: The agent might successfully call the LLM but get an output that is problematic:
- Perhaps the output is missing a section, or it’s in an unexpected format (maybe the LLM didn’t follow the Omega instructions correctly).
- In such cases, the agent can detect anomalies. For example, if the Omega script expected 3 sections (based on `WR_SECT` commands) but the LLM returned only 2 sections of text, the agent might decide to call the LLM again for the missing section.
- If the output quality is low and an evaluation threshold was specified (via `EVAL_SECT` in the script), the agent will invoke the evaluation logic. This might involve calling the LLM to self-evaluate or simply checking some heuristics (like length). If below threshold, the agent can regenerate that part. This loop is controlled by an iteration limit to avoid infinite retries ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=FOR%20sec%20IN%20%7B%2B%2B%2C,sec%2Cth%3D90%2Citer%3D3)).
- If after allowed retries the output is still not meeting criteria, the agent could either return the best attempt with a warning in the response, or return an error indicating it couldn’t fulfill the request to the desired quality. Currently, we might choose to return the best attempt and perhaps include a note like `"warning": "Output may be incomplete."` in the JSON.

**5. Post-Response Logging Errors**: Logging to Supabase is meant to be non-intrusive:
- If the logging fails (maybe Supabase is down or the network call fails), we catch that exception and simply print a warning. The client is not affected.
- We might implement a fallback to log to a local file if the database is unreachable, to not lose the data entirely.
- Because the logging happens after sending the response (or in background), it won’t delay or error out the API response. It’s important to encapsulate this to maintain the API’s responsiveness.

**6. Security Considerations in Errors**: We ensure that error messages do not reveal sensitive information:
- For example, if the OpenAI API key is wrong, the raw error from OpenAI might say "Invalid Authentication". We would catch that and respond with a 500 or 401 (Unauthorized) but **not include the API key or any stack trace** in the message.
- Similarly, if a bug in code occurs, we never send the file name, line number, or any sensitive variables in the response. All client-facing error messages are generic yet informative enough (e.g., "Internal server error during processing" or "Bad request: missing field 'omega'") ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=2,attacker%20understand%20your%20backend%20infrastructure)).
- Logging on the server side, however, can include detailed error info. Those logs are secured on the server and/or Supabase (which the developers can access but end users cannot).

By combining these strategies, the system aims to be robust against both user errors and system faults. It fails gracefully when needed, provides helpful feedback to the user (or at least notifies them to try again later), and ensures the service remains available and secure. Over time, as the system matures, the goal is to handle as many error cases as possible automatically (self-healing or self-correcting via Omega’s reflection capabilities) and to minimize the frequency of unexpected errors through thorough testing.

## Performance Metrics
Performance is a key consideration, given that calling large language models can be time-consuming and expensive. While the Omega-AGI system’s overall throughput is bounded by the LLM’s performance, we can optimize around it and measure key metrics to ensure the system meets requirements.

**Key Performance Metrics to Monitor:**
- **Response Latency**: The time from receiving a request to sending the response. We measure this for each request. It can be broken into:
  - *Processing latency* (time spent in our FastAPI + agent code before and after the LLM call).
  - *LLM latency* (time spent waiting for the external API).
  Typically, the LLM latency will dominate. For instance, generating a multi-paragraph report with GPT-4 might take several seconds. Our goal is to keep overhead low (ideally a few tens of milliseconds for processing).
- **Throughput (Requests per Second)**: How many requests can be handled concurrently. FastAPI with Uvicorn is asynchronous and lightweight, meaning it can handle many simultaneous requests if they spend most time waiting on I/O. We should test throughput with dummy LLM stubs to measure the framework overhead. Using multiple Uvicorn workers or processes can linearly scale throughput on multi-core machines.
- **Memory Usage**: Each request might consume memory for the Omega script and LLM outputs. Large outputs (e.g., long reports) could be several KB or more. We monitor memory to ensure we can handle multiple large outputs simultaneously without running out of RAM. The agent should discard any large intermediate data (like raw LLM prompts or partial outputs) as soon as they are no longer needed.
- **LLM Token Usage**: Although not a runtime performance metric, tracking how many tokens each request used is important for cost and for possibly optimizing prompts. The system can log the prompt and response lengths (if the LLM API provides usage info, OpenAI’s API often returns token counts). This helps identify if Omega-AGI formatting is indeed saving tokens as intended ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,the%20computational%20burden%20of%20interpretation)).
- **Database Insert Time**: Logging should ideally be very fast (on the order of 50ms or less). If we notice logging taking significant time, we might batch log inserts or move them to a separate worker. We expect Supabase inserts to be quick since it's a single-row insert.

**Benchmark Expectations:**
FastAPI under Uvicorn is known to be one of the fastest Python setups ([Benchmarks - FastAPI](https://fastapi.tiangolo.com/benchmarks/#:~:text=Independent%20TechEmpower%20benchmarks%20show%20FastAPI,used%20internally%20by%20FastAPI)), contributing negligible overhead compared to the LLM call. We expect the overhead per request (aside from LLM processing) to be in the low milliseconds. Independent benchmarks show FastAPI can easily handle thousands of empty requests per second on modern hardware ([Benchmarks - FastAPI](https://fastapi.tiangolo.com/benchmarks/#:~:text=Independent%20TechEmpower%20benchmarks%20show%20FastAPI,used%20internally%20by%20FastAPI)), but in our case each request involves an LLM call, so throughput will be limited by how many calls we can make in parallel:
- For OpenAI, there might be rate limits (e.g., X requests/minute). We must respect those and possibly queue or reject requests if we exceed them.
- We can configure the number of concurrent requests to the LLM (maybe limit concurrency to avoid flooding the API).

**Optimizations Implemented:**
- The system uses **async I/O** for external calls. While waiting for an LLM reply, the server can start processing another request. This improves throughput under concurrent load.
- **Connection pooling**: Reusing HTTP sessions for API calls (OpenAI’s library does this internally; if using `httpx`, we would use a Client). This reduces overhead of establishing connections each time.
- **Lazy Logging**: As mentioned, logging is offloaded to not delay the main response. In extreme cases, logging could even be sent to a message queue for out-of-process handling if needed.
- **Selective Response Detail**: We avoid sending overly large responses. If an Omega script accidentally triggers an extremely large output, we might put a cap or paginate it (though this is more of a safety than performance measure).
- **Profiling**: We include (for development) timing for each stage of the agent. For example, the agent can log how long parsing took, how long each LLM call took, etc. This helps identify bottlenecks. If we find, for example, that combining the sections at the end is slow for very large text, we could optimize that (perhaps streaming the combination or using more efficient string builders).

**Scalability:**
- To handle more load, the application can be scaled horizontally. Because it's stateless (except for the database logging), we can run multiple instances behind a load balancer. Each instance should have its own rate limit tracking for the LLM or share a global one via the database if needed.
- If using OpenAI, we might also leverage their ability to handle streaming or chunked requests to improve perceived latency for large answers (though that complicates the client side).
- Caching: If certain Omega prompts (or parts of prompts) are reused, we could cache the results. However, given the creative nature of LLM output, caching is less straightforward. One opportunity is caching the results of sub-queries or knowledge retrieval if the agent does any (not in current scope).

In summary, the system is designed to be efficient and the chosen frameworks (FastAPI/Uvicorn) are high-performance. The main cost is the LLM calls, so we focus on doing as few and as optimized calls as necessary (Omega-AGI helps by packing a lot of instruction in one prompt, potentially doing in one LLM call what might otherwise take multiple back-and-forth steps). We also adhere to best practices to maintain speed, such as asynchronous programming and minimal overhead in our Python code.

Regular performance tests (e.g., sending simultaneous requests with a dummy model) should be conducted to ensure the system meets the desired performance metrics. We also keep an eye on real usage logs to catch any slow requests and analyze if the slowness came from our system or from the LLM.

## Security Best Practices
Security is paramount, especially since this system might integrate with powerful AI models and handle potentially sensitive data (depending on what users ask the AI). We have implemented and recommended the following best practices to secure the Omega-AGI system:

- **Use HTTPS (Encryption)**: In production deployments, always serve the API over HTTPS ([How to secure APIs built with FastAPI: A complete guide](https://escape.tech/blog/how-to-secure-fastapi-api/#:~:text=First%20step%3A%20Use%20HTTPS%20for,secure%20communication)). This ensures that Omega scripts and LLM outputs (which could contain sensitive information) are encrypted in transit. If deploying on a platform like AWS or Heroku, use their SSL features or put a reverse proxy like Nginx with SSL in front of the Uvicorn server. HTTPS prevents eavesdropping and man-in-the-middle attacks, which is crucial if the content of queries or responses is confidential.
- **Authentication & Authorization**: By default, the current system is open (for ease of development). Before any public or multi-user deployment, implement strong authentication measures ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=,manage%20access%20to%20resources%20effectively)). Options include:
  - API Keys: Issue secret keys to clients and require them in headers for each request. The server checks these against a list of valid keys.
  - OAuth2/JWT: For a more robust solution, integrate OAuth2 (FastAPI provides tools for OAuth2 password flows, JWT validation, etc.). Each client or user would obtain a token and the API would verify it on each request ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=Basic%20Authentication)) ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=OAuth2%20Authentication)).
  - Role-Based Access Control (RBAC): If certain endpoints (like an admin log viewer) are added, ensure only authorized roles can access them ([
            Securing Your FastAPI Web Service: Best Practices and Techniques - LoadForge Guides
        - LoadForge
    ](https://loadforge.com/guides/securing-your-fastapi-web-service-best-practices-and-techniques#:~:text=,manage%20access%20to%20resources%20effectively)).
- **Rate Limiting & Quotas**: To prevent abuse or runaway costs, implement rate limiting. This could be as simple as limiting each API key to N requests per minute. Tools like **SlowAPI** (a rate-limit library for Starlette/FastAPI) can be used. Additionally, a quota system (X requests per day or a token usage limit per month) can be enforced by checking the logs or maintaining counters.
- **Input Validation & Sanitization**: Although the input is mostly plain text (Omega scripts), we treat it with care:
  - We ensure the input is a string and within reasonable length limits (to avoid memory issues or deliberate large payload attacks). For example, we might reject scripts longer than a certain number of characters.
  - If we ever allow any other content (like file uploads or HTML), we will sanitize it. In this project, that’s not applicable, but it’s a good practice in general (e.g., strip out HTML tags to prevent script injection into logs or future frontends).
  - Pydantic validation helps ensure correct types, which indirectly protects against certain injection attacks (e.g., it won’t treat a number where a string is expected).
- **Prompt Injection Awareness**: A new vector specific to LLM applications is prompt injection, where a user could try to manipulate the system prompt or break out of the intended behavior. Since Omega-AGI uses a structured prompt, the risk is somewhat mitigated by its strict format. However, if the user includes something in an Omega script that tries to circumvent rules (for instance, inserting a `NEURAL_BLOCK` with malicious instructions or attempting to use an undefined symbol to confuse the agent), we need to be vigilant:
  - The agent should ideally detect and refuse to execute clearly malicious or out-of-spec commands. (This could overlap with validation: disallow unsupported commands or overly recursive structures that could make the LLM behave unexpectedly.)
  - The system prompt given to the LLM will emphasize that it should follow the Omega script and not outside instructions, hopefully preventing the LLM from acting on any hidden malicious instruction that is not in proper Omega format.
- **Secure Handling of Secrets**: API keys for external services (OpenAI, Supabase, etc.) are loaded from environment variables and never hard-coded. They are not exposed in any endpoint. We also ensure not to log these secrets. Even in error messages, if an API call fails, we catch the exception and do not include the key or full response in any client-facing error.
- **Dependency Security**: All dependencies (FastAPI, supabase-py, etc.) are well-known libraries. We will keep them updated to pull in security patches. FastAPI itself encourages using the latest version for security fixes. We avoid using deprecated or unmaintained packages.
- **Content Security**: If a future UI is built or if responses are to be displayed in a browser, we would consider setting appropriate headers (like Content-Type as text/plain or application/json only) and possibly escaping content. Currently, the API just returns JSON, which is safe as long as we serve with correct content type.
- **Logging and Privacy**: The system logs the content of queries and responses to Supabase. If this system is used in production, be mindful of privacy:
  - If user queries may contain personal data, consider hashing or anonymizing certain parts before logging.
  - Ensure the Supabase database is secure (use strong passwords/service keys, restrict access, enable RLS if appropriate). Only authorized developers or services should be able to read the logs.
  - If a user requests deletion of their data (if this were a public service with user accounts), have a mechanism to delete or redact log entries for that user.
- **Exception Handling**: As described, we use global exception handlers to return generic messages. This not only helps user experience but is a security measure to not leak internal info. We’ve configured the app such that even in debug mode it doesn’t auto-expose too much (in production, FastAPI will not include the error detail unless configured, which is good).
- **Secure Deployment**: When deploying, run the Uvicorn server with a non-root user, use proper systemd or container configurations to limit exposure. If using Docker, minimize the image size and surface (e.g., using slim Python images). Also, turn off debug mode in FastAPI to avoid the interactive docs being exploited or any debug endpoints.
- **Future Security Enhancements**: Plan to integrate an authentication layer (as mentioned) and possibly an **AI usage policy**:
  - For example, to prevent certain misuse of the AI, one might add content filtering: after the LLM returns an answer, check it doesn’t contain disallowed content (hate, violence, etc.) if that’s a concern for your usage. OpenAI’s API can sometimes flag or refuse certain content; we should handle those cases (if OpenAI refuses due to content, we return a filtered message).
  - Implementing a **security profile** as noted in Omega-AGI’s goals ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=seamless%20communication%2C%20task%20coordination%2C%20and,crucial%20for%20responsible%20AGI%20deployment)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,sensitivity%20and%20criticality%20of%20each)) (Omega-AGI mentions secure communication and resource constraints) could be done by having different modes: e.g., a restricted mode where the agent disallows certain operations or requires additional authentication for them.

By adhering to these practices, we aim to keep the Omega-AGI system secure from common web vulnerabilities as well as AI-specific issues. Security will be revisited regularly as the system grows – especially when adding multi-user support or exposing it over the internet, at which point security measures like OAuth2 and rate limiting become mandatory. Developers integrating or deploying this system should always configure it with security in mind, using the guidelines above as a baseline.

---

# Endpoints.md

This document describes all API endpoints exposed by the Omega-AGI FastAPI system. For each endpoint, we provide the method, path, purpose, input format, output format, and any validation or error details. All endpoints return JSON responses and are designed to be self-documented via the OpenAPI schema (accessible through the `/docs` UI when the server is running).

## Base URL
When running locally, the base URL is typically `http://localhost:8000`. If deployed, it would be the host URL of the service. All endpoints below are relative to the base URL.

## 1. Health Check Endpoint

### **GET** `/health`
- **Description**: A simple health check endpoint to verify that the service is up and running. It performs no complex logic and is safe to be called frequently (for example by load balancers or uptime monitoring services).
- **Request**: No parameters or body required.
- **Response**: JSON object with a status message.
  - **Status Code**: `200 OK` on success (always, unless the server is down).
  - **Body**: e.g. `{ "status": "ok" }`. The content can be a simple confirmation string. In our implementation, we return a JSON with a key like "status" or "message" to make it parseable.
- **Errors**: There are no expected errors for this endpoint under normal operation. If the server is running, it should always return 200. If the server is not running, the client obviously cannot get a response (connection error).

*Example curl:*
```bash
$ curl -X GET http://localhost:8000/health
{"status":"ok"}
```

This indicates the service is alive.

## 2. Omega Execution Endpoint

### **POST** `/api/v1/omega`
- **Description**: This is the primary endpoint for sending an Omega-AGI formatted prompt to the agent and receiving the AI-generated result. The endpoint triggers the Omega agent to process the given instructions and produce an output using the configured LLM.
- **Request Format**: JSON body with the following fields:
  - `omega` (string, required): The Omega-AGI script containing the instructions for the agent. This should be a well-formed Omega prompt (see **Omega_Specs.md** for the expected format and structure).
  - `model` (string, optional): An identifier for the model or provider to use. If not provided, the system will use a default (e.g., "openai-gpt4"). Accepted values might include:
    - `"openai-gpt4"` – to use OpenAI's GPT-4 model (default).
    - `"openai-gpt3.5"` – to use OpenAI's GPT-3.5 model.
    - `"google-gemini"` – to use Google's Gemini model (if integrated).
    - `"openai-gpt4-32k"` or other specific model variants, depending on what is configured.
    - (These values can be defined in config; the endpoint will validate the string against known options.)
  - **Example Request Body**:
    ```json
    {
      "omega": "∇;Ω=>δ(ts='opt');DEFINE_SYMBOLS{Q=\"UserQuery\" /*Calculate 5+7*/}; → AGI_Rpt WR_SECT(Q, d=\"Compute the result of the query.\");",
      "model": "openai-gpt3.5"
    }
    ```
    This example Omega script uses the reflection operator `∇` (basic reflection) and defines a symbol Q for a user query "Calculate 5+7". It then instructs the agent to write a section computing the result. The request specifies the `openai-gpt3.5` model.
- **Response Format**: JSON object. On success, it will contain the result of the Omega-AGI prompt execution.
  - **Status Code**: `200 OK` (assuming the Omega script was processed without fatal errors).
  - **Body**:
    - `result` (string): The output generated by the agent/LLM in response to the Omega instructions. This could be a single answer, a formatted report, or any text depending on the prompt.
    - (In the future or with certain configurations, additional fields could be present, such as `analysis` or `steps` if we choose to return intermediate chain-of-thought. By default, we return just the final result to the user.)
  - **Example Success Body**:
    ```json
    {
      "result": "The result of 5 + 7 is 12."
    }
    ```
    If the Omega script requested a computation, the answer is provided. If the script requested a structured output (e.g., a report with sections), the result might contain newline characters and headings as part of the text. The API does not further structure that; it's all in the result string.
- **Validation**:
  - The `omega` field is mandatory. If it's missing or not a string, FastAPI will reject the request with a 422 status.
  - The `model` field, if provided, is checked against a list of allowed model identifiers. If an unsupported model is requested, the server responds with `400 Bad Request`, e.g., `{"detail": "Unknown model requested"}`.
  - The content of the `omega` script is not exhaustively validated by the API (we don't parse the entire Omega grammar at the gateway). However, some basic checks occur:
    * If the string is extremely large (beyond a configured limit, say 50,000 characters), the server might reject it to prevent abuse.
    * The agent will later validate structure; if it finds it invalid, it may throw an error that results in a 400 response (with a message about invalid Omega format).
- **Error Responses**:
  - `400 Bad Request`: This indicates an issue with the input. Examples:
    * Missing `omega` field or `omega` is empty. The response might be a validation error from FastAPI (mentioning that omega is required).
    * `model` provided is not recognized. The response will mention an invalid model parameter.
    * The Omega script was grossly malformed such that the agent refuses to process it. In this case, after internal attempt, we return 400 with detail (the agent would have raised a validation error internally).
  - `422 Unprocessable Entity`: This is typically thrown by FastAPI/Pydantic if the JSON is incorrectly formatted (e.g., a syntax error in JSON, or wrong data types).
  - `500 Internal Server Error`: This means something went wrong on the server side while processing. This could be a bug in the agent or an unexpected situation. The response will be generic, e.g. `{"detail": "Internal error processing the request"}`. The incident would be logged for developers. These should be rare.
  - `502 Bad Gateway` or `503 Service Unavailable`: These indicate issues with the upstream LLM service:
    * If the call to the LLM failed (timeout, no response), we might use 502.
    * If the service is over capacity or our API key is out of quota, etc., 503 might be returned. In both cases, the client can retry after some time.
  - `504 Gateway Timeout`: If we implement a timeout for long-running requests (say we don't want any request to run more than 60 seconds), we might return a 504 if the LLM didn't respond in time or if an eval loop took too many iterations.
- **Notes**:
  - This endpoint is **idempotent** in the sense that the same Omega prompt with the same model will *typically* produce the same output, due to Omega-AGI’s deterministic goals. However, small variations are possible because the underlying LLM is probabilistic. If absolute determinism is needed, one could set the LLM's temperature to 0 via the agent (the agent likely uses a low temperature by default to favor deterministic outputs).
  - The path includes `/api/v1/` to allow versioning. Future revisions of the API (breaking changes) can be exposed as /v2/omega, etc., without disrupting existing clients.
  - **Security**: If the API is secured with an API key or token (see Technical_Specs security section), clients must include the appropriate Authorization header. For example, `Authorization: Bearer <token>` if using JWT or OAuth2, or a custom header like `x-api-key: <key>` if using API keys. The documentation assumes an open setup for now.

*Example Usage*:
```bash
curl -X POST "http://localhost:8000/api/v1/omega" \
  -H "Content-Type: application/json" \
  -d '{
        "omega": "DEFINE_SYMBOLS{T=\"Task\" /*Find prime numbers*/}; → AGI_Rpt WR_SECT(T, d=\"List the first 5 prime numbers and explain briefly.\");",
        "model": "openai-gpt4"
      }'
```
Expected response (abridged):
```json
{
  "result": "The first five prime numbers are 2, 3, 5, 7, and 11. 
             2 is prime because its only divisors are 1 and itself. 
             3 is prime for the same reason. 
             5, 7, and 11 are also prime, as no other smaller natural numbers divide them evenly. 
             These numbers start the sequence of primes which are fundamental in number theory."
}
```
This shows a structured answer fulfilling the Omega prompt (which asked for a list and explanation).

## 3. (Optional) Validate Omega Endpoint

*This endpoint is a potential future addition.* It is not implemented in the initial version, but outlined for completeness and future reference, since **validation** is important.

### **POST** `/api/v1/omega/validate`
- **Description**: Validates an Omega-AGI script without executing it. This can be useful for developers to check if their Omega prompt meets the required structure and syntax. It does **not** call the LLM or generate an output; it only runs the Omega parser/validator.
- **Request**: JSON with one field:
  - `omega` (string, required): The Omega script to validate.
- **Response**:
  - On success (script is valid): `200 OK` with body `{ "valid": true, "message": "Omega script is valid." }`. The message might include details like detected number of sections, etc.
  - On failure: `400 Bad Request` with body `{ "valid": false, "error": "<description of error>" }` explaining what is wrong (e.g., "Missing DEFINE_SYMBOLS section", or "Undefined symbol used in MEM_GRAPH").
- **Errors**: Mainly 400 for invalid script. 422 if request JSON itself is bad. Not likely to have 500 unless internal bug.
- **Note**: This endpoint would rely on a complete Omega grammar parser to be truly useful. In absence of that, it may perform partial validation. Currently, since our initial system doesn’t have a full parser, this endpoint is left as a future enhancement.

*Example*:
```bash
curl -X POST "http://localhost:8000/api/v1/omega/validate" \
  -H "Content-Type: application/json" \
  -d '{ "omega": "WRONG_SYNTAX" }'
```
Response:
```json
{ "valid": false, "error": "Expected DEFINE_SYMBOLS section." }
```
*(This endpoint is not active in v1)*

## 4. (Optional) Logs Retrieval Endpoint

*Another potential endpoint for administrators or developers.*

### **GET** `/api/v1/logs`
- **Description**: Retrieve logged queries and responses from the Supabase database. This is an admin/diagnostic endpoint to review what queries have been made and what answers were given.
- **Security**: This should be a protected endpoint (e.g., admin-only). It might require an admin API key or be disabled in public deployments.
- **Request**: Can include query parameters for pagination or filtering:
  - `limit` (int, optional) – number of records to return (default 10 or 20).
  - `offset` (int, optional) – for pagination.
  - `order` (str, optional) – e.g., "desc" to get latest first.
- **Response**:
  - `200 OK` with JSON array of log records, each record may include:
    - `id`, `prompt` (omega text), `response` (truncated or full), `model`, `created_at`.
  - Example:
    ```json
    [
      {
        "id": 42,
        "prompt": "DEFINE_SYMBOLS{X=\"Question\" /*What is 2+2?*/}; → AGI_Rpt WR_SECT(X,...",
        "response": "The result of 2+2 is 4.",
        "model": "openai-gpt4",
        "created_at": "2025-02-14T20:39:37.123Z"
      },
      { ... next record ... }
    ]
    ```
- **Errors**:
  - `401 Unauthorized` or `403 Forbidden` if not properly authenticated.
  - Otherwise, not many errors except maybe `500` if DB is not reachable.
- **Note**: This endpoint essentially exposes the content of the `query_logs` table. It might not be included in the open API docs for security. Often developers might query the database directly instead. But it can be convenient for quick checks.

---

**Summary:** In the initial Omega-AGI API implementation, the **primary endpoint is `/api/v1/omega`** for executing instructions. This is the main one users will interact with. Health check is there for infrastructure. Additional endpoints like validation and logs are conceptual at this stage and can be implemented as needed. The API is intentionally kept small and focused. Each endpoint strictly defines its I/O to avoid confusion.

All endpoints use JSON and standard HTTP codes. They are designed to be RESTful and stateless. The versioning (`v1`) indicates that changes might come in future versions, ensuring backward compatibility can be maintained by adding `/v2/` endpoints if the need arises. 

Clients using this API should always check the HTTP status codes and handle errors gracefully (e.g., if a 400 occurs, fix the request; if 500 or 502, maybe retry after some delay, or alert the user that the service is temporarily unavailable).

For detailed information on the data structures and models behind these endpoints (like the database schema and Omega format), refer to **Data_Specs.md** and **Omega_Specs.md** respectively.

Below is the updated, comprehensive Endpoints.md file that now includes all endpoints (core plus the additional ones) with detailed summaries, pseudocode outlines, and descriptions of their functions, agent interactions, and error handling. The document begins with an overall summary of all endpoints.

---


# Endpoints.md

This document describes all API endpoints exposed by the Omega-AGI FastAPI system. For each endpoint, we provide the HTTP method, path, purpose, input/output formats, validation rules, error handling details, and detailed pseudocode outlining its functions and agent interactions. All endpoints return JSON responses and are self-documented via the OpenAPI schema (accessible via the `/docs` UI).

---

## Base URL

When running locally, the base URL is typically:  
`http://localhost:8000`  
All endpoints are relative to this base URL.

---

## Summary of All Endpoints

1. **Health Check Endpoint**  
   - **GET** `/health`

2. **Omega Execution Endpoint**  
   - **POST** `/api/v1/omega`

3. **Human-to-Omega Conversion Endpoints**  
   - **LLM-based Conversion:** **POST** `/api/v1/human-to-omega/llm`  
   - **Parser-based Conversion:** **POST** `/api/v1/human-to-omega/parser`

4. **Omega Validation Endpoint**  
   - **POST** `/api/v1/omega/validate`

5. **Omega Correction Endpoint**  
   - **POST** `/api/v1/omega/correct`

6. **Omega-to-Human Translation Endpoint**  
   - **POST** `/api/v1/omega-to-human`

7. **Reasoning Endpoint**  
   - **POST** `/api/v1/omega/reasoning`

8. **Agent Processing Endpoint**  
   - **POST** `/api/v1/agent/{agent_name}/process`

9. **Reflection Endpoint**  
   - **POST** `/api/v1/omega/reflect`

10. **Improve Omega Endpoint**  
    - **POST** `/api/v1/omega/improve`

11. **Logs Retrieval Endpoint (Admin Only)**  
    - **GET** `/api/v1/logs`

---

## 1. Health Check Endpoint

**Method:** GET  
**Path:** `/health`

**Purpose:**  
Verify that the service is running.

**Request:**  
- No parameters.

**Response:**  
- **200 OK** with JSON: `{ "status": "ok" }`

**Pseudocode:**
```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

## 2. Omega Execution Endpoint

**Method:** POST  
**Path:** `/api/v1/omega`

**Purpose:**  
Process an Omega-AGI prompt by having the Omega Agent execute it via an LLM and return the result.

**Request:**  
JSON with:
- `omega` (string, required): The Omega script.
- `model` (string, optional): e.g., `"openai-gpt4"`, `"openai-gpt3.5"`, `"google-gemini"`.

**Example Request:**
```json
{
  "omega": "∇;Ω=>δ(ts='opt');DEFINE_SYMBOLS{Q=\"UserQuery\" /*Calculate 5+7*/}; → AGI_Rpt WR_SECT(Q, d=\"Compute the result.\");",
  "model": "openai-gpt3.5"
}
```

**Response:**  
JSON with:
- `result` (string): The generated output.

**Pseudocode:**
```python
@app.post("/api/v1/omega", response_model=OmegaResponse)
async def execute_omega(request: OmegaRequest):
    agent = OmegaAgent(request.omega, model=request.model or settings.default_model)
    try:
        result_text = await agent.run()  # Executes the Omega script, including any reflection/evaluation steps.
    except OmegaValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error processing the request")
    await log_interaction(prompt=request.omega, response=result_text, model=request.model or settings.default_model)
    return {"result": result_text}
```

---

## 3. Human-to-Omega Conversion Endpoints

These endpoints convert natural language prompts into Omega-AGI formatted scripts.

### A. LLM-based Conversion

**Method:** POST  
**Path:** `/api/v1/human-to-omega/llm`

**Purpose:**  
Translate a natural language instruction into an Omega prompt using an LLM.

**Request:**  
JSON with:
- `human_text` (string, required)

**Example Request:**
```json
{
  "human_text": "Convert the following instruction into Omega format: Calculate the sum of 5 and 7."
}
```

**Response:**  
JSON with:
- `omega_text` (string)

**Pseudocode:**
```python
@app.post("/api/v1/human-to-omega/llm")
async def human_to_omega_llm(request: HumanToOmegaRequest):
    # Call the translator LLM function specifically for human-to-omega conversion.
    system_prompt = "You are an expert in Omega-AGI. Convert the following natural language instruction into a valid Omega prompt."
    full_prompt = f"{system_prompt}\nInstruction: {request.human_text}"
    omega_text = await call_translator_llm_human_to_omega(full_prompt)
    if not omega_text:
        raise HTTPException(status_code=500, detail="Conversion failure")
    return {"omega_text": omega_text}
```

**Instructions for `call_translator_llm_human_to_omega`:**  
- This function builds a system prompt with best practices from the Omega documentation and sends it along with the human instruction to the LLM (e.g., OpenAI 40-mini).  
- It returns the Omega script generated by the LLM.

---

### B. Parser-based Conversion

**Method:** POST  
**Path:** `/api/v1/human-to-omega/parser`

**Purpose:**  
Convert natural language to Omega format using a rule-based parser (i.e. without invoking an LLM).

**Request:**  
JSON with:
- `human_text` (string, required)

**Example Request:**
```json
{
  "human_text": "Convert: calculate the sum of 5 and 7."
}
```

**Response:**  
JSON with:
- `omega_text` (string)

**Pseudocode:**
```python
@app.post("/api/v1/human-to-omega/parser")
async def human_to_omega_parser(request: HumanToOmegaRequest):
    try:
        omega_text = rule_based_parser(request.human_text)  # See instructions below.
    except ParsingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not omega_text:
        raise HTTPException(status_code=500, detail="Parsing failed to produce Omega output")
    return {"omega_text": omega_text}
```

**Instructions for `rule_based_parser`:**  
- This function applies pre-defined grammar rules (using regex or a lightweight parsing library) to identify key phrases in the human text and map them to Omega symbols and structure (e.g., inserting `DEFINE_SYMBOLS` and `WR_SECT` appropriately).  
- On success, it returns a valid Omega script; on failure, it raises a `ParsingError`.

---

## 4. Omega Validation Endpoint

**Method:** POST  
**Path:** `/api/v1/omega/validate`

**Purpose:**  
Check the structure and mandatory keys of an Omega script without executing it.

**Request:**  
JSON with:
- `omega` (string, required)

**Example Request:**
```json
{
  "omega": "DEFINE_SYMBOLS{Q=\"Query\"}; → AGI_Rpt WR_SECT(Q, d=\"Compute the result.\");"
}
```

**Response:**  
- On success: `{ "valid": true, "message": "Omega script is valid." }`  
- On failure: `{ "valid": false, "error": "Missing DEFINE_SYMBOLS block" }`

**Pseudocode:**
```python
@app.post("/api/v1/omega/validate")
async def validate_omega(request: OmegaValidationRequest):
    try:
        agent = OmegaAgent(request.omega, model=settings.default_model)
        agent.validate_script()  # Checks for preamble, DEFINE_SYMBOLS, WR_SECT, etc.
        return {"valid": True, "message": "Omega script is valid."}
    except OmegaValidationError as e:
        return JSONResponse(status_code=400, content={"valid": False, "error": str(e)})
```

---

## 5. Omega Correction Endpoint

**Method:** POST  
**Path:** `/api/v1/omega/correct`

**Purpose:**  
Attempt to correct an Omega script that contains errors. Uses a combination of rule‐based and LLM-based correction (with a maximum of 3 attempts).

**Request:**  
JSON with:
- `omega` (string, required)
- `attempt` (integer, optional; default 1)

**Example Request:**
```json
{
  "omega": "WRONG_SYNTAX without DEFINE_SYMBOLS",
  "attempt": 1
}
```

**Response:**  
JSON with:
- `corrected_omega` (string)
- `attempt` (integer)

**Pseudocode:**
```python
@app.post("/api/v1/omega/correct")
async def correct_omega(request: OmegaCorrectionRequest):
    max_attempts = 3
    attempt = request.attempt or 1
    agent = OmegaAgent(request.omega, model=settings.default_model)
    try:
        agent.validate_script()
        return {"corrected_omega": request.omega, "attempt": attempt}
    except OmegaValidationError as e:
        if attempt >= max_attempts:
            raise HTTPException(status_code=400, detail="Failed to correct Omega prompt after maximum attempts")
        correction_prompt = f"Detected errors: {str(e)}. Please provide a corrected Omega script for the following input:\n{request.omega}"
        corrected = await call_translator_llm_correction(correction_prompt)
        new_request = OmegaCorrectionRequest(omega=corrected, attempt=attempt+1)
        return await correct_omega(new_request)
```

**Instructions for `call_translator_llm_correction`:**  
- This function calls an LLM (with low temperature) using a correction prompt. Its role is to output a revised Omega script that fixes structural issues.
- It should be distinct from the human-to-omega translator.

---

## 6. Omega-to-Human Translation Endpoint

**Method:** POST  
**Path:** `/api/v1/omega-to-human`

**Purpose:**  
Convert an Omega script back into plain English, so users can see the human-readable version of their symbolic instructions.

**Request:**  
JSON with:
- `omega` (string, required)

**Example Request:**
```json
{
  "omega": "DEFINE_SYMBOLS{Q=\"Query\"}; → AGI_Rpt WR_SECT(Q, d=\"Compute the sum of 5 and 7.\");"
}
```

**Response:**  
JSON with:
- `human_text` (string)

**Pseudocode:**
```python
@app.post("/api/v1/omega-to-human")
async def omega_to_human(request: OmegaToHumanRequest):
    translation_prompt = f"Translate the following Omega-AGI script into plain English:\n{request.omega}"
    human_text = await call_translator_llm_omega_to_human(translation_prompt)
    if not human_text:
        raise HTTPException(status_code=500, detail="Translation failure")
    return {"human_text": human_text}
```

**Instructions for `call_translator_llm_omega_to_human`:**  
- This function instructs an LLM (using a system prompt tuned for reverse translation) to convert Omega syntax back into natural language.

---

## 7. Reasoning Endpoint

**Method:** POST  
**Path:** `/api/v1/omega/reasoning`

**Purpose:**  
Submit an Omega script to a reasoning LLM (e.g., OpenAI 03) to perform deep analysis.

**Request:**  
JSON with:
- `omega` (string, required)

**Example Request:**
```json
{
  "omega": "DEFINE_SYMBOLS{R=\"Reasoning\"}; → AGI_Rpt WR_SECT(R, d=\"Analyze potential risks of X.\");"
}
```

**Response:**  
JSON with:
- `reasoning_output` (string)

**Pseudocode:**
```python
@app.post("/api/v1/omega/reasoning")
async def reasoning(request: ReasoningRequest):
    reasoning_result = await call_reasoning_llm(request.omega)
    if not reasoning_result:
        raise HTTPException(status_code=500, detail="Reasoning failure")
    return {"reasoning_output": reasoning_result}
```

---

## 8. Agent Processing Endpoint

**Method:** POST  
**Path:** `/api/v1/agent/{agent_name}/process`

**Purpose:**  
Invoke a specific agent (each implemented as a separate module) to process an Omega script using a chain-of-thought approach.

**Request:**  
- **Path Parameter:** `agent_name` (string) – the agent identifier.
- **JSON Body:**  
  - `omega` (string, required)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/agent/agent1/process" \
  -H "Content-Type: application/json" \
  -d '{"omega": "DEFINE_SYMBOLS{A=\"Analysis\"}; → AGI_Rpt WR_SECT(A, d=\"Provide market analysis.\");"}'
```

**Response:**  
JSON with:
- `agent_response` (string)

**Pseudocode:**
```python
@app.post("/api/v1/agent/{agent_name}/process")
async def agent_process(agent_name: str, request: OmegaRequest):
    try:
        agent_module = __import__(f"agents.{agent_name}", fromlist=["process_omega"])
        agent_response = await agent_module.process_omega(request.omega)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"agent_response": agent_response}
```

---

## 9. Reflection Endpoint

**Method:** POST  
**Path:** `/api/v1/omega/reflect`

**Purpose:**  
Evaluate an Omega script’s structure using reflection. This endpoint instructs an LLM to review the script based on best practices, assign a quality score (1–100), and provide recommendations for improvement.

**Request:**  
JSON with:
- `omega` (string, required)

**Example Request:**
```json
{
  "omega": "DEFINE_SYMBOLS{Q=\"Query\"}; → AGI_Rpt WR_SECT(Q, d=\"Compute result.\");"
}
```

**Response:**  
JSON with:
- `score` (integer, 1–100)
- `recommendations` (string): Detailed suggestions for improvement.
- `feedback` (string): A summary of the reflection.

**Pseudocode:**
```python
@app.post("/api/v1/omega/reflect")
async def reflect_omega(request: OmegaReflectionRequest):
    reflection_prompt = (
        "Review the following Omega-AGI script based on best practices. "
        "Score its structure from 1 to 100, provide detailed recommendations for improvement, "
        "and summarize your feedback.\n"
        f"Omega Script: {request.omega}"
    )
    reflection_result = await call_reflection_llm(reflection_prompt)
    if not reflection_result:
        raise HTTPException(status_code=500, detail="Reflection failure")
    # Expected reflection_result is a JSON string that includes score, recommendations, and feedback.
    return reflection_result
```

**Instructions for `call_reflection_llm`:**  
- This function sends a detailed system prompt to an LLM (configured for reflective analysis) instructing it to evaluate the Omega structure, score it, and output improvement suggestions.  
- The LLM should return a structured JSON (or parseable string) with keys: `score`, `recommendations`, and `feedback`.

---

## 10. Improve Omega Endpoint

**Method:** POST  
**Path:** `/api/v1/omega/improve`

**Purpose:**  
Improve an existing Omega script based on provided feedback and/or the score obtained from the reflection process. This endpoint calls an LLM to generate a revised version of the script.

**Request:**  
JSON with:
- `omega` (string, required): The current Omega script.
- `feedback` (string, optional): Feedback or recommendations to consider.
- `score` (integer, optional): The current score (if available).

**Example Request:**
```json
{
  "omega": "DEFINE_SYMBOLS{Q=\"Query\"}; → AGI_Rpt WR_SECT(Q, d=\"Compute result.\");",
  "feedback": "The script is missing a MEM_GRAPH and preamble for reflection.",
  "score": 65
}
```

**Response:**  
JSON with:
- `improved_omega` (string): The revised Omega script.
- `new_score` (integer, optional): A new score if the LLM re-evaluates the script.

**Pseudocode:**
```python
@app.post("/api/v1/omega/improve")
async def improve_omega(request: OmegaImproveRequest):
    improvement_prompt = (
        "Improve the following Omega-AGI script based on these recommendations. "
        "If feedback is provided, incorporate it; if a score is given, aim for a higher score.\n"
        f"Current Omega Script: {request.omega}\n"
        f"Feedback: {request.feedback or 'None'}\n"
        f"Current Score: {request.score or 'Not Provided'}\n"
        "Provide the improved Omega script."
    )
    improved_omega = await call_translator_llm_correction(improvement_prompt)
    if not improved_omega:
        raise HTTPException(status_code=500, detail="Improvement process failed")
    return {"improved_omega": improved_omega}
```

**Note:**  
- The same LLM-based correction function (`call_translator_llm_correction`) may be reused here with a specialized prompt to focus on improvement based on feedback.
- Optionally, after improvement, the client could call the reflection endpoint again to verify if the score has increased.

---

## 11. Logs Retrieval Endpoint (Admin Only)

**Method:** GET  
**Path:** `/api/v1/logs`

**Purpose:**  
Retrieve logged queries and responses from the Supabase database for monitoring and diagnostics. This endpoint is intended for administrative use only.

**Security:**  
- Requires an admin token in the header (e.g., `x-api-key`).

**Request Parameters:** (optional)
- `limit` (int): Number of records to return.
- `offset` (int): For pagination.
- `order` (string): e.g., "desc" to sort latest first.

**Response:**  
JSON array of log records, each containing:
- `id`, `prompt`, `response`, `model`, `created_at`

**Pseudocode:**
```python
@app.get("/api/v1/logs")
async def get_logs(limit: int = 20, offset: int = 0, order: str = "desc", token: str = Header(...)):
    if token != settings.admin_token:
        raise HTTPException(status_code=403, detail="Forbidden")
    logs = await fetch_logs_from_supabase(limit=limit, offset=offset, order=order)
    return logs
```

---

## Comprehensive Function Instructions

### A. `call_translator_llm` Functions

1. **`call_translator_llm_human_to_omega(prompt: str) -> str`**  
   - **Purpose:**  
     Translate human language into an Omega script.
   - **Implementation:**  
     - Prepend a system prompt that explains Omega best practices.
     - Call the LLM (e.g., OpenAI 40-mini) asynchronously.
     - Return the generated Omega text.
   - **Pseudocode:**
     ```python
     async def call_translator_llm_human_to_omega(prompt: str) -> str:
         # Build system message with instructions on converting human language to Omega.
         messages = [
             {"role": "system", "content": "You are an expert in Omega-AGI symbolic language. Convert natural language instructions into a valid Omega prompt following best practices."},
             {"role": "user", "content": prompt}
         ]
         response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0.2)
         return response['choices'][0]['message']['content']
     ```
2. **`call_translator_llm_omega_to_human(prompt: str) -> str`**  
   - **Purpose:**  
     Convert an Omega script into natural language.
   - **Implementation:**  
     - Prepend a system prompt instructing the LLM to “translate” the symbolic language into plain English.
     - Return the resulting human-readable text.
   - **Pseudocode:**
     ```python
     async def call_translator_llm_omega_to_human(prompt: str) -> str:
         messages = [
             {"role": "system", "content": "You are an expert in interpreting Omega-AGI scripts. Translate the following Omega script into plain, natural language."},
             {"role": "user", "content": prompt}
         ]
         response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0)
         return response['choices'][0]['message']['content']
     ```
3. **`call_translator_llm_correction(prompt: str) -> str`**  
   - **Purpose:**  
     Generate a corrected/improved Omega script based on a prompt that details errors or desired improvements.
   - **Implementation:**  
     - Construct a prompt explaining the errors or improvement goals.
     - Use a low-temperature setting for deterministic output.
   - **Pseudocode:**
     ```python
     async def call_translator_llm_correction(prompt: str) -> str:
         messages = [
             {"role": "system", "content": "You are an expert in Omega-AGI. Correct and improve the following Omega script based on the instructions provided."},
             {"role": "user", "content": prompt}
         ]
         response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0.1)
         return response['choices'][0]['message']['content']
     ```

### B. `rule_based_parser`

- **Purpose:**  
  Convert natural language to Omega script using fixed grammar rules.
- **Implementation:**  
  - Use regular expressions or simple text transformations to identify keywords.
  - Map keywords to pre-defined Omega symbols and structure.
- **Pseudocode:**
  ```python
  def rule_based_parser(human_text: str) -> str:
      # Example: Look for "calculate", "sum", "and" in human_text.
      # If found, output a simple Omega script.
      if "sum" in human_text.lower():
          # For instance, create a simple Omega script:
          return 'DEFINE_SYMBOLS{S="SumTask"}; → AGI_Rpt WR_SECT(S, d="Calculate the sum as requested.");'
      else:
          raise ParsingError("Unable to parse the input into Omega format.")
  ```

### C. Agents for Validation and Correction

- **For `/api/v1/omega/validate`:**  
  The OmegaAgent’s `validate_script()` method should:
  - Verify the presence of key elements such as preamble, `DEFINE_SYMBOLS`, and at least one `WR_SECT`.
  - Check that symbols used in instructions are defined.
  - Raise an `OmegaValidationError` with a descriptive message if any check fails.

- **For `/api/v1/omega/correct`:**  
  The agent, when catching a `OmegaValidationError`, prepares a correction prompt (see pseudocode above) and uses `call_translator_llm_correction` to generate a revised Omega script. The correction loop continues recursively until a valid script is produced or the maximum attempts (e.g., 3) are reached.

---

# Data_Specs.md

This document outlines the data model and schema used by the Omega-AGI system, including the Supabase database schema for logging and any in-memory or application-level data structures relevant to the system's operation. It also describes how data flows through the system and what validation is applied at the data level.

## Supabase Database Schema
The system uses Supabase (which is a hosted Postgres database with an API layer) primarily for logging queries and responses. The schema is minimal and focused on this use case. Below is the main table schema:

**Table: `query_logs`** – Stores each Omega-AGI request and its result.
- `id` – **Primary Key**, a unique identifier for each log entry.  
  *Type:* `bigint` (or `serial/bigserial`). This can be an auto-incrementing integer. Alternatively, a UUID can be used. For simplicity, we use a big integer sequence.
- `prompt` – The Omega-AGI prompt text that was received.  
  *Type:* `text`. This field stores the full Omega script sent by the client. It can be large (Omega scripts with many sections), hence using `text` type (no length limit) is appropriate.
- `response` – The result produced by the agent for the given prompt.  
  *Type:* `text`. This might also be long (especially for multi-section outputs). We store the complete response text.
- `model` – The identifier of the model used to generate the response.  
  *Type:* `varchar(50)` or `text`. Example values: "openai-gpt4", "openai-gpt3.5", etc. This helps in analyzing which model was used for which request.
- `created_at` – Timestamp when the log entry was created.  
  *Type:* `timestamp with time zone` (or simply `timestamptz`). We set a default value to the current time on insertion. This records when the query was processed.

In SQL, the creation of this table might look like:
```sql
CREATE TABLE IF NOT EXISTS public.query_logs (
    id BIGSERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
```
This assumes a single public schema (which is default in Supabase). The `NOT NULL` constraints ensure we always store prompt, response, and model. If needed, we could allow `response` to be NULL for cases where an error occurred and no response was generated, but in our design, even on error we might store an error message or mark it somehow.

**Indexing**: By default the primary key gives an index on `id`. We might add an index on `created_at` if we frequently query recent logs or on `model` if we filter by model often. However, since this table is mainly for record-keeping and low-volume (each user request generates one insert), heavy optimization isn't critical at first.

**Row Level Security (RLS)**: In Supabase, RLS is enabled by default. If we use the service role key in the server, we bypass RLS. If we were to allow clients direct access (not in this design), we'd configure RLS so that users only see their own logs, etc. With our approach (server-side logging), it's fine to disable RLS or just use the service role.

## Data Models (Application Layer)
Within the FastAPI application, we use Pydantic models to define the structure of data for requests and responses, and possibly internal models for the agent. Key data models include:

- **OmegaRequest (Pydantic Model)**: Represents the expected JSON body for the Omega execution endpoint.
  - Fields:
    - `omega`: `str` – the Omega-AGI script.
    - `model`: `Optional[str]` – the model name (with a default in case not provided).
  - This model will validate that `omega` is provided and is a string, and that if `model` is provided, it is a string (further validation on allowed values might be in the endpoint logic rather than Pydantic).
  - Example definition:
    ```python
    class OmegaRequest(BaseModel):
        omega: str
        model: Optional[str] = None
    ```
  - Pydantic ensures that if a client sends a non-string (say an object or number) in place of `omega`, a validation error is raised. It also can provide auto-generated documentation for these fields.

- **OmegaResponse (Pydantic Model)**: Defines the structure of the response returned by the API.
  - Fields:
    - `result`: `str` – The output text from the agent.
    - (We can extend this in the future with additional metadata if needed, but currently one field suffices.)
  - Example:
    ```python
    class OmegaResponse(BaseModel):
        result: str
    ```
  - FastAPI will use this model to automatically format the response. We usually don't *have* to use a Pydantic model for response (we can just return a dict), but using one helps keep documentation in sync and ensures the data types are correct.

- **Agent Internal Models**: The agent might internally use data structures to represent the parsed Omega script. For instance, we could define classes or dicts for:
  - Symbol definitions: e.g., a dictionary mapping symbol tokens to their description or meaning.
  - Memory Graph: perhaps a graph structure (adjacency list or matrix) representing dependencies.
  - Sections: a list of section objects, each with a symbol identifier, a description, and eventually content.
  - However, initially, we might not implement a full parser; the agent could just work with the raw script string and use regex to find sections etc. As we improve, introducing formal models will be beneficial.
  - If implemented, an example could be:
    ```python
    class OmegaSection:
        symbol: str  # e.g. '++' or '^'
        description: str  # e.g. "Executive Summary: High-Depth Analysis"
        content: Optional[str] = None  # Will be filled after generation
    ```
    and the agent might have something like `self.sections: List[OmegaSection]`.
  - There's also the concept of an **Omega AST (Abstract Syntax Tree)** if fully parsing. That would have node types for each construct (DefineSymbols node, MemoryGraph node, Section node, etc.). Building that is complex, so in this initial design, we consider a simpler representation.

- **Configuration Data**: Data like model API keys or settings are loaded via environment variables (not hardcoded). At runtime, these might be stored in a config object or just accessed via `os.getenv`. We might have a simple `Settings` Pydantic model to parse environment variables:
  ```python
  class Settings(BaseSettings):
      openai_api_key: str = Field(..., env="OPENAI_API_KEY")
      supabase_url: str = Field(..., env="SUPABASE_URL")
      supabase_key: str = Field(..., env="SUPABASE_SERVICE_KEY")
      default_model: str = "openai-gpt4"
      model_provider: str = "openai"
  ```
  This uses Pydantic’s BaseSettings to read from env. The app can instantiate this at startup for convenient access to config.

## Data Flow and State
**Flow of Data for a Request**:
1. A JSON request comes in (through an HTTP POST). FastAPI parses this into an `OmegaRequest` object (data is now in memory as a Python object).
2. The `OmegaRequest` contains the Omega script as a string. This string is passed to the agent. No database interaction yet.
3. Inside the agent, if we implement a parser, the Omega script string would be converted into internal data structures:
   - A list/dict of symbol definitions.
   - A structure for memory graph (could use a dict of symbol -> list of dependencies).
   - A list of sections (with symbol and description).
   - Reflection and evaluation instructions flags.
   These become the state on which the agent operates. For example, `agent.symbols` might be a dict like `{"++": "HDExecSum", "^": "IntroMethod", ...}` based on `DEFINE_SYMBOLS` ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=2.%20Symbol%20Definitions%20%28)).
   If we do not fully parse, the agent might directly craft prompts from the raw string by finding certain patterns.
4. When the agent calls the LLM, it sends some portion of this data (likely reassembled as a prompt string, potentially including markers or the whole Omega script).
   - The LLM processes and returns text, which the agent then associates with certain parts of the data model (e.g., fills in the `content` of a section).
   - The data flows out from the LLM in textual form and is integrated into our Python data structures (the agent’s memory of content).
5. After all sections are generated, the agent compiles the final result (likely by concatenating section contents in order, or if it was a single-call execution, just taking the LLM’s full output string).
   - This final result is stored in an `OmegaResponse` object (or simply held as a string to return).
6. The response is sent out as JSON. At this point, the data has flowed from internal representation back to a serializable Python dict (via the Pydantic model) and then to JSON string over the network.

**State Management**:
- The system is **stateless** between requests. That means no persistent memory of one request to the next in the application layer (the only persistence is in the database logs).
- If one wanted conversation memory or continuity, that would have to be provided in the Omega prompt itself (e.g., via symbols representing previous context or a `MEM_GRAPH` that includes past outputs). The API does not implicitly remember prior prompts.
- Each request’s data (Omega script, intermediate states, final output) lives in memory only during that request’s processing. Python’s garbage collector will clean it up afterwards.
- The Supabase log is the only place where data persists. There, each record stands alone, and currently we do not have any foreign keys linking logs to users or sessions (as we have no user concept yet).
- We should consider data retention: The logs could grow indefinitely. For now, that’s manageable (text data, and if usage is moderate). In a long-term scenario, we might archive or delete old logs, or provide tools to search them.

## Validation Strategies (Data Level)
Validation happens at multiple levels, some of which were covered in **Endpoints.md** as part of request validation. Here we summarize and add details, especially focusing on the data content:

- **JSON Schema Validation**: Performed by Pydantic (via `OmegaRequest`). This ensures the JSON has the right shape (e.g., `omega` exists and is a string). This is the first line of defense and prevents a lot of malformed data from ever reaching the agent or database.
- **Omega Script Validation**: This is more complex. Ideally, we validate that the `omega` string follows the Omega-AGI format:
  - It should start or contain certain expected sequences. For instance, a well-formed Omega prompt usually includes `DEFINE_SYMBOLS{}` and one or more `WR_SECT(` commands ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=7.%20Section%20Definitions%20%28)). We can do simple checks:
    * Does the string contain `DEFINE_SYMBOLS` and an opening/closing brace?
    * Does it contain `WR_SECT(`?
    * If it has a `MEM_GRAPH{}`, ensure it has matching braces and the arrows are well-formed.
    * If possible, ensure every symbol used in `WR_SECT` or `MEM_GRAPH` was defined in `DEFINE_SYMBOLS` ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,%E2%A7%89)).
    * Check for balanced parentheses, braces, etc., since Omega has a lot of structured syntax.
  - Some of these checks can be done with regex or by writing a small parser for key tokens. For now, we might implement a **basic validator**:
    - Look for known keywords in sequence (preamble tokens like `Ω` or `AUTH[`, then `DEFINE_SYMBOLS{`, optional `MEM_GRAPH{`, etc.). If something crucial is missing, flag it.
    - Ensure comments (the `/* ... */` in symbol definitions) are properly closed if present.
    - This won't guarantee full correctness (only a proper parser could do that), but it catches blatant errors.
  - If validation fails, the agent returns an error. (As mentioned, possibly raising an exception that the endpoint catches to send a 400 response with a message.)
  - In the future, we might integrate an EBNF grammar check as referenced in the Omega spec ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=%2A%20Structured%20Execution%3A%20Omega,reflection%20as%20a%20core%2C%20first)) for complete validation.
- **Model Field Validation**: If `model` is provided, we validate it against allowed values. This could be done via:
  - A Pydantic `validator` on the `OmegaRequest` model that checks `model` in a list, or
  - A simple `if model not in ALLOWED_MODELS: raise HTTPException(400, "Unknown model")` in the endpoint code.
  - Allowed models might be configured in an environment variable or a constant list in code (["openai-gpt4", "openai-gpt3.5", "google-gemini"] etc.). This prevents someone from requesting an undefined model and causing downstream errors.
- **Response Validation**: After generation, before returning, we might validate the response:
  - Ensure it's a string (the LLM integration should always give us a string, but double-check).
  - Optionally, ensure it’s not empty. If it's empty, perhaps replace with a message "[No output]" or an error because an empty output likely indicates something went wrong.
  - Check for any markers of failure. For example, if the LLM returned an error message as text (maybe if our prompt was misinterpreted and it said "I'm sorry, I cannot do that"), we might intercept that. However, that might be considered a valid outcome if the AI refused due to policy. This is tricky; possibly log and let the client see it.
- **Database Insertion Validation**: The Supabase client or API will ensure that our data types match the table definition:
  - If we accidentally send a too long string for a field with a length limit, it would error (we chose `text` for flexibility).
  - We ensure `model` field always has a value (we always supply one, default to default model if none). In logs, we don't want null model. If `model` was None (not provided), we substitute it with a default string before logging.
  - Supabase might reject an insert if required fields are null. Our design avoids that.
  - If an insert fails for any reason (rare with correct data), we catch it and log locally. The data in memory is still valid and already returned to client.

## Data Flow Diagrams (Conceptual)
*(Since images are not allowed, we'll describe the data flow in text form.)*

Imagine the journey of data through the system as follows:

**Client -> API -> Agent -> LLM -> Agent -> API -> Database**:

1. **Client to API**: The client sends a JSON with the Omega script. This is text data coming over HTTP.
2. **API to Agent**: FastAPI parses JSON into Python structures. The `omega` string goes into an `OmegaRequest` object. Then it's passed to the agent call. At this point, the data is in memory in a structured form: `request.omega` is accessible as a Python `str`, `request.model` as `str` or `None`.
3. **Agent internal processing**: The agent may create new data from the input:
   - If parsing, it creates data classes or dicts (e.g., `symbols = {...}`, `sections = [...]`).
   - It might transform the prompt: for example, compile a system prompt for the LLM that includes the Omega instructions in a certain format or with additional guidance. This is a new piece of data derived from `omega`.
   - It retains the original script (maybe stored as a field or accessible if needed for error messages).
4. **Agent to LLM**: The agent sends a request to the LLM API. The data going out is typically a string (for OpenAI, it's a series of messages but effectively they are strings). That string likely contains the Omega prompt (possibly verbatim or slightly reformatted) and maybe some additional text (like a one-shot example or a role specification: "You are Omega agent, ...").
   - *Example*: The agent might send a system message: "Follow the Omega-AGI instructions strictly." and a user message with the `omega` content. This combination is data leaving our system to OpenAI.
   - It's important that any sensitive info (like if the prompt had confidential data) is intended and allowed to go to the LLM provider. (This is a privacy consideration; using an external API means that data is seen by that provider.)
5. **LLM to Agent**: The LLM returns text (data coming from external service into our system). The agent receives it (likely via the OpenAI Python library, it comes as a string or part of a JSON from OpenAI).
   - The agent might parse this text if needed or directly use it. For example, if the Omega prompt was executed in one shot, the returned text might already be the final answer; agent just marks it as result.
   - If the agent was doing stepwise, maybe the returned text is one section. The agent assigns that to the corresponding section object (data assignment).
   - If there is a reflection/evaluation cycle, data flows in a loop: agent sends something, gets evaluation, decides to adjust, sends new prompt. Each of these intermediate results is stored temporarily.
6. **Agent to API (result)**: After final output is ready, the agent provides it to the API layer. Typically, the agent’s `run()` method returns a string (the result text) or an `OmegaResponse` object. FastAPI then serializes this into JSON. The data is now structured as per `OmegaResponse`, e.g., `{"result": "...text..."}`.
7. **API to Client**: The JSON is sent back over HTTP to the client. The data is now out of our system (except for the log).
8. **API to Database (Logging)**: Concurrently or just after, a log entry is created:
   - We compile a dictionary like `{"prompt": omega_str, "response": result_str, "model": model_used, "created_at": now}`.
   - This is sent to Supabase via an API call (the supabase client will send JSON or an HTTP POST to the Supabase REST endpoint). 
   - Supabase writes it to the `query_logs` table. Now the data is stored in the DB.
   - We do not read anything back except maybe a success acknowledgment. If we needed the inserted ID, Supabase can return it, but we don’t really need it for our logic.
   - If logging fails, that data might be lost (unless we implement retries or a fallback log as mentioned).

**Data Lifespan**:
- In-memory data (OmegaRequest, agent structures) lives for the duration of the request handling. Python will clean up afterwards. If using asynchronous workers, each request has its own scope.
- Database data (query_logs entries) persist until manually cleaned. This means even after the request is done, the prompt and response can be retrieved from the DB. This is useful for offline analysis and debugging. It also means sensitive info might reside there, which requires securing that DB.
- We should consider what happens if the same user sends something like a password or key in a query (not likely in normal use, but imagine the user asks "My password is X, what does that mean?" – then we logged it). The system design did not plan for scrubbing such data. As a policy, we assume the content users send is okay to log, but in a more privacy-conscious design, one might allow opting out of logging or encrypting logs.

## Validation Strategies Recap
To ensure the data remains consistent and valid throughout the flow:
- At **entry**: Use Pydantic validation for structure and types ([How to secure APIs built with FastAPI: A complete guide](https://escape.tech/blog/how-to-secure-fastapi-api/#:~:text=In%20FastAPI%2C%20handling%20and%20validating,of%20data%20in%20each%20request)).
- For **Omega content**: Basic sanity checks (with the possibility of extending to full parsing). Fail early if it's not making sense, to save LLM calls.
- For **LLM outputs**: Perhaps verify that the output contains some expected structure if the Omega prompt demanded it. For example, if the Omega instructions clearly asked for 3 sections, but output has only 2, we know something's off. The agent could decide to re-prompt or include a notice. At the very least, log this discrepancy for developers to review.
- For **database**: Ensure every insert has the required fields. We format data going into the DB carefully (no binary or special types, everything as text or standard types).
- For **concurrency**: If multiple requests come in, each has its own data. We avoid using any global variables that could mix data between requests. For instance, the agent instance is created per request, not reused globally with mutable state. This isolation is a form of data validation too (ensuring user A's data doesn't leak into user B's result).
- **Testing**: Finally, we validate our strategies by testing with various inputs:
  - Valid Omega scripts produce correct logs (check the DB entry).
  - Invalid scripts produce a 400 and do not create a log (or create a log with maybe an error marker if we choose to log attempts).
  - Large scripts near the limit still work (or are cleanly rejected if too large).
  - Special characters in scripts (like quotes, backslashes, non-ASCII like Ω symbol itself) are handled properly. We ensure correct encoding when storing in JSON and DB (UTF-8 throughout).
  - Check that the `model` selection correctly routes to different endpoints (this is more of a logic test than data, but it ensures the data in `model` field correlates with actual used model).

By designing the data schema and flow with these considerations, we aim for a robust system where data integrity is maintained from input to output to logging. This not only helps in correct functionality but also in debugging and improving the system over time, as the logs provide a reliable record of what happened internally.

---

# Omega_Specs.md

This document details the Omega-AGI format and how it is used within the system. It serves as a guide for developers to understand the structure of Omega-AGI prompts, the requirements for those prompts to be considered valid, and how the system validates and leverages them. We also reference the master Omega-AGI documentation as needed for deeper understanding.

## Overview of the Omega-AGI Format
**Omega-AGI (Ω-AGI)** is a specialized, symbolic instruction language for communicating with AI agents. Unlike plain natural language prompts, Omega-AGI provides a highly structured syntax that aims to make the AI's behavior deterministic, unambiguous, and efficient ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=language%2C%20which%20can%20be%20ambiguous,method%20for%20conveying%20complex%20instructions)). It is designed to pack complex instructions into a compact format, enabling the AI to interpret and execute multi-step tasks reliably. Key characteristics of Omega-AGI include:
- **Symbolic Representation**: It uses symbols (like `++`, `^`, `@`, etc.) to represent concepts, sections, or pieces of information, rather than verbose descriptions. This improves token efficiency and consistency ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,reliable%20and%20efficient%20processing%2C%20and)).
- **Structured Execution**: Omega-AGI prompts have a defined structure and grammar (based on EBNF grammar rules) that outline the flow of execution for the agent ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=%2A%20Structured%20Execution%3A%20Omega,reflection%20as%20a%20core%2C%20first)). This structure covers everything from initialization, to content generation, to reflection and evaluation phases.
- **Deterministic & Machine-Readable**: The format is meant to be machine-readable above all. An Omega-AGI compliant agent should interpret the same prompt in the same way every time, reducing variability in outputs ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,the%20computational%20burden%20of%20interpretation)). The structure minimizes ambiguous natural language elements.
- **Reflection and Self-Optimization**: Omega-AGI includes built-in support for reflection operators (`∇`, `∇²`) and an optimization operator (`Ω`) that allow the prompt itself to instruct the agent to evaluate and improve its output ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,Facilitates%20systemic%20optimization%2C%20adjusting%20execution)). For example, `∇` might trigger the agent to double-check or analyze its current result before finalizing, and `Ω` can indicate an optimization routine to refine the approach.
- **Modularity and Reusability**: Because prompts are structured and symbolic, parts of a prompt can be reused or adapted easily. Also, an agent can potentially modify or augment a prompt programmatically (though in our current system, prompts are authored by users, not AI).

The Omega-AGI format can be thought of as a "program" for the AI to follow. Just as a programming language has a specific syntax and keywords, Omega-AGI has its own syntax and special tokens that an Omega-aware agent or interpreter will recognize.

Our system is built to support Omega-AGI prompts as the primary input. The FastAPI endpoint expects the `omega` field to contain instructions following this format. We rely on the structure to orchestrate calls to the LLM and handle output logically.

## Required Structure of an Omega-AGI Prompt
An Omega-AGI prompt typically consists of several distinct sections in a specific order. According to the Omega-AGI Instruction Guide (v2.0 by Bradley Ross), a one-shot task prompt often includes the following components ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=4,AGI%20Prompts)):

1. **Preamble (Standard Overhead)**: This is usually a sequence of Omega operators at the very beginning of the prompt that set the stage for execution. It may include:
   - Reflection and optimization flags: e.g., `∇²` (to enable meta-reflection) and `Ω(∇ history)=>δ(ts='opt')` (which appears to relate to using historical data for optimization) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=This%20document%20provides%20a%20complete,AGI%20prompt%20engineering)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=1)).
   - Authentication and security directives: e.g., `AUTH[AGI_BA]` might designate the agent's role or permissions (AGI_BA could stand for an AI Business Analyst persona), and `SECURE_COMM(enc=True)` indicates secure communication mode ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=1)).
   - These elements are not the "content" of the prompt but rather configuration. They prepare the agent with how to execute the instructions (e.g., enabling reflection capabilities or defining a profile).
   - *Example Preamble*: `∇²;Ω(∇ history)=>δ(ts='opt');AUTH[AGI_BA];SECURE_COMM(enc=True);`  
     This example means: turn on second-level reflection ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,correction%20strategies%20over%20time)), use optimization based on history, authenticate as AGI_BA profile, and ensure communications are encrypted.

2. **Symbol Definitions (`DEFINE_SYMBOLS{...}`)**: A block that defines all symbols used in the prompt along with their meanings or mappings ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=2.%20Symbol%20Definitions%20%28)). This is critical for token efficiency and clarity.
   - The syntax is typically `DEFINE_SYMBOLS{ symbol1="Name1" /*Description1*/, symbol2="Name2" /*Description2*/, ... }`.
   - The symbols are often short tokens like `++`, `^`, `@`, etc., mapped to descriptive identifiers or roles. The comments (`/* ... */`) provide human-readable explanations.
   - **Requirement**: If a symbol will be used later (in memory graph or sections), it *must* be defined here. Conversely, symbols defined but not used are harmless but unnecessary.
   - *Example*: `DEFINE_SYMBOLS{++="HDExecSum" /*Executive Summary: High-Depth Analysis*/, ^="IntroMethod" /*Introduction & Methodology*/, @="CompProfiles" /*Competitor Profiles*/ }`  
     This defines `++` as a placeholder for the Executive Summary section, `^` for Intro/Methodology, `@` for Competitor Profiles, etc. ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=2.%20Symbol%20Definitions%20%28)).

3. **Memory Graph (`MEM_GRAPH{...}`)**: An optional but powerful section where you outline the relationships between symbols (sections or components) in a directed graph form ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=defined.%203.%20Memory%20Graph%20%28)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,%E2%A7%89)).
   - Syntax uses arrows, e.g., `A -> [B, C]` meaning A depends on B and C, or contains information from B and C.
   - This guides the logical flow of information: the agent knows which parts to complete first and how information should propagate. It's like declaring that "to complete section A, you will need content from sections B and C".
   - **Requirement**: All symbols used here should be defined in DEFINE_SYMBOLS. The graph should be acyclic (it doesn't make sense to have circular dependencies).
   - *Example*: `MEM_GRAPH{ ++->[^,@,&,&,⧉+]; ^->[@,&]; ... }`  
     This example (from the Coffee Shop analysis prompt) means the Executive Summary (`++`) draws from Introduction (`^`), Competitor Profiles (`@`), Comparative Analysis (`&` appears twice, possibly two different aspects?), and References (`⧉+`). Also `^` (Intro) depends on `@` and `&` ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,that%20depend%20on%20them%2C%20optimizing)). This informs the agent that it should gather or consider competitor profiles and analysis before writing the executive summary, etc.

4. **Conditional Logic (Optional)**: Omega-AGI can include conditional execution statements such as `IF ... THEN ...` blocks ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=4)).
   - They check some condition in memory (e.g., a variable or prior result) and decide whether to execute certain actions.
   - In the example, `IF MEM[report_status] != 'completed' THEN → AGI_Rpt GEN_R(local_coffee_shop_analysis);` means: if in memory the report_status is not completed, then generate a report. `GEN_R` might be a command to generate a full report.
   - **Requirement**: Conditions likely refer to memory keys that either have been set previously in the prompt or are default (like the example assumes a memory key `report_status`).
   - The language likely has a specific syntax for conditions (e.g., `IF <cond> THEN <OmegaCommand>;`).
   - This part is optional; many prompts won’t need it, but it's supported for more dynamic behavior.
   - For a developer, unless you plan on using memory states across runs, you might not include conditions in initial prompts.

5. **Formatting and Type Settings**: Commands to set how the output should be formatted or the style/tone of the output ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=5,Settings)).
   - Examples from the guide: `→ AGI_Rpt FMT_R(fmt="TXT", d="H");` and `→ AGI_Rpt SET_T(t=MktExpertLevel);`.
   - `FMT_R(fmt="TXT", d="H")` might mean "format the report as plain text with headings" (d="H" could indicate including headings).
   - `SET_T(t=MktExpertLevel)` could set the tone/rigor to "Marketing Expert Level".
   - These instructions tell the agent about the desired output format (e.g., maybe you could set `fmt="HTML"` for HTML output, or `d="L"` for including links, guessing from context).
   - **Requirement**: These should appear before content generation. They configure the `AGI_Rpt` (the agent's report generator module, presumably) with how to produce output.
   - They are optional if you are okay with defaults (likely default is plain text, moderate detail).
   - As an Omega prompt author, you might use these to ensure the style is correct. For instance, if you want a JSON output, there might be a format setting for JSON (if supported by Omega).

6. **Neural Block (Optional)**: `NEURAL_BLOCK("...")` allows you to insert a block of instructions or content that should be handled by a neural network as a black box ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=6)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,sensitivity%20and%20criticality%20of%20each)).
   - This is essentially an escape hatch: if there is something that doesn't fit the formal Omega-AGI language, you can wrap it in NEURAL_BLOCK and the agent/LLM will treat the inner content as raw instruction or data.
   - In the example prompt, `NEURAL_BLOCK("CoffeeShop_Competitor_Analysis");` is likely a call to a specific trained network or just a marker for context. It might load a specialized context or trigger a particular capability for coffee shop competitor analysis.
   - For our implementation, we may not have special neural modules. But if a prompt uses NEURAL_BLOCK, our agent will likely just include that text to the LLM as is. It’s optional and can be omitted if not needed.
   - **Requirement**: Use NEURAL_BLOCK only when necessary (for unstructured data or external context). Otherwise, keep everything in Omega structure.

7. **Section Definitions (`WR_SECT` loops)**: This is the core content generation part of the prompt ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=7.%20Section%20Definitions%20%28)).
   - `WR_SECT` stands for "Write Section". Each `WR_SECT(symbol, t=symbol, d="...")` call directs the agent to write a section corresponding to a symbol, with a title and description.
   - Format: `→ AGI_Rpt WR_SECT(X, t=X, d="Instructions for this section");`
     - The arrow `→ AGI_Rpt` means we are invoking the report-writing agent to execute a command.
     - `t=X` likely sets the title using symbol X's defined name (or uses X itself as a key).
     - `d="..."` is the actual content directive for that section, written in a mix of symbolic and brief natural language.
   - Several `WR_SECT` commands are typically listed in order, each for one symbol/section. They effectively break the output into manageable pieces.
   - Inside the `d="..."` description, the prompt author will often use the symbols and sometimes quoted words (likely treated as is) to instruct what to include.
   - In the example:
     ``` 
     → AGI_Rpt WR_SECT(++, t=++, d="Exec summary (3+ parag). \"Synth\" \"LocalShop\" \"CompMarkAnalysis\". Highlight key competitor strategies, comparative insights, and core \"MarketRecs\". Concise, \"AI\".");
     ```
     This is instructing the AGI to write the Executive Summary section (symbol `++`), title it with whatever `++` stands for, and in the description: 
     - It says Exec summary 3+ paragraphs, includes certain keywords in quotes (Synth, LocalShop, CompMarkAnalysis, MarketRecs) which are likely defined symbols or shorthand for concepts, and style hints like "Concise, AI" (maybe meaning concise and in an AI-professional tone).
   - **Requirement**: Each WR_SECT should refer to a symbol defined in DEFINE_SYMBOLS. The sequence of WR_SECT defines the structure of the final output. A prompt should have at least one WR_SECT (otherwise no content is being explicitly generated).
   - The agent will follow these instructions to generate each part. If any section is very complex, the LLM might do an internal breakdown, but as far as prompt format, this is how you specify content.

8. **Evaluation Loop (`FOR...DO...EVAL_SECT`)**: Optional, for quality control ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=8.%20Evaluation%20Loop%20%28)).
   - Syntax: `FOR sec IN {list of symbols} DO → AGI_Rpt EVAL_SECT(sec, th=90, iter=3);`
   - This instructs the agent to iterate through each section and evaluate its quality, with a threshold and iteration count.
   - In the example, `th=90` could represent a quality score threshold (maybe out of 100) and `iter=3` means allow up to 3 attempts to improve if below threshold.
   - `EVAL_SECT(sec, ...)` likely triggers the agent to review that section’s content (possibly by feeding it back into the LLM with some prompt like "critique this section") and then either directly improve it or provide feedback so that a subsequent generation can improve it.
   - **Requirement**: If used, sec (the section symbol or list of symbols) should be those that were generated. Typically, you'd evaluate all major sections. It's optional; if high quality isn't critical or time is short, you might skip this to save tokens.
   - Our implementation might not fully automate re-writing sections, but conceptually, if we detect issues, we could re-run with adjustments. The Omega format has this built in to allow self-improvement.

9. **Finalization**: The Omega format doesn't explicitly have an "end" marker; the script itself is the set of instructions. Once the agent has executed all commands (wrote all sections, did evaluations), the output is considered complete. The final answer returned to the user is essentially the concatenation of all the written sections (assuming a report context). If it were a simpler query, it might just be one section or even a direct answer without formal sections.

In summary, an **Omega-AGI prompt** is structured very much like a small program: it sets up some variables (symbols), optionally sets a plan (memory graph), then runs through generating content, and possibly evaluates it. All these parts use a special syntax that the agent (and LLM) need to understand.

Our system does not yet implement a parser to enforce every rule of this structure, but it expects prompts roughly in this shape. When writing Omega prompts, ensure you include at least the essentials: symbol definitions and one or more `WR_SECT` instructions. The richer features (memory graphs, eval loops) can be added as needed.

## Validation Requirements for Omega Prompts
For an Omega-AGI prompt to be processed correctly, it should meet certain criteria. These requirements are based on the design of Omega-AGI and practical considerations for our implementation:

- **Presence of Key Sections**: At minimum, the prompt should define any symbols it uses and include at least one content generation command (`WR_SECT` or a `GEN` command) that produces output. A prompt that has only a preamble and symbols but no section to output will result in no answer.
- **Define-Before-Use**: Any symbol used in `WR_SECT`, `MEM_GRAPH`, or other commands must be defined in the `DEFINE_SYMBOLS` block ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,%E2%A7%89)). Our system may check the text to ensure that, for example, if it sees `WR_SECT(X, ...)`, then `X` (or whatever symbol is inside) was introduced in a prior `DEFINE_SYMBOLS`. If not, that's an error.
- **Balanced Syntax**: All brackets and parentheses must be properly closed:
  - Every `{` must have a matching `}` (for DEFINE_SYMBOLS, MEM_GRAPH).
  - Every `(` has a `)` (for function-like syntax such as `Ω(...)` or `WR_SECT(...)`).
  - Comments `/* ... */` should be properly closed.
  - If any are mismatched, the agent might not parse it right, and our validator will likely flag it. For example, a missing brace in DEFINE_SYMBOLS could confuse everything after it.
- **Known Commands**: Use only Omega-AGI defined operators and commands. These include:
  - The reflection and optimization operators: `∇`, `∇²`, `Ω`.
  - The `DEFINE_SYMBOLS`, `MEM_GRAPH`, `WR_SECT`, `EVAL_SECT`, and perhaps `GEN_R`, `FMT_R`, `SET_T`, `NEURAL_BLOCK`, `AUTH`, `SECURE_COMM`, etc., as seen in the guide. Using an arbitrary or unknown token (e.g., if you guess a command that isn't defined) could lead to undefined behavior. Our system might not explicitly catch unknown commands, but the LLM could be confused by them.
  - If unsure, stick to the patterns seen in examples or documented features. As Omega-AGI evolves, new commands might be introduced, but then the agent must be updated to handle them.
- **Logical Consistency**: The prompt should make logical sense:
  - The memory graph should not have contradictions (like `A->B` and also `B->A` forming a cycle).
  - Symbols should be used in a consistent way (for instance, if `&` is used for two different things in comments, that's confusing; each symbol should have one purpose).
  - If the prompt is asking for something the model can’t do (e.g., an overly long report with limited context length), the output might be truncated. So there is a practical limit to how much you can ask for in one go.
- **No Overlapping Sections**: Avoid generating the same content twice. For example, do not have two `WR_SECT` for the same symbol unless intentional (the second would overwrite or append? It's unclear, better to avoid).
- **Use of Reflection/Eval**: If you include `EVAL_SECT`, ensure you also provided criteria (threshold and iter count). If you just put `EVAL_SECT(sec)` without parameters, it might default to something or cause an error. Similarly, using `Ω(∇ history)=>δ(ts='opt')` in preamble suggests there's some historical optimization; our initial agent might not actually use history (since we aren't persisting it), but including it doesn't break anything, it just won't have any past data to use. It's fine to include for future compatibility.
- **Encoding of Special Characters**: Omega uses some Unicode characters like `∇` (nabla) and `Ω` (Omega symbol). These should be included as such. If you are writing an Omega prompt in a normal text editor or JSON, ensure it is encoded in UTF-8. Our API expects UTF-8 JSON, so it should handle these characters. Just be cautious if copying from some sources that they don't get lost. Alternatively, one could use ASCII placeholders if defined (the master doc might allow some fallback, but it's not mentioned explicitly). We recommend using the actual symbols.
- **Master Document Reference**: For full details, one should refer to the **Omega-AGI Instruction Guide v2.0** by Bradley Ross, which is the authoritative source on the syntax and usage ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=This%20document%20provides%20a%20complete,AGI%20prompt%20engineering)). That guide includes examples and deeper explanations of each component of the language, as well as the rationale behind them. Our system aims to align with that spec, and any deviations or limitations are due to implementation simplicity at this stage.

In practice, when you send an Omega prompt to the system:
- If it's well-formed, the agent will either run it in one shot (giving the whole prompt to the LLM) or step by step. The better structured it is, the more likely the LLM will follow it exactly and produce the desired structured output.
- If it's ill-formed, a few things could happen: The agent might catch a problem and return an error. Or the agent might pass it through and the LLM might get confused and produce an incorrect or incomplete result. Therefore, following the required structure is important for getting good results.

Our **validation** (as described in Data_Specs) will catch some errors, but not everything. It remains the developer's responsibility to craft the Omega prompt carefully. Over time, we plan to improve the validator or even have the agent attempt to correct minor prompt issues (given Omega's self-improvement ethos).

## Reference to Master Omega-AGI Document
For a comprehensive understanding of Omega-AGI syntax and principles, refer to the master document: *"Omega-AGI Instruction Guide: A Comprehensive Overview (v2.0)" by Bradley Ross*. This guide outlines the methodology, structural components, and step-by-step instructions for effective Omega-AGI prompt engineering ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=This%20document%20provides%20a%20complete,AGI%20prompt%20engineering)). It covers in detail:
- The philosophy and goals of Omega-AGI (determinism, efficiency, etc.) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,the%20computational%20burden%20of%20interpretation)).
- The full breakdown of the language’s syntax (including any grammar definitions in EBNF).
- Examples of one-shot prompts and how they are constructed from start to finish.
- Explanation of reflection operators and when to use them ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,Facilitates%20systemic%20optimization%2C%20adjusting%20execution)).
- Best practices and common patterns for designing prompts (like how to choose symbols, how to structure memory graphs for various tasks, etc.).
- Limitations and planned extensions of the language (as of v2.0).

We highly encourage reading that document if you intend to author complex Omega-AGI prompts. It will serve as the primary reference for anything not explicitly covered in our documentation. Our Omega-AGI support is built to align with that spec, and any updates in the Omega-AGI standard may require updating the system accordingly.

In conclusion, Omega-AGI format is the backbone of this AI system's communication. By adhering to its structure and guidelines, developers can harness advanced AI behaviors (like multi-step reasoning and self-evaluation) in a controlled and consistent manner. This documentation plus the Omega-AGI guide should together provide a self-contained resource to construct and utilize Omega-AGI prompts effectively in the system.

---

# Agent_Coordination.md

In this section, we delve into the internal workings of the Omega agent – the component responsible for coordinating the processing of Omega-AGI instructions. We'll cover the agent's structure, how it handles an Omega script step-by-step (pseudocode), how it manages errors during the process, and potential improvements to make it more robust and capable in the future.

## Agent Structure and Role
The Omega Agent can be thought of as an **orchestrator** or **interpreter** for the Omega-AGI language. Its structure in the code is likely an `OmegaAgent` class (or a set of functions) that encapsulates:
- The Omega script (provided by the user).
- Any parsed representation of that script (symbols, sections, etc.).
- The logic to execute each part of the script in order.
- Interaction with the LLM through the model interface.

**Key responsibilities of the Agent:**
- **Initialization**: Read and store the input script. Possibly, do an initial parse or at least identify main sections (like find the DEFINE_SYMBOLS block, etc.) for easier reference later.
- **Validation**: Perform any checks on the script structure (as discussed in Omega_Specs). The agent might have a method `validate()` that checks for required segments and consistency.
- **LLM Prompt Construction**: Convert parts of the Omega script into actual prompts that can be sent to the LLM. For example, the agent might maintain a system prompt that informs the LLM about Omega semantics and then user prompts that include the Omega commands.
- **Chain-of-Thought Coordination**: Omega encourages a chain-of-thought style (with reflection and evaluation). The agent decides whether to let the LLM handle everything in one go or to break the task:
  - It could first prompt the LLM to "think" or create an outline (if ∇ or memory graph suggests doing so).
  - Then prompt to fill in each section.
  - Then prompt to evaluate and refine sections if needed.
  Essentially, the agent can manage a multi-turn interaction with the LLM where each turn corresponds to a part of the Omega workflow.
- **Error Handling**: If any step yields an error (e.g., LLM returns something unusable or the API call fails), the agent catches it and responds appropriately (maybe by retrying or aborting with an error).
- **Output Assembly**: Combine results from multiple steps (if the process was broken into multiple calls) into the final output.

The agent is somewhat analogous to a program executor for a domain-specific language (Omega-AGI being that DSL). Initially, we might implement it in a simplified way (perhaps treating the entire Omega script as a single prompt), but as we enhance it, the structure allows stepwise execution.

## Pseudocode of Agent Processing Flow
Let's outline the agent's logic in pseudocode to illustrate how it processes an Omega script. This pseudocode abstracts away specific API calls and focuses on logical steps:

```python
class OmegaAgent:
    def __init__(self, script: str, model: str):
        self.script = script
        self.model = model
        # Placeholders for parsed components
        self.symbols = {}
        self.sections = []
        self.memory_graph = {}
        self.preamble = ""
        self.evaluation_plan = None
        # ... other needed attributes

    def run(self) -> str:
        try:
            # Step 1: Basic validation
            self.validate_script()

            # Step 2: Parse core components (basic parsing)
            self.extract_preamble()
            self.extract_symbols()
            self.extract_memory_graph()
            self.extract_sections()
            self.extract_evaluation_plan()

            # Step 3: Optionally, handle reflection or initial analysis
            if self.has_reflection_instruction():
                # Create a prompt to ask the LLM for a reflection or outline
                reflection_prompt = self.build_reflection_prompt()
                reflection_result = call_LLM(reflection_prompt, model=self.model, max_tokens=500)
                # (We might not directly use reflection_result in v1, but could log or parse it)
                # Possibly adjust strategy based on reflection result (not implemented initially).

            # Step 4: Generate sections content
            results = {}
            for sec in self.sections:  # sections is list of section symbols in order
                section_prompt = self.build_section_prompt(sec)
                section_text = call_LLM(section_prompt, model=self.model, temperature=0.2)
                results[sec] = section_text
                # Optionally, store in memory for evaluation

            # Step 5: Evaluate sections if EVAL_SECT is specified
            if self.evaluation_plan:
                for sec, criteria in self.evaluation_plan.items():
                    # criteria might have threshold and iter count
                    quality = self.evaluate_section(results[sec], sec, criteria)
                    if quality < criteria.threshold:
                        # Try refining
                        for attempt in range(criteria.iterations):
                            feedback_prompt = self.build_feedback_prompt(results[sec], sec)
                            feedback = call_LLM(feedback_prompt, model=self.model)
                            # Possibly incorporate feedback and regenerate section
                            regen_prompt = self.build_regeneration_prompt(sec, feedback)
                            new_text = call_LLM(regen_prompt, model=self.model, temperature=0.2)
                            results[sec] = new_text
                            quality = self.evaluate_section(results[sec], sec, criteria)
                            if quality >= criteria.threshold:
                                break
                        # After attempts, proceed with whatever is there (improved or not)

            # Step 6: Assemble final output
            final_output = self.assemble_output(results)
            return final_output

        except OmegaValidationError as e:
            # Known issue with prompt structure
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Unexpected error
            # Log the error internally (not shown in pseudocode)
            raise HTTPException(status_code=500, detail="Internal error during agent processing")
```

A few notes on the above pseudocode:
- `validate_script()`: would implement checks for structural integrity.
- `extract_*` methods: not full parsing but likely using regex or string operations to find parts:
  - E.g., find substring between "DEFINE_SYMBOLS{" and the matching "}" to get symbol definitions, then parse those by splitting on commas not inside comments.
  - For sections, find every occurrence of `WR_SECT(` and extract the parameters.
  - `evaluation_plan` might capture `th` (threshold) and `iter` values from `EVAL_SECT`.
- `build_section_prompt(sec)`: constructs a prompt to send to the LLM to generate that section. One simple approach is:
  - Combine the preamble, symbol definitions (so LLM knows what symbols mean if needed), maybe a note from memory graph if relevant (or the LLM can infer structure if the entire prompt is given).
  - Then specifically instruct, e.g.: "Write the section for {symbol_name} as described: {description}." Possibly also provide context from other sections if needed (if memory graph says sec depends on others, and if we've generated those, we might include them or summarize them).
  - For initial version, we might just give the exact Omega command as prompt, expecting the LLM to have been primed to understand it.
  - For example, prompt to LLM could be: `[System: You are an Omega agent... (some explanation of format)] [User: ∇²;Ω=>... DEFINE_SYMBOLS{...}; MEM_GRAPH{...}; → AGI_Rpt WR_SECT(X,...); ...]`. Essentially feed the entire Omega script as is. GPT-4 might parse it. This is the simplest but not guaranteed method. Breaking it, as pseudocode does, might be more controlled.
- `call_LLM(prompt, model=...)`: abstracts the actual API call. It would include handling for the model name differences.
- Reflection and evaluation parts are advanced and might not be fully implemented in the first iteration. The pseudocode shows an approach: ask for reflection/outlines, and do a loop for evaluation where you ask the LLM to evaluate or improve a section. For instance, `evaluate_section` might itself call an LLM to get a score or just do a regex count of certain things as a naive check (like ensure at least 3 paragraphs if "3+ parag" was instructed).
- In initial implementation, we might skip actual reflection and eval to keep things simpler: basically go straight to generating sections and assembling output.

## Error Handling in Agent Execution
Within the agent, errors can happen at each step:
- **Parsing Errors**: If `extract_symbols` or others fail (e.g., can't find a closing brace), the agent knows the prompt is malformed. It would raise an `OmegaValidationError` (custom exception) with a message like "DEFINE_SYMBOLS block not closed" or "Undefined symbol X in WR_SECT". This is caught and translated to a 400 response.
- **LLM Call Failures**: If `call_LLM` throws (like network issue), the agent could catch and attempt a retry:
  ```python
  try:
      section_text = call_LLM(prompt, model=self.model)
  except ExternalServiceError as e:
      if can_retry(e):
          section_text = call_LLM(prompt, model=self.model)
      else:
          raise
  ```
  If ultimately it fails, we propagate an exception that becomes a 502/503 to user.
- **LLM Output Issues**: The LLM might return something unexpected. Example:
  - Instead of the section content, it might return an apology or question if it didn't understand the prompt.
  - The agent can detect if output is empty or doesn't address the prompt. If so, perhaps it will retry once with a more direct prompt.
  - Or in evaluation, if `quality` remains low after iter attempts, we either accept it or mark it. For now, maybe just accept whatever we have (but log a warning).
- **Combining Output**: There could be minor issues like if sections are supposed to be in a certain order or separated by headings. The `assemble_output` should ensure proper ordering as per the original script order, not jumbled. It likely will follow the order of `self.sections` list as extracted (which we will maintain in the order they appeared in the script).
- **Timeouts**: If a certain step is taking too long (maybe waiting on an LLM response), there's not much at agent level except to rely on the external call's timeout. We can set timeouts on `call_LLM` (OpenAI allows setting a timeout param or we handle via async).
- **Memory Management**: The agent should not hold onto extremely large strings unnecessarily. If an output is huge and causing performance issues, that's a broader system matter, not exactly error. But if we got an output so large it can't be handled (like larger than context or DB limit), we might truncate it for logging. For returning to user, maybe we return as is (or stream if supported later).
- **Thread Safety**: Each request gets its own OmegaAgent, so there shouldn't be cross-talk. But if we had any class-level or global variables (we try not to), protect them with locks or avoid altogether. For example, if using a single OpenAI client globally, it's usually fine as calls are thread-safe, but if not, we might use per-request client or a lock around calls.

## Future Improvements for the Agent
The current (initial) agent is a basic implementation to make Omega-AGI prompts work. There are many ways we plan to improve it:

- **Full Omega Parsing**: Implement a parser that can produce an AST of the Omega script. This would allow rigorous validation and also advanced manipulations (like easily retrieving dependency info, or reordering operations if needed). A parsing library or a custom grammar (maybe using Python's `re` or `lark` library) could be employed. With a proper AST, the agent execution can become more like a real interpreter of a new language.
- **Multi-step Planning**: Right now, we assume the Omega script is the plan. In the future, the agent itself could generate sub-plans. For instance, if given a high-level task in natural language, the agent (via the LLM) could generate an Omega script to solve it (basically writing its own Omega prompt) and then execute it. This would truly be AGI-like (AI generating its own Omega-AGI instructions). This is ambitious and outside the immediate scope, but Omega-AGI is designed to facilitate AI planning, so it's a logical extension.
- **Parallel Section Generation**: If the memory graph indicates some sections have no dependencies on each other, we could generate them in parallel (using `asyncio.gather` to call the LLM for each concurrently). This can speed up large tasks. We have to be mindful of rate limits, though.
- **Tool Use Integration**: Omega-AGI as a language could be extended to allow calls to external tools (like a symbol or command that triggers a web search or database query). In the future, the agent might integrate with tools. For example, if Omega had a command like `WEB_SEARCH("query")`, the agent would detect that and perform an actual web search (not via LLM) and then feed results into subsequent LLM calls. This requires a framework for tool plugins. The architecture is open to that: we could have a mapping of Omega commands to Python functions in the agent.
- **Better Reflection**: Implementing the reflection operators properly. For instance, if `∇` is in the preamble, maybe after generating initial content, the agent should call the LLM with a prompt like "Reflect on the above output: identify any errors or improvements." And then use that reflection to adjust the output or prompt. `∇²` might involve an even deeper introspection or second-order reflection.
- **Memory and Context Handling**: Omega has the concept of memory (via `MEM[...]`). In the future, the agent could maintain a state dictionary for memory values and update it as the prompt executes. For example, if a section or an LLM call yields something that should be stored (like a conclusion that could be referenced later), the agent can put it in memory. Then `MEM[X]` in a condition would refer to it. This turns the execution into more of a step-by-step program with state, rather than one-shot generation. It would allow loops like `FOR ...` to actually iterate with updated state each time.
- **Chain-of-Thought Transparency**: Optionally, the agent could return not just the final result but also an explanation of what it did (like a trace of which sections were generated in what order, what reflections were made, etc.). This could be used in a debugging endpoint or a verbose mode. It aligns with the idea of "explainable AI". Possibly, the agent might generate a brief log of decisions.
- **Adaptive Model Selection**: The agent could choose different models for different tasks if multiple are available. For example, use a cheaper model for reflection or outline, but the best model for final content. Or use a very large context model if the prompt is huge, otherwise a smaller context model to save cost.
- **Error Recovery and Learning**: If the agent repeatedly encounters issues with certain types of prompts, we could incorporate a learning mechanism. For example, using the logs, we identify patterns where output was bad and maybe adjust the system prompt or prompt templates to fix it. The agent could even do this dynamically: if first attempt yields an off-base answer, modify the prompt (maybe add more explicit instruction or reduce temperature) and try again. Currently, we might rely on `iter` loops in Omega for that, but the agent could have its own heuristics.
- **Testing and Formal Verification**: Eventually, treat Omega-AGI scripts like code and have a test suite. Small Omega scripts could be run against expected outputs or at least structure. The agent could have a "dry run" mode to simulate execution (like not calling the LLM but going through motions), useful for validating complex Omega-AGI sequences.
- **Support for Dialogs**: If we wanted a multi-turn conversation in Omega style, the agent might handle that (though Omega seems more geared to single complex tasks than a back-and-forth chat).

The **modular structure** of the agent helps in implementing these improvements. For instance, the LLM interface is separate, so adding parallel calls or switching models is localized. The parsing/validation is one module, so replacing a regex approach with a formal parser won't affect the rest drastically.

In summary, the agent currently coordinates the breakdown of an Omega prompt and ensures each part is fed to the LLM correctly, then reassembles the results. It acts as the "brain" that enforces the Omega structure on a potentially unaware LLM (unless the LLM has been prompted to know Omega format). Over time, we aim to make the agent smarter, more autonomous in improving outputs, and capable of handling the full breadth of the Omega-AGI language (including any new features introduced beyond v2.0).

The design philosophy is to keep the agent logic as deterministic and transparent as possible, in line with Omega-AGI’s goals. We want to minimize random behavior (except where creativity is desired) and maximize reliability. Every improvement will be measured against whether it increases the agent's reliability and the quality of results for Omega prompts.

---

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

Below is the updated **Setup.md** file. This version is more comprehensive and includes details on the complete project structure, including separate files for routes, agents, and other modules that require content. Each file is described with its purpose and includes a placeholder section where developers can add or update content.

---

# Setup.md

This document provides instructions for setting up the Omega-AGI FastAPI project on a development machine or server. It covers the project structure, environment configuration, dependency installation, and steps to run the application. Following these steps will ensure you have all the required components in place to start the system.

## Project Structure

The project files are organized as follows (directory names and files):

```
OmegaAGI/
├── app/
│   ├── main.py               # FastAPI application instance and route definitions.
│   ├── agent.py              # Implementation of the OmegaAgent class (agent logic).
│   ├── model_provider.py     # Functions/classes to integrate with LLM APIs (OpenAI, etc.).
│   ├── db.py                 # Database (Supabase) client setup and logging functions.
│   ├── models.py             # Pydantic data models for requests and responses (OmegaRequest, OmegaResponse, etc.).
│   ├── routes/               # Directory containing separate route files for modularity.
│   │   ├── omega_routes.py       # Routes for Omega execution, validation, correction, reflection, improvement.
│   │   ├── human_to_omega_routes.py  # Routes for human-to-Omega conversion endpoints.
│   │   ├── omega_to_human_routes.py  # Routes for converting Omega to human language.
│   │   ├── reasoning_routes.py       # Routes for reasoning endpoint.
│   │   ├── agent_routes.py           # Routes for agent processing.
│   │   └── logs_routes.py            # (Optional) Route for retrieving logs.
│   └── config.py             # Configuration loader (uses dspy to load .env).
├── plan/                    # Folder for implementation plans and related documents.
│   └── Implementation_Plan.md  # High-level implementation plan (also in docs if desired).
├── tests/                   # Test files for different components.
│   └── (placeholder for test files)
├── requirements.txt         # Python dependencies list.
├── setup.sh                 # Convenience script to set up the environment.
└── .env.example             # Example environment configuration file (to be copied to .env).
```

### Description of Key Components

- **app/main.py:**  
  Constructs the FastAPI application instance, mounts route modules (from `app/routes/`), and ties together agents, models, and the database.

- **app/agent.py:**  
  Contains the `OmegaAgent` class, which handles parsing the Omega prompt, validating its structure, and orchestrating calls to LLMs for processing, reflection, and correction.

- **app/model_provider.py:**  
  Abstracts the LLM calls (e.g., OpenAI, Google Gemini) into functions such as:
  - `call_translator_llm_human_to_omega()`
  - `call_translator_llm_omega_to_human()`
  - `call_translator_llm_correction()`
  - `call_reflection_llm()`
  
  Each function includes detailed instructions and pseudocode.

- **app/db.py:**  
  Sets up the Supabase client and defines functions (e.g., `log_interaction()`) for logging requests and responses.

- **app/models.py:**  
  Contains all the Pydantic models for request and response validation. Models include OmegaRequest, OmegaResponse, HumanToOmegaRequest, OmegaValidationRequest, etc.

- **app/routes/:**  
  This folder holds separate route files to keep code modular and best practice size:
  - **omega_routes.py:** Handles endpoints for `/api/v1/omega` (execution, validation, correction, reflection, and improvement).
  - **human_to_omega_routes.py:** Contains endpoints for human-to-Omega conversion (LLM-based and parser-based).
  - **omega_to_human_routes.py:** Contains the endpoint for translating Omega to human language.
  - **reasoning_routes.py:** Contains the reasoning endpoint.
  - **agent_routes.py:** Contains the endpoint to process Omega through specific agents.
  - **logs_routes.py:** (Optional) Contains the logs retrieval endpoint for admin usage.

- **app/config.py:**  
  Loads configuration settings using dspy from a `.env` file. This centralizes API keys and configuration values.

- **plan/:**  
  Contains planning documents. For example, the Implementation_Plan.md outlines the full development plan, milestones, and tasks.

- **tests/:**  
  Placeholder folder for unit and integration tests.

- **requirements.txt:**  
  Lists all Python package dependencies (e.g., fastapi, uvicorn, openai, supabase-python, python-dotenv).

- **setup.sh:**  
  A shell script to automate environment setup (detailed below).

- **.env.example:**  
  A template file for environment configuration. Copy this to `.env` and update with actual values.

---

## Environment Configuration

The application requires configuration values provided via environment variables. These include:

- `OPENAI_API_KEY` – Your OpenAI API key for LLM access.
- `SUPABASE_URL` – The URL of your Supabase project.
- `SUPABASE_SERVICE_KEY` – The service role API key for your Supabase project.
- `DEFAULT_MODEL` – (optional) Default model identifier (e.g., "openai-gpt4").
- `MODEL_PROVIDER` – (optional) The model provider name (e.g., "openai" or "google").
- `ADMIN_TOKEN` – (optional) Token for admin endpoints (e.g., logs retrieval).
- `MAX_CORRECTION_ATTEMPTS` – (optional) Maximum allowed correction iterations (e.g., 3).

Create a `.env` file at the project root (copy from `.env.example`) with these variables. For example:

```bash
OPENAI_API_KEY=your-openai-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-supabase-service-key
DEFAULT_MODEL=openai-gpt4
MODEL_PROVIDER=openai
ADMIN_TOKEN=change-this-for-production
MAX_CORRECTION_ATTEMPTS=3
```

Do not commit your actual `.env` file to version control.

---

## Dependency Installation

1. **Create Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows, use: venv\Scripts\activate
   ```

2. **Install Dependencies:**

   With `requirements.txt` in place, run:

   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, manually install:

   ```bash
   pip install fastapi uvicorn[standard] openai supabase-python python-dotenv pydantic
   ```

   Additional packages (e.g., pytest, flake8, black) may be installed as needed.

---

## Supabase Setup

- Create a Supabase project via [Supabase](https://supabase.com/).
- Use the SQL editor to create the `query_logs` table with columns:
  - `id` (bigserial, primary key)
  - `prompt` (text)
  - `response` (text)
  - `model` (varchar(50))
  - `created_at` (timestamp, default now())
- Retrieve the Supabase URL and service key, and set them in your `.env`.

---

## Running the Application

1. **Activate the Virtual Environment:**

   ```bash
   source venv/bin/activate
   ```

2. **Start the Server:**

   ```bash
   uvicorn app.main:app --reload
   ```

3. **Test the Application:**

   - Visit `http://localhost:8000/health` to confirm the server is running.
   - Go to `http://localhost:8000/docs` for the interactive API documentation.
   - Test endpoints using curl or via the Swagger UI.

---

## Placeholders and Modular Files

Each file that requires content (such as route files and agent files) includes placeholders where you can expand functionality:

- **app/main.py:**  
  Should import and mount routes from the `app/routes/` folder.

- **app/routes/omega_routes.py:**  
  Should contain routes for `/api/v1/omega` and related endpoints (validation, correction, reflection, improvement). Place a placeholder comment like `# TODO: Implement Omega execution logic`.

- **app/routes/human_to_omega_routes.py:**  
  Contains endpoints for human-to-omega conversion. Include placeholders.

- **app/routes/omega_to_human_routes.py:**  
  Contains the endpoint for translating Omega to human language.

- **app/routes/reasoning_routes.py:**  
  Contains the reasoning endpoint.

- **app/routes/agent_routes.py:**  
  Contains endpoints to process Omega via specific agents.

- **app/routes/logs_routes.py:**  
  (Optional) Contains the logs retrieval endpoint.

- **app/agent.py, app/model_provider.py, app/db.py, app/models.py:**  
  Each file includes basic implementations with comments and placeholders where further logic can be added.

---

## Project Maintenance

- **Updating Dependencies:**  
  Modify `requirements.txt` and reinstall as needed.

- **Running Tests:**  
  Use `pytest` for test cases placed under the `tests/` directory.

- **Common Issues:**  
  - Ensure you run uvicorn from the project root so that the `app` package is found.
  - Update the `.env` file with actual credentials.
  - If the server doesn't start, check for syntax or import errors in the terminal.

By following this setup guide, you should have a fully working instance of the Omega-AGI system. The structure supports modular development, making it easier to manage separate endpoints and agent logic as the project evolves.

Happy coding!

