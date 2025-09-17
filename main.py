
import argparse
import os
from pathlib import Path

# We will move the core logic of the scripts into functions here
# For now, we will just define the command structure

from arxiv_scraper import ArxivScraper
from config import HTTP_HEADERS

def search_arxiv(args):
    """Search arXiv and save the paper IDs to a file."""
    print("Searching arXiv...")
    scraper = ArxivScraper(user_agent=HTTP_HEADERS['User-Agent'])
    ids = scraper.search(args.query, max_results=args.size)
    
    if ids:
        with open(args.output, 'w') as f:
            for arxiv_id in ids:
                f.write(f"{arxiv_id}\n")
        print(f"Successfully found {len(ids)} IDs and saved them to {args.output}")
    else:
        print("No IDs found.")


from pdf_downloader import PDFDownloader
from config import HTTP_HEADERS

from pathlib import Path

def download_pdfs(args):
    """Download PDFs from a list of arXiv IDs."""
    print("Downloading PDFs...")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input_file, 'r') as f:
        arxiv_ids = [line.strip() for line in f if line.strip()]

    downloader = PDFDownloader(headers=HTTP_HEADERS)
    successful_downloads = 0
    failed_downloads = 0

    for arxiv_id in arxiv_ids:
        if downloader.download_pdf(arxiv_id, output_dir):
            successful_downloads += 1
        else:
            failed_downloads += 1

    print(f"\nDownload summary:")
    print(f"  Successful: {successful_downloads}")
    print(f"  Failed: {failed_downloads}")


from mineru_converter import MinerUConverter
from config import MINERU_API_TOKEN
import time
from pathlib import Path

def convert_pdfs(args):
    """Batch convert PDFs to Markdown."""
    print("Converting PDFs to Markdown...")
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    converter = MinerUConverter(token=MINERU_API_TOKEN)
    successful_conversions = 0
    failed_conversions = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        try:
            if converter.upload_and_convert_pdf(str(pdf_file), str(output_dir)):
                successful_conversions += 1
            else:
                failed_conversions += 1
        except Exception as e:
            print(f"An error occurred while converting {pdf_file.name}: {e}")
            failed_conversions += 1
        
        if i < len(pdf_files):
            print("Waiting 30 seconds before next conversion...")
            time.sleep(30)


    print(f"\nConversion summary:")
    print(f"  Successful: {successful_conversions}")
    print(f"  Failed: {failed_conversions}")


def main():
    parser = argparse.ArgumentParser(
        description="A command-line tool to download and convert arXiv papers to Markdown."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Search Command ---
    search_parser = subparsers.add_parser(
        "search", help="Search arXiv and get paper IDs."
    )
    search_parser.add_argument("query", type=str, help="The search query.")
    search_parser.add_argument(
        "--size", type=int, default=50, help="Number of results to retrieve."
    )
    search_parser.add_argument(
        "--output",
        type=str,
        default="arxiv_ids.txt",
        help="Output file to save arXiv IDs.",
    )
    search_parser.set_defaults(func=search_arxiv)

    # --- Download Command ---
    download_parser = subparsers.add_parser(
        "download", help="Download PDFs from a list of arXiv IDs."
    )
    download_parser.add_argument(
        "--input-file",
        type=str,
        default="arxiv_ids.txt",
        help="Input file with arXiv IDs.",
    )
    download_parser.add_argument(
        "--output-dir",
        type=str,
        default="data/pdfs",
        help="Directory to save downloaded PDFs.",
    )
    download_parser.set_defaults(func=download_pdfs)

    # --- Convert Command ---
    convert_parser = subparsers.add_parser(
        "convert", help="Batch convert PDFs to Markdown."
    )
    convert_parser.add_argument(
        "--input-dir",
        type=str,
        default="data/pdfs",
        help="Directory with PDFs to convert.",
    )
    convert_parser.add_argument(
        "--output-dir",
        type=str,
        default="data/markdown",
        help="Directory to save Markdown files.",
    )
    convert_parser.set_defaults(func=convert_pdfs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
