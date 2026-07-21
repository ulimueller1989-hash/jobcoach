import streamlit as st
from google import genai
from google.genai import types

# Titel der App
st.title("Dein persönlicher Job-Coach")

# 1. API-Client initialisieren
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 2. Chat-Session und Verlauf initialisieren (nur beim allerersten Start)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Fester Start-Text, der nur beim Erstellen der Session einmalig hinzugefügt wird
    erste_frage = "Hallo! Um passende Jobs für dich zu finden, brauche ich ein paar Infos. Wie lautet deine Postleitzahl oder dein Wohnort, und wie bist du mobil (Auto, Fahrrad, Bus/Bahn)?"
    st.session_state.messages.append({"role": "assistant", "content": erste_frage})

# 3. Bisherigen Chatverlauf auf dem Bildschirm anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. Benutzereingabe verarbeiten
if prompt := st.chat_input("Deine Antwort..."):
    # Nutzer-Nachricht sofort zum Verlauf hinzufügen und anzeigen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Chat-Historie für Gemini formatieren
    formatted_contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        formatted_contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
        )

    # 5. Antwort von Gemini generieren lassen
    with st.chat_message("assistant"):
        with st.spinner("Der Job-Coach denkt nach..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction="Du bist ein freundlicher, empathischer Job-Coach. Hilf Jobsuchenden Schritt für Schritt, indem du erst nach Standort/Mobilität, dann nach Berufserfahrung und Wünschen fragst."
                    ),
                )
                bot_reply = response.text
                st.write(bot_reply)
                
                # Antwort des Assistenten ebenfalls im Verlauf speichern
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                st.error(f"Ein Fehler ist aufgetreten: {e}")
