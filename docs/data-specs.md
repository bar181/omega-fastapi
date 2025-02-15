
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

