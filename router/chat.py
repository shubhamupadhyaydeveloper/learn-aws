import os
import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from litellm import completion
from dotenv import load_dotenv
import uuid
import json
from datetime import datetime
from pathlib import Path

load_dotenv(override=True)

MEMORY_DIR = os.getenv("MEMORY_DIR", "./memory")
S3_BUCKET = os.getenv("S3_BUCKET","")
USE_S3 = os.getenv("USE_S3", False)

if USE_S3:
    s3_client = boto3.client('s3')
    
def get_memory_path(session_id:str):
    return f"{session_id}.json"

def load_personality() -> str:
    try:
        with open("me.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def load_conversation(session_id: str):
    if USE_S3:
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET, Key=get_memory_path(session_id))
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return []
            raise
    else:
        path = MEMORY_DIR / f"{session_id}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
def save_conversation(session_id: str, messages: list):
    if USE_S3:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=get_memory_path(session_id),
            Body=json.dumps(messages).encode("utf-8"),
            ContentType="application/json",
        )
    else:
        path = MEMORY_DIR / f"{session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f,indent=2, ensure_ascii=False)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


router = APIRouter(prefix="/chat", tags=["Chat"])

DEFAULT_PROMPT = (
    "You are Shubham Upadhyay, a Web & Mobile Developer and CS student at IIT Patna. "
    "You are chatting on your personal website shubhamupadhyay.xyz with visitors who want to "
    "learn about you. Speak in the first person (I/me/my) as Shubham. Answer questions using "
    "only the background context provided below. Keep your tone friendly, concise, and "
    "professional. If a question cannot be answered from the context, say so honestly instead "
    "of making up details.\n\n"
    "## Background context about Shubham\n"
)
MODEL = "gemini/gemini-2.5-flash-lite"


def chat_completion(
    message: str,
    session_id: str
) -> str:
    personality = load_personality()
    conversation = load_conversation(session_id)
    messages = [
        {
            "role": "system",
            "content": DEFAULT_PROMPT + personality,
        },
        *conversation,
        {
            "role": "user",
            "content": message,
        },
    ]
    

    response = completion(
        model=MODEL,
        messages=messages,
    )
    
    model_response = response.choices[0].message.content
    
    conversation.append({"role": "user", "content": message})
    conversation.append({"role": "assistant", "content": model_response})
    save_conversation(session_id, conversation)
    
    
    return response.choices[0].message.content


@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        session_id = req.session_id or str(uuid.uuid4())
        reply = chat_completion(req.message,session_id)
        return ChatResponse(response=reply, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Retrieve conversation history"""
    try:
        conversation = load_conversation(session_id)
        return {"session_id": session_id, "messages": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
