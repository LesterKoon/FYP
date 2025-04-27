import sqlite3
import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

csv_file = os.path.join(current_dir, 'Datasets', '111111111.csv')
db_file = os.path.join(current_dir,'Datasets', 'vibesync.db')

if not os.path.exists(db_file):
    open(db_file, "w").close()

df = pd.read_csv(csv_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sp_uri TEXT,
    predicted_valence REAL,
    predicted_arousal REAL,
    track_name TEXT,
    intensity REAL,
    timbre REAL,
    pitch REAL,
    rhythm REAL,
    emotion_quadrant INTEGER,
    happy REAL,
    excited REAL,
    energetic REAL,
    fear REAL,
    sad REAL,
    depressed REAL,
    calm REAL,
    angry REAL
);
""")

df.to_sql('songs', conn, if_exists='replace', index=False)

cursor.execute("SELECT COUNT(*) FROM songs")
print(f"Total rows inserted: {cursor.fetchone()[0]}")

conn.commit()
conn.close()
