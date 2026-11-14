# Teste de conexão: verifica .env, servidor, IA e página de férias

import os
import sys
import requests
from dotenv import load_dotenv
from config import SERVIDOR_URL, SERVIDOR_PAINEL, MODELO
import servidor

# Configurar encoding para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def testar_env():
    """Verifica se o arquivo .env existe e tem LITELLM_API_KEY."""
    print("\n1. Testando arquivo .env...")
    
    if not os.path.exists(".env"):
        print("  X Arquivo .env nao encontrado")
        print("    Copie .env.exemplo para .env e preencha LITELLM_API_KEY")
        return False
    
    load_dotenv()
    chave = os.getenv("LITELLM_API_KEY")
    
    if not chave:
        print("  X LITELLM_API_KEY nao configurada")
        return False
    
    print("  OK .env carregado com LITELLM_API_KEY")
    return True


def testar_servidor_mcp():
    """Verifica se o servidor MCP está rodando."""
    print("\n2. Testando servidor MCP...")
    
    try:
        resposta = requests.get(SERVIDOR_URL, timeout=5)
        # Qualquer resposta (até 400/405) significa que o servidor está rodando
        print(f"  OK Servidor MCP respondeu (status {resposta.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"  X Nao conseguiu conectar em {SERVIDOR_URL}")
        print("    Verifique se o servidor esta rodando:")
        print("    TEMA=triagem docker compose up --build mundo")
        return False
    except requests.exceptions.Timeout:
        print(f"  X Timeout ao conectar em {SERVIDOR_URL}")
        return False
    except Exception as e:
        print(f"  OK Servidor MCP respondeu (erro esperado: {type(e).__name__})")
        return True


def testar_inicializacao_mcp():
    """Testa inicialização da sessão MCP."""
    print("\n3. Testando inicializacao MCP...")
    
    try:
        servidor.inicializar_sessao()
        # notificar_inicializado pode retornar 202, o que é normal
        try:
            servidor.notificar_inicializado()
        except:
            pass  # Erro 202 é esperado
        print("  OK Sessao MCP inicializada com sucesso")
        return True
    except Exception as e:
        print(f"  X Erro ao inicializar: {e}")
        return False


def testar_ia():
    """Testa conexão com LiteLLM."""
    print("\n4. Testando LiteLLM API...")
    
    try:
        import requests
        
        litellm_base = os.getenv("LITELLM_API_BASE")
        litellm_key = os.getenv("LITELLM_API_KEY")
        
        if not litellm_base or not litellm_key:
            print("  X LITELLM_API_BASE ou LITELLM_API_KEY nao configurados")
            return False
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Responda com OK"}],
            "temperature": 0.0,
            "max_tokens": 10
        }
        
        resposta = requests.post(
            litellm_base,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {litellm_key}"
            },
            timeout=10
        )
        
        if resposta.status_code == 200:
            dados = resposta.json()
            conteudo = dados["choices"][0]["message"]["content"]
            print(f"  OK LiteLLM respondeu: {conteudo}")
            return True
        else:
            print(f"  X LiteLLM retornou {resposta.status_code}: {resposta.text[:100]}")
            return False
    except Exception as e:
        print(f"  X Erro ao conectar com LiteLLM: {e}")
        return False


def testar_pagina_ferias():
    """Testa se a página de férias está acessível."""
    print("\n5. Testando pagina de ferias...")
    
    try:
        resposta = requests.get(f"{SERVIDOR_PAINEL}/legado/ferias", timeout=5)
        if resposta.status_code == 200:
            print("  OK Pagina de ferias acessivel")
            return True
        else:
            print(f"  X Pagina retornou {resposta.status_code}")
            return False
    except Exception as e:
        print(f"  X Erro ao acessar pagina: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTE DE CONEXAO - Hackathon UNIFEI 2026 - Triagem N1")
    print("=" * 60)
    
    testes = [
        ("Arquivo .env", testar_env),
        ("Servidor MCP", testar_servidor_mcp),
        ("Inicializacao MCP", testar_inicializacao_mcp),
        ("LiteLLM API", testar_ia),
        ("Pagina de ferias", testar_pagina_ferias),
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
    
    if passou == total:
        print("\nOK Tudo pronto! Execute: python agente.py")
        return 0
    else:
        print("\nX Corrija os erros acima antes de continuar")
        return 1


if __name__ == "__main__":
    sys.exit(main())
