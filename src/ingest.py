"""
ingest.py — მონაცემთა მომზადება და ვექტორულ ბაზაში ჩაწერა.

ნაბიჯები:
  1. წავიკითხოთ FAQ (data/faq.json)
  2. თითო კითხვა-პასუხი = ერთი დოკუმენტი (FAQ-ისთვის ეს ბუნებრივი ერთეულია,
     ამიტომ ფიქსირებული სიგრძის chunking-ს არ ვიყენებთ)
  3. დავაგენერიროთ embedding-ები multilingual-e5-ით ("passage: " პრეფიქსით)
  4. ჩავწეროთ Chroma-ში (cosine მანძილით)

გაშვება:  python -m src.ingest
"""
import json
import chromadb
from sentence_transformers import SentenceTransformer

from src import config


def load_faq(path: str):
    """წავიკითხოთ FAQ ფაილი და დავაბრუნოთ ჩანაწერების სია."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("faq", [])


def build_documents(faq):
    """
    თითო ჩანაწერისთვის ვამზადებთ:
      - text_to_embed: კითხვა + პასუხი (კითხვის ჩართვა აუმჯობესებს დამთხვევას)
      - document: პასუხის ტექსტი (რასაც კონტექსტში დავაბრუნებთ)
      - metadata: კითხვა, კატეგორია, წყარო
    """
    ids, embed_texts, documents, metadatas = [], [], [], []
    for item in faq:
        q, a = item["question"], item["answer"]
        ids.append(item["id"])
        embed_texts.append(config.PASSAGE_PREFIX + q + "\n" + a)
        documents.append(a)
        metadatas.append({
            "question": q,
            "category": item.get("category", ""),
        })
    return ids, embed_texts, documents, metadatas


def main():
    print("→ FAQ-ის წაკითხვა:", config.DATA_PATH)
    faq = load_faq(config.DATA_PATH)
    print(f"  ჩაიტვირთა {len(faq)} ჩანაწერი")

    print("→ embedding მოდელის ჩატვირთვა:", config.EMBEDDING_MODEL)
    model = SentenceTransformer(config.EMBEDDING_MODEL)

    ids, embed_texts, documents, metadatas = build_documents(faq)

    print("→ embedding-ების გენერაცია...")
    embeddings = model.encode(
        embed_texts, normalize_embeddings=True, show_progress_bar=True
    ).tolist()

    print("→ Chroma-ში ჩაწერა:", config.CHROMA_DIR)
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    # თუ კოლექცია უკვე არსებობს — წავშალოთ და თავიდან ავაშენოთ (idempotent ingest)
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    print(f"✓ მზადაა — ბაზაში ჩაიწერა {collection.count()} ვექტორი.")


if __name__ == "__main__":
    main()
