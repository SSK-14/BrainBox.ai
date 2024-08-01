import streamlit as st
from tidb_vector.integrations import TiDBVectorClient
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import ArxivLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re, secrets, ast

DB_HOST = st.secrets["database"]["DB_HOST"]
DB_PORT = st.secrets["database"]["DB_PORT"]
DB_USERNAME = st.secrets["database"]["DB_USERNAME"]
DB_PASSWORD = st.secrets["database"]["DB_PASSWORD"]
DB_DATABASE = st.secrets["database"]["DB_DATABASE"]

MODEL_NAME = 'Alibaba-NLP/gte-large-en-v1.5'

embedding_model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
embedding_model_dim = embedding_model.get_sentence_embedding_dimension()

def text_to_embedding(text):
    embedding = embedding_model.encode(text)
    return embedding.tolist()

vector_store = TiDBVectorClient(
    table_name='knowledge',
    connection_string=f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true',
    vector_dimension=embedding_model_dim,
    drop_existing_table=False,
)

def insert_embedding(documents):
    vector_store.insert(
        ids=[secrets.token_hex(16) for _ in range(len(documents))],
        texts=[doc["text"] for doc in documents],
        embeddings=[doc["embedding"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents],
    )

def create_embedding(id, docs):
    documents = []
    for doc in docs:
        doc.metadata["id"] = id
        embedding = text_to_embedding(doc.page_content)
        documents.append({
            "text": doc.page_content,
            "embedding": embedding,
            "metadata": doc.metadata
        })
    return documents

def extract_arxiv_id(url):
    match = re.search(r'arxiv\.org/abs/(\d+\.\d+v\d+)', url)
    if match:
        return match.group(1)
    return None

def ingest_knowledge(id, results, type):
    if type == "Internet search":
        docs = UnstructuredURLLoader(urls=results).load()
    else:
        docs = []
        for result in results:
            arxiv_id = extract_arxiv_id(result)
            doc = ArxivLoader(query=arxiv_id, load_max_docs=1).load()
            docs.extend(doc)
            
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n"])
    split_docs = text_splitter.split_documents(docs)
    documents = create_embedding(id, split_docs)
    insert_embedding(documents)

def vector_search(query, chat_ids):
    query_embedding = text_to_embedding(query)
    search_results = vector_store.query(query_embedding,k=4)
    results = []
    for item in search_results:
        results.append({
            "text": item.document,
            "metadata": item.metadata
        })
    return results