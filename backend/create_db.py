from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Ensure this points to your actual db.py if paths differ
# This assumes you run create_db.py from the 'backend' directory
from app.core.db import DATABASE_URL, metadata

print(f"Using database URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

try:
    metadata.create_all(bind=engine)
    print("Database tables created successfully (if they didn't exist).")
    # Verify by listing tables (optional)
    # with engine.connect() as connection:
    #     from sqlalchemy import inspect
    #     inspector = inspect(engine)
    #     print("Tables in database:", inspector.get_table_names())
except Exception as e:
    print(f"Error creating database tables: {e}")
