
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
