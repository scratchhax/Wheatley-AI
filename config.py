DISCORD_BOT_TOKEN = 'YOUR TOKEN HERE'
API_BASE_URL = 'http://localhost:11434/api'
DEBUG = True  # Set to True for extra logging
MAX_LENGTH = 11000
CHUNK_SIZE = 11000

OLLAMA_PARAMETERS = {
    "num_keep": 48,
    "seed": 42,
    "num_predict": -2,  # Increase to allow for longer summaries
    "top_k": 20,
    "top_p": 0.9,
    "tfs_z": 0.5,
    "typical_p": 0.7,
    "repeat_last_n": 33,
    "temperature": 0.8,
    "repeat_penalty": 1.2,
    "presence_penalty": 1.5,
    "frequency_penalty": 1.0,
    "mirostat": 1,
    "mirostat_tau": 0.8,
    "mirostat_eta": 0.6,
    "penalize_newline": True,
    "numa": False,
    "num_ctx": 11000,  # Increase context length if needed
    "num_batch": 32,
    "num_gpu": 64,
    "main_gpu": 0,
    "low_vram": False,
    "f16_kv": True,
    "vocab_only": False,
    "use_mmap": True,
    "use_mlock": False,
    "num_thread": 8
}

