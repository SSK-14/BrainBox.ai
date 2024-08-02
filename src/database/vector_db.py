import streamlit as st
from tidb_vector.integrations import TiDBVectorClient
from langchain_community.document_loaders import ArxivLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re, secrets, requests

DB_HOST = st.secrets["database"]["DB_HOST"]
DB_PORT = st.secrets["database"]["DB_PORT"]
DB_USERNAME = st.secrets["database"]["DB_USERNAME"]
DB_PASSWORD = st.secrets["database"]["DB_PASSWORD"]
DB_DATABASE = st.secrets["database"]["DB_DATABASE"]

def text_to_embedding(text):
    JINAN_HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.secrets["JINAAI_API_KEY"]}'
    }
    JINAAI_REQUEST_DATA = {
        'input': [text],
        'model': 'jina-embeddings-v2-base-en'
    }
    response = requests.post('https://api.jina.ai/v1/embeddings', headers=JINAN_HEADERS, json=JINAAI_REQUEST_DATA)
    return response.json()['data'][0]['embedding']

vector_store = TiDBVectorClient(
    table_name='knowledge',
    connection_string=f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true',
    vector_dimension=768,
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
    if type == "Tavily":
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
    search_results = vector_store.query(
        query_embedding,
        k=4,
        filter={"id": {
            "$in": chat_ids
        }}
    )
    results = []
    for item in search_results:
        results.append({
            "text": item.document,
            "metadata": item.metadata
        })
    return results