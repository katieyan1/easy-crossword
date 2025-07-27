from flask import Flask, jsonify 
from flask_cors import CORS
import requests
import bs4
import csv

app = Flask(__name__)
cors = CORS(app, origins='*')

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        'users': [
            'katie',
            'noah',
            'hello'
        ]
    })

@app.route('/api/words/<word>', methods=['GET'])
def get_clues_from_word(word):
    data = []
    try:
        with open('xword_modern_data.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Check if the answer matches the word parameter (case-insensitive)
                if row['answer'].upper() == word.upper():
                    data.append({
                        'answer': row['answer'],
                        'date': row['date'],
                        'clue': row['clue'],
                        'author': row['author'],
                        'editor': row['editor'],
                        'occurrences': row['occurrences']
                    })
    except FileNotFoundError:
        return jsonify({'error': 'CSV file not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 500
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)