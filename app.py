import streamlit as st
import pymupdf4llm
from openai import OpenAI
import tempfile
import pandas as pd
import time
from datetime import datetime

# --- KONFIGURATION & UI LAYOUT ---
st.set_page_config(page_title="Enterprise AI PDF Auditor", layout="wide", initial_sidebar_state="expanded")

# Custom CSS für professionelles Aussehen
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stAlert { border-radius: 10px; }
    .report-card { border: 1px solid #e6e9ef; padding: 20px; border-radius: 10px; background: white; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: EINSTELLUNGEN ---
with st.sidebar:
    st.image("https://icons8.com", width=80)
    st.title("Admin-Konsole")
    api_key = st.text_input("OpenAI API Key (GPT-4o)", type="password", help="Dein Schlüssel wird nicht gespeichert.")
    
    st.markdown("---")
    st.subheader("Prüf-Parameter")
    check_logic = st.checkbox("Logische Widersprüche", value=True)
    check_numbers = st.checkbox("Rechenfehler & Zahlen-Validierung", value=True)
    check_compliance = st.checkbox("Rechtliche Standard-Floskeln", value=False)
    
    st.markdown("---")
    model_choice = st.selectbox("KI-Modell", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    max_tokens = st.slider("Detailtiefe der Analyse", 500, 4000, 1500)

# --- HAUPTBEREICH ---
st.title("📄 Enterprise AI: PDF Logik- & Massen-Prüfung")
st.write(f"Datum: {datetime.now().strftime('%d.%m.%Y')} | Status: System bereit")

# Datei-Upload für bis zu 600 PDFs
uploaded_files = st.file_uploader(
    "Laden Sie Dokumente zur Analyse hoch (Massenverarbeitung aktiviert)", 
    type="pdf", 
    accept_multiple_files=True
)

# Speicher für Ergebnisse (Session State)
if 'results' not in st.session_state:
    st.session_state.results = []

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)} Dokumente erkannt. Bereit zur Analyse.")
    
    if st.button("🚀 Gesamtanalyse starten", use_container_width=True):
        if not api_key:
            st.error("❌ Fehler: Bitte geben Sie einen API-Key in der Seitenleiste ein.")
        else:
            client = OpenAI(api_key=api_key)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                filename = uploaded_file.name
                status_text.text(f"Verarbeite ({idx+1}/{len(uploaded_files)}): {filename}...")
                
                try:
                    # 1. Schritt: PDF zu Markdown konvertieren (Struktur erhalten)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    md_content = pymupdf4llm.to_markdown(tmp_path)
                    
                    # 2. Schritt: KI-Prompt dynamisch bauen
                    prompt = f"""
                    Du bist ein Senior-Auditor für Unternehmen. Analysiere das folgende Dokument extrem präzise auf:
                    {'- Logikfehler und Widersprüche im Textfluss' if check_logic else ''}
                    {'- Falsche Berechnungen oder unplausible Zahlenwerte' if check_numbers else ''}
                    {'- Fehlende Pflichtangaben oder Compliance-Verstöße' if check_compliance else ''}
                    
                    Dokumenten-Inhalt:
                    {md_content[:15000]}
                    
                    Gib die Antwort in folgendem Format aus:
                    ### 🚩 GEFUNDENE FEHLER
                    (Liste der Fehler mit Begründung)
                    ### 📉 LOGIK-SCORE (0-100)
                    (Zahl)
                    ### ✅ HANDLUNGSEMPFEHLUNG
                    (Was muss korrigiert werden?)
                    """

                    # 3. Schritt: KI-Anfrage
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[{"role": "system", "content": "Antworte als hochprofessioneller KI-Prüfer für Firmen."},
                                  {"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=0 # Strikte Fakten, keine Kreativität
                    )
                    
                    analysis_text = response.choices.message.content
                    
                    # Ergebnis speichern
                    st.session_state.results.append({
                        "Datei": filename,
                        "Zeitstempel": datetime.now().strftime("%H:%M:%S"),
                        "Analyse": analysis_text
                    })
                    
                except Exception as e:
                    st.error(f"Fehler bei Datei {filename}: {str(e)}")
                
                # Fortschritt aktualisieren
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.success("✅ Alle Analysen abgeschlossen!")

# --- ERGEBNIS-ANZEIGE ---
if st.session_state.results:
    st.markdown("---")
    st.subheader("📋 Analyse-Berichte")
    
    for res in st.session_state.results:
        with st.expander(f"Bericht für {res['Datei']} (Zeit: {res['Zeitstempel']})"):
            st.markdown(res['Analyse'])
            
    # Export-Funktion
    df_results = pd.DataFrame(st.session_state.results)
    csv = df_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Alle Ergebnisse als CSV exportieren",
        data=csv,
        file_name=f"Analyse_Bericht_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )

else:
    st.write("Keine Daten vorhanden. Bitte laden Sie PDFs hoch und klicken Sie auf 'Analyse starten'.")

# Footer
st.markdown("---")
st.caption("KI-Dokumentenprüfung v2.1 | Vertrauliche Verarbeitung über API
