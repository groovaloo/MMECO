import json
from substrateinterface import SubstrateInterface, Keypair

class AuditorMoralMoney:
    def __init__(self):
        # Ligação ao teu Nó Rust (Porta padrão 9944)
        try:
            self.substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
            print("✅ Auditor Ligado ao Nó RPC")
        except Exception as e:
            print(f"⚠️ Nó offline: {e}")
            self.substrate = None

    def analisar_integridade(self, projeto_id):
        """Lê o estado real da Palete Projects no Rust"""
        if not self.substrate:
            return "Erro: Sem ligação à blockchain."

        print(f"🔍 Auditoria ao Projeto #{projeto_id} iniciada...")

        # 1. Consultar a Palete de Projetos (Storage: Projects)
        # O Rust guarda isto como um Map de ID -> Project
        projeto_data = self.substrate.query(
            module="Projects",
            storage_function="Projects",
            params=[projeto_id]
        )

        if not projeto_data:
            print(f"❌ Projeto #{projeto_id} não existe na blockchain.")
            return

        # Simulação de análise de IA (Visão Computacional / Metadados)
        # Aqui o Auditor verificaria se a 'proof' (hash da foto) é válida
        projeto = projeto_data.value
        print(f"📋 Dados do Projeto: {projeto}")

        # Lógica de suspeita: Se o valor pedido for absurdo ou a prova for nula
        suspeita = False
        if projeto['balance'] > 1000000: # Exemplo: Alerta para valores muito altos
            suspeita = True

        if suspeita:
            self.abrir_disputa(projeto_id)
        else:
            print(f"✅ Integridade confirmada para o Projeto #{projeto_id}.")

    def abrir_disputa(self, projeto_id):
        """Envia um comando 'Sudo' ou 'Governance' para bloquear o projeto"""
        print(f"⚖️ FRAUDE DETETADA! A abrir disputa para o Projeto #{projeto_id}...")
        
        # No Substrate 2025, o Auditor enviaria uma transação (Extrinsic)
        # Exemplo de chamada para uma função de disputa na palete Governance
        if self.substrate:
            # Aqui usarias a chave do Auditor para assinar
            keypair = Keypair.create_from_uri('//Alice') # Simulação com Alice
            
            call = self.substrate.compose_call(
                call_module='pallet_governance',
                call_function='abrir_disputa',
                call_params={'projeto_id': projeto_id}
            )
            
            # extrinsic = self.substrate.create_signed_extrinsic(call=call, keypair=keypair)
            # self.substrate.submit_extrinsic(extrinsic)
            print(f"🚀 Transação de Disputa enviada para o bloco.")

if __name__ == "__main__":
    auditor = AuditorMoralMoney()
    # Testar com o ID 1
    auditor.analisar_integridade(1)
