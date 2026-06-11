"""Grafo multi-agente em LangGraph: o no Coder gera o codigo, o no Critic o avalia
com pylint+bandit+pytest, e uma aresta condicional repete o ciclo ate o codigo ser
aprovado ou atingir 3 iteracoes (padrao reflexivo / Reflexion)."""
import os
import json
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
import ferramentas_critic as fc

# Carrega variaveis de um arquivo .env (se existir), para voce nao precisar
# redigitar LLM_PROVIDER / chaves a cada terminal novo. Se a lib python-dotenv
# nao estiver instalada, o codigo segue usando as variaveis do sistema.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Escolha do provedor de LLM pela variavel de ambiente LLM_PROVIDER:
#   - "gemini" (padrao deste projeto) -> Gemini Flash | precisa de GOOGLE_API_KEY
#   - "openai"                        -> GPT-4o-mini   | precisa de OPENAI_API_KEY
PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

if PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
else:
    from langchain_google_genai import ChatGoogleGenerativeAI
    # Modelo configuravel via GEMINI_MODEL no .env. gemini-2.0-flash foi desligado
    # em 01/06/2026; o padrao usa um modelo atual do free tier.
    modelo_gemini = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(model=modelo_gemini, temperature=0)

# Pasta isolada onde o codigo gerado e os testes sao escritos e executados.
SANDBOX = "_sandbox"


def agente_coder(state: AgentState) -> dict:
    """No Coder: gera o codigo na 1a iteracao ou o corrige com base no feedback."""
    enunciado = state["enunciado"]
    nome_funcao = state["nome_funcao"]
    iteracao = state["iteracao_atual"]

    if iteracao == 0:
        prompt = ChatPromptTemplate.from_template(
            "Você é um programador Python especialista. Resolva o problema abaixo.\n"
            "Problema: {enunciado}\n"
            "A função DEVE se chamar EXATAMENTE '{nome_funcao}'.\n"
            "Não inclua exemplos de uso, prints, input() nem texto explicativo.\n"
            "Retorne APENAS o código Python, sem blocos markdown (```)."
        )
        inputs = {"enunciado": enunciado, "nome_funcao": nome_funcao}
    else:
        prompt = ChatPromptTemplate.from_template(
            "Você é um programador Python. Seu código foi REPROVADO pelo revisor automático.\n"
            "Código atual:\n{codigo}\n\n"
            "Feedback do revisor (JSON): {feedback}\n\n"
            "Reescreva a função '{nome_funcao}' corrigindo TODOS os pontos: faça os testes passarem, "
            "adicione docstring de módulo e de função e siga a PEP 8 para elevar a nota do pylint.\n"
            "Retorne APENAS o código Python, sem blocos markdown (```)."
        )
        inputs = {
            "codigo": state["codigo_atual"],
            "feedback": json.dumps(state.get("feedback_critic"), ensure_ascii=False),
            "nome_funcao": nome_funcao,
        }

    chain = prompt | llm
    resposta = fc.limpar_codigo(chain.invoke(inputs).content)

    historico = state.get("historico_revisoes", [])
    historico.append(resposta)

    return {
        "codigo_atual": resposta,
        "iteracao_atual": iteracao + 1,
        "historico_revisoes": historico,
    }


def agente_critic(state: AgentState) -> dict:
    """No Critic: avalia o codigo com pylint+bandit+pytest e decide se aprova."""
    codigo = state["codigo_atual"]
    nome_funcao = state["nome_funcao"]
    casos = state["casos_teste"]

    # Escreve a solucao e a suite de testes na sandbox isolada
    os.makedirs(SANDBOX, exist_ok=True)
    with open(os.path.join(SANDBOX, "solucao.py"), "w", encoding="utf-8") as f:
        f.write(codigo)
    with open(os.path.join(SANDBOX, "test_solucao.py"), "w", encoding="utf-8") as f:
        f.write(fc.gerar_arquivo_teste(nome_funcao, casos))

    # Roda as 3 ferramentas de verdade
    pylint = fc.rodar_pylint("solucao.py", SANDBOX)
    bandit = fc.rodar_bandit("solucao.py", SANDBOX)
    teste = fc.rodar_pytest("test_solucao.py", len(casos), SANDBOX)

    qualidade = fc.calcular_qualidade(teste["passou"], teste["total"], pylint["score"], bandit["qtd_issues"])
    aprovado = fc.aprovado_em(teste["passou"], teste["total"], pylint["score"], bandit["qtd_issues"])

    feedback = {
        "corretude": f"{teste['passou']}/{teste['total']} testes passaram",
        "estilo_pylint": f"{pylint['score']}/10 (minimo exigido: {fc.LIMIAR_PYLINT})",
        "mensagens_estilo": pylint["mensagens"],
        "seguranca_bandit": "OK" if bandit["qtd_issues"] == 0 else f"{bandit['qtd_issues']} problema(s)",
        "detalhes_seguranca": bandit["detalhes"],
        "saida_pytest": teste["saida"],
        "qualidade": qualidade,
    }

    return {"feedback_critic": feedback, "aprovado": aprovado}


def checar_proximo_passo(state: AgentState):
    """Aresta condicional: finaliza se aprovado ou apos 3 iteracoes; senao corrige."""
    if state["aprovado"] or state["iteracao_atual"] >= 3:
        return "finalizar"
    return "corrigir"


# Montagem do Grafo
workflow = StateGraph(AgentState)

workflow.add_node("Coder", agente_coder)
workflow.add_node("Critic", agente_critic)

workflow.set_entry_point("Coder")
workflow.add_edge("Coder", "Critic")

workflow.add_conditional_edges(
    "Critic",
    checar_proximo_passo,
    {
        "finalizar": END,
        "corrigir": "Coder",
    },
)

app = workflow.compile()
