import { useState } from "react";
import axios from "axios";
import "./App.css"

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [suggestion, setSuggestion] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const resp = await axios.post("http://localhost:8000/search", {
        query,
        k: 5,
      });
      setResults(resp.data.matches || []);

      const suggestResp = await axios.post("http://localhost:8000/suggest", {
        query,
        k: 3,
      });
      setSuggestion(suggestResp.data.suggestion);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="app-container">
        <div className="content-card">
          <h1 className="header">Incident Assist</h1>
          <div className="search-input-group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="search-input"
              placeholder="Describe your issue..."
            />
            <button
              onClick={handleSearch}
              className="search-button"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>

          {results.length > 0 && (
            <div className="results-container">
              <h2 className="section-title">Similar Tickets</h2>
              <ul className="results-list">
                {results.map((r) => (
                  <li
                    key={r.ticket_id}
                    className="result-item"
                  >
                    <p className="summary-text">{r.issue_summary}</p>
                    <p className="notes-text">{r.resolution_notes}</p>
                    <span className="similarity-text">
                      Similarity: {r.similarity?.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {suggestion && (
            <div className="suggestion-container">
              <h2 className="section-title">Suggested Resolution</h2>
              <pre className="suggestion-box">
                {suggestion}
              </pre>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
