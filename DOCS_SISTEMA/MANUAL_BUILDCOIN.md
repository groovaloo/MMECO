# Manual Buildcoin - Sistema de Economia Comunitária

## Visão Geral

O Buildcoin é a moeda digital da comunidade Moral Money, projetada para recompensar contribuições reais e mensuráveis para a sobrevivência e prosperidade coletiva.

## Princípios do Buildcoin

### 1. Base Ética
- **Não é dinheiro tradicional:** O Buildcoin não pode ser comprado com capital externo
- **Recompensa por Contribuição:** Só é gerado quando projetos são validados e concluídos com sucesso
- **Equivalência Ética:** Trabalho e capital têm o mesmo valor na geração de Buildcoins

### 2. Transparência Total
- **Blockchain Substrate:** Todas as transações são registradas em blockchain público
- **Rastreabilidade:** Cada Buildcoin pode ser rastreado até sua origem de contribuição
- **Imutabilidade:** Registros não podem ser alterados ou manipulados

## Sistema de Saldos

### 1. Conta Buildcoin
Cada membro da comunidade possui:
- **AccountId:** Identificador único na blockchain
- **Saldo:** Quantidade de Buildcoins acumulados
- **Histórico:** Registro de todas as transações e origens

### 2. Consulta de Saldos
```rust
// Função pública para consulta
pub fn get_buildcoin_balance(account: T::AccountId) -> u128 {
    BuildcoinBalance::<T>::get(account)
}
```

### 3. Tipos de Saldo
- **Saldo Ativo:** Buildcoins disponíveis para uso
- **Saldo Comprometido:** Buildcoins vinculados a projetos em andamento
- **Saldo Histórico:** Registro total de Buildcoins recebidos

## Processo de Minting (Cunhagem)

### 1. Condições para Minting
O Buildcoin só é criado quando:
- **Projeto Concluído:** Atividade produtiva foi finalizada com sucesso
- **Validação por Conselho:** Grupo de 5 especialistas aprova a contribuição
- **Impacto Mensurável:** Contribuição demonstra benefício real para a comunidade

### 2. Fluxo de Minting

#### Etapa 1: Execução do Projeto
- Membro participa de projeto comunitário
- Contribuição é registrada no sistema
- Impacto é documentado e mensurado

#### Etapa 2: Validação pelo Conselho
- Projeto é submetido à validação
- Conselho de 5 especialistas analisa a contribuição
- Decisão é registrada na blockchain

#### Etapa 3: Emissão de Buildcoins
```rust
// Função de emissão (só pode ser chamada pelo admin)
pub fn issue_buildcoin(
    origin: OriginFor<T>,
    beneficiary: T::AccountId,
    amount: u128,
) -> DispatchResult {
    // Validação de admin
    let who = ensure_signed(origin)?;
    let admin = Admin::<T>::get().ok_or(Error::<T>::NotAdmin)?;
    ensure!(who == admin, Error::<T>::NotAdmin);

    // Atualização de saldo
    BuildcoinBalance::<T>::try_mutate(&beneficiary, |balance| -> Result<(), Error<T>> {
        *balance = balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;
        Ok(())
    })?;

    // Registro de evento
    Self::deposit_event(Event::BuildcoinMinted(beneficiary, amount));
    Ok(())
}
```

#### Etapa 4: Registro de Evento
- Evento `BuildcoinMinted(AccountId, u128)` é registrado
- Transação é incluída no próximo bloco
- Saldo do beneficiário é atualizado

### 3. Regras de Emissão

#### Quantidade de Buildcoins
- **Proporcional ao Impacto:** Maior impacto = mais Buildcoins
- **Limites por Domínio:** Quantidades máximas por tipo de contribuição
- **Validação por Especialistas:** Especialistas determinam valor da contribuição

#### Limites de Emissão
- **Sem Inflação Ilimitada:** Emissão controlada por validação humana
- **Qualidade sobre Quantidade:** Projetos de baixo impacto recebem menos recompensas
- **Equilíbrio Setorial:** Distribuição equilibrada entre diferentes áreas

## Tipos de Contribuição que Geram Buildcoins

### 1. Contribuição por Trabalho
- **Construção:** Edificação de infraestrutura
- **Agricultura:** Produção de alimentos
- **Manutenção:** Conservação de equipamentos e instalações

### 2. Contribuição por Capital
- **Infraestrutura:** Investimento em equipamentos e instalações
- **Tecnologia:** Aquisição de recursos tecnológicos
- **Serviços:** Contratação de serviços essenciais

### 3. Contribuição por Conhecimento
- **Educação:** Capacitação e ensino
- **Consultoria:** Orientação estratégica
- **Inovação:** Desenvolvimento de soluções criativas

## Uso dos Buildcoins

### 1. Trocas na Comunidade
- **Bens e Serviços:** Troca por produtos e serviços locais
- **Infraestrutura:** Acesso a instalações e equipamentos
- **Educação:** Cursos e capacitação

### 2. Investimento Comunitário
- **Projetos Coletivos:** Financiamento de iniciativas comunitárias
- **Desenvolvimento:** Investimento em melhorias coletivas
- **Reservas:** Acúmulo para necessidades futuras

### 3. Reconhecimento Social
- **Status:** Demonstração de contribuição à comunidade
- **Influência:** Peso nas decisões coletivas (proporcional à contribuição)
- **Respeito:** Reconhecimento social baseado em mérito real

## Segurança e Integridade

### 1. Controle de Fraude
- **Validação Dupla:** Projetos são validados por múltiplas fontes
- **Auditoria por IA:** Sistema de auditoria automatizada
- **Transparência:** Todas as transações são públicas

### 2. Prevenção de Manipulação
- **Limites de Emissão:** Controle de quantidade total em circulação
- **Validação Humana:** Decisões críticas requerem aprovação humana
- **Registro Imutável:** Histórico de transações não pode ser alterado

### 3. Sustentabilidade
- **Emissão Controlada:** Novos Buildcoins só são criados com validação
- **Valor Baseado em Realidade:** Valor ancorado em contribuições reais
- **Crescimento Orgânico:** Expansão proporcional ao desenvolvimento da comunidade

## Integração com o Sistema de Reputação

### 1. Relacionamento com Reputação
- **Reputação por Domínio:** Especialistas validam contribuições
- **Buildcoins por Impacto:** Quantidade baseada no valor da contribuição
- **Sistema Integrado:** Ambos os sistemas trabalham em conjunto

### 2. Benefícios Combinados
- **Reputação + Buildcoins:** Reconhecimento social e recompensa econômica
- **Validação Cruzada:** Sistemas se reforçam mutuamente
- **Equilíbrio:** Evita concentração de poder em poucas mãos

## Futuro do Buildcoin

### 1. Expansão
- **Integração com Outras Comunidades:** Sistema interoperável
- **Desenvolvimento de Mercado:** Plataformas de troca interna
- **Inovação Contínua:** Melhorias baseadas em feedback real

### 2. Sustentabilidade a Longo Prazo
- **Adaptação às Necessidades:** Sistema evolutivo
- **Equilíbrio Econômico:** Prevenção de desequilíbrios
- **Valorização do Mérito:** Sistema que recompensa verdadeiramente o esforço

O Buildcoin representa a materialização prática da equivalência ética, transformando contribuições reais em valor econômico justo e transparente.