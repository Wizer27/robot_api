from fastapi import FastAPI,Request,Header,HTTPException,Depends
import uvicorn
import hmac
import hashlib
import json
import time
import requests
from pydantic import BaseModel
from typing import List,Optional

secrets_path = "data/secrets.json"

def get_api_key() -> str:
    try:
        with open(secrets_path,"r") as file:
            data = json.load(file)
        return data["api"]    
    except Exception as e:
        raise KeyError("No such key")

def get_signature_key() -> str:
    try:
        with open(secrets_path,"r") as file:
            data = json.load(file)
        return data["signature"]    
    except Exception as e:
        raise KeyError("No such key")
    
app = FastAPI()
@app.get("/")
async def main():
    return "MIRA-API"
#-----SECURITY-----
async def safe_get(req:Request):
    api = req.headers.get("X-API-KEY")
    if not api or not hmac.compare_digest(api,get_api_key()):
        raise HTTPException(status_code = 401,detail = "Invalid api key")
    

def verify_signature(data:dict,signature:str,timestamp:str) -> bool:
    if int(time.time) - int(timestamp) > 300:
        return False
    KEY = get_signature_key()
    data_to_verify = data.copy()
    data_to_verify.pop("signature",None)

    data_str = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature,signature)
#-----SECURITY-----

class Answer(BaseModel):
    request:str

@app.post("/answer")
async def answer_request(req:Answer,x_signature:str = Header(...),x_timestamp:str = Header()):
    if not verify_signature(req.model_dump(),x_signature,x_timestamp):
        raise HTTPException(status_code = 401,detail = "Invalid signature")
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code = 400,detail = f"Error : {e}")
    
