# Aplicação RGB – Raspberry Pi

Este repositório contém o sistema responsável por interpretar comandos em linguagem natural, consultar informações via RAG e acionar LEDs RGB conectados ao **Raspberry Pi**, controlando intensidade luminosa conforme valores retornados pelo modelo de linguagem.

O projeto valida o uso de **Edge AI**, processamento local, embeddings, recuperação vetorial e controle físico por GPIO.

---

## Tecnologias Fundamentais

- **Raspberry Pi**
- **GPIOZero (PWMLED)**
- **Ollama (modelos locais)**
- **LangChain**
- **RAG (Retrieval-Augmented Generation)**
- **ChromaDB**
- **PyPDFLoader**
- **Python**

---

## Objetivo Geral do Sistema

A aplicação interpreta comandos como:

- “Acenda o LED verde”
- “Ligue o LED com azul cadete”
- “Ative o LED com azul marinho”

E executa automaticamente:

- Recuperação RAG da cor solicitada
- Extração rigorosa de RGB via JSON
- Conversão de intensidade para PWM
- Controle dos LEDs físicos
- Classificação da intenção do usuário

---

# Estrutura Geral do Pipeline

## Configuração de Parâmetros

A classe `Config` define:

- **Modelo de linguagem do Ollama**
- **Modelo de embedding**
- **Tamanho de chunk**
- **Temperatura**
- **Pasta do banco vetorial**
- **Nome da coleção do ChromaDB**
- **Caminho do PDF base (Guia RGB)**

---

## Limpeza e Processamento dos Documentos

O carregamento utiliza `PyPDFLoader`.

---

## Embeddings Otimizados

A classe `OptimizedOllamaEmbeddings`:

- Gera embeddings diretamente pelo Ollama
- Utiliza **cache LRU** para evitar recomputação
- Reduz tempo e consumo de CPU no Raspberry Pi

---

## Banco Vetorial e Recuperação

Usa:

- **ChromaDB local**
- Busca via **MMR**
- Persistência em disco

Parâmetros principais:

- `k = 5`
- `lambda_mult = 0.45`
- `score_threshold = 0.5`

---

## Cadeias e Prompts

### Prompt principal de cores (LED)
- Sempre retorna JSON
- Deve conter apenas `"rgb": (x, y, z)`
- Nunca usa HEX
- Retorna `null` caso não encontre a cor

### Prompt de intenção
Classifica o comando do usuário em:

- `"led"`
- `"motor"`
- `"led_motor"`
- `"nenhum"`

Essa triagem evita erros de interpretação.

### Prompt do motor
Embora não exista motor físico no Raspberry Pi,
o sistema interpreta pedidos de:

- aumentar
- diminuir
- definir velocidade
- parar

E retorna JSON padronizado.

---

## Controle Físico dos LEDs

Os LEDs são conectados aos pinos GPIO:

| LED | Cor | Pino |
|-----|-----|------|
| 1   | Vermelho | 13 |
| 2   | Verde     | 19 |
| 3   | Azul      | 26 |

A biblioteca `gpiozero` permite controlar intensidade PWM.

- Divide cada valor por 255
- Converte para escala 0.0–1.0
- Ajusta brilho individualmente
- Gera mistura de cores real

---

## Fluxo da Aplicação

1. Usuário envia comando em linguagem natural
2. Classificador decide a intenção
3. Se for LED = consulta RAG
4. Modelo retorna RGB em JSON
5. Sistema converte para valores PWM
6. Raspberry Pi acende LEDs físicos

---

## Como Executar

1. Instale as dependências, por meio do requirements-raspberry.txt 

2. Instale e configure o Ollama

3. Com o Ollama devidamente configurado, adicione os modelos como o llama3.2:3b por este comando:

`ollama pull llama3.2:3b`

4. Execute o script.

---

## Requisitos de Hardware

- Raspberry Pi 5 (recomendado)
- Protoboard
- 3 LEDs RGB individuais
- 3 resistores
- Jumpers
- Fonte 5V

---

## Referências

- GPIOZero documentação: https://gpiozero.readthedocs.io/
- Ollama documentação: https://ollama.com/library
- ChromaDB documentação: https://docs.trychroma.com/
- LangChain documentação: https://python.langchain.com/docs/
