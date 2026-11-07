from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import agent

app = FastAPI(title="Gov Scheme API")

class UserRequest(BaseModel):
    profile: str

@app.post("/api/schemes")
async def get_schemes(req: UserRequest):
    if not req.profile:
        raise HTTPException(status_code=400, detail="Profile is required")
    
    try:
        results = agent.find_matches(req.profile)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))