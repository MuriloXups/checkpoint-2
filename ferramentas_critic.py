"""
Ferramentas do agente Critic.

Aqui mora o nucleo que torna a avaliacao REAL (e nao simulada): wrappers que
executam pylint (estilo/PEP 8), bandit (seguranca) e pytest (corretude) sobre o
codigo gerado pelo Coder, e devolvem o resultado estruturado. Assim a qualidade
do codigo passa a ser MEDIDA a cada iteracao, em vez de inventada.
"""
import re
import sys
import json
import subprocess

# Nota minima do pylint (0-10) para o codigo ser considerado aprovado no quesito estilo.
LIMIAR_PYLINT = 8.0
# Tempo maximo (s) por ferramenta, evita travar se o codigo gerado tiver input()/laco infinito.
TIMEOUT = 60


def _rodar(args, cwd):
    """Executa um comando capturando a saida, sem levantar excecao em caso de erro."""
    try:
        proc = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=TIMEOUT, check=False,
        )
        return (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return "TIMEOUT: a ferramenta demorou demais (possivel laco infinito ou input())."


def limpar_codigo(codigo: str) -> str:
    """Remove cercas markdown (```python ... ```) que o LLM as vezes inclui mesmo sendo proibido."""
    txt = codigo.strip()
    if txt.startswith("```"):
        linhas = txt.splitlines()
        if linhas and linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip().startswith("```"):
            linhas = linhas[:-1]
        txt = "\n".join(linhas)
    return txt.strip() + "\n"


def gerar_arquivo_teste(nome_funcao: str, casos_teste: list) -> str:
    """Gera o conteudo de um arquivo pytest que importa a funcao e checa cada caso."""
    return (
        "import pytest\n"
        f"from solucao import {nome_funcao}\n\n"
        f"CASOS = {casos_teste!r}\n\n"
        '@pytest.mark.parametrize("args,esperado", CASOS)\n'
        f"def test_{nome_funcao}(args, esperado):\n"
        f"    assert {nome_funcao}(*args) == esperado\n"
    )


def rodar_pylint(arquivo: str, cwd: str) -> dict:
    """Roda o pylint e extrai a nota (0-10) e as principais mensagens."""
    saida = _rodar([sys.executable, "-m", "pylint", arquivo, "--score=y"], cwd)
    m = re.search(r"rated at (-?\d+\.\d+)/10", saida)
    score = float(m.group(1)) if m else 0.0
    mensagens = re.findall(r"^.*:\d+:\d+: [A-Z]\d+:.*$", saida, flags=re.MULTILINE)
    return {"score": round(score, 2), "mensagens": mensagens[:8]}


def rodar_bandit(arquivo: str, cwd: str) -> dict:
    """Roda o bandit e conta as vulnerabilidades encontradas."""
    saida = _rodar([sys.executable, "-m", "bandit", "-f", "json", "-q", arquivo], cwd)
    try:
        resultados = json.loads(saida).get("results", [])
    except (json.JSONDecodeError, ValueError):
        resultados = []
    detalhes = [
        {"severidade": r.get("issue_severity"), "problema": r.get("issue_text"), "id": r.get("test_id")}
        for r in resultados
    ]
    return {"qtd_issues": len(resultados), "detalhes": detalhes[:5]}


def rodar_pytest(arquivo_teste: str, total_casos: int, cwd: str) -> dict:
    """Roda o pytest e conta quantos casos passaram."""
    saida = _rodar(
        [sys.executable, "-m", "pytest", arquivo_teste, "-q", "--tb=line", "--no-header", "-p", "no:cacheprovider"],
        cwd,
    )
    m_pass = re.search(r"(\d+) passed", saida)
    passou = int(m_pass.group(1)) if m_pass else 0
    return {"passou": passou, "total": total_casos, "saida": saida.strip()[-600:]}


def calcular_qualidade(passou: int, total: int, pylint_score: float, bandit_issues: int) -> float:
    """Combina corretude (50%), estilo (40%) e seguranca (10%) numa nota 0-10."""
    corretude = (passou / total * 10) if total else 0.0
    estilo = max(0.0, min(10.0, pylint_score))
    seguranca = 10.0 if bandit_issues == 0 else max(0.0, 10.0 - 3.0 * bandit_issues)
    return round(0.5 * corretude + 0.4 * estilo + 0.1 * seguranca, 2)


def aprovado_em(passou: int, total: int, pylint_score: float, bandit_issues: int) -> bool:
    """Aprova so se TODOS os testes passam, o estilo atinge o limiar e nao ha falha de seguranca."""
    return passou == total and pylint_score >= LIMIAR_PYLINT and bandit_issues == 0
