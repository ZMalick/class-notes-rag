# app/retriever.py — query-time retrieval (Day 4, step 1: embed a query)

from sentence_transformers import SentenceTransformer

# Load the SAME model the chunks were embedded with.
# (Different model = vectors in a different "space" = distances are meaningless.)
# BLANK 1: the model name. It's in embedder.py if you need to look it up — looking it up IS the skill.
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# A hard-coded test query for now (later this becomes the real user question).
query = "what is a vector embedding?"

# encode() takes a LIST of texts and returns a LIST of vectors.
# So we pass [query], then grab the first (and only) result.
# normalize_embeddings=True is pre-filled — it must match embedder.py (matters for distances next session).
# BLANK 2: the index that grabs the first vector out of the returned list.
vector = model.encode([query], normalize_embeddings=True)[0]

# Should print 1024 (matches the `embedding vector(1024)` column in the schema).
print(len(vector))
