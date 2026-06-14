"""
app_cli.py — მარტივი ტერმინალის ჩატი ტესტირებისთვის.

გაშვება (ჯერ უნდა გაეშვას ingest):
    python -m src.ingest
    python app_cli.py
"""
from src.rag import RAGPipeline


def main():
    print("IBSU მიღების ჩატბოტი (DEMO). გასასვლელად ჩაწერეთ: exit\n")
    rag = RAGPipeline()
    while True:
        try:
            q = input("თქვენ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if q.lower() in {"exit", "quit", "გასვლა"}:
            break
        if not q:
            continue
        out = rag.answer(q)
        print("\nბოტი:", out["answer"])
        src = ", ".join(f"{s['question']} ({s['similarity']})" for s in out["sources"])
        print("წყაროები:", src, "\n")


if __name__ == "__main__":
    main()
