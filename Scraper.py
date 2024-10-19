import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os
import time
import random
from datetime import datetime

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Mozilla/5.0 (Linux; Ubuntu 20.04; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Mozilla/5.0 (Linux; Android 10; SM-J610FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36'
    ]
    return random.choice(user_agents)

def log_error(url, error, error_file='nhs_inform_errors.json'):
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'url': url,
        'error': str(error)
    }
    try:
        if os.path.exists(error_file):
            with open(error_file, 'r+', encoding='utf-8') as f:
                file_data = json.load(f)
                file_data.append(error_data)
                f.seek(0)
                f.truncate()
                json.dump(file_data, f, ensure_ascii=False, indent=2)
        else:
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump([error_data], f, ensure_ascii=False, indent=2)
        print(f"Error logged for URL: {url}")
    except Exception as e:
        print(f"Error logging failed for {url}: {e}")

def scrape_page(url, depth=0, max_depth=0, output_file='nhs_inform_data.json', error_file='nhs_inform_errors.json', session=None, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()

    if depth > max_depth or url in visited_urls:
        return None

    visited_urls.add(url)

    if session is None:
        session = requests.Session()

    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }

    try:
        time.sleep(random.uniform(1, 3))  # Random delay between requests
        print(f"Parsing URL: {url}")  # Print statement for parsed URL
        response = session.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        log_error(url, e, error_file)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    data = {
        'url': url,
        'title': soup.title.string if soup.title else None,
        'content': '',
        'links': []      # Initialize 'links' key as an empty list
    }

    body = soup.body
    
    # Check if the body exists before proceeding
    if body:
        # Create a list to hold all text content
        text_content = []

        # Find all headings and paragraphs within the body tag only
        for element in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
            text_content.append(element.get_text(strip=True))

        # Join all text content into a single string
        data['content'] = ' '.join(text_content)

    # # Collect all text content
    # text_content = []
    # for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
    #     text_content.append(element.get_text(strip=True))
    # data['content'] = ' '.join(text_content)

    # Collect all valid links on the page
    for a_tag in soup.find_all('a', href=True):
        full_url = urljoin(url, a_tag['href'])
        if full_url.startswith('https://www.nhsinform.scot/illnesses-and-conditions/'):
            data['links'].append({
                'text': a_tag.get_text(strip=True),
                'href': full_url
            })
    # data = {
    #     'url': url,
    #     'title': soup.title.string if soup.title else None,
    #     'content': []  # To store content in the order it appears on the page
    # }

    # # Create a list to hold all content in order
    # for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'a']):
    #     if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # If it's a heading
    #         data['content'].append({
    #             'type': 'heading',
    #             'level': element.name,
    #             'text': element.get_text(strip=True)
    #         })
    #     elif element.name == 'p':  # If it's a paragraph
    #         data['content'].append({
    #             'type': 'paragraph',
    #             'text': element.get_text(strip=True)
    #         })
    #     elif element.name == 'img':  # If it's an image
    #         data['content'].append({
    #             'type': 'image',
    #             'src': urljoin(url, element.get('src', '')),
    #             'alt': element.get('alt', '')
    #         })
    #     elif element.name == 'a':  # If it's a link
    #         full_url = urljoin(url, element['href'])
    #         data['content'].append({
    #             'type': 'link',
    #             'text': element.get_text(strip=True),
    #             'href': full_url
    #         })


    # Save the current page data
    save_data(data, output_file)

    # Scrape subpages
    if depth < max_depth:
        for link in data['links']:
            if link['href'].startswith('https://www.nhsinform.scot/illnesses-and-conditions/'):
                subpage_data = scrape_page(link['href'], depth + 1, max_depth, output_file, error_file, session, visited_urls)
                if subpage_data:
                    data['subpages'].append(subpage_data['url'])  # Only store the URL of subpages

    return data

def save_data(data, output_file):
    try:
        if os.path.exists(output_file):
            with open(output_file, 'r+', encoding='utf-8') as f:
                file_data = json.load(f)
                file_data.append(data)
                f.seek(0)
                f.truncate()
                json.dump(file_data, f, ensure_ascii=False, indent=2)
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([data], f, ensure_ascii=False, indent=2)
        print(f"Data saved for URL: {data['url']}")  # Print statement for saved data
    except Exception as e:
        print(f"Error saving data for {data['url']}: {e}")

def main():
    start_url = 'https://www.nhsinform.scot/illnesses-and-conditions/a-to-z/abdominal-aortic-aneurysm/'
    output_file = 'test1.json'
    error_file = 'tester.json'
    
    # Initialize the output and error files with empty lists
    for file in [output_file, error_file]:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump([], f)

    session = requests.Session()
    visited_urls = set()
    scrape_page(start_url, output_file=output_file, error_file=error_file, session=session, visited_urls=visited_urls)

    print(f"Scraping completed. Total unique URLs visited: {len(visited_urls)}")

if __name__ == "__main__":
    main()