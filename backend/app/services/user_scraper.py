import cloudscraper
from bs4 import BeautifulSoup
import random
import time

def scrape_user_watchlist(username_or_url):
    """
    Scrapes a user's 'Completed' list from MyDramaList.
    Uses robust browser emulation to bypass Cloudflare 403 on Render.
    """
    # 1. Extract Username
    username = username_or_url
    if "mydramalist.com" in username:
        # Handle cases like "https://mydramalist.com/profile/CashUser"
        # or "https://mydramalist.com/dramalist/CashUser"
        parts = username.split('/')
        # Logic to find the username part
        if 'profile' in parts:
            username = parts[parts.index('profile') + 1]
        elif 'dramalist' in parts:
            username = parts[parts.index('dramalist') + 1]
    
    # Clean query params if any
    if '?' in username:
        username = username.split('?')[0]

    # 2. Construct URL (status=1 is Completed)
    url = f"https://mydramalist.com/dramalist/{username}?status=1"
    print(f"📡 Fetching watchlist for: {username}...")

    # 3. Create a fresh Scraper instance for every request
    # This prevents cookie/session leaking which can trigger bans
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Add a tiny delay to simulate network latency
        time.sleep(random.uniform(0.5, 1.5))

        response = scraper.get(url)
        
        if response.status_code == 403:
            print("❌ Error: 403 Forbidden. Cloudflare blocked the Render IP.")
            print("This is common on free cloud hosting.")
            return []
            
        if response.status_code != 200:
            print(f"❌ Error: Status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 4. Extract Titles
        titles = []
        # MDL Watchlist structure usually puts titles in <td> with class 'title'
        rows = soup.find_all('tr')
        
        for row in rows:
            # Check for the title column
            title_col = row.find('td', class_='title')
            if title_col:
                link = title_col.find('a')
                if link:
                    titles.append(link.text.strip())
        
        # Fallback: Sometimes the layout is different (Card view vs List view)
        if not titles:
            # Try finding .text-primary links inside .box
            card_links = soup.select('.box .text-primary')
            for link in card_links:
                if link.get('href') and '/people/' not in link['href']: # Avoid actor links
                    titles.append(link.text.strip())

        print(f"✅ Found {len(titles)} completed shows.")
        return titles
        
    except Exception as e:
        print(f"❌ Error scraping user list: {e}")
        return []

# LOCAL VERSION

# import cloudscraper
# from bs4 import BeautifulSoup
# import random
# import time

# scraper = cloudscraper.create_scraper(browser='chrome')

# def scrape_user_watchlist(username_or_url):
#     """
#     Scrapes a user's 'Completed' list from MyDramaList.
#     Input: 'https://mydramalist.com/profile/SomeUser' OR 'SomeUser'
#     Returns: List of show titles [String]
#     Uses robust browser emulation to bypass Cloudflare 403 on Render.
#     """
#     # 1. Extract Username
#     if "mydramalist.com" in username_or_url:
#         # Handle full URL (remove trailing slashes)
#         username = username_or_url.rstrip('/').split('/')[-1]
#     else:
#         username = username_or_url
    
#     # 2. Construct Watchlist URL (status=1 means Completed)
#     url = f"https://mydramalist.com/dramalist/{username}?status=1"
    
#     print(f"Fetching watchlist for: {username}...")
    
#     try:
#         response = scraper.get(url)
#         if response.status_code != 200:
#             print(f"Error: Status code {response.status_code}")
#             return []
            
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         titles = []
        
#         # 3. Find Rows based on your HTML snippet
#         # The rows have IDs like "ml52941", "ml288", etc.
#         rows = soup.find_all('tr', id=lambda x: x and x.startswith('ml'))
        
#         for row in rows:
#             # 4. Find the Title Link
#             # HTML: <a class="title text-primary _600" ...><span>18 Again</span></a>
#             title_link = row.find('a', class_='title')
            
#             if title_link:
#                 # Extract the text (e.g., "18 Again")
#                 title_text = title_link.get_text(strip=True)
#                 titles.append(title_text)
                    
#         print(f"Found {len(titles)} completed shows.")
#         return titles
        
#     except Exception as e:
#         print(f"Error scraping user list: {e}")
#         return []