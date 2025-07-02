from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Conversation
from app.schemas import ChatRequest, ChatResponse, ConversationCreate, UserCreate
from app.mental_agent_graph import build_mental_graph
from app.crud import create_message, create_user

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db  
    finally:
        db.close()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter_by(conversation_id=req.conversation_id, user_id=req.user_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="대화 세션을 찾을 수 없습니다.")
    
    create_message(
        db,
        conversation_id=req.conversation_id,
        sender_type="user",
        agent_type="TBD(router)",
        content=req.user_input
    )

    g = build_mental_graph()
    runnable = g.compile()
    state = {
        "user_id": req.user_id,
        "conversation_id": req.conversation_id,
        "user_input": req.user_input,
        "phq9_suggested": False,
        "db": db,  # db session을 state에 추가!
    }
    result = runnable.invoke(state)
    return result

@app.post("/create_conversation")
def create_conversation(req: ConversationCreate, db: Session = Depends(get_db)):
    from app.models import Conversation
    from datetime import datetime
    conv = Conversation(
        user_id=req.user_id, conversation_type=req.conversation_type, started_at=datetime.now()
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"conversation_id": conv.conversation_id}

@app.post("/signup")
def signup(req: UserCreate, db: Session = Depends(get_db)):
    user = create_user(
        db,
        email=req.email,
        password=req.password,
        nickname=req.nickname,
        business_type=req.business_type
    )
    return {"user_id": user.user_id}
