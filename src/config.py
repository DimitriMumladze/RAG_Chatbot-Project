"""
config.py — სისტემის ცენტრალური პარამეტრები.
ერთ ადგილას თავმოყრილი პარამეტრები აადვილებს ექსპერიმენტებს (მაგ. top_k-ის ან
embedding მოდელის შეცვლა) — ეს ნაშრომის „შედეგების“ თავისთვისაც მოსახერხებელია.
"""
import os

# ── გზები ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "faq.json")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_store")  # ლოკალური ვექტ. ბაზის საცავი
COLLECTION_NAME = "ibsu_faq"

# ── Embedding მოდელი (ლოკალური, უფასო, მრავალენოვანი) ─────────────────
# multilingual-e5 მოითხოვს პრეფიქსებს: "query: " და "passage: "
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "

# ── Retrieval ────────────────────────────────────────────────────────
TOP_K = 3  # რამდენი ყველაზე რელევანტური ჩანაწერი ამოვიღოთ კონტექსტისთვის

# ── LLM backend ──────────────────────────────────────────────────────
# "ollama" — სრულად ლოკალური (default); "gemini" — უფასო-ტარიფიანი API
LLM_BACKEND = os.environ.get("LLM_BACKEND", "ollama")

# Ollama (ლოკალური)
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma2")

# Gemini (არასავალდებულო fallback) — API გასაღები გარემოს ცვლადიდან
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── ფიქსირებული პასუხი, როცა ინფ. კონტექსტში არ მოიძებნა ──────────────
FALLBACK_ANSWER = (
    "ბოდიში, ამ კითხვაზე პასუხი ჩემს ბაზაში ვერ ვიპოვე. "
    "გთხოვთ, მიმართოთ უნივერსიტეტის ოფიციალურ საიტს ან მიღების ოფისს."
)
