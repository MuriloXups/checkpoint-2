"""
Teste de fumaca OFFLINE - valida o pipeline SEM chamar a API do LLM.

Troca o modelo real por um modelo "dublado" (fake) com respostas pre-definidas,
mas mantem o Critic REAL rodando pylint + bandit + pytest. Assim voce confirma,
de graca e sem chave, que:
  1) o loop reflexivo funciona (reprova -> corrige -> aprova);
  2) a avaliacao e de verdade (a nota de qualidade sobe quando o codigo melhora).

Como rodar (com o ambiente virtual ativado):
    python smoke_test_offline.py
"""
# Os imports vem depois de configurar as variaveis de ambiente, de proposito:
# pylint: disable=wrong-import-position,wrong-import-order
import os

# Forca o provedor OpenAI so para CONSTRUIR o objeto do modelo com uma chave
# falsa. O modelo nunca e chamado (sera substituido pelo fake abaixo).
os.environ["LLM_PROVIDER"] = "openai"
os.environ.setdefault("OPENAI_API_KEY", "sk-chave-falsa-apenas-para-teste-offline")

import graph
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from exercicios import EXERCICIOS, estado_inicial

EX = EXERCICIOS[0]  # soma_elementos

# 1a resposta do Coder: SEM docstring  -> pylint reprova (nota baixa)
CODIGO_RUIM = "def soma_elementos(lista):\n    return sum(lista)\n"
# 2a resposta do Coder: COM docstrings -> pylint aprova
CODIGO_BOM = ('"""Modulo de solucao."""\n\n\n'
              'def soma_elementos(lista):\n'
              '    """Retorna a soma dos elementos da lista (0 se vazia)."""\n'
              '    return sum(lista)\n')

graph.llm = FakeListChatModel(responses=[CODIGO_RUIM, CODIGO_BOM, CODIGO_BOM])

print(f"== Pipeline OFFLINE no exercício '{EX['id']}' (Critic real: pylint+bandit+pytest) ==\n")

qualidades = []
for evento in graph.app.stream(estado_inicial(EX)):
    dados = evento.get("Critic")
    if dados:
        fb = dados["feedback_critic"]
        qualidades.append(fb["qualidade"])
        print(f"  iteração {len(qualidades)}: qualidade={fb['qualidade']} | {fb['corretude']} | "
              f"pylint {fb['estilo_pylint']} | bandit {fb['seguranca_bandit']} | aprovado={dados['aprovado']}")

assert len(qualidades) >= 2, "deveria iterar pelo menos 2x (reprovar e depois aprovar)"
assert qualidades[-1] > qualidades[0], "a qualidade deveria SUBIR após a correção"

print("\nOK! Loop reflexivo + avaliação real validados:")
print(f"   qualidade evoluiu de {qualidades[0]} para {qualidades[-1]} (medida por ferramentas de verdade).")
