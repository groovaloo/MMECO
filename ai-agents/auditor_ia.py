import json
import requests

class AuditorMoralMoney:
    def __init__(self, state_path="../blockchain-core/moral_money_state.json"):
        self.state_path = state_path
        self.blockchain_url = "http://127.0.0.1:9945"

    def analisar_integridade(self, projeto_id, dominio):
        """Lê o estado do Rust e verifica se há anomalias"""
        try:
            with open(self.state_path, 'r') as f:
                dados = json.load(f)
            
            projeto = dados['projetos'].get(str(projeto_id))
            if not projeto:
                return "Projeto não encontrado."

            # Simulação de verificação de metadados da foto
            print(f"🔍 Analisando hashes de prova do Projeto #{projeto_id}...")
            
            # Se a IA detetar algo estranho (simulado), abre disputa
            suspeita = False # Aqui entraria a lógica de visão computacional
            
            if suspeita:
                self.abrir_disputa(projeto_id, dominio)
            else:
                print(f"✅ Provas do Projeto #{projeto_id} parecem legítimas em BLD.")
                
        except Exception as e:
            print(f"❌ Erro na auditoria: {e}")

    def abrir_disputa(self, p_id, dominio):
        payload = {
            "jsonrpc": "2.0",
            "method": "moral_openDispute",
            "params": [int(p_id), dominio],
            "id": 1
        }
        response = requests.post(self.blockchain_url, json=payload)
        print("⚖️ Alerta de Fraude! Sistema de Disputa Ativado.")
        print(f"Resposta do Nó: {response.json().get('result')}")

if __name__ == "__main__":
    auditor = AuditorMoralMoney()
    auditor.analisar_integridade(1, "Agricultura")
