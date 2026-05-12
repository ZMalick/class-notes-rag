from pathlib import Path
import tiktoken

# Constants
CHUNK_SIZE = 500
OVERLAP = 50
STRIDE = CHUNK_SIZE - OVERLAP


def chunk_session(session_folder: Path) -> list[dict]:

    """ This function aims to read the audio_tiny.txt file in the session folder, then, divide the transcript into chunks.
    Chunks are token-based, not character/sentence-based
    It will return dictionaries with metadata, including the date, label, idx
    The metadata comes from the folder name, not the file content """


    # ------------- Obtain the Audio Transcript and gives token ints -------------

    transcript_path = session_folder / "audio_tiny.txt"

    full_text = transcript_path.read_text(encoding="utf-8")
    print(f"Read {len(full_text)} characters")

    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(full_text)
    print(f"Encoded into {len(tokens)} tokens")

    # --------------------------------------------------------------------------

    # -------------------Begin the Chunking Process-----------------------------

    chunks = []
    start = 0

    parts = session_folder.name.split("-")
    # parts = ["2026", "04", "20", "week2, "day1""]

    session_date = "-".join(parts[:3])
    # 2026-04-20
    session_label = f"Week {parts[3][4:]} Day {parts[4][3:]}" 
    # sesion_label = Week 2 Day 1

    chunk_idx = 0
    while start < len(tokens):
        chunk_tokens = tokens[start: start + CHUNK_SIZE]
        chunk_text = encoder.decode(chunk_tokens) 
        chunks.append({
            "text": chunk_text,
            "session_date": session_date,
            "session_label": session_label,
            "chunk_idx": chunk_idx


        })
        start += STRIDE
        chunk_idx += 1


    return chunks



if __name__ == "__main__":

    session_folder = Path(r"C:\Users\zaidm\OneDrive\Desktop\Personal\the AI assistant Practice\Executive Assistant\data\learning\agentic-ai-bootcamp\2026-04-20-week2-day1")
    chunks = chunk_session(session_folder)

    print(f"Built {len(chunks)} chunks")
    print("--- Chunk 0, first 150 chars ---")
    print(chunks[0]["text"][:150])
    print("--- Chunk 0, LAST 150 chars ---")
    print(chunks[0]["text"][-150:])
    print("--- Chunk 1, first 150 chars ---")
    print(chunks[1]["text"][:150])

    print("--- Chunk 0 full dict (metadata) ---")
    print({k: v for k, v in chunks[0].items() if k != "text"})