Local Text-to-SQL using Schema RAG (Streamlit + PostgreSQL + Ollama)

A fully local Text-to-SQL application that converts natural language questions into valid PostgreSQL queries using a Schema-based Retrieval Augmented Generation (RAG) pipeline.

This project combines:

Streamlit – Web interface

PostgreSQL – Relational database

ChromaDB – Vector database

Sentence Transformers – Schema embeddings

Ollama (Qwen2.5:3B) – Local LLM for SQL generation

The system ensures SQL is generated strictly from the actual database schema.

Architecture
PostgreSQL → Extract Schema → Save .sql
            ↓
      Chunk Schema
            ↓
     Generate Embeddings
            ↓
        Store in ChromaDB
            ↓
User Question → Retrieve Relevant Schema
            ↓
Schema Context + Question → Qwen2.5:3B (Ollama)
            ↓
Generated PostgreSQL SQL
Features

Fully local (no cloud APIs required)

Automatic schema extraction

Schema-aware SQL generation

Vector-based schema retrieval

Deterministic SQL output (temperature = 0)

No unnecessary joins (prompt controlled)

Requirements
1. Python

Python 3.9 or higher

2. PostgreSQL

Installed and running

Database must exist

Update credentials inside the code:

dbname="postgres1"
user="postgres"
password="147585"
host="localhost"
port=5432
3. Ollama

Install Ollama from:

https://ollama.com

Pull the required model:

ollama pull qwen2.5:3b

Verify installation:

ollama list
Installation
1. Clone the Repository
git clone https://github.com/yourusername/text-to-sql-rag.git
cd text-to-sql-rag
2. Create Virtual Environment (Recommended)
python -m venv venv

Activate:

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt

If you don’t have a requirements file, install manually:

pip install streamlit psycopg2-binary ollama chromadb sentence-transformers torch
Running the Application

Start the Streamlit app:

streamlit run app.py

Open in browser:

http://localhost:8501
Project Structure
.
├── app.py
├── db_schema.sql
├── schema_vectors/
└── README.md
How It Works
Schema Extraction

The app connects to PostgreSQL and extracts:

Table names

Column names

Data types

The schema is saved as db_schema.sql.

Vector Indexing

Schema is split into chunks

Embedded using paraphrase-MiniLM-L3-v2

Stored in ChromaDB for retrieval

Retrieval + Generation

User submits a natural language query.

Relevant schema sections are retrieved.

Retrieved schema is sent to Qwen2.5:3B via Ollama.

The model returns a valid PostgreSQL query.

Example

Input:

show total cost of sugar for fiscal year 2025

Output:

SELECT SUM(cost)
FROM sugar_table
WHERE fiscal_year = 2025;
Notes

Ollama must be running before generating SQL.

If schema changes, delete db_schema.sql and restart the app.

Works completely offline after model download.

Tech Stack

Streamlit

PostgreSQL

ChromaDB

Sentence Transformers

Ollama

Qwen2.5:3B

Future Improvements

Query execution preview

SQL validation layer

Multi-database support

Docker containerization

Role-based schema filtering
