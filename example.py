import requests
import json
import hmac
import hashlib
import time

secrets_json_path = "data/secrets.json" # путь к файлу где лежать api ключ и signature ключ
API_URL = "http://0.0.0.0:8080" # нужно будет поменять на настоящий
def get_signature_key() -> str:
    try:
        with open(secrets_json_path,"r") as file:
            data = json.load(file)
        return data["signature"]    
    except Exception as e:
        raise Exception(f"Error : {e}")

def generate_siganture(data:dict) -> str:
    KEY = get_signature_key()
    data_to_ver = data.copy()
    data_to_ver.pop("signature",None)
    data_str = json.dumps(data_to_ver, sort_keys=True, separators=(',', ':'))
    expected_signature = hmac.new(KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    return str(expected_signature)


def ask_ai(message:str):
    data = {
        "request":message
    }
    headers = {
        "X-Signature":generate_siganture(data),
        "X-Timestamp":str(int(time.time()))
    }
    resp = requests.post(f"{API_URL}/answer",json = data,headers=headers)
    print(resp.text)
print(ask_ai("привет"))