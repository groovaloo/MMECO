# Rede P2P Offline - Conexão Mac ↔ VPS

## Visão Geral

Este documento fornece instruções detalhadas para estabelecer uma conexão P2P offline entre o Mac (nó local) e a VPS (nó remoto) usando apenas IPs locais/fixos, sem dependência de internet.

## Pré-requisitos

### Hardware Necessário
- **MacBook Pro 2018:** Nó local da comunidade
- **VPS (Virtual Private Server):** Nó remoto/servidor
- **Roteador com Port Forwarding:** Para expor a VPS
- **Conexão de Rede Estável:** Entre Mac e roteador

### Configurações Básicas
- **IP Fixo na VPS:** Configurado no provedor de hospedagem
- **Porta 9944 Aberta:** Para comunicação WebSocket
- **Porta 30333 Aberta:** Para comunicação P2P
- **Firewall Configurado:** Permissões para as portas especificadas

## Configuração da VPS

### 1. Obtenção do IP Fixo
```bash
# Verificar IP atual da VPS
curl ifconfig.me

# Verificar interfaces de rede
ip addr show

# Configurar IP fixo permanente (exemplo para Ubuntu)
sudo nano /etc/netplan/01-netcfg.yaml
```

### 2. Configuração de Rede Permanente
```yaml
# Arquivo: /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24  # IP fixo da VPS
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

### 3. Aplicar Configuração
```bash
sudo netplan apply
sudo systemctl restart networking
```

### 4. Configurar Firewall na VPS
```bash
# Instalar UFW (se necessário)
sudo apt install ufw

# Configurar regras de firewall
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 9944/tcp   # WebSocket
sudo ufw allow 30333/tcp  # P2P
sudo ufw enable

# Verificar status
sudo ufw status
```

## Configuração do Roteador

### 1. Port Forwarding
Acesse o painel do roteador e configure:
- **Porta Externa:** 9944 → **Porta Interna:** 9944 → **IP:** 192.168.1.100
- **Porta Externa:** 30333 → **Porta Interna:** 30333 → **IP:** 192.168.1.100

### 2. DHCP Reservation
Reserve IPs fixos para dispositivos:
- **Mac:** 192.168.1.50
- **VPS (via roteador):** 192.168.1.100

## Configuração do Mac

### 1. Verificar Conexão de Rede
```bash
# Verificar IP local
ifconfig | grep "inet " | grep -v 127.0.0.1

# Testar conexão com VPS
ping 192.168.1.100

# Testar portas
telnet 192.168.1.100 9944
telnet 192.168.1.100 30333
```

### 2. Configurar IP Fixo no Mac
```bash
# Configurar IP fixo via terminal
sudo ifconfig en0 192.168.1.50 netmask 255.255.255.0

# Configurar gateway padrão
sudo route add default 192.168.1.1
```

## Configuração do Nó Substrate

### 1. Parâmetros de Inicialização

#### Para a VPS (Nó Remoto)
```bash
# Iniciar nó em modo validador
./target/release/node \
  --base-path /tmp/node \
  --chain local \
  --port 30333 \
  --ws-port 9944 \
  --rpc-port 9933 \
  --validator \
  --name "VPS-Validator" \
  --rpc-cors all \
  --rpc-methods Unsafe \
  --listen-addr /ip4/0.0.0.0/tcp/30333 \
  --ws-external \
  --rpc-external
```

#### Para o Mac (Nó Local)
```bash
# Iniciar nó em modo full node
./target/release/node \
  --base-path /tmp/node \
  --chain local \
  --port 30334 \
  --ws-port 9945 \
  --rpc-port 9934 \
  --name "Mac-FullNode" \
  --rpc-cors all \
  --rpc-methods Unsafe \
  --bootnodes /ip4/192.168.1.100/tcp/30333/p2p/<VPS_PEER_ID> \
  --ws-external \
  --rpc-external
```

### 2. Descoberta de Peer ID
```bash
# Na VPS, obter o Peer ID
./target/release/node key inspect-node-key --file /tmp/node/network/secret

# Ou verificar logs na inicialização
./target/release/node --chain local --validator --name "VPS-Validator" 2>&1 | grep "Local node identity"
```

## Testes de Conexão

### 1. Verificar Conexão P2P
```bash
# No Mac, verificar peers conectados
./target/release/node --chain local --name "Mac-FullNode" --bootnodes /ip4/192.168.1.100/tcp/30333/p2p/<VPS_PEER_ID>

# Verificar logs de conexão
tail -f /tmp/node/logs/*.log | grep -i "peer\|connected\|discovered"
```

### 2. Testar Comunicação WebSocket
```bash
# Testar WebSocket da VPS
wscat -c ws://192.168.1.100:9944

# Testar RPC
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' http://192.168.1.100:9933
```

### 3. Verificar Sincronização
```bash
# Verificar saúde do nó
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' http://192.168.1.100:9933

# Verificar peers
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_peers", "params":[]}' http://192.168.1.100:9933
```

## Troubleshooting

### 1. Problemas Comuns

#### Conexão Não Estabelecida
```bash
# Verificar firewall na VPS
sudo ufw status verbose

# Verificar portas abertas
netstat -tuln | grep -E "(9944|30333)"

# Testar conectividade
telnet 192.168.1.100 30333
```

#### Portas Bloqueadas
```bash
# Verificar regras de firewall no Mac
sudo pfctl -sr | grep -E "(9944|30333)"

# Abrir portas no Mac (se necessário)
sudo pfctl -f /etc/pf.conf
```

#### DNS/Resolução de IP
```bash
# Verificar resolução de nomes
nslookup 192.168.1.100

# Testar ping
ping -c 4 192.168.1.100
```

### 2. Soluções Rápidas

#### Reiniciar Serviços de Rede
```bash
# Na VPS
sudo systemctl restart networking
sudo systemctl restart ufw

# No Mac
sudo ifconfig en0 down
sudo ifconfig en0 up
```

#### Verificar Logs de Erro
```bash
# Logs do nó Substrate
tail -f /tmp/node/logs/*.log

# Logs do sistema
journalctl -f | grep -i "network\|firewall\|port"
```

## Segurança

### 1. Configurações de Segurança
- **SSH Key Authentication:** Use chaves SSH em vez de senhas
- **Firewall Restrictivo:** Apenas portas essenciais abertas
- **Monitoramento:** Logs de acesso e tentativas de conexão

### 2. Boas Práticas
- **Atualizações Regulares:** Mantenha o sistema e pacotes atualizados
- **Backup de Configurações:** Salve configurações de rede e firewall
- **Monitoramento de Conexões:** Verifique conexões ativas periodicamente

## Manutenção

### 1. Verificações Periódicas
```bash
# Verificar status da rede
ping -c 4 192.168.1.100

# Verificar sincronização do blockchain
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "chain_getHeader", "params":[]}' http://192.168.1.100:9933

# Verificar saúde dos nós
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "system_health", "params":[]}' http://192.168.1.100:9933
```

### 2. Atualizações de Configuração
- **Atualizar Peer IDs:** Quando os nós forem reiniciados
- **Verificar Portas:** Após atualizações de sistema
- **Testar Conexões:** Após mudanças na rede

## Documentação de Suporte

### Comandos Úteis
```bash
# Verificar status da blockchain
./target/release/node --chain local --name "Mac-FullNode" --bootnodes /ip4/192.168.1.100/tcp/30333/p2p/<VPS_PEER_ID> --rpc-methods Unsafe

# Verificar logs em tempo real
tail -f /tmp/node/logs/*.log

# Testar RPC endpoints
curl -H "Content-Type: application/json" -d '{"id":1, "jsonrpc":"2.0", "method": "rpc_methods", "params":[]}' http://192.168.1.100:9933
```

### Arquivos de Configuração
- **VPS Network:** `/etc/netplan/01-netcfg.yaml`
- **VPS Firewall:** `/etc/ufw/`
- **Mac Network:** Configurações de Rede (System Preferences)
- **Substrate Config:** Parâmetros de inicialização dos nós

Esta configuração garante uma conexão P2P offline estável e segura entre o Mac e a VPS, permitindo o funcionamento contínuo da rede blockchain sem dependência de internet.