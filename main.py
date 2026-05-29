from graph import app

if __name__ == "__main__":
    # Exemplo de teste do pipeline funcional requerido pela Sprint 2
    input_inicial = {
        "enunciado": "Escreva uma função 'soma_elementos(lista)' que recebe uma lista e retorna a soma. Retorne 0 se vazia.",
        "codigo_atual": "",
        "feedback_critic": None,
        "historico_revisoes": [],
        "iteracao_atual": 0,
        "aprovado": False
    }
    
    print("Iniciando Execução do Grafo Multi-Agente...")
    for evento in app.stream(input_inicial):
        print(evento)
        print("-" * 40)
