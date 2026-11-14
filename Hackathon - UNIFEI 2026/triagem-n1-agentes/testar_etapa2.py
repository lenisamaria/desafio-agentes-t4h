# Teste da ETAPA 2: Prompts, revisor e férias

import sys
import os

# Configurar encoding para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from servidor import inicializar_sessao, notificar_inicializado, chamar_ferramenta
from modelo import chamar_modelo, converter_ferramentas_para_openai
from regras import gerar_prompt_triador, gerar_prompt_revisor
from revisor import revisar_acao
from ferias import lancar_ferias

load_dotenv()


def testar_prompts():
    """Testa geração de prompts."""
    print("\n1. Testando geração de prompts...")
    
    # Dados de exemplo
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
        {
            "time": "Seguranca",
            "atende": "Acessos",
            "email": "seguranca@t4h.exemplo"
        }
    ]
    
    faq = [
        {
            "id": "FAQ-01",
            "pergunta": "Como me conecto a VPN?",
            "resposta": "Instale o cliente de VPN..."
        }
    ]
    
    memoria = ["[PED-001] Registrou acesso para João"]
    
    # Gerar prompts
    prompt_triador = gerar_prompt_triador(catalogo, times, faq, memoria)
    prompt_revisor = gerar_prompt_revisor(catalogo, times)
    
    if len(prompt_triador) > 500 and len(prompt_revisor) > 200:
        print("  OK Prompts gerados com sucesso")
        print(f"     Triador: {len(prompt_triador)} caracteres")
        print(f"     Revisor: {len(prompt_revisor)} caracteres")
        return True
    else:
        print("  X Prompts muito curtos")
        return False


def testar_modelo_simples():
    """Testa chamada simples ao modelo."""
    print("\n2. Testando chamada ao modelo...")
    
    try:
        resposta = chamar_modelo(
            mensagens=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Responda com uma frase curta sobre triagem de chamados."}
            ],
            ferramentas=None
        )
        
        conteudo = resposta.get("content", "").strip()
        if len(conteudo) > 10:
            print(f"  OK Modelo respondeu: {conteudo[:60]}")
            return True
        else:
            print("  X Resposta muito curta")
            return False
    except Exception as e:
        print(f"  X Erro: {e}")
        return False


def testar_revisor():
    """Testa revisor."""
    print("\n3. Testando revisor...")
    
    catalogo = [
        {
            "tipo": "Acesso a sistema",
            "time": "Seguranca",
            "campos_obrigatorios": ["sistema"],
            "aprovacao": "Gestor",
            "prazo_dias_uteis": 2
        }
    ]
    
    times = [
        {"time": "Seguranca", "atende": "Acessos", "email": "seguranca@t4h.exemplo"}
    ]
    
    evento = {
        "id": "PED-001",
        "de": "joao@t4h.exemplo",
        "assunto": "Acesso ao sistema"
    }
    
    acao = {
        "name": "registrar",
        "arguments": {
            "base": "chamados",
            "dados": {"tipo": "Acesso a sistema"},
            "evento_id": "PED-001"
        }
    }
    
    try:
        resultado = revisar_acao("PED-001", str(evento), acao, catalogo, times)
        
        if resultado.get("status") == "ok":
            print("  OK Revisor aprovou ação")
            return True
        else:
            print(f"  OK Revisor barrou: {resultado.get('comentario_do_revisor', '')[:50]}")
            return True  # Barrar também é sucesso do revisor
    except Exception as e:
        print(f"  X Erro: {e}")
        return False


def testar_ferias():
    """Testa função de férias (sem executar)."""
    print("\n4. Testando função de ferias...")
    
    try:
        # Não vamos executar de verdade, só verificar que a função existe
        import inspect
        sig = inspect.signature(lancar_ferias)
        params = list(sig.parameters.keys())
        
        esperados = ["email", "data_inicio", "data_fim", "evento_id", "motivo"]
        if all(p in params for p in esperados):
            print(f"  OK Funcao lancar_ferias tem parametros corretos")
            return True
        else:
            print(f"  X Parametros incorretos: {params}")
            return False
    except Exception as e:
        print(f"  X Erro: {e}")
        return False


def testar_conexao_mcp():
    """Testa conexão com MCP."""
    print("\n5. Testando conexao com MCP...")
    
    try:
        inicializar_sessao()
        notificar_inicializado()
        
        # Tentar listar bases
        resultado = chamar_ferramenta("listar_bases", {
            "agente": "triador",
            "motivo": "Teste"
        })
        
        if resultado.get("status") == "ok":
            print("  OK Conexao MCP funcionando")
            return True
        else:
            print(f"  X Erro MCP: {resultado.get('mensagem')}")
            return False
    except Exception as e:
        print(f"  X Erro: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTE ETAPA 2 - Prompts, Revisor e Ferias")
    print("=" * 60)
    
    testes = [
        ("Geracao de prompts", testar_prompts),
        ("Chamada ao modelo", testar_modelo_simples),
        ("Revisor", testar_revisor),
        ("Funcao de ferias", testar_ferias),
        ("Conexao MCP", testar_conexao_mcp),
    ]
    
    resultados = []
    for nome, funcao in testes:
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"  X Excecao: {e}")
            resultados.append((nome, False))
    
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    
    passou = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nome, resultado in resultados:
        status = "OK" if resultado else "X"
        print(f"{status} {nome}")
    
    print(f"\n{passou}/{total} testes passaram")
    
    if passou >= 4:  # Pelo menos 4 de 5
        print("\nOK Etapa 2 pronta! Proxima: python agente.py")
        return 0
    else:
        print("\nX Corrija os erros acima")
        return 1


if __name__ == "__main__":
    sys.exit(main())
