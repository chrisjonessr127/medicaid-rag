"""Ask the indexed fictional demo corpus a question from the terminal."""
import sys
from rag_core import answer_question

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python query.py 'How long is a demo request review?'")
    response, sources = answer_question(" ".join(sys.argv[1:]))
    print("\n" + response + "\n")
    if sources:
        print("Sources:", ", ".join(sorted({name for name, _ in sources})))
