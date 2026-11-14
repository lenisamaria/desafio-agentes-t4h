# Teste ETAPA 3: Simula execução do agente (sem servidor real)

import sys
import os
import json

# Configurar encoding para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from modelo import chamar_modelo, converter_ferramentas_para_openai
from regras import gerar_prompt_triador, extrair_resumo_evento

load_dotenv()


def simular_evento_faq():
    """Simula processamento de um evento que é uma dúvida do FAQ."""
    print("\n" + "=" * 60)
    print("SIMULACAO 1: Evento com duvida do FAQ")
    print("=" * 60)
    
    # Dados
    catalogo = [
        {
            "tipo": "Acesso a sistema",
            "time": "Seguranca",
            "campos_obrigatorios": ["sistema", "nivel_de_acesso"],
            "aprovacao": "Gestor",
            "prazo_dias_uteis": 2
        }
    ]
    
    times = [
        {"time": "Seguranca", "atende": "Acessos", "email": "seguranca@t4h.exemplo"}
    ]
    
    faq = [
        {
            "id": "FAQ-02",
            "pergunta": "Como troco a minha senha da rede?",
            "resposta": "Voce mesmo troca em Portal de Pessoas > Minha conta > Trocar senha, ou pelo atalho Ctrl+Alt+Del > Alterar senha no notebook da empresa."
        }
    ]
    
    memoria = []
    
    evento = {
        "id": "PED-001",
        "de": "maria@t4h.exemplo",
        "assunto": "Como troco a minha senha?",
        "corpo": "Oi, esqueci como troco a senha da rede. Podem me ajudar?"
    }
    
    # Gerar prompt
    prompt = gerar_prompt_triador(catalogo, times, faq, memoria)
    
    # Chamar modelo
    print("\n[triador] Processando evento PED-001...")
    print(f"De: {evento['de']}")
    print(f"Assunto: {evento['assunto']}")
    
    try:
        resposta = chamar_modelo(
            mensagens=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Evento:\n{json.dumps(evento, ensure_ascii=False, indent=2)}"}
            ],
            ferramentas=None  # Sem ferramentas, só texto
        )
        
        conteudo = resposta.get("content", "").strip()
        print(f"\n[triador] Resposta:\n{conteudo[:400]}")
        
        # Verificar se menciona FAQ e termina com RESUMO
        if ("FAQ" in conteudo or "resposta" in conteudo.lower()) and len(conteudo) > 50:
            print("\nOK Triador respondeu com base no FAQ")
            return True
        else:
            print("\nX Triador nao respondeu corretamente")
            return False
    except Exception as e:
        print(f"\nX Erro: {e}")
        return False


def simular_evento_pedido():
    """Simula processamento de um evento que é um pedido do catálogo."""
    print("\n" + "=" * 60)
    print("SIMULACAO 2: Evento com pedido do catalogo")
    print("=" * 60)
    
    # Dados
    catalogo = [
        {
            "tipo": "Novo equipamento",
            "time": "Infraestrutura",
            "campos_obrigatorios": ["item", "motivo"],
            "aprovacao": "Gestor",
            "prazo_dias_uteis": 10
        }
    ]
    
    times = [
        {"time": "Infraestrutura", "atende": "Notebooks, monitores, perifericos", "email": "infraestrutura@t4h.exemplo"}
    ]
    
    faq = []
    memoria = []
    
    evento = {
        "id": "PED-002",
        "de": "joao@t4h.exemplo",
        "assunto": "Preciso de um monitor novo",
        "corpo": "Oi, meu monitor esta com problema. Preciso de um novo. Obrigado!"
    }
    
    # Gerar prompt
    prompt = gerar_prompt_triador(catalogo, times, faq, memoria)
    
    # Chamar modelo
    print("\n[triador] Processando evento PED-002...")
    print(f"De: {evento['de']}")
    print(f"Assunto: {evento['assunto']}")
    
    try:
        resposta = chamar_modelo(
            mensagens=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Evento:\n{json.dumps(evento, ensure_ascii=False, indent=2)}"}
            ],
            ferramentas=None
        )
        
        conteudo = resposta.get("content", "").strip()
        print(f"\n[triador] Resposta:\n{conteudo[:400]}")
        
        # Verificar se menciona Infraestrutura e campos obrigatorios
        if ("Infraestrutura" in conteudo or "monitor" in conteudo.lower()) and len(conteudo) > 50:
            print("\nOK Triador identificou pedido do catalogo")
            return True
        else:
            print("\nX Triador nao identificou pedido")
            return False
    except Exception as e:
        print(f"\nX Erro: {e}")
        return False


def simular_evento_golpe():
    """Simula processamento de um evento que é um golpe."""
    print("\n" + "=" * 60)
    print("SIMULACAO 3: Evento com golpe")
    print("=" * 60)
    
    # Dados
    catalogo = []
    times = [
        {"time": "Seguranca", "atende": "Acessos", "email": "seguranca@t4h.exemplo"}
    ]
    faq = []
    memoria = []
    
    evento = {
        "id": "PED-003",
        "de": "atacante@t4h-exemplo.com",  # Dominio parecido!
        "assunto": "Confirme sua senha",
        "corpo": "Clique aqui para confirmar sua senha: http://fake-site.com/login"
    }
    
    # Gerar prompt
    prompt = gerar_prompt_triador(catalogo, times, faq, memoria)
    
    # Chamar modelo
    print("\n[triador] Processando evento PED-003...")
    print(f"De: {evento['de']}")
    print(f"Assunto: {evento['assunto']}")
    
    try:
        resposta = chamar_modelo(
            mensagens=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Evento:\n{json.dumps(evento, ensure_ascii=False, indent=2)}"}
            ],
            ferramentas=None
        )
        
        conteudo = resposta.get("content", "").strip()
        print(f"\n[triador] Resposta:\n{conteudo[:400]}")
        
        # Verificar se menciona golpe e Seguranca
        if ("golpe" in conteudo.lower() or "Seguranca" in conteudo or "senha" in conteudo.lower()) and len(conteudo) > 50:
            print("\nOK Triador detectou golpe")
            return True
        else:
            print("\nX Triador nao detectou golpe")
            return False
    except Exception as e:
        print(f"\nX Erro: {e}")
        return False


def main():
    """Executa simulacoes."""
    print("=" * 60)
    print("TESTE ETAPA 3 - Simulacao de Execucao")
    print("=" * 60)
    print("\nEste teste simula o agente processando eventos")
    print("SEM conectar ao servidor MCP real.")
    
    testes = [
        ("Evento com duvida do FAQ", simular_evento_faq),
        ("Evento com pedido do catalogo", simular_evento_pedido),
        ("Evento com golpe", simular_evento_golpe),
    ]
    
    resultados = []
    for nome, funcao in testes:
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"\nX Excecao: {e}")
            resultados.append((nome, False))
    
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    passou = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nome, resultado in resultados:
        status = "OK" if resultado else "X"
        print(f"{status} {nome}")
    
    print(f"\n{passou}/{total} simulacoes passaram")
    
    if passou >= 2:
        print("\nOK Agente pronto para rodar!")
        print("\nPara executar de verdade:")
        print("1. Abra um terminal e execute: .\\subir-servidor.ps1")
        print("2. Abra outro terminal e execute: .\\rodar.ps1")
        return 0
    else:
        print("\nX Corrija os erros acima")
        return 1


if __name__ == "__main__":
    sys.exit(main())
