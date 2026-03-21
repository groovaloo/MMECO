#!/bin/bash
# Script para extrair e categorizar erros de compilação do cargo build
# Uso: ./parse-build-errors.sh <ficheiro_log> <diretorio_output>

LOG_FILE="${1:-/tmp/build.log}"
OUTPUT_DIR="${2:-./docs/internal/error-tracker}"

echo "🔍 A analisar erros de compilação..."

# Criar diretório temporário
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Extrair erros do log
grep -E "^error" "$LOG_FILE" > "$TEMP_DIR/errors.txt" 2>/dev/null || true

# Se não houver erros, sair
if [ ! -s "$TEMP_DIR/errors.txt" ]; then
    echo "✅ Nenhum erro encontrado na compilação!"
    exit 0
fi

# Contar erros
ERROR_COUNT=$(wc -l < "$TEMP_DIR/errors.txt")
echo "📊 Encontrados $ERROR_COUNT erros"

# Categorizar erros comuns
CATEGORIES=(
    "E0432:import"
    "E0277:MaxEncodedLen"
    "E0308:types"
    "sintaxe"
)

# Atualizar all-errors.md com novos erros
ERROR_MD="$OUTPUT_DIR/all-errors.md"
if [ -f "$ERROR_MD" ]; then
    # Adicionar timestamp
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
    
    # Criar secção para novos erros
    cat >> "$ERROR_MD" << EOF

---

## [$(date +"%Y-%m-%d")] Erros de Build Automático

### Timestamp
$TIMESTAMP

### Erros Detetados
\`\`\`
$(cat "$TEMP_DIR/errors.txt")
\`\`\`

### Status
🔴 **NOVOS** — Requerem análise manual

EOF
    echo "✅ all-errors.md atualizado!"
fi

# Verificar se é erro frequente (3+ ocorrências no histórico)
if [ -f "$OUTPUT_DIR/all-errors.md" ]; then
    for error in $(cat "$TEMP_DIR/errors.txt"); do
        OCCURRENCES=$(grep -c "$error" "$OUTPUT_DIR/all-errors.md" 2>/dev/null || echo 0)
        if [ "$OCCURRENCES" -ge 2 ]; then
            echo "⚠️  Erro frequente detetado: $error (ocorreu $((OCCURRENCES + 1)) vezes)"
        fi
    done
fi

echo "✅ Análise concluída!"
echo "📁 Verifica $OUTPUT_DIR/all-errors.md"
