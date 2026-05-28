from fastapi import APIRouter
from pydantic import BaseModel
from ..llm.guardrails import is_relevant
from ..llm.agent import get_agent
router = APIRouter()
class ChatReq(BaseModel):
    message: str
    session_id: str = "default"
class ChatRes(BaseModel):
    response: str
@router.post("/", response_model=ChatRes)
async def chat(req: ChatReq):
    if not is_relevant(req.message):
        return ChatRes(response="I only answer inventory-related questions. Please ask about stock, reorders, forecasts, or suppliers.")
    agent = get_agent(req.session_id)
    try:
        out = agent.invoke({"input": req.message})
        return ChatRes(response=out["output"])
    except Exception as e:
        return ChatRes(response=f"Error: {str(e)}")
