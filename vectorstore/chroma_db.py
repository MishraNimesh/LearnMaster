from langchain_chroma import Chroma
from langchain_core.documents import Document
from vectorstore.embeddings import embeddings

vector_store = Chroma(
    collection_name="researchos",
    embedding_function=embeddings,
    persist_directory="chroma_db"
)


def store_chunks(chunks, metadata=None):
    documents = [
        Document(
            page_content=chunk,
            metadata=metadata or {}
        )
        for chunk in chunks
    ]

    vector_store.add_documents(documents)