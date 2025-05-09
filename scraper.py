import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import deque
from typing import List, Dict, Optional
import json

def scrape_website(start_url: str, max_depth: int = 3, delay: float = 0.5) -> List[Dict]:
    """
    Scrapes a website starting from the given URL, extracting text content and following links.

    Args:
        start_url: The URL to begin scraping from.
        max_depth: The maximum depth to traverse links (0 for only the start URL).
        delay: Time in seconds to wait between requests to be respectful.

    Returns:
        A list of dictionaries, where each dictionary contains the 'url' and 'text'
        of a scraped page.
    """

    base_url = urlparse(start_url).netloc
    visited_urls = set()
    queue = deque([(start_url, 0)])  # (url, depth)
    scraped_data: List[Dict] = []

    print(f"Starting website scraping from: {start_url}")

    while queue:
        current_url, depth = queue.popleft()

        if current_url in visited_urls:
            print(f"Skipping already visited: {current_url}")
            continue

        print(f"Scraping: {current_url} (Depth: {depth})")
        visited_urls.add(current_url)

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content
            text_content = ' '.join(soup.stripped_strings)
            if text_content:
                scraped_data.append({"url": current_url, "text": text_content})

            # Find and queue links (if within max_depth)
            if depth < max_depth:
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(current_url, link['href'])
                    parsed_url = urlparse(absolute_url)
                    if parsed_url.netloc == base_url and absolute_url not in visited_urls:
                        queue.append((absolute_url, depth + 1))

            time.sleep(delay)  # Be nice to the server

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {current_url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {current_url}: {e}")

    print(f"Scraping finished. Found {len(scraped_data)} pages of content.")
    return scraped_data


def save_scraped_data(data: List[Dict], filename: str = "scraped_data.json") -> None:
    """Saves the scraped data to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Scraped data saved to {filename}")
    except Exception as e:
        print(f"Error saving scraped data: {e}")


if __name__ == '__main__':
    target_url = "https://34ml.com/"  # Replace with the homepage URL you want to scrape
    scraped_data = scrape_website(target_url, max_depth=2, delay=0.2)  # Adjust max_depth and delay as needed
    save_scraped_data(scraped_data)