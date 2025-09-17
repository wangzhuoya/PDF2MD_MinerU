import requests
from bs4 import BeautifulSoup
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ArxivScraper:
    def __init__(self, user_agent):
        self.headers = {'User-Agent': user_agent}
        self.base_url = 'https://arxiv.org'

    def search(self, query, max_results=50, start=0):
        """
        Searches arXiv for a given query and returns the paper IDs.
        """
        allowed_sizes = [25, 50, 100, 200]
        if max_results not in allowed_sizes:
            logging.warning(f"Invalid size {max_results}. Defaulting to 50. Allowed values are {allowed_sizes}")
            max_results = 50

        params = {
            'query': query,
            'searchtype': 'all',
            'abstracts': 'show',
            'order': '-announced_date_first',
            'size': max_results,
            'start': start
        }
        search_url = f"{self.base_url}/search/"
        logging.info(f"Searching arXiv with URL: {search_url} and params: {params}")
        
        try:
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch search results: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('li', class_='arxiv-result')

        if not search_results:
            logging.warning("No search results found. The page structure might have changed.")
            return []

        arxiv_ids = []
        for result in search_results:
            id_link = result.find('a', string=re.compile(r'^arXiv:'))
            if id_link and id_link.string:
                arxiv_id = id_link.string.strip().split(':')[-1]
                arxiv_ids.append(arxiv_id)
        
        logging.info(f"Found {len(arxiv_ids)} arXiv IDs.")
        return arxiv_ids
