# Integração com LiteLLM e conversão de ferramentas para OpenAI format

import os
import json
import time
from dotenv import load_dotenv
import requests
from config import MODELO, TEMPERATURA, TEMPOS_RETRY_RATE_LIMIT

load_dotenv()

# Configuração LiteLLM
LITELLM_API_BASE = os.getenv("LITELLM_API_BASE", "https://litellm.tech4humans.com.br/v1/chat/completions")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

if not LITELLM_API_KEY:
    raise Exception("LITELLM_API_KEY não configurada no .env")


def converter_ferramentas_para_openai(ferramentas_mcp):
    """Converte ferramentas do MCP para o formato de tools da OpenAI.
    
    Remove o parâmetro 'agente' (preenchido pelo código) e torna 'motivo' obrigatório.
    Esconde proximo_evento e listar_bases do modelo.
    """
    ferramentas_openai = []
    
    for ferramenta in ferramentas_mcp:
        nome = ferramenta.get("name", "")
        
        # Esconder ferramentas que o código chama diretamente
        if nome in ["proximo_evento", "listar_bases"]:
            continue
        
        descricao = ferramenta.get("description", "")
        input_schema = ferramenta.get("inputSchema", {})
        
        # Copiar schema de parâmetros
        parametros = {
            "type": "object",
            "properties": input_schema.get("properties", {}).copy(),
            "required": list(input_schema.get("required", []))
        }
        
        # Remover 'agente' das propriedades (o código preenche)
        if "agente" in parametros["properties"]:
            del parametros["properties"]["agente"]
        if "agente" in parametros["required"]:
            parametros["required"].remove("agente")
        
        # Tornar 'motivo' obrigatório
        if "motivo" in parametros["properties"]:
            if "motivo" not in parametros["required"]:
                parametros["required"].append("motivo")
        
        ferramenta_openai = {
            "type": "function",
            "function": {
                "name": nome,
                "description": descricao,
                "parameters": parametros
            }
        }
        
        ferramentas_openai.append(ferramenta_openai)
    
    return ferramentas_openai


def chamar_modelo(mensagens, ferramentas=None, nome_agente="triador"):
    """Chama o modelo LiteLLM com tool calling.
    
    Argumentos:
    - mensagens: lista de dicts com "role" e "content"
    - ferramentas: lista de ferramentas no formato OpenAI (opcional)
    - nome_agente: nome do agente (para logs)
    
    Retorna:
    - resposta: dict com "role", "content" e "tool_calls" (se houver)
    """
    
    payload = {
        "model": MODELO,
        "messages": mensagens,
        "temperature": TEMPERATURA,
        "max_tokens": 4096
    }
    
    if ferramentas:
        payload["tools"] = ferramentas
        payload["tool_choice"] = "auto"
    
    tentativa = 0
    while tentativa <= len(TEMPOS_RETRY_RATE_LIMIT):
        try:
            resposta = requests.post(
                LITELLM_API_BASE,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LITELLM_API_KEY}"
                },
                timeout=30
            )
            
            # Tratar erro 429 (RateLimitError)
            if resposta.status_code == 429:
                if tentativa < len(TEMPOS_RETRY_RATE_LIMIT):
                    tempo_espera = TEMPOS_RETRY_RATE_LIMIT[tentativa]
                    print(f"  ⚠ Rate limit (429), aguardando {tempo_espera}s...")
                    time.sleep(tempo_espera)
                    tentativa += 1
                    continue
                else:
                    raise Exception("Rate limit excedido após múltiplas tentativas")
            
            if resposta.status_code != 200:
                raise Exception(f"Erro HTTP {resposta.status_code}: {resposta.text[:200]}")
            
            dados = resposta.json()
            
            # Extrair resposta
            if "choices" not in dados or len(dados["choices"]) == 0:
                raise Exception(f"Resposta inválida do modelo: {dados}")
            
            escolha = dados["choices"][0]
            mensagem = escolha.get("message", {})
            
            resultado = {
                "role": "assistant",
                "content": mensagem.get("content", ""),
                "tool_calls": []
            }
            
            # Extrair tool calls se houver
            if "tool_calls" in mensagem:
                for tool_call in mensagem["tool_calls"]:
                    resultado["tool_calls"].append({
                        "id": tool_call.get("id", ""),
                        "function": {
                            "name": tool_call.get("function", {}).get("name", ""),
                            "arguments": tool_call.get("function", {}).get("arguments", "{}")
                        }
                    })
            
            return resultado
        
        except requests.exceptions.Timeout:
            raise Exception("Timeout ao chamar modelo")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro de conexão com modelo: {str(e)}")
    
    raise Exception("Falha ao chamar modelo após múltiplas tentativas")


def extrair_tool_calls(resposta_modelo):
    """Extrai as chamadas de ferramenta da resposta do modelo.
    
    Retorna uma lista de dicts com:
    - id: identificador da chamada
    - name: nome da ferramenta
    - arguments: dict com os argumentos
    """
    tool_calls = []
    
    if "tool_calls" not in resposta_modelo:
        return tool_calls
    
    for tool_call in resposta_modelo["tool_calls"]:
        try:
            argumentos = tool_call["function"]["arguments"]
            if isinstance(argumentos, str):
                argumentos = json.loads(argumentos)
            
            tool_calls.append({
                "id": tool_call.get("id", ""),
                "name": tool_call["function"]["name"],
                "arguments": argumentos
            })
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ✗ Erro ao extrair tool call: {e}")
    
    return tool_calls
