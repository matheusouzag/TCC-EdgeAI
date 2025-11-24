# Aplicação RGB - Simulação de Motor e LEDs

Este repositório contém o código responsável pela aplicação RGB desktop do projeto, cujo objetivo foi integrar interpretação de comandos naturais, consulta via RAG, controle de LEDs RGB, ajuste de velocidade de motor e uma interface gráfica interativa, simulando o comportamento esperado no ambiente físico (Raspberry Pi).

---

## Tecnologias Fundamentais

- **RAG (Retrieval-Augmented Generation)**
- **LangChain**
- **ChromaDB**
- **HuggingFace**
- **Ollama (para modelos locais)**
- **PyPDFLoader**
- **Tkinter**
- **Python**

---

## Objetivo Geral do Sistema

O sistema interpreta comandos naturais como:

- “Acenda o LED 2 de azul claro”  
- “Aumente a velocidade do motor”  

E executa automaticamente:

- Busca via RAG da cor solicitada  
- Parsing rigoroso de JSON  
- Controle visual de LEDs  
- Controle de velocidade do motor  
- Explicações no painel gráfico  

---

# Estrutura Geral do Pipeline

## Configuração de Parâmetros

A classe `Config` define:

- **Embedding**
- **Modelo de Linguagem** 
- **Chunking**
- **Temperatura** 
- **Pasta do banco vetorial**
- **PDF base** 

---

## Limpeza e Processamento dos Documentos

O carregamento utiliza `PyPDFLoader`.

A função `clean_Memoriaspost()`:

- Remove cabeçalhos, numerações e ruídos  
- Normaliza padrões  
- Prepara texto para embeddings  

---

## Banco Vetorial e Recuperação

Usa:

- **ChromaDB**  
- Similaridade por **cosine**  
- Busca com **MMR**

Parâmetros principais:

- `k = 9`
- `lambda_mult = 0.45`
- `score_threshold = 0.5`

---

## Cadeias e Prompts

### Prompt principal de cores (LED)
- Sempre retorna JSON
- Interpreta número do LED e a cor
- RAG fornece RGB exato

### Prompt para motor
- Regras explicitas para aumentar/diminuir velocidade
- Retorna objeto JSON

### Prompt de intenção

A classificação de intenção do usuário é feita para determinar qual subsistema deve ser ativado:

- `led` → comandos relacionados a LEDs  
- `motor` → comandos relacionados ao motor  
- `led_motor` → comandos mistos  
- `nenhum` → quando o texto não tem relação com o sistema  

Essa etapa garante que cada prompt especializado receba apenas instruções coerentes e evita interpretações erradas pelo modelo.

---

## Interface Tkinter

A interface gráfica foi desenvolvida para simular o comportamento do sistema embarcado, oferecendo:

- **Três LEDs RGB simulados**, atualizados dinamicamente conforme o JSON retornado pela IA  
- **Simulação de motor**, com indicador gráfico de rotação  
- **Campo de entrada**, local para digitar 
- **Painel de logs e explicações** fornecidas pelo modelo  
- **Thread dedicada para animação** do motor, evitando travamentos na interface  

## Como Executar

1. Instale as dependências, por meio do requirements-desktop.txt 

2. Instale e configure o Ollama.

3. Com o Ollama devidamente configurado, adicione os modelos como o llama3.2:3b por este comando:

`ollama pull llama3.2:3b`

---

## Referências

- LangChain – Documentação dos parâmetros: https://api.python.langchain.com/en/latest/vectorstores/langchain_core.vectorstores.base.VectorStore.html
- LangChain – Documentação geral: https://python.langchain.com/docs/
- ChromaDB – Documentação oficial: https://docs.trychroma.com/
- Ollama (Documentação oficial): https://ollama.com/library
- PyPDFLoader (LangChain): https://python.langchain.com/docs/integrations/document_loaders/pdf

