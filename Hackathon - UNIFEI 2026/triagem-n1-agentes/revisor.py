# Revisor: valida ações antes de executar

import json
from modelo import chamar_modelo
from regras import gerar_prompt_revisor

# Contador de recusas por evento (para não travar)
recusas_por_evento = {}


def revisar_acao(evento_id, evento_json, acao_proposta, catalogo, times):
    """Revisa uma ação proposta antes de executar.
    
    Argumentos:
    - evento_id: ID do evento
    - evento_json: JSON do evento completo
    - acao_proposta: dict com nome da ferramenta e argumentos
    - catalogo: lista de tipos de chamado
    - times: lista de times
    
    Retorna:
    - {"status": "ok"} se passou
    - {"status": "erro", "revisao": "BARRADA", "comentario_do_revisor": "...", "instrucao": "..."} se barrou
    """
    
    # Contar recusas deste evento
    if evento_id not in recusas_por_evento:
        recusas_por_evento[evento_id] = {}
    
    nome_ferramenta = acao_proposta.get("name", "")
    if nome_ferramenta not in recusas_por_evento[evento_id]:
        recusas_por_evento[evento_id][nome_ferramenta] = 0
    
    # Se já foi barrada 2 vezes, deixar passar na terceira
    if recusas_por_evento[evento_id][nome_ferramenta] >= 2:
        print(f"  [revisor] Limite de recusas atingido para {nome_ferramenta}, deixando passar")
        return {"status": "ok"}
    
    # Gerar prompt do revisor
    prompt_revisor = gerar_prompt_revisor(catalogo, times)
    
    # Montar mensagem para o revisor
    mensagem_revisor = f"""Evento: {evento_json}

Ação proposta:
- Ferramenta: {nome_ferramenta}
- Argumentos: {json.dumps(acao_proposta.get('arguments', {}), ensure_ascii=False, indent=2)}

Valide esta ação."""
    
    # Chamar modelo do revisor (SEM ferramentas)
    try:
        resposta = chamar_modelo(
            mensagens=[
                {"role": "system", "content": prompt_revisor},
                {"role": "user", "content": mensagem_revisor}
            ],
            ferramentas=None,
            nome_agente="revisor"
        )
        
        conteudo = resposta.get("content", "").strip()
        
        # Verificar resposta
        if conteudo.startswith("OK"):
            print(f"  [revisor] OK - {conteudo[:50]}")
            return {"status": "ok"}
        elif conteudo.startswith("PROBLEMA:"):
            # Extrair comentário
            comentario = conteudo[9:].strip()
            recusas_por_evento[evento_id][nome_ferramenta] += 1
            
            print(f"  [revisor] BARRADA - {comentario[:60]}")
            
            return {
                "status": "erro",
                "revisao": "BARRADA",
                "comentario_do_revisor": comentario,
                "instrucao": "Corrija e tente de novo"
            }
        else:
            # Resposta ambígua, deixar passar
            print(f"  [revisor] Resposta ambígua, deixando passar")
            return {"status": "ok"}
    
    except Exception as e:
        # Se a IA do revisor falhar, deixar passar
        print(f"  [revisor] Erro ao revisar: {e}, deixando passar")
        return {"status": "ok"}


def limpar_recusas_evento(evento_id):
    """Limpa o contador de recusas de um evento (ao terminar)."""
    if evento_id in recusas_por_evento:
        del recusas_por_evento[evento_id]
