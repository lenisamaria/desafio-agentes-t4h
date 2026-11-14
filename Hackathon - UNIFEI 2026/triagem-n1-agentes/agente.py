# Laço principal do time de agentes

import json
import time
from config import (
    AGENTE_TRIADOR, AGENTE_REVISOR, AGENTE_OPERADOR_TELA,
    MAX_CHAMADAS_MODELO_POR_EVENTO, MAX_EVENTOS_MEMORIA,
    ESPERAR_SEGUNDOS_PROXIMO_EVENTO
)
from servidor import inicializar_sessao, notificar_inicializado, chamar_ferramenta
from modelo import chamar_modelo, converter_ferramentas_para_openai, extrair_tool_calls
from revisor import revisar_acao, limpar_recusas_evento
from ferias import lancar_ferias
from regras import gerar_prompt_triador, extrair_resumo_evento

# Estado global
ferramentas_mcp = []
catalogo = []
times = []
faq = []
memoria = []
ferramentas_openai = []


def carregar_bases():
    """Carrega catálogo, times e FAQ do servidor."""
    global catalogo, times, faq
    
    print("\n[agente] Carregando bases do servidor...")
    
    # Carregar catálogo
    resultado = chamar_ferramenta("consultar", {
        "agente": AGENTE_TRIADOR,
        "motivo": "Carregar catálogo de tipos de chamado",
        "base": "catalogo",
        "limite": 100
    })
    
    if resultado["status"] == "ok":
        catalogo = resultado["resultado"].get("registros", [])
        print(f"  OK Catálogo carregado: {len(catalogo)} tipos")
    else:
        print(f"  X Erro ao carregar catálogo: {resultado.get('mensagem')}")
    
    # Carregar times
    resultado = chamar_ferramenta("consultar", {
        "agente": AGENTE_TRIADOR,
        "motivo": "Carregar times",
        "base": "times",
        "limite": 100
    })
    
    if resultado["status"] == "ok":
        times = resultado["resultado"].get("registros", [])
        print(f"  OK Times carregados: {len(times)} times")
    else:
        print(f"  X Erro ao carregar times: {resultado.get('mensagem')}")
    
    # Carregar FAQ
    resultado = chamar_ferramenta("consultar", {
        "agente": AGENTE_TRIADOR,
        "motivo": "Carregar FAQ",
        "base": "faq",
        "limite": 100
    })
    
    if resultado["status"] == "ok":
        faq = resultado["resultado"].get("registros", [])
        print(f"  OK FAQ carregado: {len(faq)} itens")
    else:
        print(f"  X Erro ao carregar FAQ: {resultado.get('mensagem')}")


def listar_ferramentas_servidor():
    """Lista ferramentas disponíveis no servidor."""
    global ferramentas_mcp, ferramentas_openai
    
    print("\n[agente] Listando ferramentas do servidor...")
    
    resultado = chamar_ferramenta("listar_bases", {
        "agente": AGENTE_TRIADOR,
        "motivo": "Listar ferramentas disponíveis"
    })
    
    # Nota: listar_bases retorna as bases, não as ferramentas
    # Vamos usar as ferramentas padrão do MCP
    ferramentas_mcp = [
        {
            "name": "proximo_evento",
            "description": "Pega o próximo evento novo",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "esperar_segundos": {"type": "integer"}
                },
                "required": ["agente", "motivo"]
            }
        },
        {
            "name": "ler_evento",
            "description": "Lê um evento específico",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "evento_id": {"type": "string"}
                },
                "required": ["agente", "motivo", "evento_id"]
            }
        },
        {
            "name": "responder_evento",
            "description": "Responde a um evento",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "evento_id": {"type": "string"},
                    "mensagem": {"type": "string"},
                    "aguardar_resposta": {"type": "boolean"}
                },
                "required": ["agente", "motivo", "evento_id", "mensagem"]
            }
        },
        {
            "name": "enviar_mensagem",
            "description": "Envia uma mensagem",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "para": {"type": "string"},
                    "assunto": {"type": "string"},
                    "mensagem": {"type": "string"},
                    "evento_id": {"type": "string"}
                },
                "required": ["agente", "motivo", "para", "assunto", "mensagem"]
            }
        },
        {
            "name": "registrar",
            "description": "Registra um novo item em uma base",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "base": {"type": "string"},
                    "dados": {"type": "object"},
                    "evento_id": {"type": "string"}
                },
                "required": ["agente", "motivo", "base", "dados"]
            }
        },
        {
            "name": "atualizar",
            "description": "Atualiza um item em uma base",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "base": {"type": "string"},
                    "id": {"type": "string"},
                    "dados": {"type": "object"},
                    "evento_id": {"type": "string"}
                },
                "required": ["agente", "motivo", "base", "id", "dados"]
            }
        },
        {
            "name": "consultar",
            "description": "Consulta itens em uma base",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "base": {"type": "string"},
                    "filtro": {"type": "object"},
                    "busca": {"type": "string"},
                    "limite": {"type": "integer"}
                },
                "required": ["agente", "motivo", "base"]
            }
        },
        {
            "name": "registrar_conversa",
            "description": "Registra uma conversa entre agentes",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agente": {"type": "string"},
                    "motivo": {"type": "string"},
                    "de": {"type": "string"},
                    "para": {"type": "string"},
                    "mensagem": {"type": "string"}
                },
                "required": ["agente", "motivo", "de", "para", "mensagem"]
            }
        }
    ]
    
    # Converter para formato OpenAI
    ferramentas_openai = converter_ferramentas_para_openai(ferramentas_mcp)
    print(f"  OK {len(ferramentas_openai)} ferramentas disponíveis")


def processar_evento(evento):
    """Processa um evento com o triador.
    
    Argumentos:
    - evento: dict com os dados do evento
    
    Retorna:
    - True se processado com sucesso
    - False se erro
    """
    global memoria
    
    evento_id = evento.get("id", "DESCONHECIDO")
    print(f"\n[agente] Processando evento: {evento_id}")
    print(f"  De: {evento.get('de', '?')}")
    print(f"  Assunto: {evento.get('assunto', '?')[:60]}")
    
    # Gerar prompt do triador
    prompt_triador = gerar_prompt_triador(catalogo, times, faq, memoria)
    
    # Montar mensagens iniciais
    mensagens = [
        {"role": "system", "content": prompt_triador},
        {"role": "user", "content": f"Evento:\n{json.dumps(evento, ensure_ascii=False, indent=2)}"}
    ]
    
    # Loop do triador (máximo 15 chamadas ao modelo)
    chamadas = 0
    while chamadas < MAX_CHAMADAS_MODELO_POR_EVENTO:
        chamadas += 1
        
        # Chamar modelo
        try:
            resposta = chamar_modelo(
                mensagens=mensagens,
                ferramentas=ferramentas_openai,
                nome_agente=AGENTE_TRIADOR
            )
        except Exception as e:
            print(f"  X Erro ao chamar modelo: {e}")
            return False
        
        # Adicionar resposta às mensagens
        mensagens.append(resposta)
        
        # Verificar se terminou (resposta em texto começando com "RESUMO:")
        conteudo = resposta.get("content", "").strip()
        if conteudo.startswith("RESUMO:"):
            print(f"  OK Triador terminou: {conteudo[:80]}")
            # Adicionar à memória
            resumo = extrair_resumo_evento(evento_id, conteudo)
            memoria.append(resumo)
            if len(memoria) > MAX_EVENTOS_MEMORIA:
                memoria.pop(0)
            return True
        
        # Extrair tool calls
        tool_calls = extrair_tool_calls(resposta)
        
        if not tool_calls:
            # Sem tool calls e sem RESUMO = erro
            print(f"  X Triador não terminou corretamente: {conteudo[:80]}")
            return False
        
        # Executar cada tool call
        for tool_call in tool_calls:
            nome_ferramenta = tool_call["name"]
            argumentos = tool_call["arguments"]
            
            print(f"  -> {nome_ferramenta}")
            
            # Adicionar agente aos argumentos
            argumentos["agente"] = AGENTE_TRIADOR
            
            # Revisar ação (se não for consulta)
            if nome_ferramenta not in ["consultar", "ler_evento", "listar_eventos"]:
                resultado_revisao = revisar_acao(evento_id, json.dumps(evento), tool_call, catalogo, times)
                if resultado_revisao["status"] != "ok":
                    # Ação barrada
                    resultado_ferramenta = resultado_revisao
                    # Registrar recusa no painel
                    chamar_ferramenta("registrar_conversa", {
                        "agente": AGENTE_REVISOR,
                        "motivo": "Registrar recusa",
                        "de": AGENTE_REVISOR,
                        "para": AGENTE_TRIADOR,
                        "mensagem": f"[{evento_id}] Barrei {nome_ferramenta}: {resultado_revisao.get('comentario_do_revisor', '')}"
                    })
                else:
                    # Ação aprovada, executar
                    resultado_ferramenta = chamar_ferramenta(nome_ferramenta, argumentos)
            else:
                # Consulta, executar direto
                resultado_ferramenta = chamar_ferramenta(nome_ferramenta, argumentos)
            
            # Mostrar resultado (encurtado)
            status = resultado_ferramenta.get("status", "?")
            msg = resultado_ferramenta.get("resultado", {}).get("mensagem", "")[:60]
            print(f"     {status}: {msg}")
            
            # Adicionar resultado às mensagens
            mensagens.append({
                "role": "user",
                "content": f"Resultado de {nome_ferramenta}:\n{json.dumps(resultado_ferramenta, ensure_ascii=False)[:500]}"
            })
    
    print(f"  X Triador excedeu limite de chamadas ({MAX_CHAMADAS_MODELO_POR_EVENTO})")
    return False


def laço_principal():
    """Laço principal: pega eventos e processa."""
    global ferramentas_mcp, ferramentas_openai
    
    print("=" * 60)
    print("TIME DE AGENTES - Hackathon UNIFEI 2026 - Triagem N1")
    print("=" * 60)
    
    # Inicializar
    print("\n[agente] Inicializando...")
    inicializar_sessao()
    notificar_inicializado()
    
    # Carregar dados
    listar_ferramentas_servidor()
    carregar_bases()
    
    # Laço principal
    print("\n[agente] Entrando em laço...")
    while True:
        # Pegar próximo evento
        resultado = chamar_ferramenta("proximo_evento", {
            "agente": AGENTE_TRIADOR,
            "motivo": "Pegar próximo evento",
            "esperar_segundos": ESPERAR_SEGUNDOS_PROXIMO_EVENTO
        })
        
        if resultado["status"] != "ok":
            print(f"X Erro ao pegar evento: {resultado.get('mensagem')}")
            continue
        
        dados = resultado.get("resultado", {})
        
        # Verificar se cenário acabou
        if dados.get("encerrado"):
            print("\n[agente] Cenário encerrado!")
            break
        
        # Verificar se há evento
        evento = dados.get("evento")
        if not evento:
            tempo_proximo = dados.get("tempo_proximo_evento_segundos", "?")
            print(f"[agente] Sem evento agora, próximo em {tempo_proximo}s...")
            continue
        
        # Processar evento
        processar_evento(evento)
        limpar_recusas_evento(evento.get("id", ""))
    
    print("\n[agente] Programa encerrado")


if __name__ == "__main__":
    laço_principal()
