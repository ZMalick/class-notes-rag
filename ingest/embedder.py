# Walks every bootcamp session folder, chunks each transcript, and produces
# one flat list of chunk dicts ready for embedding.
from pathlib import Path
from ingest.chunker import chunk_session
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import os
import psycopg
from pgvector.psycopg import register_vector

load_dotenv()

# Parent of the dated session folders. Lives outside this project — under
# EA's data/learning/ area. See project AGENTS.md for the data-source rules.
DATA_DIR = Path(r"C:\Users\zaidm\OneDrive\Desktop\Personal\the AI assistant Practice\Executive Assistant\data\learning\agentic-ai-bootcamp")


def main() -> None:
    all_chunks: list[dict] = []

    # iterdir() yields EVERY entry inside DATA_DIR — folders AND loose files
    # (README.md, transcribe.log, etc.). Two filters below trim it down.
    for entry in DATA_DIR.iterdir():
        # Filter 1: keep folders only; drop loose files.
        if not entry.is_dir():
            continue
        # Filter 2: keep folders that actually contain a transcript.
        # Week 4 + Week 5 folders exist but their audio hasn't been transcribed yet.
        transcript = entry / "audio_tiny.txt"
        if not transcript.exists():
            print(f"SKIP {entry.name}: no audio_tiny.txt")
            continue
        chunks = chunk_session(entry)
        # extend (not append) — flatten the 4 per-session lists into one big list.
        all_chunks.extend(chunks)

    print(f"Collected {len(all_chunks)} chunks across all sessions")

    model = SentenceTransformer("BAAI/bge-large-en-v1.5") 
    vectors = model.encode(
        [c["text"] for c in all_chunks], # list of just the text strings
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    print(f"Embedded {len(vectors)} chunks, each {len(vectors[0])}-dim")
    
    with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for chunk, vector in zip(all_chunks, vectors):
                cur.execute(
                    "INSERT INTO chunks (text, embedding, session_date, session_label, chunk_idx) VALUES (%s, %s, %s, %s, %s)",
                    (chunk["text"], vector, chunk["session_date"], chunk["session_label"], chunk["chunk_idx"]),

                ) 
        print(f"Inserted {len(all_chunks)} rows into chunks table")    





if __name__ == "__main__":
    main()