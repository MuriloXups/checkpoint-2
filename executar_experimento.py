"""Experimento completo do G6: roda os 10 exercicios pelo pipeline multi-agente,
coleta a qualidade de cada iteracao e gera o grafico de evolucao.

Resiliente: salva o progresso a cada exercicio em resultados.json. Se a API
falhar (ex.: cota esgotada), o que ja rodou fica salvo e o grafico e gerado
mesmo assim. Basta rodar de novo para CONTINUAR de onde parou (pula os ja feitos).

Uso (com o ambiente virtual ativado e a chave no .env):
    python executar_experimento.py
"""
import os
import json
from graph import app
from exercicios import EXERCICIOS, estado_inicial
from relatorio import imprimir_resumo, gerar_grafico

ARQUIVO_RESULTADOS = "resultados.json"


def carregar_resultados() -> dict:
    """Le os resultados ja salvos, para permitir retomar de onde parou."""
    if os.path.exists(ARQUIVO_RESULTADOS):
        try:
            with open(ARQUIVO_RESULTADOS, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def salvar_resultados(resultados: dict) -> None:
    """Grava os resultados em disco (salvamento incremental)."""
    with open(ARQUIVO_RESULTADOS, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)


def rodar_exercicio(ex: dict) -> dict:
    """Roda um exercicio pelo grafo e coleta a qualidade de cada iteracao."""
    print(f"\n=== Exercício: {ex['id']} ===")
    qualidades, aprovados = [], []
    for evento in app.stream(estado_inicial(ex)):
        dados = evento.get("Critic")
        if dados:  # so o no Critic produz avaliacao
            fb = dados["feedback_critic"]
            qualidades.append(fb["qualidade"])
            aprovados.append(dados["aprovado"])
            print(f"  iteração {len(qualidades)}: qualidade={fb['qualidade']:<5} | "
                  f"{fb['corretude']} | pylint {fb['estilo_pylint']} | "
                  f"bandit {fb['seguranca_bandit']} | aprovado={dados['aprovado']}")
    return {
        "qualidades": qualidades,
        "iteracoes": len(qualidades),
        "aprovado_final": bool(aprovados and aprovados[-1]),
    }


def _eh_erro_de_cota(erro: Exception) -> bool:
    """Indica se o erro foi de cota/limite de requisicoes da API."""
    txt = str(erro).lower()
    return "resource_exhausted" in txt or "429" in txt or "rate limit" in txt


def main() -> None:
    """Roda (ou retoma) o experimento completo e gera o resumo + o grafico."""
    resultados = carregar_resultados()
    pendentes = [ex for ex in EXERCICIOS if ex["id"] not in resultados]

    if resultados:
        print(f"Retomando: {len(resultados)} já concluído(s), {len(pendentes)} pendente(s).")
    else:
        print("Iniciando experimento com os 10 exercícios...")

    interrompido = None
    try:
        for ex in pendentes:
            try:
                resultados[ex["id"]] = rodar_exercicio(ex)
                salvar_resultados(resultados)  # nunca perde progresso
            except Exception as erro:  # pylint: disable=broad-exception-caught
                interrompido = erro
                if _eh_erro_de_cota(erro):
                    print(f"\n[!] Cota da API esgotada ao rodar '{ex['id']}'.")
                    print("    O progresso já está salvo. Rode o script de novo mais tarde")
                    print("    para CONTINUAR de onde parou (ele pula os exercícios já feitos).")
                else:
                    print(f"\n[!] Erro em '{ex['id']}': {type(erro).__name__}: {str(erro)[:200]}")
                break
    except KeyboardInterrupt:
        interrompido = "Ctrl+C"
        print("\n[!] Interrompido manualmente (Ctrl+C). O progresso já está salvo;")
        print("    rode o script de novo para continuar de onde parou.")

    if resultados:
        imprimir_resumo(resultados)
        gerar_grafico(resultados)
        salvar_resultados(resultados)
        print(f"\nDados brutos salvos em: {ARQUIVO_RESULTADOS}")

    total = len(EXERCICIOS)
    estado = "PARCIAL" if (interrompido or len(resultados) < total) else "COMPLETO"
    print(f"\nExperimento {estado}: {len(resultados)}/{total} exercícios concluídos.")


if __name__ == "__main__":
    main()
