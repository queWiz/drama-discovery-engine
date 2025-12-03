import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper(browser='chrome')

def scrape_user_watchlist(username_or_url):
    """
    Scrapes a user's 'Completed' list from MyDramaList.
    Input: 'https://mydramalist.com/profile/SomeUser' OR 'SomeUser'
    Returns: List of show titles [String]
    """
    # 1. Extract Username
    if "mydramalist.com" in username_or_url:
        # Handle full URL (remove trailing slashes)
        username = username_or_url.rstrip('/').split('/')[-1]
    else:
        username = username_or_url
    
    # 2. Construct Watchlist URL (status=1 means Completed)
    url = f"https://mydramalist.com/dramalist/{username}?status=1"
    
    print(f"Fetching watchlist for: {username}...")
    
    try:
        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titles = []
        
        # 3. Find Rows based on your HTML snippet
        # The rows have IDs like "ml52941", "ml288", etc.
        rows = soup.find_all('tr', id=lambda x: x and x.startswith('ml'))
        
        for row in rows:
            # 4. Find the Title Link
            # HTML: <a class="title text-primary _600" ...><span>18 Again</span></a>
            title_link = row.find('a', class_='title')
            
            if title_link:
                # Extract the text (e.g., "18 Again")
                title_text = title_link.get_text(strip=True)
                titles.append(title_text)
                    
        print(f"Found {len(titles)} completed shows.")
        return titles
        
    except Exception as e:
        print(f"Error scraping user list: {e}")
        return []