import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
MINERU_API_TOKEN = os.getenv("MINERU_API_TOKEN")

# Default paths
DEFAULT_ID_FILE = "arxiv_ids.txt"
DEFAULT_PDF_DIR = "data/pdfs"
DEFAULT_MD_DIR = "data/markdown"

# HTTP Headers
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
