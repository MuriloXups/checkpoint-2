import os
import json
import subprocess
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState

# Inicializa o modelo GPT-4o-mini
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Nó 1: Agente Coder (Daniel)
def agente_coder(state: AgentState) -> dict:
    enunciado = state["enunciado"]
    feedback = state.get("feedback_critic")
    iteracao = state["iteracao_atual"]
    
    if iteracao == 0:
        prompt = ChatPromptTemplate.from_template(
            "Você é um programador Python especialista. Resolva o seguinte problema:\n{enunciado}\n"
            "Retorne APENAS o código Python limpo, sem markdown block (```)."
        )
        inputs = {"enunciado": enunciado}
    else:
        prompt = ChatPromptTemplate.from_template(
            "Seu código anterior precisa de correções baseadas no feedback abaixo:\n"
            "Feedback: {feedback}\n"
            "Reescreva a solução corrigindo os erros apontados.\n"
            "Retorne APENAS o código Python limpo, sem markdown block (
```)."
        )
        inputs = {"feedback": json.dumps(feedback)}
        
    chain = prompt | llm
    resposta = chain.invoke(inputs).content
    
    historico = state.get("historico_revisoes", [])
    historico.append(resposta)
    
    return {
        "codigo_atual": resposta,
        "iteracao_atual": iteracao + 1,
        "historico_revisoes": historico
    }

# Nó 2: Agente Critic (Rafael)
def agente_critic(state: AgentState) -> dict:
    codigo = state["codigo_atual"]
    
    # Salva temporariamente o código gerado pelo LLM para análise estática/dinâmica
    with open("temp_solucao.py", "w", encoding="utf-8") as f:
        f.write(codigo)
        
    # Exemplo estruturado de análise (Em S2/S3 deve encapsular chamadas de subprocess para pylint/pytest)
    feedback = {"pylint": "Aprovado", "bandit": "Nenhuma vulnerabilidade", "pytest": "Passou"}
    aprovado = True
    
    # Simulação de falha no primeiro ciclo para demonstrar o funcionamento do loop reflexivo
    if state["iteracao_atual"] == 1:
        feedback["pylint"] = "Erro C0114: Missing module docstring"
        feedback["pytest"] = "Falhou no caso de teste 2 (números negativos)"
        aprovado = False

    return {
        "feedback_critic": feedback,
        "aprovado":渊aprovado
    }

# Aresta Condicional (David)
def checar_proximo_passo(state: AgentState):
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
        "corrigir": "Coder"
    }
)

app = workflow.compile()
