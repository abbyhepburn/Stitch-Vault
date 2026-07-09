import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('crochet_vault.db')
    cursor = conn.cursor()

    print("Creating tables...")
    
    #Create Crafts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Stitch Recipes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stitch_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            craft_id INTEGER,
            project_type TEXT NOT NULL,
            component_name TEXT NOT NULL,
            required_yarn TEXT NOT NULL,
            instructions TEXT NOT NULL,
            FOREIGN KEY (craft_id) REFERENCES crafts (id)
        )
    ''')

    #Insert default craft entry for Crocheting
    cursor.execute("INSERT OR IGNORE INTO crafts (name) VALUES ('Crocheting')")
    conn.commit()
# Create a table specifically for AI-generated RAG patterns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1, -- Defaults to 1 for single-user local testing
        requested_description TEXT NOT NULL,
        compiled_pattern_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    # 4. Create Mock Pattern Data to seed the database
    #craft_id 1 = Crocheting
    print("Seeding synthetic pattern data blocks...")
    synthetic_data = [
        {
            "craft_id": 1,
            "project_type": "Beanie",
            "component_name": "Ribbed Brim",
            "required_yarn": "Worsted",
            "instructions": "Row 1: Ch 9. Sc in 2nd ch from hook and each ch across. Turn.\nRow 2: Ch 1. Sc in BLO of each st across. Turn.\nRepeat Row 2 until piece measures 18 inches."
        },
        {
            "craft_id": 1,
            "project_type": "Beanie",
            "component_name": "Classic Hat Body",
            "required_yarn": "Worsted",
            "instructions": "Row 1: Ch 1. Work Hdc evenly along the edge of the brim rows. Join. \nRow 2: Ch 1. Hdc in each st around. Join.\nRepeat Row 2 until hat reaches 7.5 inches total height. Fasten off."
        },
        {
            "craft_id": 1,
            "project_type": "Scarf",
            "component_name": "Chevron Stitch Body",
            "required_yarn": "Chunky",
            "instructions": "Row 1: Ch 27. Dc in 3rd ch from hook. Dc in next 3 ch. [Dc3tog, Dc in next 3 ch, 3 Dc in next ch, Dc in next 3 ch] repeat to end. Turn."
        }
    ]
    

    # Convert our list of dictionaries into a clean Pandas DataFrame
    df = pd.DataFrame(synthetic_data)
    
    # Write the DataFrame directly into our SQL database table
    df.to_sql('stitch_recipes', conn, if_exists='replace', index=False)
    
    conn.close()
    print("Database built successfully! 'crochet_vault.db' is ready.")

if __name__ == "__main__":
    init_db()