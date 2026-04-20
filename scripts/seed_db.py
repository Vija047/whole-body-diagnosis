"""
Seed the database with initial model metadata.
"""
from database import SessionLocal, ModelMetadata, init_db
from config import get_settings

def seed_data():
    settings = get_settings()
    print(f"Seeding database at {settings.DATABASE_URL}...")
    
    # Ensure tables exist
    init_db()
    
    db = SessionLocal()
    try:
        diseases = ['diabetes', 'ckd', 'cld', 'heart']
        
        for disease in diseases:
            # Check if already exists
            existing = db.query(ModelMetadata).filter(ModelMetadata.disease == disease).first()
            if not existing:
                meta = ModelMetadata(
                    disease=disease,
                    model_version="1.0.0-initial",
                    accuracy=0.95,  # Placeholder, in real world pull from training logs
                    precision=0.94,
                    recall=0.96,
                    f1_score=0.95,
                    auc_score=0.98,
                    is_active=True
                )
                db.add(meta)
                print(f"Added metadata for {disease}")
            else:
                print(f"Metadata for {disease} already exists")
        
        db.commit()
        print("Success: Database seeded.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
