import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios'

interface ClueData {
  answer: string;
  date: string;
  clue: string;
  author: string;
  editor: string;
  occurrences: string;
}

function App() {
  const [word, setWord] = useState('');
  const [ran, setRan] = useState(false);
  const [clues, setClues] = useState<ClueData[]>([]);
  const [randomClue, setRandomClue] = useState<ClueData | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchClues = async (searchWord: string) => {
    if (!searchWord.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8080/api/words/${searchWord}`);
      setClues(response.data);
      
      // Select a random clue from the results
      if (response.data.length > 0) {
        const randomIndex = Math.floor(Math.random() * response.data.length);
        setRandomClue(response.data[randomIndex]);
        setRan(true);
      } else {
        setRandomClue(null);
      }
    } catch (error) {
      console.error('Error fetching clues:', error);
      setClues([]);
      setRandomClue(null);
    } finally {
      setLoading(false);
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchClues(word);
  }

  return (
    <>
      <h1>Crossword Clue Finder</h1>
      
      <div className="card">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={word}
            onChange={(e) => setWord(e.target.value)}
            placeholder="Enter a word to find clues..."
            style={{ padding: '8px', marginRight: '10px', fontSize: '16px' }}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Find Clues'}
          </button>
        </form>

        {loading && <p>Loading clues...</p>}
        
        {randomClue && (
          <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
            <h3>Random Clue for "{randomClue.answer}":</h3>
            <p><strong>Clue:</strong> {randomClue.clue}</p>
            <p><strong>Date:</strong> {randomClue.date}</p>
            <p><strong>Author:</strong> {randomClue.author}</p>
            <p><strong>Editor:</strong> {randomClue.editor}</p>
            <p><strong>Occurrences:</strong> {randomClue.occurrences}</p>
          </div>
        )}

        {ran && clues.length === 0 && (
          <p style={{ marginTop: '20px', color: '#666' }}>
            No clues found for "{word}"
          </p>
        )}
      </div>
    </>
  )
}

export default App
