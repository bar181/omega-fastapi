import openai
from app.config import settings

# Initialize OpenAI with API key from configuration.
openai.api_key = settings.OPENAI_API_KEY

async def call_translator_llm_human_to_omega(prompt: str) -> str:
    # Translate natural language into a valid Omega script.
    messages = [
        {"role": "system", "content": "You are an expert in Omega-AGI symbolic language. Convert natural language instructions into a valid Omega prompt following best practices."},
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0.2)
    return response['choices'][0]['message']['content']

async def call_translator_llm_omega_to_human(prompt: str) -> str:
    # Translate Omega script into plain English.
    messages = [
        {"role": "system", "content": "You are an expert in interpreting Omega-AGI scripts. Translate the following Omega script into plain, natural language."},
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0.0)
    return response['choices'][0]['message']['content']

async def call_translator_llm_correction(prompt: str) -> str:
    # Correct or improve an Omega script based on the provided instructions.
    messages = [
        {"role": "system", "content": "You are an expert in Omega-AGI. Correct and improve the following Omega script based on the provided instructions."},
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0.1)
    return response['choices'][0]['message']['content']

async def call_reflection_llm(prompt: str) -> str:
    # Evaluate the Omega script: score structure (1-100) and provide improvement recommendations.
    messages = [
        {"role": "system", "content": "You are an expert in Omega-AGI. Evaluate the following Omega script for structure, assign a quality score from 1 to 100, and provide detailed recommendations for improvement."},
        {"role": "user", "content": prompt}
    ]
    response = await openai.ChatCompletion.acreate(model="gpt-4", messages=messages, temperature=0.1)
    return response['choices'][0]['message']['content']
