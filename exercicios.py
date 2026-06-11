"""
Catalogo dos 10 exercicios usados no experimento (entregavel do G6).

Cada exercicio define:
  - id          : identificador curto
  - nome_funcao : nome EXATO que a funcao gerada deve ter (os testes importam por ele)
  - enunciado   : descricao passada ao agente Coder
  - casos_teste : lista de (args, esperado), onde args e a tupla de argumentos
                  posicionais. Ex.: ( ([1, 2, 3],), 6 ) chama soma_elementos([1, 2, 3]).
"""

EXERCICIOS = [
    {
        "id": "soma_elementos",
        "nome_funcao": "soma_elementos",
        "enunciado": "Receba uma lista de numeros e retorne a soma de todos. Retorne 0 se a lista estiver vazia.",
        "casos_teste": [(([],), 0), (([1, 2, 3],), 6), (([-1, 1],), 0), (([10],), 10), (([1, 2, 3, 4, 5],), 15)],
    },
    {
        "id": "fatorial",
        "nome_funcao": "fatorial",
        "enunciado": "Receba um inteiro n >= 0 e retorne o fatorial de n. Considere fatorial(0) = 1.",
        "casos_teste": [((0,), 1), ((1,), 1), ((3,), 6), ((5,), 120), ((6,), 720)],
    },
    {
        "id": "eh_palindromo",
        "nome_funcao": "eh_palindromo",
        "enunciado": ("Receba uma palavra (string em minusculas, sem espacos) e retorne True "
                      "se ela for um palindromo, senao False."),
        "casos_teste": [(("arara",), True), (("python",), False), (("",), True), (("a",), True), (("osso",), True)],
    },
    {
        "id": "eh_primo",
        "nome_funcao": "eh_primo",
        "enunciado": ("Receba um inteiro n e retorne True se n for um numero primo, senao False. "
                      "Numeros menores que 2 nao sao primos."),
        "casos_teste": [((2,), True), ((3,), True), ((4,), False), ((1,), False), ((17,), True), ((20,), False)],
    },
    {
        "id": "fibonacci",
        "nome_funcao": "fibonacci",
        "enunciado": ("Receba um inteiro n >= 0 e retorne o n-esimo numero da sequencia de "
                      "Fibonacci, com fibonacci(0) = 0 e fibonacci(1) = 1."),
        "casos_teste": [((0,), 0), ((1,), 1), ((2,), 1), ((6,), 8), ((10,), 55)],
    },
    {
        "id": "inverter_string",
        "nome_funcao": "inverter_string",
        "enunciado": "Receba uma string e retorne a string invertida.",
        "casos_teste": [(("abc",), "cba"), (("",), ""), (("a",), "a"), (("python",), "nohtyp")],
    },
    {
        "id": "contar_vogais",
        "nome_funcao": "contar_vogais",
        "enunciado": "Receba uma string em minusculas e retorne quantas vogais (a, e, i, o, u) ela contem.",
        "casos_teste": [(("banana",), 3), (("xyz",), 0), (("",), 0), (("aeiou",), 5), (("python",), 1)],
    },
    {
        "id": "maior_elemento",
        "nome_funcao": "maior_elemento",
        "enunciado": "Receba uma lista nao-vazia de numeros e retorne o maior elemento.",
        "casos_teste": [(([3, 1, 2],), 3), (([-5, -2, -9],), -2), (([42],), 42), (([1, 2, 3, 4],), 4)],
    },
    {
        "id": "fizzbuzz",
        "nome_funcao": "fizzbuzz",
        "enunciado": ("Receba um inteiro n e retorne uma lista de strings de 1 ate n. Para multiplos de 3 use 'Fizz', "
                      "para multiplos de 5 use 'Buzz', para multiplos de 3 e 5 use 'FizzBuzz', "
                      "caso contrario use o proprio numero como string."),
        "casos_teste": [
            ((1,), ["1"]),
            ((3,), ["1", "2", "Fizz"]),
            ((5,), ["1", "2", "Fizz", "4", "Buzz"]),
            ((15,), ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8",
                     "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]),
        ],
    },
    {
        "id": "ordenar_lista",
        "nome_funcao": "ordenar_lista",
        "enunciado": ("Receba uma lista de numeros e retorne uma NOVA lista com os numeros "
                      "ordenados em ordem crescente."),
        "casos_teste": [(([3, 1, 2],), [1, 2, 3]), (([],), []), (([5],), [5]), (([9, -1, 4, 4],), [-1, 4, 4, 9])],
    },
]


def estado_inicial(exercicio: dict) -> dict:
    """Monta o estado inicial do grafo para um exercicio do catalogo."""
    return {
        "enunciado": exercicio["enunciado"],
        "codigo_atual": "",
        "feedback_critic": None,
        "historico_revisoes": [],
        "iteracao_atual": 0,
        "aprovado": False,
        "exercicio_id": exercicio["id"],
        "nome_funcao": exercicio["nome_funcao"],
        "casos_teste": exercicio["casos_teste"],
    }
