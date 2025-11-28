from fastapi import FastAPI,Request,Header,HTTPException,Depends
import uvicorn
import hmac
import hashlib
import json
import time
import requests
from pydantic import BaseModel
from typing import List,Optional
from secrets import compare_digest




secrets_path = "data/secrets.json"


def try_excpet_decorator(func):
    def main_func(*args,**kwargs):
        try:
            func()
        except Exception as e:
            raise Exception(e)  
    return main_func      

@try_excpet_decorator
def get_api_key() -> str:
    try:
        with open(secrets_path,"r") as file:
            data = json.load(file)
        return data["api"]    
    except Exception as e:
        raise KeyError("No such key")
@try_excpet_decorator    
def get_giga_chat_token() -> str:
    try:
        with open(secrets_path,"r") as file:
            data = json.load(file)
        return data["gigachat"]    
    except Exception as e:
        raise KeyError("No suck key")    
@try_excpet_decorator
def get_signature_key() -> str:
    try:
        with open(secrets_path,"r") as file:
            data = json.load(file)
        return data["signature"]    
    except Exception as e:
        raise KeyError("No such key")
    


    
@try_excpet_decorator
def request_to_giga_chat(request:str) -> Optional[str]:
    API_URL = "https://api.gigachat.ai/v1/completions"  # URL конечной точки API
    API_KEY = get_giga_chat_token()  # токен доступа к API

    payload = {
        "model": "GigaChat",  # Указываем используемую модель
        "messages": [
            {"role": "system", "content": "Ты эксперт по программированию."},
            {"role": "user", "content": request}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print(result["choices"][0]["message"]["content"])
        try:
            return str(result["choices"][0]["message"]["content"])
        except Exception as e:
            raise TypeError(f"Error : {e}")
    else:
       return ""
    
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
        response = request_to_giga_chat(req.request)
        if response != "":
            return response
        raise HTTPException(status_code = 400,detail = "Error while asking gigachat")
    except Exception as e:
        raise HTTPException(status_code = 400,detail = f"Error : {e}")
    
