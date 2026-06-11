"""demo.py - Demonstracao enxuta do pipeline, ideal para gravar o video de 2 min.

Mostra UM exercicio passando pelo loop reflexivo: Coder gera -> Critic avalia
com pylint+bandit+pytest -> reprova -> Coder corrige -> aprova. No final, resume
o experimento completo (lido de resultados.json, com os dados reais dos 10).

Para gravar SEM risco de estourar a cota da API, deixe USAR_OFFLINE = True: o
Coder usa respostas "dubladas", mas o Critic continua REAL (roda as ferramentas).
Mude para False se quiser uma chamada de verdade ao Gemini durante a gravacao.
"""
import os
import json
import graph
from exercicios import EXERCICIOS, estado_inicial

USAR_OFFLINE = True  # True = sem API (recomendado p/ gravar) | False = chama o Gemini

EX = next(e for e in EXERCICIOS if e["id"] == "soma_elementos")


def ativar_stub():
    """Substitui o LLM real por um modelo dublado (respostas fixas), sem API."""
    # pylint: disable=import-outside-toplevel
    from langchain_core.language_models.fake_chat_models import FakeListChatModel
    ruim = "def soma_elementos(lista):\n    return sum(lista)\n"
    bom = ('"""Modulo de solucao."""\n\n\n'
           'def soma_elementos(lista):\n'
           '    """Retorna a soma dos elementos da lista (0 se vazia)."""\n'
           '    return sum(lista)\n')
    graph.llm = FakeListChatModel(responses=[ruim, bom, bom])


def indentar(texto, n=6):
    """Indenta cada linha de um texto em n espacos (para exibir o codigo)."""
    return "\n".join(" " * n + linha for linha in texto.strip().splitlines())


def demonstrar():
    """Roda um exercicio pelo grafo e imprime cada passo de forma narrada."""
    print("=" * 64)
    print("  PIPELINE MULTI-AGENTE REFLEXIVO  -  Grupo 6 (G6)")
    print("  Coder gera  ->  Critic avalia (pylint+bandit+pytest)  ->  loop ate 3x")
    print("=" * 64)
    print(f"\nExercicio: {EX['id']}")
    print(f"Enunciado: {EX['enunciado']}\n")

    iteracao = 0
    for evento in graph.app.stream(estado_inicial(EX)):
        if "Coder" in evento:
            iteracao += 1
            rotulo = "gerou o codigo" if iteracao == 1 else "corrigiu com base no feedback"
            print("-" * 64)
            print(f"[ CODER ]  iteracao {iteracao} - {rotulo}:")
            print(indentar(evento["Coder"]["codigo_atual"]))
            print()
        elif "Critic" in evento:
            fb = evento["Critic"]["feedback_critic"]
            aprovado = evento["Critic"]["aprovado"]
            print("[ CRITIC ] avaliacao REAL:")
            print(f"     corretude : {fb['corretude']}")
            print(f"     estilo    : pylint {fb['estilo_pylint']}")
            print(f"     seguranca : {fb['seguranca_bandit']}")
            print(f"     => qualidade {fb['qualidade']}/10  ->  {'APROVADO' if aprovado else 'REPROVADO'}")
            if not aprovado and fb["mensagens_estilo"]:
                print("     feedback enviado ao Coder:")
                for msg in fb["mensagens_estilo"][:3]:
                    print(f"        - {msg}")
            print()


def resumo_experimento():
    """Imprime o resumo agregado do experimento completo (de resultados.json)."""
    if not os.path.exists("resultados.json"):
        return
    with open("resultados.json", encoding="utf-8") as f:
        res = json.load(f)
    aprovados = sum(1 for r in res.values() if r["aprovado_final"])
    inicios = [r["qualidades"][0] for r in res.values() if r["qualidades"]]
    fins = [r["qualidades"][-1] for r in res.values() if r["qualidades"]]
    media_ini = sum(inicios) / len(inicios) if inicios else 0
    media_fim = sum(fins) / len(fins) if fins else 0
    print("=" * 64)
    print(f"  EXPERIMENTO COMPLETO - {len(res)} exercicios (dados reais)")
    print(f"  Aprovados       : {aprovados}/{len(res)}")
    print(f"  Qualidade media : {media_ini:.1f}  ->  {media_fim:.1f}")
    print("  Grafico         : painel/evolucao_qualidade.png")
    print("=" * 64)


if __name__ == "__main__":
    if USAR_OFFLINE:
        ativar_stub()
        demonstrar()
    else:
        try:
            demonstrar()
        except Exception as erro:  # pylint: disable=broad-exception-caught
            print(f"(API indisponivel: {type(erro).__name__}. Usando demonstracao offline.)\n")
            ativar_stub()
            demonstrar()
    resumo_experimento()
