from fastapi import FastAPI
from app.routes import omega_routes, human_to_omega_routes, omega_to_human_routes, reasoning_routes, agent_routes, logs_routes
from app import config

app = FastAPI()

# Mount route modules
app.include_router(omega_routes.router, prefix="/api/v1/omega")
app.include_router(human_to_omega_routes.router, prefix="/api/v1/human-to-omega")
app.include_router(omega_to_human_routes.router, prefix="/api/v1/omega-to-human")
app.include_router(reasoning_routes.router, prefix="/api/v1/omega/reasoning")
app.include_router(agent_routes.router, prefix="/api/v1/agent")
app.include_router(logs_routes.router, prefix="/api/v1/logs")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
