import streamlit as st
from tidb_vector.integrations import TiDBVectorClient
from langchain_community.embeddings import JinaEmbeddings
from langchain_community.document_loaders import ArxivLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re, secrets, os

DB_HOST = st.secrets["database"]["DB_HOST"]
DB_PORT = st.secrets["database"]["DB_PORT"]
DB_USERNAME = st.secrets["database"]["DB_USERNAME"]
DB_PASSWORD = st.secrets["database"]["DB_PASSWORD"]
DB_DATABASE = st.secrets["database"]["DB_DATABASE"]
SSL_PATH = st.secrets["database"]["SSL_PATH"]

text_embeddings = JinaEmbeddings(
    jina_api_key=st.secrets["JINAAI_API_KEY"], 
    model_name="jina-embeddings-v2-base-en"
)

vector_store = TiDBVectorClient(
    table_name='knowledge',
    connection_string=f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?ssl_ca={SSL_PATH}&ssl_verify_cert=true&ssl_verify_identity=true',
    vector_dimension=768,
    drop_existing_table=False,
)

doc_vector_store = TiDBVectorClient(
    table_name='documents',
    connection_string=f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?ssl_ca=/etc/ssl/cert.pem&ssl_verify_cert=true&ssl_verify_identity=true',
    vector_dimension=768,
    drop_existing_table=True,
)

def init_temp_folder():
    if not os.path.exists(".tmp"):
        os.makedirs(".tmp")
    for file in os.listdir(".tmp"):
        os.remove(f".tmp/{file}")   

init_temp_folder()


def insert_embedding(documents, vector_store=vector_store):
    vector_store.insert(
        ids=[secrets.token_hex(16) for _ in range(len(documents))],
        texts=[doc["text"] for doc in documents],
        embeddings=[doc["embedding"] for doc in documents],
        metadatas=[doc["metadata"] for doc in documents],
    )

def create_embedding(docs, id=None):
    documents = []
    for doc in docs:
        if id:
            doc.metadata["id"] = id
        embedding = text_embeddings.embed_query(doc.page_content)
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

def ingest_document(uploaded_files):
    if uploaded_files:
        docs = []
        for uploaded_file in uploaded_files:
            with open(f".tmp/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.getvalue())
            data = PyMuPDFLoader(f".tmp/{uploaded_file.name}").load()
            docs.append(data[0])
            st.session_state.documents.append(uploaded_file.name)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n"])
    split_docs = text_splitter.split_documents(docs)
    documents = create_embedding(split_docs)
    insert_embedding(documents, doc_vector_store)

def document_search(query):
    return vector_search(query, None, doc_vector_store)

def ingest_knowledge(id, results, type):
    if type == "Tavily":
        docs = UnstructuredURLLoader(urls=results).load()
    elif type == "ArXiv":
        docs = []
        for result in results:
            arxiv_id = extract_arxiv_id(result)
            doc = ArxivLoader(query=arxiv_id, load_max_docs=1).load()
            docs.extend(doc)
    elif type == "Documents":
        docs = []
        for result in results:
            doc = PyMuPDFLoader(f".tmp/{result}").load()
            docs.extend(doc)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n"])
    split_docs = text_splitter.split_documents(docs)
    documents = create_embedding(split_docs, id)
    insert_embedding(documents)


def delete_knowledge(id):
    vector_store.delete(filter={"id": {"$eq": id}})

def vector_search(query, filter=None, vector_store=vector_store):
    query_embedding = text_embeddings.embed_query(query)
    search_results = vector_store.query(
        query_embedding,
        k=4,
        filter=filter
    )
    results = []
    for item in search_results:
        results.append({
            "text": item.document,
            "metadata": item.metadata
        })
    return results