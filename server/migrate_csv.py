#!/usr/bin/env python3
"""
Script to migrate crossword data from CSV to SQLite database
"""

import csv
import sqlite3
import os
from pathlib import Path

DATABASE = 'crossword_data.db'
CSV_FILE = 'xword_modern_data.csv'

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crossword_clues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer TEXT NOT NULL,
            clue TEXT NOT NULL,
            date TEXT NOT NULL,
            author TEXT,
            editor TEXT,
            occurrences INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index for faster searches
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_answer ON crossword_clues(answer)')
    
    conn.commit()
    conn.close()

def migrate_csv_to_db():
    """Migrate data from CSV to database"""
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file '{CSV_FILE}' not found!")
        return False
    
    print(f"📁 Found CSV file: {CSV_FILE}")
    
    # Initialize database
    init_db()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            total_rows = 0
            inserted_rows = 0
            
            for row in csv_reader:
                total_rows += 1
                
                # Check if this clue already exists
                cursor.execute('''
                    SELECT id FROM crossword_clues 
                    WHERE UPPER(answer) = UPPER(?) AND UPPER(clue) = UPPER(?)
                ''', (row['answer'], row['clue']))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update occurrences if clue already exists
                    cursor.execute('''
                        UPDATE crossword_clues 
                        SET occurrences = occurrences + 1 
                        WHERE id = ?
                    ''', (existing[0],))  # Use tuple indexing
                else:
                    # Insert new clue
                    cursor.execute('''
                        INSERT INTO crossword_clues (answer, clue, date, author, editor, occurrences)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row['answer'],
                        row['clue'],
                        row['date'],
                        row['author'],
                        row['editor'],
                        int(row['occurrences']) if row['occurrences'].isdigit() else 1
                    ))
                    inserted_rows += 1
                
                # Progress update every 1000 rows
                if total_rows % 1000 == 0:
                    print(f"📊 Processed {total_rows} rows...")
            
            conn.commit()
            
            print(f"✅ Migration completed!")
            print(f"📊 Total rows processed: {total_rows}")
            print(f"📊 New rows inserted: {inserted_rows}")
            print(f"📊 Duplicate rows updated: {total_rows - inserted_rows}")
            
            # Show some stats
            cursor.execute('SELECT COUNT(*) FROM crossword_clues')
            total_in_db = cursor.fetchone()[0]
            print(f"📊 Total rows in database: {total_in_db}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def show_db_stats():
    """Show database statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM crossword_clues')
        total_clues = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT answer) FROM crossword_clues')
        unique_answers = cursor.fetchone()[0]
        
        cursor.execute('SELECT answer, COUNT(*) as count FROM crossword_clues GROUP BY answer ORDER BY count DESC LIMIT 10')
        top_answers = cursor.fetchall()
        
        print(f"📊 Database Statistics:")
        print(f"   Total clues: {total_clues}")
        print(f"   Unique answers: {unique_answers}")
        print(f"   Top 10 most common answers:")
        
        for answer, count in top_answers:
            print(f"     {answer}: {count} clues")
            
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Crossword CSV to Database Migration")
    print("=" * 50)
    
    if os.path.exists(DATABASE):
        print(f"⚠️  Database '{DATABASE}' already exists!")
        response = input("Do you want to continue and potentially add duplicate data? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            exit()
    
    if migrate_csv_to_db():
        print("\n📈 Migration successful! Here are the stats:")
        show_db_stats()
    else:
        print("\n❌ Migration failed!") 