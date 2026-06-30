"""src — RAG ჩატბოტის ძირითადი პაკეტი."""
import sys

# Windows-ის კონსოლი ნაგულისხმევად cp1252-ს იყენებს და ქართულ ასოებს ვერ ბეჭდავს.
# ვაიძულებთ UTF-8-ს, რომ print()/input() ქართულ ტექსტს უმტყუნებლად ამუშავებდეს.
for _stream in (sys.stdout, sys.stdin, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass