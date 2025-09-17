import os
import requests
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PDFDownloader:
    def __init__(self, headers):
        self.headers = headers

    def download_pdf(self, arxiv_id, output_dir, max_retries=3, delay=1):
        """
        Download a single arXiv paper as PDF.
        """
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        filename = f"{arxiv_id}.pdf"
        filepath = output_dir / filename

        if filepath.exists():
            logging.info(f"✓ {arxiv_id}: Already exists, skipping")
            return True

        for attempt in range(max_retries):
            try:
                logging.info(f"📥 Downloading {arxiv_id}... (attempt {attempt + 1}/{max_retries})")
                response = requests.get(pdf_url, headers=self.headers, stream=True, timeout=30)
                response.raise_for_status()

                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type:
                    logging.warning(f"❌ {arxiv_id}: Response is not a PDF (content-type: {content_type})")
                    return False

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                logging.info(f"✅ {arxiv_id}: Downloaded successfully ({filepath.stat().st_size} bytes)")
                time.sleep(delay)
                return True

            except requests.exceptions.RequestException as e:
                logging.warning(f"⚠️  {arxiv_id}: Download failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))

            except Exception as e:
                logging.error(f"❌ {arxiv_id}: Unexpected error: {e}")
                return False

        logging.error(f"❌ {arxiv_id}: Failed after {max_retries} attempts")
        return False
