# Teste de Benchmark - RGB e Trânsito

Este repositório contém dois códigos de **benchmark** utilizados para avaliar a performance de diferentes modelos de linguagem (SLMs) e modelos de *embedding* em dois cenários distintos:  
1. **Aplicação RGB** – onde o objetivo é recuperar códigos RGB a partir de um documento técnico.  
2. **Aplicação Trânsito** – onde o modelo responde questões de múltipla escolha com base em materiais educacionais de trânsito.

Ambos os códigos realizam testes automatizados de desempenho e precisão, analisando como cada modelo se comporta com diferentes parâmetros de fragmentação, recuperação e embeddings, os resultados dos benchmarks estão na pasta "Planilhas" deste repositório.

---

## Tecnologias e Ferramentas Utilizadas

- **Python**
- **LangChain**
- **ChromaDB**
- **HuggingFace**
- **Ollama**
- **PyPDFLoader**
- **Benchmark automatizado com psutil**

---

## Estrutura Geral dos Códigos

### Configuração de Parâmetros

Cada código possui uma classe `Config` que controla:

- **Modelo de *embedding***
- **Modelo de linguagem (SLM)**
- **CHUNK_SIZE** e **CHUNK_OVERLAP**
- **Temperatura do modelo**
- **Caminhos dos PDFs**
- **Diretório de persistência do ChromaDB**

Isso permite rapidamente testar diferentes combinações sem alterar o restante da lógica.

---

## Carregamento, Limpeza e Fragmentação dos Documentos

Ambos os scripts:

- Carregam PDFs com `PyPDFLoader`
- Limpam texto removendo múltiplos espaços e ruídos

Os dois experimentos variam nos tamanhos de *chunks*, pois cada contexto tem características diferentes:
- **RGB:** micropassagens pequenas (8 tokens)
- **Trânsito:** trechos maiores contendo contexto completo (500 tokens)

---

## Construção do Banco Vetorial (ChromaDB)

A recuperação utiliza **MMR** com:
- `k` variável (1,3,7,10)
- `lambda_mult = 0.45`
- `score_threshold = 0.25`

---

## Execução do Pipeline RAG

Ambos os códigos seguem o mesmo fluxo:

1. Inserção do *system prompt*
2. Criação de `PromptTemplate`
3. Construção da cadeia RAG (`RetrievalQA`)
4. Execução das perguntas de teste
5. Registro das respostas e métricas

---

## Métricas Avaliadas

Para cada pergunta:

- **Resposta do modelo**
- **Resposta esperada**
- Similaridade de cosseno usando `all-MiniLM-L6-v2`
- Tempo de execução (s)
- CPU antes/depois
- RAM antes/depois (via psutil)

Resultados são armazenados em planilhas `.xlsx` automaticamente.

---

## Aplicação RGB – Detalhes Específicos

- Perguntas seguem o padrão:  
  **"Qual o código RGB da cor X?"**
- Resposta esperada no formato:  
  **LED: (R,G,B)**
- O *system prompt* impede alucinações e força o formato exato.
- Foram analisados diferentes valores de **k** e diferentes embeddings.

O objetivo é comparar precisão × tempo para um sistema embarcado.

---

## Aplicação Trânsito – Detalhes Específicos

- Perguntas carregadas de uma planilha Excel
- Respostas esperadas são alternativas (a, b, c, d)
- O *prompt* exige que o modelo responda **somente a letra**
- Foram testados:
  - Diferentes LLMs (LLaMA, Gemma, Phi)
  - Diferentes *embeddings* (BGE, Granite, Nomic, Paraphrase etc.)

Esse teste representa um cenário real de interpretação de documentos extensos.

---

## Como Executar

1. Instale as dependências, por meio do requirements-raspberry.txt 

2. Instale e configure o Ollama.

3. Com o Ollama devidamente configurado, adicione os modelos como o llama3.2:3b por este comando:

`ollama pull llama3.2:3b`

4. Execute o script python.

Resultados serão salvos automaticamente em arquivos Excel.

---

## Referências

- LangChain – Documentação dos parâmetros: https://api.python.langchain.com/en/latest/vectorstores/langchain_core.vectorstores.base.VectorStore.html
- LangChain: https://python.langchain.com/docs/
- ChromaDB: https://docs.trychroma.com/
- Sentence-Transformers: https://www.sbert.net/
- Ollama: https://ollama.com/library
