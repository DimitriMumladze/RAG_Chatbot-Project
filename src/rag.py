"""
rag.py — RAG-ის ბირთვი: retrieval → prompt-ის გამდიდრება → გენერაცია.

ცენტრალური იდეა: LLM პასუხობს *მხოლოდ* ამოღებული კონტექსტის საფუძველზე.
თუ კონტექსტში პასუხი არ არის — ვაბრუნებთ ფიქსირებულ შეტყობინებას და არ ვაგენერირებთ
გამოგონილ ინფორმაციას. სწორედ ეს ამცირებს ჰალუცინაციას (RAG-ის მთავარი ღირებულება).
"""
import chromadb
from sentence_transformers import SentenceTransformer

from src import config
from src import llm

# სისტემური ინსტრუქცია LLM-ისთვის (ქართულად)
SYSTEM_PROMPT = (
    "შენ ხარ უნივერსიტეტის მიღების დამხმარე ასისტენტი. "
    "უპასუხე მომხმარებლის კითხვას მხოლოდ ქვემოთ მოწოდებული კონტექსტის საფუძველზე, "
    "ქართულ ენაზე, მოკლედ და ზუსტად. "
    "თუ პასუხი კონტექსტში არ მოიძებნება, ზუსტად დააბრუნე ეს ფრაზა: "
    f"\"{config.FALLBACK_ANSWER}\" "
    "არასოდეს მოიგონო ინფორმაცია, რომელიც კონტექსტში არ წერია."
)


class RAGPipeline:
    """ერთხელ იტვირთება მოდელი/ბაზა, შემდეგ ემსახურება კითხვებს."""

    def __init__(self):
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=config.CHROMA_DIR)
        self.collection = client.get_collection(config.COLLECTION_NAME)

    def retrieve(self, question: str):
        """კითხვის embedding → top-k ჩანაწერის ამოღება ბაზიდან."""
        q_emb = self.embedder.encode(
            config.QUERY_PREFIX + question, normalize_embeddings=True
        ).tolist()
        res = self.collection.query(
            query_embeddings=[q_emb], n_results=config.TOP_K
        )
        ids = res["ids"][0]
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        # cosine მანძილი → მსგავსება (1 - dist), მხოლოდ ანალიზისთვის
        hits = [
            {"id": i, "answer": d, "question": m.get("question", ""),
             "category": m.get("category", ""), "similarity": round(1 - dist, 3)}
            for i, d, m, dist in zip(ids, docs, metas, dists)
        ]
        return hits

    def build_context(self, hits):
        """ამოღებული ჩანაწერებიდან ავაწყოთ კონტექსტის ტექსტი."""
        return "\n\n".join(
            f"[{i+1}] {h['question']}\n{h['answer']}" for i, h in enumerate(hits)
        )

    def answer(self, question: str):
        """სრული ციკლი: retrieve → augment → generate."""
        hits = self.retrieve(question)
        context = self.build_context(hits)
        user_prompt = (
            f"კონტექსტი:\n{context}\n\n"
            f"კითხვა: {question}\n"
            f"პასუხი:"
        )
        text = llm.generate(SYSTEM_PROMPT, user_prompt)
        return {"answer": text, "sources": hits}


if __name__ == "__main__":
    # სწრაფი ტესტი
    rag = RAGPipeline()
    out = rag.answer("რა საბუთები მჭირდება ჩასაბარებლად?")
    print("\nპასუხი:\n", out["answer"])
    print("\nწყაროები:")
    for s in out["sources"]:
        print(f"  - ({s['similarity']}) {s['question']}")
