# Comunicação com o servidor MCP via HTTP JSON-RPC 2.0

import json
import time
import requests
from config import SERVIDOR_URL, TIMEOUT_SEGUNDOS, TEMPOS_RETRY_FALHA

# Sessão global do MCP
sessao_mcp_id = None
contador_requisicoes = 0


def inicializar_sessao():
    """Inicializa a sessão MCP e retorna o session-id."""
    global sessao_mcp_id, contador_requisicoes
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "time-triagem",
                "version": "1.0"
            }
        }
    }
    
    resposta = requests.post(
        SERVIDOR_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        timeout=TIMEOUT_SEGUNDOS
    )
    
    if resposta.status_code != 200:
        raise Exception(f"Erro ao inicializar: {resposta.status_code} {resposta.text}")
    
    sessao_mcp_id = resposta.headers.get("mcp-session-id")
    if not sessao_mcp_id:
        raise Exception("Servidor não retornou mcp-session-id")
    
    print(f"✓ Sessão MCP inicializada: {sessao_mcp_id}")
    return sessao_mcp_id


def notificar_inicializado():
    """Notifica ao servidor que o cliente foi inicializado."""
    payload = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    
    resposta = requests.post(
        SERVIDOR_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Mcp-Session-Id": sessao_mcp_id
        },
        timeout=TIMEOUT_SEGUNDOS
    )
    
    if resposta.status_code != 200:
        raise Exception(f"Erro ao notificar: {resposta.status_code}")


def chamar_ferramenta(nome_ferramenta, argumentos):
    """Chama uma ferramenta do servidor MCP.
    
    Retorna um dicionário com:
    - status: "ok" ou "erro"
    - resultado: o resultado da ferramenta (se status="ok")
    - codigo: código de erro (se status="erro")
    - mensagem: mensagem de erro (se status="erro")
    """
    global contador_requisicoes
    
    if not sessao_mcp_id:
        raise Exception("Sessão MCP não inicializada. Chame inicializar_sessao() primeiro.")
    
    contador_requisicoes += 1
    payload = {
        "jsonrpc": "2.0",
        "id": contador_requisicoes,
        "method": "tools/call",
        "params": {
            "name": nome_ferramenta,
            "arguments": argumentos
        }
    }
    
    tentativa = 0
    while tentativa <= len(TEMPOS_RETRY_FALHA):
        try:
            resposta = requests.post(
                SERVIDOR_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Mcp-Session-Id": sessao_mcp_id,
                    "Accept": "application/json, text/event-stream"
                },
                timeout=TIMEOUT_SEGUNDOS
            )
            
            # Verificar se a sessão foi perdida
            if resposta.status_code in [400, 404]:
                raise Exception("Sessão MCP perdida. Reconectando...")
            
            # Processar resposta Server-Sent Events
            linhas = resposta.text.split("\n")
            for linha in linhas:
                if linha.startswith("data: "):
                    dados_json = linha[6:]  # Remove "data: "
                    dados = json.loads(dados_json)
                    
                    # Extrair resultado
                    if "result" in dados and "content" in dados["result"]:
                        conteudo = dados["result"]["content"]
                        if conteudo and len(conteudo) > 0:
                            texto_resultado = conteudo[0].get("text", "")
                            resultado_json = json.loads(texto_resultado)
                            
                            # Retornar resultado
                            if resultado_json.get("status") == "ok":
                                return {
                                    "status": "ok",
                                    "resultado": resultado_json
                                }
                            else:
                                return {
                                    "status": "erro",
                                    "codigo": resultado_json.get("codigo"),
                                    "mensagem": resultado_json.get("mensagem"),
                                    "resultado": resultado_json
                                }
            
            # Se chegou aqui, não encontrou resposta válida
            if resposta.status_code == 200:
                return {
                    "status": "ok",
                    "resultado": {}
                }
            
            # Tratar erros 503 e 409 com retry
            if resposta.status_code in [503, 409] and tentativa < len(TEMPOS_RETRY_FALHA):
                tempo_espera = TEMPOS_RETRY_FALHA[tentativa]
                print(f"  ⚠ Erro {resposta.status_code}, aguardando {tempo_espera}s...")
                time.sleep(tempo_espera)
                tentativa += 1
                continue
            
            # Outros erros
            return {
                "status": "erro",
                "codigo": resposta.status_code,
                "mensagem": f"Erro HTTP {resposta.status_code}: {resposta.text[:200]}"
            }
        
        except requests.exceptions.Timeout:
            return {
                "status": "erro",
                "codigo": 504,
                "mensagem": "Timeout na requisição ao servidor"
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "erro",
                "codigo": 500,
                "mensagem": f"Erro de conexão: {str(e)}"
            }
    
    return {
        "status": "erro",
        "codigo": 503,
        "mensagem": "Servidor indisponível após múltiplas tentativas"
    }


def listar_ferramentas():
    """Lista todas as ferramentas disponíveis no servidor."""
    payload = {
        "jsonrpc": "2.0",
        "id": 999,
        "method": "tools/list"
    }
    
    resposta = requests.post(
        SERVIDOR_URL,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Mcp-Session-Id": sessao_mcp_id,
            "Accept": "application/json, text/event-stream"
        },
        timeout=TIMEOUT_SEGUNDOS
    )
    
    linhas = resposta.text.split("\n")
    for linha in linhas:
        if linha.startswith("data: "):
            dados_json = linha[6:]
            dados = json.loads(dados_json)
            if "result" in dados and "tools" in dados["result"]:
                return dados["result"]["tools"]
    
    return []
