# checkpoint-2
Trabalho douglas 


# Pipeline Multi-Agente Reflexivo para Otimização de Código Python

Este projeto implementa um pipeline multi-agente utilizando a arquitetura de loop reflexivo (padrão Reflexion) para elevar de forma mensurável a qualidade de código Python gerado por LLMs. 

O sistema distribui a tarefa entre dois agentes especializados: um Coder (gerador) e um Critic (avaliador estático e dinâmico), orquestrados via LangGraph.

## Objetivo do Projeto
O objetivo principal é avaliar se um pipeline multi-agente consegue corrigir incorreções, mitigar vulnerabilidades e alinhar o código a padrões de estilo (PEP 8) de forma autônoma, limitando-se a um teto de até 3 iterações por exercício.

---

## Stack Técnica e Dependências

O projeto utiliza as seguintes tecnologias:
* Orquestração: LangGraph (0.2+)
* Modelo de Linguagem: GPT-4o-mini (OpenAI API)
* Qualidade e Estilo: Pylint (PEP 8)
* Segurança: Bandit
* Testes de Corretude: Pytest
* Observabilidade: LangSmith

---

Divisão de Contribuições (Sprint 2)
David (Tech Lead): Implementação da estrutura do grafo no LangGraph, definição das arestas condicionais e gerência de estado.

Daniel (Dev Coder): Engenharia de prompt do agente Coder, integração com a API do GPT-4o-mini e tratamento de saídas.

Rafael (Dev Critic): Integração dos wrappers de execução local para o pylint, bandit e pytest estruturando o retorno em JSON.

Gabriel (QA): Curadoria dos 10 exercícios propostos e escrita da suíte completa de testes automatizados unitários.

Murilo (Design/Comunicação): Estruturação da documentação técnica e organização dos dados preliminares.

---

## Como Instalar e Executar

### 1. Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado em sua máquina.

### 2. Clonar o Repositório
```bash
git clone [https://github.com/](https://github.com/)[SEU-USUARIO]/[NOME-DO-REPO].git
cd [NOME-DO-REPO]



