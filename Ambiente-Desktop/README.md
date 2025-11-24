# Teste Inicial - Desktop

Este repositório contém o código utilizado no **primeiro teste experimental** do projeto, cujo objetivo foi compreender, na prática, como as escolhas de parâmetros, como *chunk size*, *chunk overlap*, temperatura, (tipo de busca e métricas de diversidade) afetam o desempenho em termos de precisão, clareza da resposta e tempo de execução, paralelamente ao teste do RAG e suas ferramentas.  
Além disso, o código permitiu analisar o impacto de diferentes **prompts** na forma como o modelo estrutura e entrega a resposta, etapa fundamental para posteriores experimentos no sistema embarcado.

---

## Tecnologias e Técnicas Principais

- **RAG**
- **Python**
- **LangChain**
- **ChromaDB** 
- **HuggingFace**
- **Ollama**
- **PyPDFLoader**

---

## Estrutura Geral do Pipeline

### Configuração de Parâmetros
Toda a parametrização do pipeline está concentrada na classe `Config`, que define:

- **Modelo de embedding**
- **Modelo de linguagem**
- Fragmentação do texto:  
  **CHUNK_SIZE** 
  **CHUNK_OVERLAP**
- **Temperatura do modelo**
- **Caminhos dos PDFs utilizados no teste**

Esses parâmetros foram escolhidos justamente por serem aqueles cuja alteração tem impacto direto no desempenho, como discutido no TCC.

---

## Tratamento e Processamento dos Documentos

O código emprega um fluxo completo de limpeza e preparação dos textos.

### Limpeza de Texto
A função `clean_brazilian_legal_text()`:

- Remove padrões repetitivos (Diário Oficial, numeração, cabeçalhos)
- Normaliza estruturas jurídicas  
  - “artigo” → “Art. X”  
  - “§ único” → “§ único”
- Reduz ruído e aumenta a precisão dos embeddings

### Carregamento via PyPDFLoader
Os PDFs são divididos página a página, facilitando:

- tokenização
- segmentação eficiente
- preservação da estrutura original

---

## Banco Vetorial e Estratégia de Recuperação

Foi utilizado o **ChromaDB**, com persistência local.  
O código também trata **duplicatas**, reduzindo redundância e melhorando a qualidade da recuperação.

A etapa de recuperação padrão utiliza:

- `search_type="mmr"`
- `k = 7`
- `lambda_mult = 0.45`
- `score_threshold = 0.25`

Esses parâmetros correspondem exatamente à Tabela de Parâmetros apresentada no TCC.

O **Retriever** abstrai a consulta ao banco vetorial, equilibrando diversidade e similaridade, ponto central do estudo.

---

## Inicialização do Modelo e Execução

A execução ocorre da seguinte forma:

1. **Inicialização do modelo via (`Ollama`)**  
   Com temperatura e comportamento definidos via *system prompt*, instruindo o modelo a agir como especialista em legislação de trânsito.

2. **Definição do PromptTemplate**  
   Estrutura a resposta e exige:
   - Base legal  
   - Explicação técnica  
   - Fontes utilizadas  

3. **Criação da cadeia RAG (`RetrievalQA`)**

4. **Função `consultar()`**  
   Envia a pergunta, executa a recuperação, gera a resposta e lista as fontes utilizadas.

---

## Como Executar

1. Instale as dependências, por meio do requirements-desktop.txt 

2. Instale e configure o Ollama.

3. Com o Ollama devidamente configurado, adicione os modelos como o llama3.2:3b por este comando:

`ollama pull llama3.2:3b`

4. Execute o script e faça uma consulta:

consultar("Qual é a idade mínima para habilitação na categoria D?")

---

## Referências

- LangChain – Documentação dos parâmetros: https://api.python.langchain.com/en/latest/vectorstores/langchain_core.vectorstores.base.VectorStore.html
- LangChain – Documentação geral: https://python.langchain.com/docs/
- ChromaDB – Documentação oficial: https://docs.trychroma.com/
- Ollama (Documentação oficial): https://ollama.com/library
- PyPDFLoader (LangChain): https://python.langchain.com/docs/integrations/document_loaders/pdf

