from .database import SessionLocal, engine
from . import models
from .services.scraper import scrape_top_dramas

def populate_database():
    # Create the table if it doesn't exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Checking if database is already populated...")
        if db.query(models.Show).count() > 0:
            print("Database already contains data. Skipping population.")
            return

        print("Database is empty. Starting to scrape and populate...")
        # Let's scrape 3 pages for a good amount of data (~60 shows)
        dramas = scrape_top_dramas(num_pages=3)
        
        for drama_data in dramas:
            # Check if the show already exists to avoid duplicates
            existing_show = db.query(models.Show).filter(models.Show.title == drama_data['title']).first()
            if not existing_show:
                db_show = models.Show(
                    title=drama_data['title'],
                    synopsis=drama_data['synopsis'],
                    genres=drama_data['genres'],
                    image_url=drama_data['image_url']
                )
                db.add(db_show)
        
        db.commit()
        print(f"Successfully populated database with {len(dramas)} shows.")

    finally:
        db.close()

if __name__ == "__main__":
    populate_database()