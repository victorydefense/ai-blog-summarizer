from fastapi import FastAPI
from src import routes

app = FastAPI()

app.include_router(routes.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Blog Summarizer API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)