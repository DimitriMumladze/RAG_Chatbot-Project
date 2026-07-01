# IBSU მიღების ჩატბოტი — RAG სისტემა

**RAG (Retrieval-Augmented Generation)** არქიტექტურაზე დაფუძნებული ჩატბოტი, რომელიც
შავი ზღვის საერთაშორისო უნივერსიტეტში (IBSU) ჩაბარების მსურველთა კითხვებს ქართულ
ენაზე პასუხობს — უნივერსიტეტის რეალურ მონაცემებზე დაყრდნობით და გამოგონილი პასუხის
გარეშე (ანტი-ჰალუცინაცია).

---

## 🚀 გაშვება (უმარტივესი გზა)

პროექტი უკვე სრულად დაყენებულია. ჩატბოტის გასაშვებად უბრალოდ **ორმაგად დააწკაპუნეთ**
`Code` ფოლდერში:

| ფაილი | რას აკეთებს |
|---|---|
| **`Start-Chatbot-Web.bat`** | ხსნის ვებ-ინტერფეისს ბრაუზერში (რეკომენდებული) |
| **`Start-Chatbot-Terminal.bat`** | ხსნის ჩატს ტერმინალში |

პირველი პასუხი ~1 წუთს იღებს (მოდელი მეხსიერებაში იტვირთება), შემდეგ თითო პასუხი ~6–10 წამია.

> ალტერნატივა PowerShell-იდან: `.\run_web.ps1` (ვები) ან `.\run.ps1` (ტერმინალი).
> თუ სკრიპტი დაბლოკილია: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

---

## 🧱 ტექნოლოგიური სტეკი (უფასო / ლოკალური)
- **Python 3.13**
- **Embedding:** `intfloat/multilingual-e5-base` (sentence-transformers, ქართულის მხარდაჭერა)
- **ვექტორული ბაზა:** ChromaDB (ლოკალური, ფაილური)
- **LLM:** **Ollama `gemma2`** (default, სრულად ლოკალური) — ალტერნატივა: Google Gemini (`gemini-2.5-flash`)
- **ინტერფეისი:** Streamlit (ვები) + CLI

## 📚 მონაცემები
`data/faq.json` — **46 რეალური კითხვა-პასუხი** IBSU-ის ოფიციალური საიტიდან:
- საბაზისო 29 ჩანაწერი — [ხშირად დასმული კითხვები](https://ibsu.edu.ge/ge/faq/) (რეგისტრაცია, მობილობა, სტატუსი, გაცვლა…)
- 17 აბიტურიენტული ჩანაწერი — [სწავლის საფასური](https://ibsu.edu.ge/ge/entrant/tuition-fees/) და [შიდა გრანტები](https://ibsu.edu.ge/ge/entrant/calculation/) (მიღება, საფასურები, გრანტები)

თითოეულ დამატებით ჩანაწერს ახლავს `source` (URL) და `retrieved` (თარიღი). საფასურები/გრანტები
მოცემულია ამოღების თარიღისთვის და შესაძლოა შეიცვალოს.

## 🏗️ არქიტექტურა
```
data/faq.json ──[1 FAQ = 1 chunk]──► [e5 embedding] ──► chroma_store/ (ვექტ. ბაზა)
                                                              │
კითხვა ──► [e5 embedding] ──► [top-k=3 მოძიება] ───────────────┘
                                     │
                                     ▼
                    [prompt + კონტექსტი] ──► LLM (Ollama/Gemini) ──► პასუხი (+ წყაროები)
```
თუ პასუხი კონტექსტში არ მოიძებნა → სისტემა აბრუნებს ფიქსირებულ შეტყობინებას (არ იგონებს).

---

## ⚙️ დაყენება ნულიდან (ახალ კომპიუტერზე)
```powershell
# 1. ვირტუალური გარემო + დამოკიდებულებები
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Ollama (ლოკალური LLM) — https://ollama.com
ollama pull gemma2

# 3. ვექტორული ბაზის აგება
python -m src.ingest
```
> ⚠️ გააქტიურებული venv-ის შემდეგ ბრძანება არის `python` (და არა `py -3`).

## 🔧 კონფიგურაცია (`.env`)
```
LLM_BACKEND=ollama          # ან: gemini
OLLAMA_MODEL=gemma2
GEMINI_API_KEY=<გასაღები>    # მხოლოდ gemini backend-ისთვის (aistudio.google.com)
GEMINI_MODEL=gemini-2.5-flash
```
`.env` `.gitignore`-შია — გასაღები რეპოზიტორიაში არ აიტვირთება. backend-ის გადართვა ერთი ხაზით ხდება.

## 📊 შეფასება (Evaluation)
სისტემის ხარისხის გასაზომად:
```powershell
python -m evaluation.evaluate            # მოძიება + გენერაცია
python -m evaluation.evaluate --no-gen   # მხოლოდ მოძიება (სწრაფი)
```
შედეგები იწერება `evaluation/results.md`-ში. ბოლო გაშვება (Ollama/gemma2, 46 ჩანაწერი):

| მაჩვენებელი | შედეგი |
|---|---|
| Precision@3 | 93% (14/15) |
| Precision@1 | 93% (14/15) |
| in-scope პასუხის სიზუსტე | 80% (12/15) |
| out-of-scope fallback | 100% (4/4) |
| საშ. მოძიება / გენერაცია | ~84 ms / ~9.6 წმ |

## ✏️ ცოდნის ბაზის განახლება
1. დაარედაქტირეთ `data/faq.json` (დაამატეთ/შეცვალეთ ჩანაწერი).
2. გაუშვით `python -m src.ingest` (ან უბრალოდ გაუშვით `run.ps1` — თუ ბაზა აკლია, თავად ააშენებს).

## 📁 ფაილების სტრუქტურა
```
Code/
├── Start-Chatbot-Web.bat      # ორმაგი წკაპით გაშვება (ვები)
├── Start-Chatbot-Terminal.bat # ორმაგი წკაპით გაშვება (ტერმინალი)
├── run.ps1 / run_web.ps1      # PowerShell გამშვებები
├── .env                       # backend + გასაღები (gitignored)
├── .streamlit/config.toml     # ვებ-ინტერფეისის თემა
├── data/faq.json              # 46 რეალური Q&A (ცოდნის ბაზა)
├── chroma_store/              # ვექტორული ბაზა (რეგენერირებადი, gitignored)
├── src/
│   ├── config.py              # ყველა პარამეტრი + .env ჩატვირთვა
│   ├── ingest.py              # მონაცემთა მომზადება → ვექტორული ბაზა
│   ├── rag.py                 # RAG ბირთვი (retrieve → augment → generate)
│   └── llm.py                 # LLM backend (Ollama / Gemini)
├── evaluation/
│   ├── testset.json           # საკონტროლო კითხვები
│   ├── evaluate.py            # Precision@k, fallback, latency
│   └── results.md             # ბოლო შეფასების შედეგები
├── app_cli.py                 # ტერმინალის ჩატი
├── app_streamlit.py           # ვებ-ინტერფეისი
└── requirements.txt
```

## 📝 შენიშვნები
- `chroma_store/` არის **build artifact** — `data/faq.json`-იდან რეგენერირდება; შენახვა არ სჭირდება.
- Windows-ის კონსოლი UTF-8-ზეა გადართული `src/__init__.py`-ში (ქართული ტექსტისთვის).
- ლოკალური მოდელი ხანდახან ქართულ პასუხზე ზედმეტად ფრთხილია (over-refusal) — Gemini backend უკეთ ართმევს თავს.
