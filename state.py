"""Estado compartilhado do grafo multi-agente (AgentState)."""
from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    """Ficha de estado que circula entre os nos Coder e Critic do grafo."""

    # Enunciado do exercicio que o Coder deve resolver
    enunciado: str
    # Codigo Python mais recente gerado pelo Coder
    codigo_atual: str
    # Feedback estruturado (JSON) devolvido pelo Critic
    feedback_critic: Optional[dict]
    # Todas as versoes de codigo ja geradas (1 por iteracao)
    historico_revisoes: List[str]
    # Numero da iteracao atual (0, 1, 2, ...)
    iteracao_atual: int
    # O Critic aprovou o codigo?
    aprovado: bool

    # --- Campos do experimento (10 exercicios + avaliacao real) ---
    # Identificador curto do exercicio (ex.: "soma_elementos")
    exercicio_id: str
    # Nome EXATO que a funcao gerada deve ter (usado pelos testes)
    nome_funcao: str
    # Casos de teste: lista de tuplas (args, resultado_esperado)
    casos_teste: list
