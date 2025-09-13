import React, { useState } from "react";

// Backend API URL (update when deployed)
const API_URL = "http://127.0.0.1:5000";

const App = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [uploadResults, setUploadResults] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);

  // Handles file selection
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // Handles search input
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  // Upload handler
  const handleFileUpload = async (event) => {
    event.preventDefault();
    setIsUploading(true);
    setError(null);
    setUploadResults(null);

    if (!selectedFile) {
      setError("Please select a file to upload.");
      setIsUploading(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Upload failed.");
      }

      const data = await response.json();
      setUploadResults(data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Search handler
  const handleSearchSubmit = async (event) => {
    event.preventDefault();
    setIsSearching(true);
    setError(null);
    setSearchResults(null);

    if (!searchQuery.trim()) {
      setError("Please enter a problem description.");
      setIsSearching(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || "Search failed.");
      }

      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="container py-5">
      {/* Bootstrap CSS */}
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
        rel="stylesheet"
      />
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

      <div className="card shadow-lg p-4 mx-auto" style={{ maxWidth: "900px" }}>
        <h1 className="text-center fw-bold text-primary mb-3">
          🛠 Service Problem Resolution
        </h1>
        <p className="text-center text-muted mb-4">
          Upload a file or search for a problem to find solutions.
        </p>

        <div className="row g-4">
          {/* File Upload */}
          <div className="col-md-6">
            <div className="card h-100 border-0 bg-light shadow-sm p-3">
              <h5 className="fw-semibold mb-3">📂 Upload a File</h5>
              <form onSubmit={handleFileUpload}>
                <div className="mb-3">
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileChange}
                    className="form-control"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isUploading}
                  className="btn btn-primary w-100"
                >
                  {isUploading ? "Processing..." : "Upload & Resolve"}
                </button>
              </form>
            </div>
          </div>

          {/* Problem Search */}
          <div className="col-md-6">
            <div className="card h-100 border-0 bg-light shadow-sm p-3">
              <h5 className="fw-semibold mb-3">🔍 Search for a Problem</h5>
              <form onSubmit={handleSearchSubmit}>
                <div className="mb-3">
                  <input
                    type="text"
                    placeholder="e.g., Laptop won't turn on"
                    value={searchQuery}
                    onChange={handleSearchChange}
                    className="form-control"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSearching}
                  className="btn btn-success w-100"
                >
                  {isSearching ? "Searching..." : "Search for Solution"}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="alert alert-danger mt-4 rounded-3">
            <strong>⚠ Error: </strong> {error}
          </div>
        )}

        {/* Upload Results */}
        {uploadResults && (
          <div className="mt-5">
            <h4 className="fw-bold text-primary mb-3">
              📂 File Upload Results
            </h4>
            <div className="list-group">
              {uploadResults.map((result, index) => (
                <div
                  key={index}
                  className="list-group-item list-group-item-action flex-column align-items-start"
                >
                  <p className="mb-1">
                    <strong>Problem:</strong> {result.description}
                  </p>
                  {result.solution ? (
                    <div>
                      <p className="text-success mb-1">
                        ✅ Best Solution: {result.solution}
                      </p>
                      {result.matches && result.matches.length > 0 && (
                        <small className="text-muted">
                          Similarity:{" "}
                          {(result.matches[0].similarity * 100).toFixed(1)}%
                        </small>
                      )}
                    </div>
                  ) : (
                    <p className="text-warning mb-0">
                      ⚠ No similar problem found.
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResults && (
          <div className="mt-5">
            <h4 className="fw-bold text-success mb-3">🔍 Search Result</h4>
            <div className="card p-3 shadow-sm">
              <p>
                <strong>Query:</strong> {searchResults.query}
              </p>
              {searchResults.solution ? (
                <>
                  {searchResults.matches &&
                  searchResults.matches.length === 1 ? (
                    // ✅ Case 1: Only one solution
                    <div>
                      <p>
                        <strong>Similar Problem:</strong>{" "}
                        {searchResults.matches[0].matched_text}
                      </p>
                      <p className="text-success mb-1">
                        ✅ Best Solution: {searchResults.matches[0].solution}
                      </p>
                      <small className="text-muted">
                        Similarity:{" "}
                        {(searchResults.matches[0].similarity * 100).toFixed(1)}
                        %
                      </small>
                    </div>
                  ) : (
                    // ✅ Case 2: Multiple solutions
                    <div>
                      <p>
                        <strong>Most Similar Problem:</strong>{" "}
                        {searchResults.description}
                      </p>
                      <p className="text-success mb-1">
                        ✅ Best Solution: {searchResults.solution}
                      </p>
                      <small className="text-muted d-block mb-2">
                        Similarity:{" "}
                        {(searchResults.matches[0].similarity * 100).toFixed(1)}
                        %
                      </small>

                      <hr />
                      <h6 className="fw-bold mt-3">Other Similar Problems</h6>
                      <ul className="list-group list-group-flush">
                        {searchResults.matches.map((match, index) => (
                          <li key={index} className="list-group-item">
                            <p className="mb-1">
                              <strong>Problem:</strong> {match.matched_text}
                            </p>
                            <p className="mb-1 text-success">
                              <strong>Solution:</strong> {match.solution}
                            </p>
                            <small className="text-muted">
                              Similarity: {(match.similarity * 100).toFixed(1)}%
                            </small>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-warning mb-0">⚠ No similar problem found.</p>
              )}
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {(isUploading || isSearching) && (
          <div className="d-flex justify-content-center mt-4">
            <div
              className="spinner-border text-primary"
              style={{ width: "3rem", height: "3rem" }}
              role="status"
            >
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
