def _map_reputation_call(self, event: Dict[str, Any], data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Mapeia para a função real da tua palete reputation.rs"""
        return {
            'call_module': 'Reputation',
            'call_function': 'add_reputation', # Nome exato no Rust
            'call_params': {
                'target': agent_id,
                'amount': data.get('score', 0)
            }
        }

    def _map_project_call(self, event: Dict[str, Any], data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Mapeia para a função real da tua palete pallet_projects/lib.rs"""
        return {
            'call_module': 'Projects', # Nome definido no construct_runtime!
            'call_function': 'create_project', # Nome exato no Rust
            'call_params': {
                'content': data.get('hash', '0x00'), # Hash da prova/foto
                'value': data.get('value', 1000)
            }
        }
