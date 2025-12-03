import cloudscraper
from bs4 import BeautifulSoup
import time
import random
import re

# NEW URL: Advanced Search (Korean, Drama, Completed, Top Rated)
# This allows deep pagination (hundreds of pages)
URL = "https://mydramalist.com/search?adv=titles&ty=68&co=3&st=3&so=top"

scraper = cloudscraper.create_scraper(browser='chrome')

def scrape_reviews(base_url):
    """Visits the /reviews page and fetches top 3 reviews."""
    review_url = base_url + "/reviews"
    try:
        # Reduced sleep slightly for efficiency, but kept safe
        time.sleep(random.uniform(0.5, 1.5)) 
        response = scraper.get(review_url)
        if response.status_code != 200: return ""

        soup = BeautifulSoup(response.text, 'html.parser')
        review_divs = soup.find_all('div', class_='review-body')
        
        top_reviews = []
        for div in review_divs[:3]:
            text = div.get_text(separator=" ", strip=True)
            top_reviews.append(text)
            
        return " ||| ".join(top_reviews)
    except Exception as e:
        print(f"Error scraping reviews: {e}")
        return ""

def scrape_show_details(url):
    try:
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Synopsis
        synopsis_p = soup.select_one('.show-synopsis > p')
        synopsis = synopsis_p.text.strip() if synopsis_p else ""

        # 2. Image (Using the official Schema tag)
        image_url = ""
        poster_img = soup.find('img', attrs={'itempropx': 'image'})
        if poster_img:
            image_url = poster_img.get('src')
        if image_url and '?' in image_url: 
            image_url = image_url.split('?')[0]

        # 3. Reviews
        reviews_text = scrape_reviews(url)

        # 4. Genres & Tags
        genres = []
        tags = []
        
        genres_li = soup.find('li', class_='show-genres')
        if genres_li:
            genres = [a.text.strip() for a in genres_li.find_all('a') if a.text.strip()]

        tags_li = soup.find('li', class_='show-tags')
        if tags_li:
            tags = [
                a.text.strip() for a in tags_li.find_all('a') 
                if a.text.strip() and "Vote tags" not in a.text
            ]

        # 5. Rating
        rating = 0.0
        score_label = soup.find('b', string='Score:')
        if score_label and score_label.parent:
            full_text = score_label.parent.get_text()
            try:
                score_text = full_text.replace('Score:', '').strip().split(' ')[0]
                rating = float(score_text)
            except:
                pass
        
        if rating == 0.0:
            rating_box = soup.find('div', class_='box deep-orange') or soup.find('div', class_='box light-blue')
            if rating_box:
                try: rating = float(rating_box.text.strip())
                except: pass

        # 6. YEAR (NEW LOGIC)
        year = 0
        # Look for the "Aired:" label in the sidebar
        aired_label = soup.find('b', string='Aired:')
        if aired_label and aired_label.parent:
            aired_text = aired_label.parent.get_text() # e.g. "Aired: May 14, 2021"
            # Use Regex to find a 4-digit number
            match = re.search(r'\d{4}', aired_text)
            if match:
                year = int(match.group(0))

        return {
            "synopsis": synopsis,
            "image_url": image_url,
            "reviews": reviews_text,
            "genres": genres,   
            "tags": tags,       
            "rating": rating,
            "year": year
        }
    except Exception as e:
        print(f"Error fetching details from {url}: {e}")
        return None

def scrape_top_dramas(num_pages=1, existing_titles=set()):
    all_shows = []
    
    for page in range(1, num_pages + 1):
        print(f"--- Scraping Page {page}/{num_pages} ---")
        
        # 1. Base Sleep: Wait 3-5 seconds between list pages
        time.sleep(random.uniform(3, 5))
        
        # 2. "Cool Down" Break: Every 5 pages, take a break
        if page % 5 == 0:
            print("☕ Taking a 20s break to avoid detection...")
            time.sleep(20)

        # UPDATED URL LOGIC: Use '&' because the URL already has '?'
        page_url = f"{URL}&page={page}"
        
        try:
            response = scraper.get(page_url)
            if response.status_code == 403:
                print("⚠️  403 Forbidden. Waiting 60s...")
                time.sleep(60)
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # The search results also use 'div.box', so this selector still works!
            show_boxes = soup.find_all('div', class_='box')
            
            if not show_boxes:
                print(f"⚠️  No shows found on page {page}. Stopping.")
                break

            for box in show_boxes:
                try:
                    title_header = box.find('h6', class_='title')
                    if not title_header: continue
                    title_link = title_header.find('a')
                    if not title_link: continue

                    title = title_link.text.strip()

                    # --- OPTIMIZATION CHECK ---
                    if title in existing_titles:
                        print(f"⏩ Skipping existing: {title}")
                        continue
                    # --------------------------

                    details_link = "https://mydramalist.com" + title_link['href']
                    
                    show_details = scrape_show_details(details_link)
                    if show_details:
                        show_details['title'] = title
                        all_shows.append(show_details)
                        print(f" -> Scraped: {title}")
                    
                    # Random sleep between shows
                    time.sleep(random.uniform(2, 4))
                except Exception:
                    continue
        except Exception as e:
            print(f"Page error: {e}")
            continue
            
    return all_shows


# import cloudscraper
# from bs4 import BeautifulSoup
# import time
# import random

# URL = "https://mydramalist.com/shows/top_korean_dramas"

# # Create a scraper instance that mimics a real Chrome browser
# scraper = cloudscraper.create_scraper(browser='chrome')

# def scrape_top_dramas(num_pages=1):
#     """Scrapes top K-dramas from MyDramaList for a given number of pages."""
#     all_shows = []
#     for page in range(1, num_pages + 1):
#         print(f"Scraping page {page}...")

#         # 1. Base Sleep: Wait 3-6 seconds between list pages
#         time.sleep(random.uniform(3, 6))
        
#         # 2. "Cool Down" Break: Every 2 pages, take a long break (15-30 seconds)
#         # This makes you look like a human going to get coffee.
#         if page % 2 == 0:
#             print("☕ Taking a coffee break to avoid detection...")
#             time.sleep(random.uniform(15, 30))
#         page_url = f"{URL}?page={page}"
        
#         try:
#             response = scraper.get(page_url)
#             if response.status_code == 403:
#                 print(f"Blocked (403) on page {page}. Waiting longer...")
#                 time.sleep(10)
#                 continue
#             response.raise_for_status() 
#         except Exception as e:
#             print(f"Error fetching page {page}: {e}")
#             continue

#         soup = BeautifulSoup(response.text, 'html.parser')
#         show_boxes = soup.find_all('div', class_='box')
        
#         if not show_boxes:
#             print(f"Warning: No shows found on page {page}. HTML structure might be different.")

#         for box in show_boxes:
#             try:
#                 # FIX 1: Defensive check for title element
#                 title_header = box.find('h6', class_='title')
#                 if not title_header:
#                     # This box is likely an ad or spacer, skip it
#                     continue
                
#                 title_link = title_header.find('a')
#                 if not title_link:
#                     continue

#                 title = title_link.text.strip()
#                 details_link = "https://mydramalist.com" + title_link['href']
                
#                 # Scrape the details
#                 show_details = scrape_show_details(details_link)

#                 if show_details:
#                     show_details['title'] = title
#                     all_shows.append(show_details)
#                     print(f" -> Scraped: {title}")
                
#                 time.sleep(random.uniform(2, 4))
                
#             except Exception as e:
#                 # Print the error but keep going!
#                 print(f"Skipping a box due to error: {e}")
#                 continue

#     return all_shows
    
# def scrape_reviews(base_url):
#     """
#     Given a show URL (e.g., .../move-to-heaven), 
#     visits the /reviews page and fetches top 3 reviews.
#     """
#     review_url = base_url + "/reviews"
#     try:
#         # Add a small sleep to be polite
#         time.sleep(random.uniform(1, 2))
#         response = scraper.get(review_url)
        
#         # If reviews page doesn't exist or is blocked
#         if response.status_code != 200:
#             return ""

#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Find all divs with class 'review-body'
#         review_divs = soup.find_all('div', class_='review-body')
        
#         # Take the top 3 reviews
#         top_reviews = []
#         for div in review_divs[:3]:
#             # Clean up the text (remove extra whitespace)
#             text = div.get_text(separator=" ", strip=True)
#             top_reviews.append(text)
            
#         # Join them into one giant block of text
#         return " ||| ".join(top_reviews)
        
#     except Exception as e:
#         print(f"Error scraping reviews for {base_url}: {e}")
#         return ""

# def scrape_show_details(url):
#     """Scrapes detailed information including reviews."""
#     try:
#         response = scraper.get(url)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # 1. Synopsis
#         synopsis_p = soup.select_one('.show-synopsis > p')
#         if not synopsis_p:
#             synopsis_div = soup.select_one('.show-synopsis')
#             synopsis = synopsis_div.text.strip() if synopsis_div else "No synopsis available."
#         else:
#             synopsis = synopsis_p.text.strip()

#         # 2. Genres
#         genres_ul = soup.find('ul', class_='list-genres')
#         genres = [li.text.strip() for li in genres_ul.find_all('a')] if genres_ul else []

#         # 3. Image
#         image_url = ""
#         poster_img = soup.find('img', attrs={'itempropx': 'image'})
        
#         if poster_img:
#             image_url = poster_img.get('src')
#         else:
#             cover_div = soup.find('div', class_='film-cover')
#             if cover_div:
#                 img = cover_div.find('img')
#                 if img:
#                     image_url = img.get('src') or img.get('data-src')

#         # Clean the URL (sometimes they have query params like ?v=1 we don't need)
#         if image_url and '?' in image_url:
#             image_url = image_url.split('?')[0]
            
#         # 4. Reviews (NEW)
#         # We pass the URL of the show page, and the function handles adding "/reviews"
#         reviews_text = scrape_reviews(url)

#         # 5. Scrape Genres, Tags, and Rating from the Sidebar
#         genres = []
#         tags = []
#         rating = 0.0

#         # Target the specific list item for Genres
#         genres_li = soup.find('li', class_='show-genres')
#         if genres_li:
#             # Get all links, but ignore any that might be empty
#             genres = [a.text.strip() for a in genres_li.find_all('a') if a.text.strip()]

#         # Target the specific list item for Tags
#         tags_li = soup.find('li', class_='show-tags')
#         if tags_li:
#             # Get all links, but FILTER OUT the "(Vote tags)" link
#             tags = [
#                 a.text.strip() for a in tags_li.find_all('a') 
#                 if a.text.strip() and "Vote tags" not in a.text
#             ]

#         # --- Get Rating ---
#         # Look for the rating box (class usually varies by score color)
#         # We try finding the box by the specific structure
#         rating_box = soup.find('div', class_='box deep-orange') # High rating
#         if not rating_box:
#              rating_box = soup.find('div', class_='box light-blue') # Mid rating
        
#         if rating_box:
#             try:
#                 rating = float(rating_box.text.strip())
#             except:
#                 rating = 0.0

#          # Method B: Fallback to the list item (The HTML you provided)
#         # Look for <b class="inline">Score:</b>
#         if rating == 0.0:
#             score_label = soup.find('b', string='Score:')
#             if score_label and score_label.parent:
#                 # The text usually looks like "Score: 9.1 (scored by...)"
#                 # We need to extract just the number
#                 full_text = score_label.parent.get_text()
#                 try:
#                     # Remove "Score:" and take the first part
#                     score_text = full_text.replace('Score:', '').strip().split(' ')[0]
#                     rating = float(score_text)
#                 except:
#                     pass

#         return {
#             "synopsis": synopsis,
#             "genres": genres,
#             "image_url": image_url,
#             "reviews": reviews_text,
#             "tags": tags,       # Crucial for Underrated feature
#             "rating": rating    # Crucial for Underrated feature
#         }
#     except Exception as e:
#         print(f"Error fetching details from {url}: {e}")
#         return None

# if __name__ == '__main__':
#     print("Starting scraper...")
#     dramas = scrape_top_dramas(num_pages=1) 
#     print(f"Successfully scraped {len(dramas)} dramas.")
#     if dramas:
#         print("\nExample of scraped data:")
#         print(dramas[0])