"""
evaluate.py — სისტემის ავტომატური შეფასება საკონტროლო ნაკრებზე.

ზომავს:
  • Precision@3 და Precision@1 — რამდენად ხშირად ხვდება სწორი ჩანაწერი
    მოძიებულ top-3 (ან top-1) შედეგში (in-scope კითხვებზე);
  • fallback-ის სიზუსტე — out-of-scope კითხვებზე სისტემა იგონებს თუ არა
    პასუხს, თუ სწორად აბრუნებს ფიქსირებულ შეტყობინებას;
  • დაყოვნება (latency) — მოძიებისა და გენერაციის საშუალო დრო.

გაშვება:
    python -m evaluation.evaluate            # სრული (მოძიება + გენერაცია)
    python -m evaluation.evaluate --no-gen   # მხოლოდ მოძიება (სწრაფი)

შედეგი იწერება კონსოლში და ფაილში evaluation/results.md (ცხრილი ნაშრომის
მე-3 თავისთვის).
"""
import argparse
import json
import os
import time

from src import config
from src import llm
from src.rag import RAGPipeline, SYSTEM_PROMPT

TESTSET_PATH = os.path.join(os.path.dirname(__file__), "testset.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.md")

# fallback-ის ამომცნობი ფრაგმენტი (FALLBACK_ANSWER-ის ბირთვი)
FALLBACK_MARK = "ვერ ვიპოვე"


def is_fallback(answer: str) -> bool:
    return FALLBACK_MARK in (answer or "")


def load_testset():
    with open(TESTSET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["questions"]


def run(generate: bool):
    rag = RAGPipeline()
    questions = load_testset()

    # გენერაციის გახურება — პირველი გამოძახება მოდელს მეხსიერებაში ტვირთავს,
    # ამიტომ მისი დრო არ უნდა ჩაითვალოს საშუალოში.
    if generate:
        print("→ მოდელის გახურება (warmup)...", flush=True)
        try:
            llm.generate(SYSTEM_PROMPT, "კონტექსტი: ცდა\n\nკითხვა: გამარჯობა\nპასუხი:")
        except Exception as e:
            print(f"  ⚠ გენერაცია მიუწვდომელია ({e}). ვაგრძელებ მხოლოდ მოძიებით.")
            generate = False

    rows = []
    print(f"\n→ ფასდება {len(questions)} კითხვა "
          f"({'მოძიება + გენერაცია' if generate else 'მხოლოდ მოძიება'})\n", flush=True)

    for i, item in enumerate(questions, 1):
        q = item["q"]
        expected = item["expected_id"]            # None → out-of-scope
        in_scope = expected is not None

        t0 = time.time()
        hits = rag.retrieve(q)
        ret_ms = (time.time() - t0) * 1000

        top_ids = [h["id"] for h in hits]
        sim_top = hits[0]["similarity"] if hits else None

        # in-scope: მოხვდა თუ არა მოსალოდნელი ჩანაწერი top-3 / top-1-ში
        found3 = in_scope and expected in top_ids
        found1 = in_scope and top_ids[:1] == [expected]
        rank = (top_ids.index(expected) + 1) if found3 else None

        answer, gen_ms, fb = None, None, None
        if generate:
            context = rag.build_context(hits)
            prompt = f"კონტექსტი:\n{context}\n\nკითხვა: {q}\nპასუხი:"
            t1 = time.time()
            answer = llm.generate(SYSTEM_PROMPT, prompt)
            gen_ms = (time.time() - t1) * 1000
            fb = is_fallback(answer)

        rows.append({
            "q": q, "in_scope": in_scope, "expected": expected,
            "top_ids": top_ids, "found3": found3, "found1": found1,
            "rank": rank, "sim_top": sim_top, "ret_ms": ret_ms,
            "gen_ms": gen_ms, "is_fallback": fb, "answer": answer,
        })

        tag = "IN " if in_scope else "OUT"
        mark = "✓" if (found3 if in_scope else fb) else "✗"
        extra = f" rank={rank}" if rank else ""
        gtxt = f", gen={gen_ms:.0f}ms" if gen_ms is not None else ""
        print(f"[{i:2}/{len(questions)}] {tag} {mark} sim={sim_top}{extra}"
              f"  (ret={ret_ms:.0f}ms{gtxt})  {q}", flush=True)

    return rows, generate


def summarize(rows, generated):
    ins = [r for r in rows if r["in_scope"]]
    outs = [r for r in rows if not r["in_scope"]]

    p_at_3 = sum(r["found3"] for r in ins) / len(ins) if ins else 0
    p_at_1 = sum(r["found1"] for r in ins) / len(ins) if ins else 0
    fb_rate = (sum(bool(r["is_fallback"]) for r in outs) / len(outs)
               if (outs and generated) else None)

    # end-to-end წარმატება in-scope-ზე: სწორი წყარო მოიძებნა ДА მოდელმა
    # რეალური პასუხი გასცა (და არა fallback). ეს იჭერს მოდელის "ზედმეტ უარს".
    ans_ok = (sum(1 for r in ins if r["found3"] and not r["is_fallback"]) / len(ins)
              if (ins and generated) else None)

    avg_ret = sum(r["ret_ms"] for r in rows) / len(rows) if rows else 0
    gen_vals = [r["gen_ms"] for r in rows if r["gen_ms"] is not None]
    avg_gen = sum(gen_vals) / len(gen_vals) if gen_vals else None

    return {
        "n_in": len(ins), "n_out": len(outs),
        "p_at_3": p_at_3, "p_at_1": p_at_1, "fb_rate": fb_rate,
        "ans_ok": ans_ok, "avg_ret": avg_ret, "avg_gen": avg_gen,
    }


def print_summary(s):
    print("\n" + "=" * 60)
    print("შეჯამება")
    print("=" * 60)
    print(f"in-scope კითხვები:   {s['n_in']}")
    print(f"  Precision@3:       {s['p_at_3']*100:.0f}%  "
          f"({round(s['p_at_3']*s['n_in'])}/{s['n_in']})")
    print(f"  Precision@1:       {s['p_at_1']*100:.0f}%  "
          f"({round(s['p_at_1']*s['n_in'])}/{s['n_in']})")
    if s["ans_ok"] is not None:
        print(f"  პასუხის სიზუსტე:   {s['ans_ok']*100:.0f}%  "
              f"({round(s['ans_ok']*s['n_in'])}/{s['n_in']})  [სწორი წყარო + რეალური პასუხი]")
    print(f"out-of-scope კითხვები: {s['n_out']}")
    if s["fb_rate"] is not None:
        print(f"  fallback სიზუსტე:  {s['fb_rate']*100:.0f}%  "
              f"({round(s['fb_rate']*s['n_out'])}/{s['n_out']})")
    else:
        print("  fallback სიზუსტე:  — (გენერაცია გამოტოვებულია)")
    print(f"საშ. მოძიების დრო:   {s['avg_ret']:.0f} ms")
    if s["avg_gen"] is not None:
        print(f"საშ. გენერაციის დრო: {s['avg_gen']:.0f} ms")


def write_markdown(rows, s, generated):
    lines = []
    lines.append("# შეფასების შედეგები\n")
    lines.append(f"backend: `{config.LLM_BACKEND}`  |  "
                 f"model: `{config.OLLAMA_MODEL if config.LLM_BACKEND=='ollama' else config.GEMINI_MODEL}`  |  "
                 f"TOP_K = {config.TOP_K}  |  embedding: `{config.EMBEDDING_MODEL}`\n")

    lines.append("## შეჯამება\n")
    lines.append("| მაჩვენებელი | მნიშვნელობა |")
    lines.append("|---|---|")
    lines.append(f"| in-scope კითხვები | {s['n_in']} |")
    lines.append(f"| Precision@3 | {s['p_at_3']*100:.0f}% ({round(s['p_at_3']*s['n_in'])}/{s['n_in']}) |")
    lines.append(f"| Precision@1 | {s['p_at_1']*100:.0f}% ({round(s['p_at_1']*s['n_in'])}/{s['n_in']}) |")
    if s["ans_ok"] is not None:
        lines.append(f"| in-scope პასუხის სიზუსტე | {s['ans_ok']*100:.0f}% ({round(s['ans_ok']*s['n_in'])}/{s['n_in']}) |")
    lines.append(f"| out-of-scope კითხვები | {s['n_out']} |")
    if s["fb_rate"] is not None:
        lines.append(f"| fallback სიზუსტე | {s['fb_rate']*100:.0f}% ({round(s['fb_rate']*s['n_out'])}/{s['n_out']}) |")
    lines.append(f"| საშ. მოძიების დრო | {s['avg_ret']:.0f} ms |")
    if s["avg_gen"] is not None:
        lines.append(f"| საშ. გენერაციის დრო | {s['avg_gen']:.0f} ms |")

    lines.append("\n## დეტალები\n")
    head = "| # | ტიპი | კითხვა | მოსალ. | top-3 | rank | მსგ. |"
    sep = "|---|---|---|---|---|---|---|"
    if generated:
        head = head + " fallback |"
        sep = sep + "---|"
    lines.append(head)
    lines.append(sep)
    for i, r in enumerate(rows, 1):
        tp = "in" if r["in_scope"] else "out"
        exp = r["expected"] or "—"
        rank = r["rank"] or "—"
        row = (f"| {i} | {tp} | {r['q']} | {exp} | "
               f"{', '.join(r['top_ids'])} | {rank} | {r['sim_top']} |")
        if generated:
            row = row + f" {'fallback' if r['is_fallback'] else 'პასუხი'} |"
        lines.append(row)

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n✓ შედეგები ჩაიწერა: {RESULTS_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-gen", action="store_true",
                    help="გამოტოვე გენერაცია, მხოლოდ მოძიების შეფასება")
    args = ap.parse_args()

    rows, generated = run(generate=not args.no_gen)
    s = summarize(rows, generated)
    print_summary(s)
    write_markdown(rows, s, generated)


if __name__ == "__main__":
    main()
