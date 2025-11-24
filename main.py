from fastapi import FastAPI,Request,Header,HTTPException,Depends
import uvicorn
import hmac
import hashlib
import json
import time
import requests


app = FastAPI()
@app.get("/")
async def main():
    return "MIRA-API"