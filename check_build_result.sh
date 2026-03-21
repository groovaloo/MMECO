#!/bin/bash
echo "🔍 Verificando resultado do último build..."

# Obter último run
LAST_RUN=$(gh run list --limit 1 --json databaseId,conclusion,status -q '.[0]')
RUN_ID=$(echo $LAST_RUN | jq -r '.databaseId')
STATUS=$(echo $LAST_RUN | jq -r '.status')
CONCLUSION=$(echo $LAST_RUN | jq -r '.conclusion')

echo "Run ID: $RUN_ID"
echo "Status: $STATUS"
echo "Conclusion: $CONCLUSION"

if [ "$STATUS" = "completed" ]; then
    if [ "$CONCLUSION" = "success" ]; then
        echo ""
        echo "🎉🎉🎉 BUILD COM SUCESSO! 🎉🎉🎉"
        echo ""
        echo "✅ A correção do Executive funcionou!"
        echo "✅ Sistema de agentes aprendeu a solução!"
        echo ""
        echo "Próximo passo: Download do binário:"
        echo "  gh run download $RUN_ID"
    else
        echo ""
        echo "❌ Build falhou. Extraindo erros..."
        echo ""
        gh run view $RUN_ID --log | grep -A 10 "error:" | head -50
        echo ""
        echo "💡 Próximo passo: Analisar erro e executar:"
        echo "   python ai-agents/sync_with_claude.py teach"
    fi
else
    echo ""
    echo "⏳ Build ainda a correr... (status: $STATUS)"
fi
