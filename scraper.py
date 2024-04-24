import random

import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
from requests.exceptions import RequestException

# List of User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36"
]

def fetch_page(url, retry_count=3, delay=5):
    """Fetches the content of the page with retries."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    for attempt in range(retry_count):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(response)
            if response.status_code == 200:
                return response.text, response.status_code
        except RequestException as e:
            print(f"Request failed: {e}, retrying ({attempt+1}/{retry_count})")
            sleep(delay)
    return None, None

def parse_page(html):
    """Parses the HTML content of a single page for items."""
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='listing-map-text-readmore')
    data = []
    for item in items:
        name = item.find('h4').get_text(strip=True) if item.find('h4') else 'No Name'
        email = item.find('a', href=lambda href: href and href.startswith('mailto:'))
        email = email['href'][7:] if email else 'No Email'
        phone = item.find('a', href=lambda href: href and href.startswith('tel:'))
        phone = phone.get_text(strip=True) if phone else 'No Phone'
        data.append([name, email, phone])
    return data

def scrape_directory(base_url, start_page, total_pages, output_file, throttle):
    """Scrapes multiple pages, collects the data, and writes it to a CSV file as it is scraped."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Email', 'Phone'])  # Writing header
        page_number = start_page
        while True:
            url = f"{base_url}{page_number}"
            html, status_code = fetch_page(url)
            if status_code == 404:
                print(f"Page {page_number} gave a 404 error, stopping.")
                break
            if html and status_code == 200:
                page_data = parse_page(html)
                for row in page_data:
                    writer.writerow(row)
                print(f"Page {page_number} scraped successfully.")
            else:
                print(f"Failed to fetch page {page_number} with status code: {status_code}")
            page_number += 1
            if total_pages and page_number > total_pages:
                print(f"Reached the maximum limit of {total_pages} pages, stopping.")
                break
            sleep(throttle)

# Main usage
base_url = 'https://www.marealtor.com/realtor-directory/'
start_page = 1
total_pages = None  # Set the total number of pages to scrape, None for all
throttle = 1

scrape_directory(base_url, start_page, total_pages, 'realtors_data.csv', throttle)
print("Data scraping complete, file saved to realtors_data.csv")
