import requests
import json

URL_BLOCKCHAIN = "http://127.0.0.1:9945"

def sync():
    populacao = {}
    config = [
        ("worker", 40, "Construcao"),
        ("medical", 5, "Saude"),
        ("farmer", 30, "Agricultura"),
        ("trader", 15, "Comercio"),
        ("admin", 10, "Gestao_Logistica")
    ]

    for prefix, qtd, dominio in config:
        for i in range(1, qtd + 1):
            m_id = f"{prefix}_{i:03d}"
            populacao[m_id] = {
                "reputacao_dominios": {dominio: 50.0},
                "saldo_bld": 100.0
            }

    # CORREÇÃO AQUI: Enviamos o dicionário diretamente como o primeiro e único parâmetro
    payload = {
        "jsonrpc": "2.0",
        "method": "moral_syncPopulation",
        "params": populacao, 
        "id": 1
    }

    try:
        r = requests.post(URL_BLOCKCHAIN, json=payload)
        print(f"✅ {len(populacao)} Agentes sincronizados!")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    sync()
