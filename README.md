# 🛠 Incident Resolution System

An intelligent incident resolution system that uses AI-powered semantic search to find solutions for technical problems. The system can process Excel files containing incident data and provide intelligent matching for new problems based on historical solutions.

## ✨ Features

- **📂 Excel File Upload**: Upload incident data from Excel files with automatic column detection
- **🔍 Intelligent Search**: Semantic search using sentence transformers to find similar problems
- **🤖 AI-Powered Matching**: Uses vector embeddings to find the most similar historical incidents
- **📊 Similarity Scoring**: Shows confidence scores for matched solutions
- **🎨 Modern UI**: Clean, responsive interface built with React and Bootstrap
- **⚡ Real-time Processing**: Fast search and upload processing

## ��️ Architecture

The system consists of two main components:

### Backend (Python/Flask)

- **Framework**: Flask with CORS support
- **Database**: PostgreSQL with pgvector extension for vector operations
- **AI Model**: Sentence Transformers (all-MiniLM-L6-v2) for text embeddings
- **Vector Search**: Cosine similarity search using pgvector

### Frontend (React/Vite)

- **Framework**: React 19 with Vite
- **Styling**: Bootstrap 5 for responsive design
- **HTTP Client**: Axios for API communication
- **UI Components**: Custom components with loading states and error handling

## �� Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **PostgreSQL** (v12 or higher) with pgvector extension
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd incident-resolution
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd incident_resolution_backend

# Create virtual environment
python -m venv myenv

# Activate virtual environment
# On Windows:
myenv\Scripts\activate
# On macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DATABASE_URL=postgresql://username:password@localhost:5432/incident_db" > .env
echo "EMBEDDING_MODEL=all-MiniLM-L6-v2" >> .env
echo "PORT=5000" >> .env

# Start the backend server
python app.py
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd incident_resolution_frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Database Setup

```sql
-- Connect to your PostgreSQL database
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- The application will automatically create the required tables
```

## 📋 Configuration

### Environment Variables

Create a `.env` file in the `incident_resolution_backend` directory:

```env
# Database connection
DATABASE_URL=postgresql://username:password@localhost:5432/incident_db

# AI Model configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Server configuration
PORT=5000
```

### Excel File Format

Your Excel files should contain the following columns:

- **Short description** (or "Short_description" or "Description"): The problem description
- **Resolved**: The solution for the problem

Example:
| Short description | Resolved |
|-------------------|----------|
| Laptop won't turn on | Check power cable and battery connection |
| Printer not printing | Update printer drivers and check paper tray |

## 🔧 API Endpoints

### Upload File

- **POST** `/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: Excel file
- **Response**: Array of problems with matched solutions

### Search Problems

- **POST** `/search`
- **Content-Type**: `application/json`
- **Body**: `{"query": "problem description"}`
- **Response**: Best matching solution with similarity score

### Debug Vector Operations

- **POST** `/debug-vector`
- **Content-Type**: `application/json`
- **Body**: `{"text": "test text"}`
- **Response**: Vector embedding format tests

## 🛠️ Development

### Backend Development

```bash
cd incident_resolution_backend

# Activate virtual environment
source myenv/bin/activate  # On macOS/Linux
# or
myenv\Scripts\activate     # On Windows

# Install development dependencies
pip install -r requirements.txt

# Run with debug mode
python app.py
```

### Frontend Development

```bash
cd incident_resolution_frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🧪 Testing

### Test the API

```bash
# Test search endpoint
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop not starting"}'

# Test upload endpoint
curl -X POST http://localhost:5000/upload \
  -F "file=@your_incident_file.xlsx"
```

### Test Vector Operations

```bash
curl -X POST http://localhost:5000/debug-vector \
  -H "Content-Type: application/json" \
  -d '{"text": "test problem description"}'
```

## 📊 How It Works

1. **Data Ingestion**: Excel files are processed and incident data is extracted
2. **Text Embedding**: Problem descriptions are converted to vector embeddings using sentence transformers
3. **Vector Storage**: Embeddings are stored in PostgreSQL with pgvector extension
4. **Similarity Search**: New queries are embedded and compared using cosine similarity
5. **Solution Matching**: The most similar historical problems are returned with confidence scores

## �� Troubleshooting

### Common Issues

1. **Database Connection Error**

   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env file
   - Ensure pgvector extension is installed

2. **No Matches Found**

   - Check if database has data
   - Lower similarity threshold in code
   - Verify text preprocessing

3. **Vector Conversion Errors**
   - Check pgvector installation
   - Verify embedding model is loaded
   - Test with debug-vector endpoint

### Debug Steps

1. Check backend logs for errors
2. Verify database connection
3. Test vector operations with debug endpoint
4. Check frontend console for API errors

## 📈 Performance

- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Similarity Threshold**: 0.5 (configurable)
- **Top Results**: 5 (configurable)
- **Vector Index**: Uses pgvector for fast similarity search

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## �� Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for text embeddings
- [pgvector](https://github.com/pgvector/pgvector) for vector operations
- [Flask](https://flask.palletsprojects.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
- [Bootstrap](https://getbootstrap.com/) for UI components

## �� Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Happy Problem Solving! 🎉**
