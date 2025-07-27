from flask import Flask, jsonify 
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
cors = CORS(app, origins='*')

# Database setup
DATABASE = 'crossword_data.db'

def init_db():
    """Initialize the database with the crossword table"""
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

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/api/words/<word>', methods=['GET'])
def get_clues_from_word(word):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Search for clues with case-insensitive matching
        cursor.execute('''
            SELECT answer, clue, date, author, editor, occurrences
            FROM crossword_clues 
            WHERE UPPER(answer) = UPPER(?)
        ''', (word,))
        
        results = cursor.fetchall()
        data = []
        
        for row in results:
            data.append({
                'answer': row[0],      # answer
                'clue': row[1],        # clue
                'date': row[2],        # date
                'author': row[3],      # author
                'editor': row[4],      # editor
                'occurrences': str(row[5])  # occurrences
            })
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)