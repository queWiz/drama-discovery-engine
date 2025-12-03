from .database import SessionLocal, engine
from . import models
from .services.scraper import scrape_top_dramas

def populate_database():
    # Create the table if it doesn't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Get list of titles ALREADY in the database
        print("Checking existing database...")
        existing_shows = db.query(models.Show.title).all()
        # Convert list of tuples [('Title1',), ('Title2',)] -> Set {'Title1', 'Title2'}
        existing_titles = {title[0] for title in existing_shows}
        
        print(f"Found {len(existing_titles)} shows in database.")

        print("Starting to scrape and populate...")
        # Let's scrape 3 pages for a good amount of data (~60 shows)
        dramas = scrape_top_dramas(num_pages=1, existing_titles=existing_titles)

        if not dramas:
            print("No new dramas found.")
            return
        
        print(f"Found {len(dramas)} new dramas. Saving...")
        
        for drama_data in dramas:
            db_show = models.Show(
                title=drama_data['title'],
                synopsis=drama_data['synopsis'],
                image_url=drama_data['image_url'],
                reviews=drama_data['reviews'],
                genres=drama_data['genres'],
                tags=drama_data['tags'],
                rating=drama_data['rating'],
                year=drama_data['year'] 
            )
            db.add(db_show)
        
        db.commit()
        print(f"Successfully populated database with {len(dramas)} shows.")

    finally:
        db.close()

if __name__ == "__main__":
    populate_database()