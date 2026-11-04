from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def salud():
    return {"status": "ok"}