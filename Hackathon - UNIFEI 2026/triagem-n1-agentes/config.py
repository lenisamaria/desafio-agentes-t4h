# Configurações e constantes do time de agentes

# Servidor MCP
SERVIDOR_URL = "http://localhost:8765/mcp"
SERVIDOR_PAINEL = "http://localhost:8765"
TIMEOUT_SEGUNDOS = 20

# Agentes
AGENTE_TRIADOR = "triador"
AGENTE_REVISOR = "revisor"
AGENTE_OPERADOR_TELA = "operador-de-tela"

# Modelo de IA
MODELO = "gpt-4o-mini"
TEMPERATURA = 0.0

# Limites
MAX_CHAMADAS_MODELO_POR_EVENTO = 15
MAX_EVENTOS_MEMORIA = 40
MAX_TENTATIVAS_FALHA = 3
ESPERAR_SEGUNDOS_PROXIMO_EVENTO = 30

# Tempos de retry para RateLimitError (segundos)
TEMPOS_RETRY_RATE_LIMIT = [5, 15, 30, 60]

# Tempos de retry para 503/409 (segundos)
TEMPOS_RETRY_FALHA = [1, 2, 4]

# Limite de recusas do revisor antes de passar
LIMITE_RECUSAS_REVISOR = 2
