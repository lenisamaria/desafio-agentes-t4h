# Script de setup para Windows PowerShell
# Execute: .\setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup - Hackathon UNIFEI 2026 - Triagem N1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Criar ambiente virtual
Write-Host "`n1. Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "   ✓ Ambiente virtual já existe" -ForegroundColor Green
} else {
    python -m venv .venv
    if ($?) {
        Write-Host "   ✓ Ambiente virtual criado" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Erro ao criar ambiente virtual" -ForegroundColor Red
        exit 1
    }
}

# 2. Ativar ambiente virtual
Write-Host "`n2. Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
Write-Host "   ✓ Ambiente ativado" -ForegroundColor Green

# 3. Instalar dependências
Write-Host "`n3. Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($?) {
    Write-Host "   ✓ Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}

# 4. Instalar Playwright
Write-Host "`n4. Instalando Playwright..." -ForegroundColor Yellow
playwright install chromium
if ($?) {
    Write-Host "   ✓ Playwright instalado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro ao instalar Playwright" -ForegroundColor Red
    exit 1
}

# 5. Copiar .env.exemplo para .env
Write-Host "`n5. Configurando .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   ✓ Arquivo .env já existe" -ForegroundColor Green
} else {
    Copy-Item ".env.exemplo" ".env"
    Write-Host "   ✓ Arquivo .env criado" -ForegroundColor Green
    Write-Host "   ⚠ IMPORTANTE: Edite .env e preencha OPENAI_API_KEY" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup concluído!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nPróximos passos:" -ForegroundColor Yellow
Write-Host "1. Edite .env e preencha OPENAI_API_KEY" -ForegroundColor White
Write-Host "2. Suba o servidor MCP em outro terminal:" -ForegroundColor White
Write-Host "   cd '..\Servidor MCP (Compartilhado)'" -ForegroundColor Gray
Write-Host "   `$env:TEMA='triagem'" -ForegroundColor Gray
Write-Host "   docker compose up --build mundo" -ForegroundColor Gray
Write-Host "3. Teste a conexão:" -ForegroundColor White
Write-Host "   python testar_conexao.py" -ForegroundColor Gray
