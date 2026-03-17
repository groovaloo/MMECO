import ollama
from substrateinterface import SubstrateInterface, Keypair

# 1. Configuração de Ligação à Blockchain
# O URL deve ser o do teu nó (127.0.0.1 se for na mesma máquina)
try:
    substrate = SubstrateInterface(
        url="ws://127.0.0.1:9944",
        ss58_format=42,
        type_registry_preset='substrate-node-template'
    )
    print("✅ Ligado à Blockchain Moral Money")
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível ligar à blockchain (o nó está a correr?): {e}")
    substrate = None

def analisar_contributo_ia(nome, tipo, detalhe, valor_estimado):
    """Usa o Llama3 para decidir o mérito ético."""
    prompt = f"""
    És o Auditor de Ética da comunidade Moral Money.
    Analisa o seguinte contributo e explica por que razão este membro deve ter mérito na rede:
    
    Membro: {nome}
    Tipo de Contributo: {tipo}
    Detalhe: {detalhe}
    Valor Estimado: {valor_estimado}
    
    Regra de Ouro: O benefício real para a sobrevivência coletiva é o que conta. 
    Infraestrutura (estufas/irrigação) tem o mesmo mérito que trabalho físico, 
    pois ambos garantem a vida da comunidade.
    
    Responde de forma concisa e termina com uma RECOMENDAÇÃO DE PONTOS (0-100).
    """
    
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Erro ao ligar ao Ollama: {e}"

def processar_e_registar(nome, tipo, detalhe, valor, account_id):
    """Analisa e prepara o registo na blockchain."""
    print(f"\n--- 🧐 AUDITORIA EM CURSO: {nome} ---")
    
    # Passo 1: IA decide
    parecer_etico = analisar_contributo_ia(nome, tipo, detalhe, valor)
    print(f"Parecer da IA:\n{parecer_etico}")
    
    # Passo 2: Enviar para a Blockchain (quando o nó estiver ativo)
    if substrate:
        print(f"\n--- ⛓️ A enviar parecer para a Palete Reputation ---")
        # Aqui, no futuro, faremos: 
        # substrate.compose_call("Reputation", "add_reputation", {"target": account_id, "amount": 50})
        print("Status: Aguardando compilação do nó para ativar submissão automática.")
    else:
        print("\n⚠️ Nota: Parecer gerado, mas não gravado na chain (sem ligação).")

# --- TESTE DE CAMPO ---
# Simulação: Um investidor que traz estufas
processar_e_registar(
    nome="Investidor Sénior (60 anos)", 
    tipo="Capital/Infraestrutura", 
    detalhe="Sistema de irrigação inteligente e estufas industriais", 
    valor="4.000.000€",
    account_id="5GrwvaEFW6th2ZqadWVP7mZ8A465MtK1ix21yv9GL2BTqvT" # Endereço (Ex: Alice)
)
