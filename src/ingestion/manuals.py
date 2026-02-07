"""CLI script to ingest repair manuals from a data directory."""

import argparse
import sys
from pathlib import Path

# Ensure project root on path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.services.chunker import chunk_documents
from src.services.document_loader import load_document
from src.services.vector_store import add_chunks_to_store, get_vector_store


def main():
    parser = argparse.ArgumentParser(description="Ingest repair manuals into the vector store.")
    parser.add_argument(
        "data_dir",
        nargs="?",
        default="data/manuals",
        help="Directory containing PDF and .txt files",
    )
    parser.add_argument("--namespace", default="manuals", help="Vector store namespace")
    args = parser.parse_args()

    base = Path(args.data_dir)
    if not base.exists():
        print(f"Error: Directory {base} does not exist.", file=sys.stderr)
        sys.exit(1)

    files = list(base.rglob("*.pdf")) + list(base.rglob("*.txt"))
    if not files:
        print(f"No PDF or .txt files found in {base}", file=sys.stderr)
        sys.exit(1)

    vs, ns = get_vector_store(namespace=args.namespace)
    all_chunks = []
    for p in files:
        try:
            docs = list(load_document(p, source_type="manual"))
            all_chunks.extend(chunk_documents(docs))
        except Exception as e:
            print(f"Warning: Skipped {p}: {e}", file=sys.stderr)

    if all_chunks:
        add_chunks_to_store(vs, all_chunks)
        print(f"Indexed {len(all_chunks)} chunks from {len(files)} file(s) to namespace '{ns}'.")
    else:
        print("No content extracted.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
