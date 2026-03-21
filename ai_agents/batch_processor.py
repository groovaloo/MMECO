from substrateinterface import SubstrateInterface, Keypair

# Ligação real ao teu Nó
try:
    substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
    # Chave do "Relayer" (quem paga as taxas do batch, ex: Alice)
    relayer_kp = Keypair.create_from_uri('//Alice') 
except:
    substrate = None

def send_to_blockchain(batch: Dict[str, Any]):
    """Envia o lote de eventos agrupados para o Rust em uma única transação."""
    if not substrate:
        logger.warning("⚠️ Blockchain offline. Batch simulado.")
        return True

    try:
        logger.info(f"🚀 Enviando Batch de {batch['type']} para a Chain...")
        
        calls = []
        for event in batch['events']:
            # Traduz o evento do Redis para uma chamada de Palete Rust
            if batch['type'] == "reputation":
                call = substrate.compose_call(
                    call_module='Reputation',
                    call_function='add_reputation',
                    call_params={
                        'target': event['data']['target'],
                        'amount': event['data']['amount']
                    }
                )
                calls.append(call)
        
        if not calls:
            return True

        # O SEGREDO: Agrupar todas as chamadas num único lote atómico
        batch_call = substrate.compose_call(
            call_module='Utility',
            call_function='batch',
            call_params={'calls': calls}
        )

        extrinsic = substrate.create_signed_extrinsic(call=batch_call, keypair=relayer_kp)
        receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        
        logger.info(f"✅ Batch incluído no bloco! Hash: {receipt.extrinsic_hash}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao submeter batch: {e}")
        return False
