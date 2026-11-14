# Operador de tela: preenche formulário de férias com Playwright

from playwright.sync_api import sync_playwright
from config import SERVIDOR_PAINEL


def lancar_ferias(email, data_inicio, data_fim, evento_id, motivo):
    """Lança férias no sistema legado usando Playwright.
    
    Argumentos:
    - email: e-mail do colaborador
    - data_inicio: data no formato DD/MM/AAAA
    - data_fim: data no formato DD/MM/AAAA
    - evento_id: ID do evento (para ligar a ação)
    - motivo: motivo da ação
    
    Retorna:
    - {"status": "ok", "protocolo": "FER-..."} se sucesso
    - {"status": "erro", "mensagem": "..."} se erro
    """
    
    url_ferias = f"{SERVIDOR_PAINEL}/legado/ferias"
    
    try:
        with sync_playwright() as p:
            # Abrir navegador
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navegar para a página
            page.goto(url_ferias, wait_until="networkidle")
            
            # Preencher formulário
            # Campo: name="agente"
            page.fill('input[name="agente"]', "operador-de-tela")
            
            # Campo: name="email"
            page.fill('input[name="email"]', email)
            
            # Campo: name="inicio" (DD/MM/AAAA)
            page.fill('input[name="inicio"]', data_inicio)
            
            # Campo: name="fim" (DD/MM/AAAA)
            page.fill('input[name="fim"]', data_fim)
            
            # Campo: name="evento" (evento_id)
            page.fill('input[name="evento"]', evento_id)
            
            # Clicar em submit
            page.click('button[type="submit"]')
            
            # Aguardar resposta
            page.wait_for_load_state("networkidle")
            
            # Ler conteúdo da página
            conteudo = page.content()
            
            # Fechar navegador
            browser.close()
            
            # Verificar sucesso
            if "Férias lançadas" in conteudo or "FER-" in conteudo:
                # Extrair protocolo
                protocolo = extrair_protocolo(conteudo)
                return {
                    "status": "ok",
                    "protocolo": protocolo,
                    "mensagem": f"Férias lançadas com sucesso: {protocolo}"
                }
            else:
                # Extrair erros
                erros = extrair_erros(conteudo)
                return {
                    "status": "erro",
                    "mensagem": f"Erro ao lançar férias: {erros}"
                }
    
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao acessar página de férias: {str(e)}"
        }


def extrair_protocolo(conteudo_html):
    """Extrai o número do protocolo FER-... do HTML."""
    import re
    match = re.search(r'FER-\d+', conteudo_html)
    if match:
        return match.group(0)
    return "FER-DESCONHECIDO"


def extrair_erros(conteudo_html):
    """Extrai mensagens de erro do HTML."""
    import re
    # Procurar por divs com classe "error" ou "alert"
    erros = re.findall(r'<div[^>]*class="[^"]*error[^"]*"[^>]*>([^<]+)</div>', conteudo_html)
    if not erros:
        erros = re.findall(r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>([^<]+)</div>', conteudo_html)
    
    if erros:
        return "; ".join(erros)
    return "Erro desconhecido"
