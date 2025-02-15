# omega-fastapi
open source omega agi neural symbolic language translator for AI to AI optimized communications including agent coordination


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
