import os

DATA_DIR = os.getenv("DATA_DIR", "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
INDEX_DIR = os.path.join(DATA_DIR, "index")

# Use env var if set; otherwise use provided key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "CF2DvjIoshzasO0mtBkPj44fo2nXDwPk")

# Models
EMBED_MODEL = os.getenv("EMBED_MODEL", "mistral-embed")
CHAT_MODEL = os.getenv("CHAT_MODEL", "mistral-small-latest")

# Chunking knobs
CHUNK_SIZE_CHARS = 1200
CHUNK_OVERLAP_CHARS = 200

# Retrieval knobs
TOP_K = 6
SEMANTIC_MIN_SIM = 0.25  # evidence threshold (tune as needed)

HYBRID_WEIGHT_SEM = 0.7
HYBRID_WEIGHT_KW = 0.3
