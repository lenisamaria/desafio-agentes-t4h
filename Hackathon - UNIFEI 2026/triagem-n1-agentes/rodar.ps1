# Script para rodar servidor MCP e agente em paralelo

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Hackathon UNIFEI 2026 - Triagem N1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar se servidor está rodando
Write-Host "`nVerificando servidor MCP..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri http://localhost:8765 -TimeoutSec 2 -ErrorAction Stop
    Write-Host "OK Servidor ja esta rodando" -ForegroundColor Green
} catch {
    Write-Host "X Servidor nao esta rodando" -ForegroundColor Red
    Write-Host "`nPara subir o servidor, abra OUTRO terminal e execute:" -ForegroundColor Yellow
    Write-Host "  cd '..\Servidor MCP (Compartilhado)'" -ForegroundColor Gray
    Write-Host "  `$env:TEMA='triagem'" -ForegroundColor Gray
    Write-Host "  docker compose up --build mundo" -ForegroundColor Gray
    Write-Host "`nOu sem Docker:" -ForegroundColor Gray
    Write-Host "  python mundo.py --tema triagem" -ForegroundColor Gray
    Write-Host "`nDepois volte aqui e pressione ENTER para continuar..." -ForegroundColor Yellow
    Read-Host
}

# Ativar ambiente virtual
Write-Host "`nAtivando ambiente virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Rodar agente
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Iniciando agente..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nPainel ao vivo: http://localhost:8765" -ForegroundColor Cyan
Write-Host "`nPressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

python agente.py
