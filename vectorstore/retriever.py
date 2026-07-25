from vectorstore.chroma_db import vector_store

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 10,
        "lambda_mult": 0.5
    }
)

def retrieve(query):
    return retriever.invoke(query)