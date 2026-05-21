"""
Ingestão simplificada: só docs curados em rag/docs/.
Snapshots reais da SAP virão em segundo momento.

Uso: python rag/ingest.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from config import RAG_DOCS_DIR, CHROMA_PATH, EMBED_MODEL, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE


def chunk_markdown(text: str, source: str) -> list[dict]:
    chunks = []
    sections = text.split("\n## ")
    for i, section in enumerate(sections):
        content = section.strip() if i == 0 else "## " + section.strip()
        if len(content) < MIN_CHUNK_SIZE:
            continue
        if len(content) > MAX_CHUNK_SIZE:
            subsections = content.split("\n### ")
            for j, sub in enumerate(subsections):
                sub_content = sub.strip() if j == 0 else "### " + sub.strip()
                if MIN_CHUNK_SIZE <= len(sub_content) <= MAX_CHUNK_SIZE * 1.5:
                    chunks.append({
                        "text": sub_content,
                        "source": source,
                        "section": f"section_{i}_sub_{j}",
                    })
        else:
            chunks.append({
                "text": content,
                "source": source,
                "section": f"section_{i}",
            })
    return chunks


def main():
    print(f"📚 Ingestão de docs curados em {RAG_DOCS_DIR}\n")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    try:
        client.delete_collection("sap_docs")
        print("  ⚠️  Coleção existente removida\n")
    except Exception:
        pass

    collection = client.create_collection(
        name="sap_docs",
        embedding_function=embed_fn,
    )

    docs_dir = Path(RAG_DOCS_DIR)
    md_files = list(docs_dir.glob("*.md"))
    
    if not md_files:
        print(f"❌ Nenhum .md em {docs_dir}. Crie os arquivos primeiro.")
        return

    print(f"📄 {len(md_files)} arquivos encontrados\n")

    all_chunks = []
    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        chunks = chunk_markdown(text, source=md_file.name)
        print(f"   {md_file.name}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("\n❌ Nenhum chunk gerado.")
        return

    collection.add(
        documents=[c["text"] for c in all_chunks],
        metadatas=[{"source": c["source"], "section": c["section"]} for c in all_chunks],
        ids=[f"chunk_{i:04d}" for i in range(len(all_chunks))],
    )

    print(f"\n✅ {len(all_chunks)} chunks indexados em {CHROMA_PATH}")


if __name__ == "__main__":
    main()
