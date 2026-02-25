import os
import streamlit as st
import psycopg2
import ollama
import chromadb
from sentence_transformers import SentenceTransformer


SCHEMA_FILE = "db_schema.sql"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DIR = os.path.join(BASE_DIR, "schema_vectors")
EMBED_MODEL = "paraphrase-MiniLM-L3-v2"
LLM_MODEL = "qwen2.5:3b"


@st.cache_resource
def get_connection():
    return psycopg2.connect(
        dbname="",
        user="",
        password="",
        host="localhost",
        port=
    )


def save_schema_to_sql(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        rows = cur.fetchall()

    tables = {}
    for table, col, dtype in rows:
        tables.setdefault(table, []).append(f"    {col} {dtype}")

    schema_sql = []
    for table, cols in tables.items():
        schema_sql.append(f"CREATE TABLE {table} (")
        schema_sql.append(",\n".join(cols))
        schema_sql.append(");\n")

    with open(SCHEMA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(schema_sql))

    return "\n".join(schema_sql)


@st.cache_resource
def load_vector_db():
    client = chromadb.Client(
        chromadb.config.Settings(
            persist_directory=VECTOR_DIR,
            anonymized_telemetry=False
        )
    )
    return client.get_or_create_collection(name="db_schema")

@st.cache_resource
def load_embedder():
    return SentenceTransformer(EMBED_MODEL)

def index_schema(schema_text):
    embedder = load_embedder()
    collection = load_vector_db()

    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    chunks = schema_text.split(";\n")
    embeddings = embedder.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[str(i) for i in range(len(chunks))]
    )

def retrieve_schema(question, k=4):
    embedder = load_embedder()
    collection = load_vector_db()

    q_embed = embedder.encode([question]).tolist()
    results = collection.query(
        query_embeddings=q_embed,
        n_results=k
    )

    return "\n".join(results["documents"][0])



def generate_sql(question, schema_context):
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Generate PostgreSQL SQL using ONLY the schema below.\n"
                    "Return ONLY valid SQL.\n\n"
                    "Do not do unnecesary joins.\n\n\n"
                    f"{schema_context}"
                )
            },
            {"role": "user", "content": question}
        ],
        options={"temperature": 0}
    )

    return response["message"]["content"].strip()



st.set_page_config(page_title="Local Text → SQL (Schema RAG)")
st.title("Local Text → SQL")
st.caption("Schema → .sql → Vector DB → LLM")

conn = get_connection()

if not os.path.exists(SCHEMA_FILE):
    schema_text = save_schema_to_sql(conn)
    index_schema(schema_text)
    st.success("Schema extracted, saved, and indexed.")
else:
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_text = f.read()
    index_schema(schema_text)

question = st.text_area(
    "Ask your database:",
    placeholder="show total cost of sugar for fiscal year 2025",
    height=100
)

if st.button("Generate SQL"):
    if question.strip():
        schema_context = retrieve_schema(question)
        sql = generate_sql(question, schema_context)

        st.subheader("Generated SQL")
        st.code(sql, language="sql")
    else:
        st.warning("Please enter a question.")

