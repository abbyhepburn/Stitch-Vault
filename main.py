from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Stitch Vault")

# CRITICAL: Allows your React app (running on a different port) to securely talk to your FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to your specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI Client
try:
    client = OpenAI()
except Exception:
    print("OpenAI Client failed to load.")

def init_db_tables():
    conn = sqlite3.connect('crochet_vault.db')
    cursor = conn.cursor()
    # Ensure supply closet inventory components exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS yarn_stash 
        (id INTEGER PRIMARY KEY, color TEXT, weight TEXT, texture TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS hook_vault 
        (id INTEGER PRIMARY KEY, size_mm REAL, size_letter TEXT, material TEXT, available INTEGER)''')
    conn.commit()
    conn.close()

init_db_tables()


# --- DATA MODELS (Pydantic models to validate incoming JSON data) ---
class YarnInput(BaseModel):
    color: str
    weight: str
    texture: str

class HookInput(BaseModel):
    size_mm: float
    size_letter: str
    material: str

class PromptInput(BaseModel):
    prompt: str

# --- API ENDPOINTS ---

@app.get("/api/yarn")
def get_yarn():
    conn = sqlite3.connect('crochet_vault.db')
    df = pd.read_sql("SELECT id, color, weight, texture FROM yarn_stash", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.post("/api/yarn")
def add_yarn(yarn: YarnInput):
    conn = sqlite3.connect('crochet_vault.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO yarn_stash (color, weight, texture) VALUES (?, ?, ?)",
                   (yarn.color, yarn.weight, yarn.texture))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Yarn logged to closet!"}

@app.get("/api/hooks")
def get_hooks():
    conn = sqlite3.connect('crochet_vault.db')
    df = pd.read_sql("SELECT id, size_mm, size_letter, material FROM hook_vault", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.post("/api/hooks")
def add_hook(hook: HookInput):
    conn = sqlite3.connect('crochet_vault.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hook_vault (size_mm, size_letter, material, available) VALUES (?, ?, ?, 1)",
                   (hook.size_mm, hook.size_letter, hook.material))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Hook registered!"}

@app.post("/api/architect")
def architect_pattern(payload: PromptInput):
    # (Your existing RAG context gathering code goes here)
    # For brief demonstration, passing prompt directly to OpenAI:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a master crochet instructor."},
                {"role": "user", "content": payload.prompt}
            ],
            temperature=0.3
        )
        ai_pattern = response.choices[0].message.content
        return {"status": "success", "pattern": ai_pattern}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    #uvicorn main:app --reload