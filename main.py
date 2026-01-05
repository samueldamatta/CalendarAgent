from fastapi import FastAPI
from dotenv import load_dotenv
from app.webhook.router import router

load_dotenv()

app = FastAPI()

# Include the modular router
app.include_router(router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Calendar Agent API is running (Modular)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
