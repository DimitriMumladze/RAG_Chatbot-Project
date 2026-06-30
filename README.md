# IBSU მიღების ჩატბოტი — RAG პროტოტიპი

საბაკალავრო ნაშრომის სადემონსტრაციო პროტოტიპი: **RAG (Retrieval-Augmented Generation)**
არქიტექტურაზე დაფუძნებული ჩატბოტი, რომელიც პასუხობს ჩაბარების მსურველთა ხშირად
დასმულ კითხვებს IBSU-ის რეალურ მონაცემებზე დაყრდნობით.

> ℹ️ **მონაცემთა წყარო.** `data/faq.json` შეიცავს IBSU-ის ხშირად დასმული კითხვების
> გვერდიდან (https://ibsu.edu.ge/ge/faq/, ამოღება 2026-06-14) ამოღებულ 29 რეალურ
> ჩანაწერს (7 კატეგორია).

## სტეკი (უფასო / ღია კოდის)
- **Python 3.13**
- **Embedding:** `intfloat/multilingual-e5-base` (sentence-transformers, ქართულის მხარდაჭერა)
- **Vector store:** Chroma (ლოკალური)
- **LLM:** Gemini `gemini-2.5-flash` (default, უფასო-ტარიფიანი) ან Ollama (სრულად ლოკალური)

## არქიტექტურა
```
faq.json ──> [chunking: 1 FAQ = 1 დოკ.] ──> [e5 embedding] ──> Chroma
                                                                  │
კითხვა ──> [e5 embedding] ──> [top-k retrieval] ───────────────────┘
                                      │
                                      ▼
                       [prompt + კონტექსტი] ──> LLM ──> პასუხი (+ წყაროები)
```

## სწრაფი გაშვება

გარემო და დამოკიდებულებები უკვე დაყენებულია (`venv/`), backend კი კონფიგურირებულია
`.env` ფაილში. ჩატბოტის გასაშვებად საკმარისია:

```powershell
# ტერმინალის ჩატი
.\run.ps1

# ან ვებ-ინტერფეისი (ბრაუზერში)
.\run_web.ps1
```

ორივე სკრიპტი თავად ამოწმებს ვექტორულ ბაზას და საჭიროებისას ააშენებს მას.

> თუ PowerShell სკრიპტის გაშვებას არ უშვებს, ერთხელ გაუშვით:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

## კონფიგურაცია (`.env`)
```
LLM_BACKEND=gemini
GEMINI_API_KEY=<თქვენი_გასაღები>
GEMINI_MODEL=gemini-2.5-flash
```
- გასაღები მიიღება უფასოდ: https://aistudio.google.com → „Get API key“.
- `.env` `.gitignore`-შია — გასაღები რეპოზიტორიაში არ აიტვირთება.

## ხელით გაშვება (დეტალურად)
```powershell
.\venv\Scripts\Activate.ps1     # გარემოს გააქტიურება  →  (venv) prompt
python -m src.ingest            # ვექტორული ბაზის აგება (ერთხელ / მონაცემთა ცვლილებაზე)
python app_cli.py               # ან: streamlit run app_streamlit.py
```
> ⚠️ გააქტიურებული venv-ის შემდეგ ბრძანება არის `python` (და არა `py -3`).
> `py -3` გლობალურ Python-ს უშვებს, რომელშიც პაკეტები არ არის.

### ლოკალური backend (Ollama, სრულად offline)
```powershell
# დააინსტალირეთ Ollama: https://ollama.com
ollama pull gemma2
# .env-ში: LLM_BACKEND=ollama
pip install ollama
```

## ფაილების სტრუქტურა
```
Code/
├── .env                   # backend + API გასაღები (gitignored)
├── data/faq.json          # მონაცემები (29 რეალური Q&A, IBSU FAQ)
├── src/
│   ├── __init__.py        # პაკეტი + UTF-8 კონსოლის fix (Windows)
│   ├── config.py          # ყველა პარამეტრი + .env ჩატვირთვა
│   ├── ingest.py          # მონაცემთა მომზადება + ბაზაში ჩაწერა
│   ├── rag.py             # RAG ბირთვი (retrieve → augment → generate)
│   └── llm.py             # LLM backend (Gemini / Ollama)
├── app_cli.py             # ტერმინალის ჩატი
├── app_streamlit.py       # ვებ-ინტერფეისი
├── run.ps1 / run_web.ps1  # გამშვები სკრიპტები
└── requirements.txt
```

## შემდეგი ნაბიჯები (ნაშრომისთვის)
1. ✅ რეალური მონაცემების შეგროვება IBSU-ის საიტიდან (29 ჩანაწერი, 7 კატეგორია).
2. Evaluation: ტესტ-კითხვების ნაკრები → retrieval-ის სიზუსტე (Precision@k), latency.
3. პარამეტრების ექსპერიმენტი (`TOP_K`, embedding მოდელი) და შედეგების შედარება.
