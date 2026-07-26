from vectorstore.chroma_db import vector_store


def retrieve(query, topic=None, chapter=None):
    kwargs = {"k": 2, "fetch_k": 5, "lambda_mult": 0.5}
    if topic and chapter:
        kwargs["filter"] = {"$and": [{"topic": topic}, {"chapter": chapter}]}
    elif topic:
        kwargs["filter"] = {"topic": topic}
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs=kwargs)
    return retriever.invoke(query)
