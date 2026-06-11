"""Geracao do relatorio do experimento: tabela-resumo no terminal e o grafico de
evolucao da qualidade por iteracao (entregavel do G6, vai no painel A1)."""
import os
import matplotlib
matplotlib.use("Agg")  # backend sem janela, so salva o arquivo
import matplotlib.pyplot as plt  # pylint: disable=wrong-import-position


def imprimir_resumo(resultados: dict) -> None:
    """Imprime no terminal a tabela-resumo dos resultados do experimento."""
    print("\n==================== RESUMO DO EXPERIMENTO ====================")
    print(f"{'Exercicio':<18}{'Iteracoes':<11}{'Qualidade ini -> fim':<24}{'Aprovado'}")
    print("-" * 62)
    for nome, r in resultados.items():
        q = r["qualidades"]
        ini_fim = f"{q[0]} -> {q[-1]}" if q else "-"
        print(f"{nome:<18}{r['iteracoes']:<11}{ini_fim:<24}{'SIM' if r['aprovado_final'] else 'NAO'}")
    aprovados = sum(1 for r in resultados.values() if r["aprovado_final"])
    print("-" * 62)
    print(f"Aprovados: {aprovados}/{len(resultados)}")


def gerar_grafico(resultados: dict, caminho: str = "painel/evolucao_qualidade.png") -> None:
    """Gera e salva o grafico de evolucao da qualidade por iteracao."""
    # pylint: disable=too-many-locals
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    max_it = max((len(r["qualidades"]) for r in resultados.values()), default=1)
    iteracoes = list(range(1, max_it + 1))

    # ---- Grafico 1: evolucao da qualidade por iteracao ----
    medias = []
    for i in iteracoes:
        vals = [r["qualidades"][i - 1] for r in resultados.values() if len(r["qualidades"]) >= i]
        medias.append(sum(vals) / len(vals) if vals else None)

    for nome, r in resultados.items():
        q = r["qualidades"]
        ax1.plot(range(1, len(q) + 1), q, marker="o", alpha=0.35, linewidth=1, label=nome)
    ax1.plot(iteracoes, medias, marker="s", color="black", linewidth=2.5, label="MÉDIA")
    ax1.set_xticks(iteracoes)
    ax1.set_xlabel("Iteração")
    ax1.set_ylabel("Qualidade (0–10)")
    ax1.set_ylim(0, 10.6)
    ax1.set_title("Evolução da qualidade por iteração")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=7, ncol=2)

    # ---- Grafico 2: iteracoes ate finalizar, por exercicio ----
    nomes = list(resultados.keys())
    its = [resultados[n]["iteracoes"] for n in nomes]
    cores = ["#2e7d32" if resultados[n]["aprovado_final"] else "#c62828" for n in nomes]
    ax2.bar(range(len(nomes)), its, color=cores)
    ax2.set_xticks(range(len(nomes)))
    ax2.set_xticklabels(nomes, rotation=60, ha="right", fontsize=8)
    ax2.set_ylabel("Iterações")
    ax2.set_title("Iterações por exercício (verde = aprovado)")
    ax2.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print(f"\nGráfico salvo em: {caminho}")
