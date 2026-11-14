#!/bin/bash
# Script de setup para macOS/Linux
# Execute: bash setup.sh

echo "========================================"
echo "Setup - Hackathon UNIFEI 2026 - Triagem N1"
echo "========================================"

# 1. Criar ambiente virtual
echo ""
echo "1. Criando ambiente virtual..."
if [ -d ".venv" ]; then
    echo "   ✓ Ambiente virtual já existe"
else
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "   ✓ Ambiente virtual criado"
    else
        echo "   ✗ Erro ao criar ambiente virtual"
        exit 1
    fi
fi

# 2. Ativar ambiente virtual
echo ""
echo "2. Ativando ambiente virtual..."
source .venv/bin/activate
echo "   ✓ Ambiente ativado"

# 3. Instalar dependências
echo ""
echo "3. Instalando dependências..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✓ Dependências instaladas"
else
    echo "   ✗ Erro ao instalar dependências"
    exit 1
fi

# 4. Instalar Playwright
echo ""
echo "4. Instalando Playwright..."
playwright install chromium
if [ $? -eq 0 ]; then
    echo "   ✓ Playwright instalado"
else
    echo "   ✗ Erro ao instalar Playwright"
    exit 1
fi

# 5. Copiar .env.exemplo para .env
echo ""
echo "5. Configurando .env..."
if [ -f ".env" ]; then
    echo "   ✓ Arquivo .env já existe"
else
    cp .env.exemplo .env
    echo "   ✓ Arquivo .env criado"
    echo "   ⚠ IMPORTANTE: Edite .env e preencha OPENAI_API_KEY"
fi

echo ""
echo "========================================"
echo "Setup concluído!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Edite .env e preencha OPENAI_API_KEY"
echo "2. Suba o servidor MCP em outro terminal:"
echo "   cd '../Servidor MCP (Compartilhado)'"
echo "   export TEMA=triagem"
echo "   docker compose up --build mundo"
echo "3. Teste a conexão:"
echo "   python testar_conexao.py"
