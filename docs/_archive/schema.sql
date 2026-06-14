-- Defines the tables and indexes inside the database created by Postgres container's env vars.

-- Load the extension for vector, and make sure it doesnt load or re-register twice if it exists
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
    id  BIGSERIAL PRIMARY KEY,
    text    TEXT NOT NULL,
    embedding   vector(1024) NOT NULL,
    -- Used for Citations and Ordering
    session_date    DATE NOT NULL,
    session_label   TEXT NOT NULL,
    chunk_idx   INT NOT NULL

);

-- HNSW is the algorithm used to skim through to find the nearest neighbor. We use cosine because embeddings encode semantic similarity by direction, not magnitude
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);