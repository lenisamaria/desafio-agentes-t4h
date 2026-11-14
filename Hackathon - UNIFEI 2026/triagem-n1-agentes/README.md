# Time de Agentes - Triagem N1 (Hackathon UNIFEI 2026)

Um time de agentes de IA que trabalha sozinho para triagem de chamados e incidentes em uma empresa fictícia.

## Arquitetura

- **Triador**: Recebe cada evento e decide as ações com tool calling
- **Revisor**: Valida cada ação antes de executar
- **Operador de Tela**: Preenche formulários que não têm API (como férias)

## Como rodar

### 1. Preparar o ambiente

```bash
# Clonar ou entrar na pasta do projeto
cd "Hackathon - UNIFEI 2026/triagem-n1-agentes"

# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (macOS/Linux)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Playwright (para automação de telas)
playwright install chromium
```

### 2. Configurar .env

```bash
# Copiar arquivo de exemplo
cp .env.exemplo .env

# Editar .env e preencher OPENAI_API_KEY
# OPENAI_API_KEY=sk-...
```

### 3. Subir o servidor MCP

Em outro terminal:

```bash
cd "Hackathon - UNIFEI 2026/Servidor MCP (Compartilhado)"

# Com Docker
TEMA=triagem docker compose up --build mundo

# Ou sem Docker (Python 3.11+)
python mundo.py --tema triagem
```

Verifique o painel em: http://localhost:8765

### 4. Testar conexão

```bash
python testar_conexao.py
```

Deve passar em todos os 5 testes.

### 5. Rodar o time de agentes

```bash
python agente.py
```

O programa vai:
1. Conectar ao servidor MCP
2. Entrar em laço: pegar próximo evento, analisar, agir
3. Mostrar cada ferramenta chamada e o resultado
4. Parar quando o cenário acabar (encerrado=true)

## Arquivos

- `config.py` — Constantes e configuração
- `servidor.py` — Comunicação com MCP via HTTP JSON-RPC 2.0
- `modelo.py` — Integração com OpenAI e conversão de ferramentas
- `revisor.py` — Validação de ações antes de executar
- `ferias.py` — Automação de tela para lançar férias (Playwright)
- `regras.py` — Prompts do triador e revisor
- `agente.py` — Laço principal e loop do triador
- `testar_conexao.py` — Check-up de .env, servidor, IA e página de férias
- `requirements.txt` — Dependências Python
- `.env.exemplo` — Template de variáveis de ambiente
- `.gitignore` — Arquivos a ignorar no Git

## Papel de cada agente

### Triador (agente="triador")

Recebe cada evento e decide as ações:
- Detectar golpes e avisar Segurança
- Responder dúvidas do FAQ
- Registrar pedidos do catálogo
- Criar incidentes para problemas de produto
- Lançar férias
- Escalar para outros times

Sempre com `evento_id` e `motivo` em cada chamada.

### Revisor (agente="revisor")

Valida cada ação antes de executar:
- Verifica se há `evento_id`
- Detecta mensagens para fora de @t4h.exemplo
- Valida campos obrigatórios
- Confere se o tipo de chamado está correto
- Barra problemas graves (golpe tratado como pedido normal, etc)

Responde "OK ..." para passar ou "PROBLEMA: ..." para barrar.

### Operador de Tela (agente="operador-de-tela")

Preenche formulários sem API usando Playwright:
- Sistema de férias: http://localhost:8765/legado/ferias

## Memória

O triador guarda um resumo de cada evento (máximo 40) e usa na próxima análise para não duplicar ações.

## Falhas simuladas

O servidor simula falhas em 15% das chamadas:
- **503**: Indisponível; tente de novo
- **504**: Timeout; em consultas tente de novo; em ações, confira se já foi feita
- **409**: Conflito; tente de novo
- **410**: Cenário acabou; encerre o programa

## Executar o agente

### Passo 1: Subir o servidor MCP (em um terminal)

```powershell
cd "Hackathon - UNIFEI 2026\triagem-n1-agentes"
.\subir-servidor.ps1
```

Escolha a opção (1 = Docker, 2 = Python).

Verifique o painel em: **http://localhost:8765**

### Passo 2: Rodar o agente (em outro terminal)

```powershell
cd "Hackathon - UNIFEI 2026\triagem-n1-agentes"
.\rodar.ps1
```

O agente vai:
1. Conectar ao servidor MCP
2. Carregar catálogo, times e FAQ
3. Entrar em laço: pegar evento → analisar → agir
4. Mostrar cada ferramenta chamada e o resultado
5. Parar quando o cenário acabar

## Teste de cada etapa

Após cada etapa de desenvolvimento, execute:

```bash
python testar_conexao.py    # ETAPA 1
python testar_etapa2.py     # ETAPA 2
python agente.py            # ETAPA 3
```

E verifique o painel em http://localhost:8765 para ver as ações ao vivo.

## Observações

- Nunca altere o servidor MCP
- Todas as decisões vêm do modelo de IA, guiado por prompts com regras gerais
- Nenhuma resposta de evento é hardcoded no código
- O código segue estilo C: funções simples, sem classes, sem async/await
