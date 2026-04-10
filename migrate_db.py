import sqlite3
import os

db_path = r"c:\Users\beast\OneDrive\Documents\flask_lost_found\instance\site_v3.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE item ADD COLUMN latitude FLOAT")
        print("Added latitude column.")
    except Exception as e:
        print("Latitude column skip:", e)
        
    try:
        cursor.execute("ALTER TABLE item ADD COLUMN longitude FLOAT")
        print("Added longitude column.")
    except Exception as e:
        print("Longitude column skip:", e)
        
    conn.commit()
    conn.close()
else:
    print("Database not found at expected path.")
