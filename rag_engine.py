import os
import chromadb
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# ---- טעינת המפתח ומודל ה-embedding ----
load_dotenv()

Settings.embed_model = GoogleGenAIEmbedding(
    model_name="gemini-embedding-001",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# ---- התחברות למאגר שכבר מלא ----
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="inventions")
vector_store = ChromaVectorStore(chroma_collection=collection)

# ---- טעינת האינדקס מהמאגר ----
index = VectorStoreIndex.from_vector_store(vector_store)

# ---- כלי חיפוש: מחזיר 3 קטעים ----
retriever = index.as_retriever(similarity_top_k=3)


def retrieve(question):
    return retriever.retrieve(question)


# ---- בדיקה ----
if __name__ == "__main__":
    results = retrieve("מי המציא את הדפוס?")
    for result in results:
        print("Score:", round(result.score, 3))
        print(result.node.get_content()[:200])
        print("-----")