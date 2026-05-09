import requests
import random
import time

URL = "https://monitoramento-de-consumo.onrender.com/api/leituras"

while True:

    dados = {
        "token": "abc123iot",
        "consumo": round(random.uniform(10, 50), 2),
        "temperatura": round(random.uniform(20, 35), 2)
    }

    resposta = requests.post(URL, json=dados)

    print("Status:", resposta.status_code)
    print("Resposta:", resposta.text)
    print("Dados enviados:", dados)

    print("-" * 50)

    time.sleep(5)