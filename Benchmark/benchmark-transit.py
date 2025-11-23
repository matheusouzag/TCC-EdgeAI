import os
import re
import time
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

# Parâmetros
class Config:
    EMBEDDING_MODEL = "google/embeddinggemma-300M"
    LLM_MODEL = "llama3.2:3b"
    TEMPERATURE = 0.2
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 200
    PERSIST_DIR = "./chroma_db_transit"
    PDF_PATHS = [
        r"M:\\tcc\\pdfs\\questionario\\Sinalização.pdf",
        r"M:\\tcc\\pdfs\\questionario\\Direção Defensiva.pdf",
        r"M:\\tcc\\pdfs\\questionario\\Segurança no Transporte crianças e gestantes.pdf",
        r"M:\\tcc\\pdfs\\questionario\\Noções de Primeiros Socorros no Trânsito.pdf",
        r"M:\\tcc\\pdfs\\questionario\\Manual de Primeiros Socorros.pdf"
    ]

from huggingface_hub import login
login()

# Carregar as perguntas e respostas da planilha
excel_input = r"M:\\tcc\\pergunta\\Questionário_1.xlsx" 
df_questions = pd.read_excel(excel_input)

TEST_QUESTIONS = df_questions["Pergunta"].dropna().tolist()
EXPECTED_ANSWERS = df_questions["Resposta"].fillna("").tolist()

# Prompt de sistema do LLM
system_prompt = """
Você é um instrutor especialista em educação para o trânsito e segurança viária.
Sua tarefa é responder perguntas de múltipla escolha com base exclusiva nos documentos fornecidos (materiais de trânsito).

Regras:
- Use somente informações que estejam nos documentos para justificar a resposta.
- Sempre que possível, indique a alternativa correta (a, b, c, d).
- Justifique a escolha de forma breve e objetiva, mas sem inventar nada que não esteja nos documentos.
- Caso não haja informação suficiente nos documentos, responda que não é possível determinar com base no material.
"""

# Limpeza de texto
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Processamento de documentos
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
        print(f"{os.path.basename(path)} processado")
    except Exception as e:
        print(f"Erro em {path}: {str(e)}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=Config.CHUNK_SIZE,
    chunk_overlap=Config.CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
    length_function=len,
    is_separator_regex=False
)

texts = text_splitter.split_documents(documents)
print(f"Total de chunks gerados: {len(texts)}")

embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
db = Chroma.from_documents(
    texts,
    embeddings,
    persist_directory=Config.PERSIST_DIR,
    collection_metadata={"hnsw:space": "cosine"}
)
retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": 3, "lambda_mult": 0.45, "score_threshold": 0.25})

# Inicialização do LLM/SLM
llm = Ollama(
    model=Config.LLM_MODEL,
    temperature=Config.TEMPERATURE,
    system=system_prompt
)

# Prompt template
prompt_template = """
Contexto extraído dos documentos:
{context}

Pergunta de múltipla escolha:
{question}

Instrução:
Escolha a alternativa correta (a, b, c ou d) com base nos documentos.
Responda somente com a letra (a, b, c ou d), sem ponto, sem parêntese e sem texto adicional.
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
        start_time = time.time()
        result = qa_chain.invoke({"query": question})
        end_time = time.time()

        elapsed = end_time - start_time
        answer = result['result']
        expected = EXPECTED_ANSWERS[i] if i < len(EXPECTED_ANSWERS) else ""

        similarity = None
        if expected:
            emb_out = embedder.encode([answer])
            emb_exp = embedder.encode([expected])
            similarity = cosine_similarity([emb_out[0]], [emb_exp[0]])[0][0]

        results.append({
            "Modelo": Config.LLM_MODEL,
            "Embedding": Config.EMBEDDING_MODEL,
            "Temperatura": Config.TEMPERATURE,
            "Chunk size": Config.CHUNK_SIZE,
            "Chunk overlap": Config.CHUNK_OVERLAP,
            "Pergunta": question,
            "Resposta esperada": expected,
            "Resposta modelo": answer,
            "Similaridade": similarity,
            "Tempo (s)": round(elapsed, 3),
        })

    return results

# Resultados
results = run_benchmark()
results_df = pd.DataFrame(results)

excel_file = "benchmark_transit_500_200.xlsx"
results_df.to_excel(excel_file, index=False)
print(f"Benchmark concluído! Resultados salvos em {excel_file}.")
