from fastapi import FastAPI,Request,Header,HTTPException,Depends
import uvicorn
import hmac
import hashlib
import json
import time
import requests

secrets_path = "data/secrets.json"

def get_api_key() -> str:
    try:
        with open(secrets_path,"r") as file:
            data = json.load(file)
        return data["api"]    
    except Exception as e:
        raise KeyError("No such key")


app = FastAPI()
@app.get("/")
async def main():
    return "MIRA-API"

async def safe_get(req:Request):
    api = req.headers.get("X-API-KEY")
    if not api or not hmac.compare_digest(api,get_api_key()):
        raise HTTPException(status_code = 401,detail = "Invalid api key")

