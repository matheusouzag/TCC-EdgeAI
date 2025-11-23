import os
import re
import time
import psutil
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import OllamaEmbeddings

# Parâmetros
class Config:
    EMBEDDING_MODEL = "paraphrase-multilingual"  
    LLM_MODEL = "gemma3n:e2b"  
    TEMPERATURE = 0.2
    CHUNK_SIZE = 8
    CHUNK_OVERLAP = 2
    PERSIST_DIR = "./chroma_db_benchmark"
    PDF_PATHS = [
        r"/home/matheus/Guia Cores RGB.pdf"]  

# Lista de perguntas de benchmark 
TEST_QUESTIONS = TEST_QUESTIONS = [
    "Qual o código RGB da cor Preto?",
    "Qual o código RGB da cor Cinza muito escuro?",
    "Qual o código RGB da cor Azul céu profundo?",
    "Qual o código RGB da cor Oliva?",
    "Qual o código RGB da cor Tijolo de fogo?",
    "Qual o código RGB da cor Azul marinho?",
    "Qual o código RGB da cor Azul cadete?",
    "Qual o código RGB da cor Cinza ardósia escuro?",
    "Qual o código RGB da cor Verde oliva escuro?",
    "Qual o código RGB da cor Trigo?",
    "Qual o código RGB da cor Azul céu claro?",
    "Qual o código RGB da cor Ciano / Aqua?",
    "Qual o código RGB da cor Verde mar claro?",
    "Qual o código RGB da cor Verde claro?",
    "Qual o código RGB da cor Branco navajo?",
]

EXPECTED_ANSWERS = [
    "LED: (0,0,0)",
    "LED: (28,28,28)",
    "LED: (0,191,255)",
    "LED: (128,128,0)",
    "LED: (178,34,34)",
    "LED: (0,0,128)",
    "LED: (95,158,160)",
    "LED: (47,79,79)",
    "LED: (107,142,35)",
    "LED: (245,222,179)",
    "LED: (135,206,250)",
    "LED: (0,255,255)",
    "LED: (32,178,170)",
    "LED: (144,238,144)",
    "LED: (255,222,173)"
]

system_prompt = """
Você é um assistente especializado em interpretar documentos técnicos e responder perguntas com base no Documento de Cores.

Regras obrigatórias para suas respostas:
1. Responda **apenas** com o código RGB no formato: LED: (R,G,B).
2. Não adicione explicações, comentários ou texto extra.
3. Se não encontrar a resposta no contexto fornecido, responda exatamente: LED: (0,0,0).
4. Não invente cores ou aja com incerteza.
"""

# Limpeza de Texto
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Processamento dos documentos e Vetorstore
documents = []
for path in Config.PDF_PATHS:
    try:
        loader = PyPDFLoader(path)
        pages = loader.load_and_split(text_splitter=None)
        for page in pages:
            cleaned = clean_text(page.page_content)
            if cleaned.strip():
                page.page_content = cleaned
                documents.append(page)
        print(f"✓ {os.path.basename(path)} processado")
    except Exception as e:
        print(f"✗ Erro em {path}: {str(e)}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=Config.CHUNK_SIZE,
    chunk_overlap=Config.CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
    length_function=lambda x: len(x.split()),
    is_separator_regex=False
)

texts = text_splitter.split_documents(documents)
print(f"Total de chunks gerados: {len(texts)}")
embeddings = OllamaEmbeddings(model=Config.EMBEDDING_MODEL) # Trocar com base no embedding selecionado
# embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL) # Trocar com base no embedding selecionado
db = Chroma.from_documents(
    texts,
    embeddings,
    persist_directory=Config.PERSIST_DIR,
    collection_metadata={"hnsw:space": "cosine"}
)
retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 10, "lambda_mult": 0.45, "score_threshold": 0.25})


# Inicialização do LLM/SLM
llm = Ollama(
    model=Config.LLM_MODEL,
    temperature=Config.TEMPERATURE,
    system=system_prompt
)

prompt_template = """
Contexto (extraído dos documentos):
{context}

Pergunta:
{question}

Responda somente no formato: LED: (R,G,B)
Se não encontrar, responda: LED: (0,0,0)
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

# Benchmark
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def run_benchmark():
    results = []

    for i, question in enumerate(TEST_QUESTIONS):
        process = psutil.Process(os.getpid())
        cpu_before = psutil.cpu_percent(interval=None)
        mem_before = process.memory_info().rss / (1024 * 1024)

        start_time = time.time()
        result = qa_chain.invoke({"query": question})
        end_time = time.time()

        elapsed = end_time - start_time
        cpu_after = psutil.cpu_percent(interval=None)
        mem_after = process.memory_info().rss / (1024 * 1024)

        answer = result['result']
        expected = EXPECTED_ANSWERS[i] if i < len(EXPECTED_ANSWERS) else ""

        similarity = None
        if expected:
            emb_out = embedder.encode([answer])
            emb_exp = embedder.encode([expected])
            similarity = cosine_similarity([emb_out[0]], [emb_exp[0]])[0][0]

        results.append({
            "Modelo": Config.LLM_MODEL,
            "Temperatura": Config.TEMPERATURE,
            "Chunk size": Config.CHUNK_SIZE,
            "Chunk overlap": Config.CHUNK_OVERLAP,
            "Pergunta": question,
            "Resposta modelo": answer,
            "Resposta esperada": expected,
            "Similaridade": similarity,
            "Tempo (s)": round(elapsed, 3),
            "CPU antes (%)": cpu_before,
            "CPU depois (%)": cpu_after,
            "RAM antes (MB)": round(mem_before, 2),
            "RAM depois (MB)": round(mem_after, 2),
        })

    return results

# Resultados
results = run_benchmark()
results_df = pd.DataFrame(results)

excel_file = "benchmark_results_rasp_gemma3n:e2b_paraphrase-multilingual_mmr_k10_0-45_0-25_82_5.xlsx"
if os.path.exists(excel_file):
    old_df = pd.read_excel(excel_file)
    results_df = pd.concat([old_df, results_df], ignore_index=True)

results_df.to_excel(excel_file, index=False)
print(f"Benchmark concluído! Resultados salvos em {excel_file}.")
