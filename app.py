import streamlit as st
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="StitchVault Master Engine", page_icon="🧶")
st.title("StitchVault: Smart Pattern Compiler")
st.write("A deterministic, data-engineered platform to view, filter, or custom-architect patterns.")

# Initialize the OpenAI client
try:
    client = OpenAI()
except Exception:
    st.sidebar.error("OpenAI Client failed to load. Check your .env file setup.")

#Dropdown Controls
st.sidebar.header("Deterministic Vault Search")
selected_project = st.sidebar.selectbox("Target Project:", ["Select...", "Beanie", "Scarf", "Sweater"])
selected_yarn = st.sidebar.selectbox("Yarn Weight Status:", ["Select...", "Worsted", "Chunky", "Lace"])

# Helper function to get pattern from dropdown selections
def query_pattern_components(project, yarn):
    conn = sqlite3.connect('crochet_vault.db')
    query = f"""
        SELECT component_name, instructions 
        FROM stitch_recipes 
        WHERE project_type = '{project}' AND required_yarn = '{yarn}'
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df



#RAG Pipeline for AI Custom Pattern Generation
def retrieve_relevant_context(user_sentence):
    """Searches the database to find rows matching keywords in the user's sentence."""
    conn = sqlite3.connect('crochet_vault.db')
    master_df = pd.read_sql("SELECT project_type, component_name, required_yarn, instructions FROM stitch_recipes", conn)
    conn.close()
    
    matched_instructions = []
    sentence_lower = user_sentence.lower()
    
    for index, row in master_df.iterrows():
        # Context-matching check
        if row['project_type'].lower() in sentence_lower or row['required_yarn'].lower() in sentence_lower:
            block_summary = f"[{row['project_type']} - {row['component_name']} ({row['required_yarn']} Yarn)]: {row['instructions']}"
            matched_instructions.append(block_summary)
            
    return "\n\n".join(matched_instructions)

def save_custom_pattern(description, pattern_content):
    """Saves an AI-compiled custom pattern back into the user_patterns table."""
    conn = sqlite3.connect('crochet_vault.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_patterns (requested_description, compiled_pattern_text)
        VALUES (?, ?)
    ''', (description, pattern_content))
    conn.commit()
    conn.close()


# Tab layout for UI
tab1, tab2 = st.tabs(["🔍 Pattern Vault", "🤖 AI Pattern Architect"])

#Tab 1: Deterministic Query of Pre-Existing Patterns
with tab1:
    st.subheader("Query Pre-Existing Database Patterns")
    st.write("Select options in the sidebar to search for exact, verified database rows.")
    
    if st.sidebar.button("Compile Structural Pattern"):
        if selected_project == "Select..." or selected_yarn == "Select...":
            st.error("❌ Aborting compiler. You must specify both a target project and a yarn weight configuration.")
        else:
            st.info(f"Checking data vault for: **{selected_project}** requiring **{selected_yarn}** yarn...")
            retrieved_data = query_pattern_components(selected_project, selected_yarn)
            
            if retrieved_data.empty:
                st.error("⚠️ CRITICAL ERROR: Insufficient data logs. The pre-existing recipes in the database are inadequate to assemble this request without structural hallucinations.")
            else:
                st.success("🎉 Assembly complete! Combined structural data matching verified blocks.")
                for index, row in retrieved_data.iterrows():
                    st.subheader(f"📍 Step: {row['component_name']}")
                    st.code(row['instructions'], language="markdown")


# Tab 2: AI-Driven Pattern Architect
with tab2:
    st.subheader("Architect a New Pattern with AI")
    st.write("Describe what you want to make in a sentence. The engine will retrieve the building blocks and write your pattern.")
    
    user_prompt = st.text_input(
        label="What custom creation would you like to design?", 
        placeholder="e.g., I want to make a cozy winter Beanie using some Worsted weight yarn I found."
    )
    
    if st.button("Architect Pattern with RAG"):
        if not user_prompt.strip():
            st.warning("Please type a description first!")
        else:
            with st.spinner("Executing RAG Pipeline... Searching database rows..."):
                retrieved_context = retrieve_relevant_context(user_prompt)
                
                if not retrieved_context:
                    st.error("❌ Generation Halted: No verified stitch building blocks matching your prompt keywords were found in the database.")
                else:
                    st.info("Found matching verified stitch components inside database. Passing context to AI...")
                    
                    system_instruction = (
                        "You are a master crochet instructor. Your job is to take a user's custom design request "
                        "and fulfill it strictly using the verified database blocks provided below. "
                        "Do not invent new stitch abbreviations or structurally impossible methods.\n\n"
                        f"VERIFIED DATABASE BLOCKS:\n{retrieved_context}"
                    )
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "user", "content": f"Construct a new custom pattern based on this request: {user_prompt}"}
                            ],
                            temperature=0.3
                        )
                        
                        ai_pattern = response.choices[0].message.content
                        save_custom_pattern(user_prompt, ai_pattern)
                        
                        st.success("🎉 Custom Pattern generated and saved to your personal vault!")
                        st.markdown("### 📋 Your Custom Pattern Details")
                        st.write(ai_pattern)
                        
                    except Exception as e:
                        st.error(f"Failed to connect to OpenAI API: {e}")

#Global Footer - My Patterns Vault
st.write("---")
st.subheader("📚 My Patterns Vault")

conn = sqlite3.connect('crochet_vault.db')
try:
    history_df = pd.read_sql("SELECT id, requested_description, created_at, compiled_pattern_text FROM user_patterns ORDER BY created_at DESC", conn)
    if history_df.empty:
        st.info("You haven't generated any custom AI patterns yet.")
    else:
        for index, row in history_df.iterrows():
            with st.expander(f"Pattern #{row['id']}: {row['requested_description'][:40]}... ({row['created_at'][:10]})"):
                st.caption(f"**Original User Intent:** {row['requested_description']}")
                st.text(row['compiled_pattern_text'])
except Exception:
    st.info("Database table empty or missing initialization.")
finally:
    conn.close()