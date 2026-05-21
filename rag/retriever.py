import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_PATH = "./rag/chroma_db"
EMBED_MODEL = "intfloat/multilingual-e5-base"

class SAPDocRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        self.collection = self.client.get_or_create_collection(
            name="sap_docs",
            embedding_function=self.embed_fn,
        )

    def retrieve(self, query: str, k: int = 3) -> list[dict]:
        """
        Query: nome do objeto SAP + contexto (ex: "BAPI_PO_CREATE1 purchase order").
        Retorna top-k trechos relevantes com metadata.
        """
        results = self.collection.query(query_texts=[query], n_results=k)
        return [
            {"texto": doc, "fonte": meta.get("source", "unknown")}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
