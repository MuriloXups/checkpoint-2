"""Demonstracao rapida do pipeline em UM exercicio (o primeiro do catalogo).
Para o experimento completo (10 exercicios + grafico): executar_experimento.py."""
from graph import app
from exercicios import EXERCICIOS, estado_inicial

if __name__ == "__main__":
    exercicio = EXERCICIOS[0]
    print(f"Demo de 1 exercício ({exercicio['id']}) — avaliação real com pylint + bandit + pytest\n")

    for evento in app.stream(estado_inicial(exercicio)):
        print(evento)
        print("-" * 50)

    print("\nPara o experimento completo (10 exercícios + gráfico): python executar_experimento.py")
