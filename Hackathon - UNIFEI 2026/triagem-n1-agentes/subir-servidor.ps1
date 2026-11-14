# Script para subir o servidor MCP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Subindo Servidor MCP - Tema Triagem" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$servidor_path = "..\Servidor MCP (Compartilhado)"

if (-not (Test-Path $servidor_path)) {
    Write-Host "X Pasta do servidor nao encontrada: $servidor_path" -ForegroundColor Red
    exit 1
}

Write-Host "`nOpcoes:" -ForegroundColor Yellow
Write-Host "1. Com Docker (recomendado)" -ForegroundColor White
Write-Host "2. Sem Docker (Python direto)" -ForegroundColor White
$opcao = Read-Host "Escolha (1 ou 2)"

cd $servidor_path

if ($opcao -eq "1") {
    Write-Host "`nSubindo com Docker..." -ForegroundColor Yellow
    Write-Host "Painel: http://localhost:8765" -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
    Write-Host ""
    
    $env:TEMA = "triagem"
    docker compose up --build mundo
} else {
    Write-Host "`nSubindo com Python..." -ForegroundColor Yellow
    Write-Host "Painel: http://localhost:8765" -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
    Write-Host ""
    
    python mundo.py --tema triagem
}
