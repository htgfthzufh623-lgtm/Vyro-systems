import streamlit as st
import pymupdf4llm
import google.generativeai as genai
import tempfile

st.set_page_config(page_title="Free AI PDF Auditor", layout="wide")

with st.sidebar:
    st.title("Admin-Konsole")
    google_key = st.text_input("Google API Key (Gemini)", type="password")
    st.info("Kostenloser Key von ://google.com")

st.title("📄 Kostenloser KI PDF-Logik-Scanner")

uploaded_files = st.file_uploader("PDFs hochladen", type="pdf", accept_multiple_files=True)

if uploaded_files and google_key:
    genai.configure(api_key=google_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if st.button("🚀 Kostenlose Analyse starten"):
        for uploaded_file in uploaded_files:
            with st.status(f"Analysiere {uploaded_file.name}..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    md_text = pymupdf4llm.to_markdown(tmp.name)

            response = model.generate_content(f"Prüfe auf Logikfehler:\n\n{md_text[:30000]}")
            st.subheader(f"Ergebnis: {uploaded_file.name}")
            st.write(response.text)
