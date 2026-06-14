"""
llm.py — LLM-ის აბსტრაქცია. ერთი ფუნქცია generate(), ორი backend-ით:
  - "ollama" (default): სრულად ლოკალური, უფასო
  - "gemini": უფასო-ტარიფიანი API (ქართულის უკეთესი ხარისხი)

backend ირჩევა config.LLM_BACKEND-ით (გარემოს ცვლადი LLM_BACKEND).
"""
from src import config


def _generate_ollama(system: str, user: str) -> str:
    """ლოკალური მოდელი Ollama-ს გავლით (საჭიროა გაშვებული ollama serve)."""
    import ollama
    resp = ollama.chat(
        model=config.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        options={"temperature": 0.2},  # დაბალი temp — ნაკლები ჰალუცინაცია
    )
    return resp["message"]["content"].strip()


def _generate_gemini(system: str, user: str) -> str:
    """უფასო-ტარიფიანი Gemini API (საჭიროა GEMINI_API_KEY)."""
    import google.generativeai as genai
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY არ არის მითითებული.")
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        config.GEMINI_MODEL, system_instruction=system
    )
    resp = model.generate_content(
        user, generation_config={"temperature": 0.2}
    )
    return resp.text.strip()


def generate(system: str, user: str) -> str:
    """შერჩეული backend-ით პასუხის გენერაცია."""
    if config.LLM_BACKEND == "gemini":
        return _generate_gemini(system, user)
    return _generate_ollama(system, user)
