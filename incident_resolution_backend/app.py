import os
import traceback
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

# ------------------ Load Config ------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: postgresql://user:pass@localhost:5432/mydb
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # outputs 384-dim embeddings

# ------------------ Flask App ------------------
app = Flask(__name__)
CORS(app)  # allow cross-origin for React dev

# ------------------ DB Connection ------------------
connection = None
try:
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")

    connection = psycopg2.connect(DATABASE_URL)
    connection.autocommit = True
    register_vector(connection)  # pgvector adapter
    print("✅ Connected to PostgreSQL + registered pgvector.")
except Exception as e:
    print("❌ DB connection error:", e)
    connection = None

# ------------------ Ensure Table ------------------
def ensure_db_schema():
    if connection is None:
        return
    try:
        with connection.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sentences (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    embedding VECTOR(384),
                    resolved_solution TEXT
                );
            """)
            print("✅ Ensured pgvector extension + sentences table.")
    except Exception as e:
        print("❌ Error ensuring DB schema:", e)

ensure_db_schema()

# ------------------ Load Model ------------------
try:
    model = SentenceTransformer(MODEL_NAME)
    print(f"✅ Loaded embedding model: {MODEL_NAME}")
except Exception as e:
    print("❌ Error loading model:", e)
    model = None

# ------------------ Helpers ------------------
def embed_text(text):
    if model is None:
        raise RuntimeError("Embedding model not loaded")
    emb = model.encode(text)
    return np.asarray(emb, dtype=np.float32).tolist()

def embed_and_store(cursor, description, resolved):
    """Embed a sentence and insert into DB"""
    if not description:
        return
    try:
        description_embedding = embed_text(description)
        cursor.execute(
            "INSERT INTO sentences (text, embedding, resolved_solution) VALUES (%s, %s, %s)",
            (description, description_embedding, resolved),
        )
    except Exception as e:
        print("❌ Error inserting row:", e)
        traceback.print_exc()

def find_similar_problems(cursor, new_sentence, similarity_threshold=0.65, top_k=5):
    """Return list of similar problems + solutions"""
    if not new_sentence:
        return []

    new_embedding = embed_text(new_sentence)
    try:
        # Method 1: Use string formatting to convert list to PostgreSQL array format
        embedding_str = '[' + ','.join(map(str, new_embedding)) + ']'
        
        query = """
        SELECT text, resolved_solution, 1 - (embedding <=> %s::vector) AS cosine_similarity
        FROM sentences
        WHERE text IS NOT NULL
        ORDER BY cosine_similarity DESC
        LIMIT %s;
        """
        
        cursor.execute(query, (embedding_str, top_k))
        rows = cursor.fetchall()

        results = []
        for text, resolved, sim in rows:
            if sim >= similarity_threshold:
                results.append({
                    "matched_text": text,
                    "solution": resolved,
                    "similarity": float(sim)
                })
        return results
        
    except Exception as e:
        print("❌ Error during similarity search:", e)
        traceback.print_exc()
        
        # Fallback method: Use numpy array conversion
        try:
            print("🔄 Trying fallback method...")
            embedding_array = np.array(new_embedding, dtype=np.float32)
            
            query = """
            SELECT text, resolved_solution, 1 - (embedding <=> %s) AS cosine_similarity
            FROM sentences
            WHERE text IS NOT NULL
            ORDER BY cosine_similarity DESC
            LIMIT %s;
            """
            
            cursor.execute(query, (embedding_array, top_k))
            rows = cursor.fetchall()

            results = []
            for text, resolved, sim in rows:
                if sim >= similarity_threshold:
                    results.append({
                        "matched_text": text,
                        "solution": resolved,
                        "similarity": float(sim)
                    })
            return results
            
        except Exception as e2:
            print("❌ Fallback method also failed:", e2)
            traceback.print_exc()
            return []

# Alternative implementation using explicit vector casting
def find_similar_problems_v2(cursor, new_sentence, similarity_threshold=0.65, top_k=5):
    """Alternative implementation with explicit vector casting"""
    if not new_sentence:
        return []

    new_embedding = embed_text(new_sentence)
    try:
        # Convert to PostgreSQL array format explicitly
        embedding_str = '{' + ','.join(map(str, new_embedding)) + '}'
        
        query = """
        SELECT text, resolved_solution, 
               1 - (embedding <=> CAST(%s AS vector)) AS cosine_similarity
        FROM sentences
        WHERE text IS NOT NULL AND text != ''
        ORDER BY cosine_similarity DESC
        LIMIT %s;
        """
        
        cursor.execute(query, (embedding_str, top_k))
        rows = cursor.fetchall()

        results = []
        for text, resolved, sim in rows:
            if sim >= similarity_threshold:
                results.append({
                    "matched_text": text,
                    "solution": resolved,
                    "similarity": float(sim)
                })
        return results
        
    except Exception as e:
        print("❌ Error in v2 similarity search:", e)
        traceback.print_exc()
        return []

# ------------------ Routes ------------------
@app.get("/")
def home():
    return jsonify({"message": "Backend is running!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if connection is None:
        return jsonify({"error": "DB connection not available"}), 500

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = pd.read_excel(file)
        cols = {c.strip().lower(): c for c in df.columns}
        short_col = cols.get("short description") or cols.get("short_description") or cols.get("description")
        resolved_col = cols.get("resolved")

        if not short_col or not resolved_col:
            return jsonify({"error": "Excel must have 'Short description' and 'Resolved' columns."}), 400

        results = []
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                short_description = str(row[short_col]) if pd.notna(row[short_col]) else ""
                resolved_solution = str(row[resolved_col]) if pd.notna(row[resolved_col]) else ""

                if not short_description.strip():
                    continue

                # search DB for similar
                matches = find_similar_problems(cursor, short_description)
                # Get the best match as solution
                best_solution = matches[0]["solution"] if matches else None
                results.append({
                    "description": short_description,
                    "solution": best_solution,
                    "matches": matches
                })

                # store new record
                embed_and_store(cursor, short_description, resolved_solution)

        return jsonify({"results": results}), 200
    except Exception as e:
        print("❌ Upload error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["POST"])
def search_problem():
    if connection is None:
        return jsonify({"error": "DB connection not available"}), 500

    data = request.get_json(force=True, silent=True)
    if not data or not data.get("query"):
        return jsonify({"error": "Query text required"}), 400

    query_text = data["query"]
    try:
        with connection.cursor() as cursor:
            matches = find_similar_problems(cursor, query_text, similarity_threshold=0.65, top_k=5)
            # Get the best match as solution
            best_solution = matches[0]["solution"] if matches else None
            return jsonify({
                "query": query_text,
                "solution": best_solution,
                "matches": matches
            }), 200
    except Exception as e:
        print("❌ Search error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/search-v2", methods=["POST"])
def search_problem_v2():
    """Alternative search endpoint using v2 method"""
    if connection is None:
        return jsonify({"error": "DB connection not available"}), 500

    data = request.get_json(force=True, silent=True)
    if not data or not data.get("query"):
        return jsonify({"error": "Query text required"}), 400

    query_text = data["query"]
    try:
        with connection.cursor() as cursor:
            matches = find_similar_problems_v2(cursor, query_text, similarity_threshold=0.65, top_k=5)
            return jsonify({
                "query": query_text,
                "matches": matches,
                "method": "v2"
            }), 200
    except Exception as e:
        print("❌ Search v2 error:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ------------------ Debug Route ------------------
@app.route("/debug-vector", methods=["POST"])
def debug_vector():
    """Debug endpoint to test vector operations"""
    if connection is None:
        return jsonify({"error": "DB connection not available"}), 500

    data = request.get_json(force=True, silent=True)
    test_text = data.get("text", "test query") if data else "test query"
    
    try:
        # Generate embedding
        embedding = embed_text(test_text)
        
        # Test different formats
        formats = {
            "list": embedding,
            "numpy_array": np.array(embedding, dtype=np.float32),
            "bracket_string": '[' + ','.join(map(str, embedding)) + ']',
            "brace_string": '{' + ','.join(map(str, embedding)) + '}'
        }
        
        results = {}
        
        with connection.cursor() as cursor:
            for format_name, format_data in formats.items():
                try:
                    if format_name in ["bracket_string", "brace_string"]:
                        query = "SELECT %s::vector AS test_vector"
                        cursor.execute(query, (format_data,))
                    else:
                        query = "SELECT %s::vector AS test_vector"
                        cursor.execute(query, (format_data,))
                    
                    result = cursor.fetchone()
                    results[format_name] = {"status": "success", "result": "conversion worked"}
                    
                except Exception as e:
                    results[format_name] = {"status": "error", "error": str(e)}
        
        return jsonify({
            "text": test_text,
            "embedding_length": len(embedding),
            "format_tests": results
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ Run ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)