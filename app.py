import streamlit as st
from google import genai
from google.genai import types

# API-Client initialisieren
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Chat-Session und Verlauf initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Fester Start-Text, spart API-Limits beim Laden!
    erste_frage = "Hallo! Um passende Jobs für dich zu finden, brauche ich ein paar Infos. Wie lautet deine Postleitzahl oder dein Wohnort, und wie bist du mobil (Auto, Fahrrad, Bus/Bahn)?"
    st.session_state.messages.append({"role": "assistant", "content": erste_frage})

# Nachrichten sauber in der App anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# API-Schlüssel laden
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Bitte hinterlege den GEMINI_API_KEY in den Streamlit-Einstellungen (Secrets)!")
    st.stop()

# Client initialisieren
client = genai.Client(api_key=api_key)

# SYSTEMPROMPT
SYSTEM_PROMPT = """
# ROLLE UND LOGIK
Du bist ein hochpräziser KI-Jobcoach für Menschen mit geringen Deutschkenntnissen oder ohne anerkannte Abschlüsse. 
Du führst ein Daten-Interview durch. Jede Antwort des Nutzers wird von dir im Kontext interpretiert, abgespeichert und für sinnvolle Vertiefungsfragen genutzt.

# STRIKTE ABLAUFLOGIK (PHASEN & ANSCHLUSSFRAGEN)
Arbeite das Interview strikt nach den Phasen ab.
WICHTIG: Wenn der Nutzer eine praktische Erfahrung, ein Werkzeug, ein Fahrzeug oder ein Talent nennt, stelle EINMALIG EINE SINNVOLLE ANSCHLUSSFRAGE, um dieses Profilmerkmal zu verfeinern!

- Phase 1: Genaue Region & Mobilität (PLZ/Wohnort, ÖPNV, Auto/Fahrrad, maximale Fahrzeit).
- Phase 2: Rahmenbedingungen (Arbeitserlaubnis, Stunden/Woche, Schicht-/Wochenendbereitschaft, Betreuung).
- Phase 3: Sprach- & Digitalkenntnisse (Muttersprache, Deutsch beim Sprechen/Verstehen/Lesen, WhatsApp/Smartphone/PC).
- Phase 4: Berufliche Vorerfahrungen & Vertiefung (Exakte Tätigkeiten im In-/Ausland).
- Phase 5: Außerberufliche & informelle Fertigkeiten (Haushalt, Pflege, Landwirtschaft, Bau, Reparaturen, Handwerk, Kochen).
- Phase 6: Physische Belastbarkeit & Praxistests (Schwer heben, ganztägig stehen, Kälte/Hitze, Höhe).
- Phase 7: Soziale & praktische Stärken (Arbeit mit Menschen, Pünktlichkeit, Anweisungen befolgen vs. selbstständig).
- Phase 8: Konkrete Ausschlusskriterien (Was kann/will die Person auf keinen Fall tun?).
- Phase 9: Bisherige Bewerbungsversuche & Status in Deutschland.

Sobald Phase 9 abgeschlossen ist, gehst du ZWINGEND zur ABSCHLUSSAUSWERTUNG über.

# RADIKALE FORMULIERUNGSREGELN
1. NUR EINE EINZIGE FRAGE: Pro Nachricht absolut NUR EINE konkrete Frage stellen.
2. KEINE PROSA / KEIN SMALLTALK: Antworte ausschließlich mit der Frage.
3. KLARHEIT: Nutze einfache Sprache (A2-Niveau).

# ABSCHLUSSAUSWERTUNG
Erstelle die finale Auswertung in folgender Struktur:
1. Steckbrief (Wohnort, Mobilität, Sprachen, Kernkompetenzen).
2. Erfasste Kernkompetenzen.
3. Kurzfristig passende Jobs in der Region (3-5 Stellenbezeichnungen & typische Arbeitgeber).
4. Sprach- & Erreichbarkeits-Check.
5. Aktionsplan für die nächsten 14 Tage.

# START
Stelle ohne Begrüßung direkt die ERSTE Frage aus Phase 1 (PLZ/Wohnort und Mobilität).
"""

# Chat-Session und Verlauf initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # 💡 OPTIMIERUNG: Erste Frage fest einprogrammieren, um API-Limits zu sparen!
    erste_frage = "Hallo! Um passende Jobs für dich zu finden, brauche ich ein paar Infos. Wie lautet deine Postleitzahl oder dein Wohnort, und wie bist du mobil (Auto, Fahrrad, Bus/Bahn)?"
    st.session_state.messages.append({"role": "assistant", "content": erste_frage})

# Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User-Eingabe
if user_input := st.chat_input("Deine Antwort eingeben..."):
    # User-Nachricht speichern und anzeigen
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Chat-Historie für den nächsten Aufruf zusammenbauen
    formatted_contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        formatted_contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=m["content"])])
        )

    # Antwort generieren
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=formatted_contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3
        )
    )

    st.session_state.messages.append({"role": "assistant", "content": response.text})
    with st.chat_message("assistant"):
        st.write(response.text)
