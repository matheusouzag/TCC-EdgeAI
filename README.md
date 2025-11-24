Este repositório reúne todo o projeto, incluindo aplicações desktop e embarcadas, benchmarks, documentação, planilhas de resultados e experimentos relacionados ao uso de RAG, controle RGB e execução em Raspberry Pi.

A seguir, uma visão detalhada das pastas e seus conteúdos

---

## Ambiente-Desktop
Principais arquivos:
- rag-transito.ipynb (testes de RAG com contexto sobre trânsito)
- README.md (documentação específica da pasta)

---

## Aplicação-RGB
Local onde está a aplicação desktop principal, interface gráfica, pipeline RAG e simulação de LEDs/motor.

Principais arquivos:
- simulacao.ipynb (protótipo e testes da simulação RGB)
- README.md (explicação da aplicação)

---

## Benchmark
Scripts usados para medir desempenho, precisão, latência e comparação entre modelos, embeddings, fontes de contexto e estratégias de RAG.

Principais arquivos:
- benchmark-transit.py (benchmark voltado ao tema trânsito)
- benchmark.py (comparativo geral entre modelos na busca RGB)
- README.md — documentação e metodologia de benchmark

---

## Documentos
Base de conhecimento consultada pelo sistema, utilizada para RAG. E o arquivo com as perguntas utilizadas para o Benchmark de Contexto de Alternativas.

Inclui PDFs como:
- Direção defensiva
- Guia de cores RGB
- Noções de primeiros socorros
- Sinalização de trânsito
- Segurança no transporte infantil

---

## Planilhas
Registros estruturados de experimentos, métricas e resultados avaliativos.

Exemplos:
- Comparação de embeddings
- Avaliação de modelos no Raspberry Pi
- Resultados de testes com contextos de alternativas
- Testes com os parâmetros Chunk Size e Overlap

---

## Raspberry-Pi
Arquivos específicos para execução da aplicação no hardware real.

Conteúdos:
- Código adaptado para GPIO
- Versão embarcada da aplicação RGB
- Notebook de execução (rasp.ipynb)
- README.md (informações a respeito do notebook)

---

## requirements-desktop.txt
Lista de dependências necessárias para rodar a aplicação em ambiente desktop

## requirements-raspberry.txt
Lista de dependências necessárias para rodar a aplicação no Raspberry Pi

