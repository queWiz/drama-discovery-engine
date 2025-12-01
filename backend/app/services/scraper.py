import cloudscraper
from bs4 import BeautifulSoup
import time
import random

URL = "https://mydramalist.com/shows/top"

# Create a scraper instance that mimics a real Chrome browser
scraper = cloudscraper.create_scraper(browser='chrome')

def scrape_top_dramas(num_pages=1):
    """Scrapes top K-dramas from MyDramaList for a given number of pages."""
    all_shows = []
    for page in range(1, num_pages + 1):
        print(f"Scraping page {page}...")
        page_url = f"{URL}?page={page}"
        
        try:
            response = scraper.get(page_url)
            if response.status_code == 403:
                print(f"Blocked (403) on page {page}. Waiting longer...")
                time.sleep(10)
                continue
            response.raise_for_status() 
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        show_boxes = soup.find_all('div', class_='box')
        
        if not show_boxes:
            print(f"Warning: No shows found on page {page}. HTML structure might be different.")

        for box in show_boxes:
            try:
                # FIX 1: Defensive check for title element
                title_header = box.find('h6', class_='title')
                if not title_header:
                    # This box is likely an ad or spacer, skip it
                    continue
                
                title_link = title_header.find('a')
                if not title_link:
                    continue

                title = title_link.text.strip()
                details_link = "https://mydramalist.com" + title_link['href']
                
                # Scrape the details
                show_details = scrape_show_details(details_link)

                if show_details:
                    show_details['title'] = title
                    all_shows.append(show_details)
                    print(f" -> Scraped: {title}")
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                # Print the error but keep going!
                print(f"Skipping a box due to error: {e}")
                continue

    return all_shows

def scrape_show_details(url):
    """Scrapes detailed information from a single show's page."""
    try:
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract synopsis
        synopsis_p = soup.select_one('.show-synopsis > p')
        if not synopsis_p:
            synopsis_div = soup.select_one('.show-synopsis')
            synopsis = synopsis_div.text.strip() if synopsis_div else "No synopsis available."
        else:
            synopsis = synopsis_p.text.strip()

        # Extract genres
        genres_ul = soup.find('ul', class_='list-genres')
        genres = [li.text.strip() for li in genres_ul.find_all('a')] if genres_ul else []

        # FIX 2: Handle Lazy Loaded Images
        # Websites often hide the real URL in 'data-src' to load it later.
        img_element = soup.find('img', class_='img-responsive')
        image_url = ""
        if img_element:
            # Try 'data-src' first, then 'src', then default to empty string
            image_url = img_element.get('data-src') or img_element.get('src') or ""

        return {
            "synopsis": synopsis,
            "genres": genres,
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error fetching details from {url}: {e}")
        return None

if __name__ == '__main__':
    print("Starting scraper...")
    dramas = scrape_top_dramas(num_pages=1) 
    print(f"Successfully scraped {len(dramas)} dramas.")
    if dramas:
        print("\nExample of scraped data:")
        print(dramas[0])