import ollama

def analisar_contributo(nome, tipo, detalhe, valor_estimado):
    prompt = f"""
    És o Auditor de Ética da comunidade Moral Money.
    Analisa o seguinte contributo e explica por que razão este membro deve ter soberania total:
    
    Membro: {nome}
    Tipo de Contributo: {tipo}
    Detalhe: {detalhe}
    Valor Estimado: {valor_estimado}
    
    Regra de Ouro: O benefício real para a sobrevivência coletiva é o que conta. 
    Se um investidor de 60 anos traz infraestrutura (irrigação/estufas), ele tem o mesmo mérito 
    que um jovem que trabalha 5 anos, pois ambos viabilizam a vida da comunidade.
    """
    
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Erro ao ligar ao Ollama: {e}"

# Teste com o teu exemplo:
print("\n--- ANALISANDO CONTRIBUTO ---")
print(analisar_contributo(
    "Investidor Sénior (60 anos)", 
    "Capital/Infraestrutura", 
    "Sistema de irrigação inteligente e estufas industriais", 
    "4.000.000€"
))