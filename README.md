# IBSU მიღების ჩატბოტი — RAG პროტოტიპი

საბაკალავრო ნაშრომის სადემონსტრაციო პროტოტიპი: **RAG (Retrieval-Augmented Generation)**
არქიტექტურაზე დაფუძნებული ჩატბოტი, რომელიც პასუხობს ჩაბარების მსურველთა ხშირად
დასმულ კითხვებს.

> ℹ️ **მონაცემთა წყარო.** `data/faq.json` შეიცავს IBSU-ის ხშირად დასმული კითხვების
> გვერდიდან (https://ibsu.edu.ge/ge/faq/, ამოღება 2026-06-14) ამოღებულ რეალურ
> ჩანაწერებს. განახლებამდე გადაამოწმეთ ოფიციალურ წყაროსთან.

## სტეკი (სრულად უფასო / ლოკალური)
- **Python**
- **Embedding:** `intfloat/multilingual-e5-base` (sentence-transformers, ქართულის მხარდაჭერა)
- **Vector store:** Chroma (ლოკალური)
- **LLM:** Ollama (default, ლოკალური) ან Gemini free-tier (არასავალდებულო)

## არქიტექტურა
```
faq.json ──> [chunking: 1 FAQ = 1 დოკ.] ──> [e5 embedding] ──> Chroma
                                                                  │
კითხვა ──> [e5 embedding] ──> [top-k retrieval] ───────────────────┘
                                      │
                                      ▼
                       [prompt + კონტექსტი] ──> LLM ──> პასუხი (+ წყაროები)
```

## დაყენება
```bash
# 1. ვირტუალური გარემო (რეკომენდებული)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. დამოკიდებულებები
pip install -r requirements.txt
```

### LLM backend არჩევა

**ვარიანტი A — ლოკალური (default, ნულოვანი ხარჯი):**
```bash
# დააინსტალირეთ Ollama: https://ollama.com
ollama pull gemma2          # ან qwen2.5
ollama serve                # ფონურად გაშვებული
```

**ვარიანტი B — Gemini free-tier (ქართულის უკეთესი ხარისხი):**
```bash
pip install google-generativeai
export LLM_BACKEND=gemini
export GEMINI_API_KEY=your_free_key   # https://aistudio.google.com
```

## გაშვება
```bash
# 1. მონაცემთა ჩაწერა ვექტორულ ბაზაში (ერთხელ, ან მონაცემთა განახლებისას)
python -m src.ingest

# 2a. ტერმინალის ჩატი
python app_cli.py

# 2b. ან ვებ-ინტერფეისი
streamlit run app_streamlit.py
```

> ℹ️ ბრძანებები გაუშვით პროექტის ძირიდან (`Code/`), რომ `from src import ...`
> იმპორტებმა იმუშაოს.

## ფაილების სტრუქტურა
```
Code/
├── data/faq.json          # მონაცემები (რეალური, IBSU FAQ-დან)
├── src/
│   ├── __init__.py        # პაკეტის ნიშანი
│   ├── config.py          # ყველა პარამეტრი
│   ├── ingest.py          # მონაცემთა მომზადება + ბაზაში ჩაწერა
│   ├── rag.py             # RAG ბირთვი (retrieve → augment → generate)
│   └── llm.py             # LLM backend (Ollama / Gemini)
├── app_cli.py             # ტერმინალის ჩატი
├── app_streamlit.py       # ვებ-ინტერფეისი
└── requirements.txt
```

## შემდეგი ნაბიჯები (ნაშრომისთვის)
1. ✅ რეალური მონაცემების შეგროვება IBSU-ის საიტიდან (29 ჩანაწერი, 7 კატეგორია).
2. Evaluation: ტესტ-კითხვების ნაკრები → retrieval-ის სიზუსტე (Precision@k), latency.
3. პარამეტრების ექსპერიმენტი (`TOP_K`, embedding მოდელი) და შედეგების შედარება.
