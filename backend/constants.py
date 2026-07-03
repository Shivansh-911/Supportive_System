

CONTENT_HASH_LENGTH  = 64   # SHA-256 hex digest

EMBEDDING_DIMENSIONS = 1536

EMBEDDING_PROVIDER = "openai"
EMBEDDING_MODEL    = "text-embedding-3-small"

HNSW_M               = 16
HNSW_EF_CONSTRUCTION = 64

# --- freshdesk ---
FRESHDESK_IMAGE_URL_PREFIX = "https://s3-ap-south-1.amazonaws.com/ind-cdn.freshdesk.com/data/helpdesk/attachments/production"
FRESHDESK_IMAGE_URL_PREFIX2 = "https://img-cdn.thepublive.com/filters"
# --- chunking ---
CHUNK_TOKENIZER_ENCODING   = "cl100k_base"
CHUNK_MIN_TOKENS           = 150
CHUNK_SINGLE_MAX_TOKENS    = 350
CHUNK_OVERLAP_TOKENS       = 50
CHUNK_OVERLAP_WORDS        = 50
CHUNK_LAST_MIN_WORDS       = 150

# --- process_agent ---
PROCESS_AGENT_PROVIDER   = "openai"
PROCESS_AGENT_CONTEXT_MODEL = "gpt-4o-mini"

# --- question_agent ---
QUESTION_AGENT_PROVIDER    = "openai"
QUESTION_AGENT_ANSWER_MODEL = "gpt-4o"
TOP_K_CHUNKS_VECTOR               = 20
TOP_K_CHUNKS_BM25                 = 20
RRF_K                             = 60
TOP_K_FUSED                       = 10
RRF_VECTOR_WEIGHT                 = 0.7
RRF_BM25_WEIGHT                   = 0.3

# --- llm generation ---
TOP_K_CHUNKS_FOR_LLM              = 5

# --- orchestrator_agent ---
ORCHESTRATOR_AGENT_PROVIDER = "openai"
ORCHESTRATOR_AGENT_MODEL    = "gpt-4o-mini"
