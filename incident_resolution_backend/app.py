import os
import io
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# --- Configuration & Initialization ---
load_dotenv()
app = Flask(__name__)
# The database URL is pulled from your .env file
url = os.getenv("DATABASE_URL")

# Connect to the PostgreSQL database
try:
    connection = psycopg2.connect(url)
    connection.autocommit = True # Ensures changes are immediately saved
    print("Database connection established successfully.")
except (Exception, psycopg2.Error) as error:
    print(f"Error while connecting to PostgreSQL: {error}")
    connection = None

# Initialize the Sentence Transformer model
MODEL_NAME = 'all-MiniLM-L6-v2'
model = SentenceTransformer(MODEL_NAME)

# --- Database Functions ---
def embed_and_store(cursor, description, resolved):
    """Generates an embedding and stores a single entry in the database."""
    if not description or not resolved:
        return
    
    try:
        description_embedding = model.encode(description).tolist()
        cursor.execute(
            "INSERT INTO sentences (text, embedding, resolved_solution) VALUES (%s, %s, %s)",
            (description, description_embedding, resolved)
        )
        print("Successfully stored a new entry.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while inserting data: {error}")

def find_similar_problem(cursor, new_sentence, similarity_threshold=0.7):
    """
    Finds and returns the most similar problem and its resolution from the database.
    Returns (text, resolved_solution) or None.
    """
    new_embedding = model.encode(new_sentence).tolist()
    
    try:
        query = """
        SELECT text, resolved_solution, 1 - (embedding <=> %s) AS cosine_similarity
        FROM sentences
        ORDER BY cosine_similarity DESC
        LIMIT 1;
        """
        cursor.execute(query, (new_embedding,))
        result = cursor.fetchone()
        
        if result and result[2] >= similarity_threshold:
            return result[0], result[1]
        
    except (Exception, psycopg2.Error) as error:
        print(f"Error during similarity search: {error}")
        return None
        
    return None

# --- API Endpoints ---
@app.get("/")
def home():
    """Simple API status check."""
    return jsonify({"message": "Backend is running!"})

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file upload, processes the data, and performs similarity searches.
    """
    if connection is None:
        return jsonify({"error": "Database connection is not available."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Read the file directly from the in-memory stream
        df = pd.read_excel(file)

        if 'Short description' not in df.columns or 'Resolved' not in df.columns:
            return jsonify({"error": "Excel file must contain 'short description' and 'Resolved' columns."}), 400

        results = []
        with connection.cursor() as cursor:
            for index, row in df.iterrows():
                short_description = str(row['Short description'])
                resolved_solution = str(row['Resolved'])

                # Find a similar problem in the database
                found_text, found_solution = find_similar_problem(cursor, short_description)
                
                if found_solution:
                    results.append({
                        'description': short_description,
                        'solution': found_solution
                    })
                else:
                    results.append({
                        'description': short_description,
                        'solution': None
                    })
                
                # Always embed and store the new entry
                embed_and_store(cursor, short_description, resolved_solution)

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
