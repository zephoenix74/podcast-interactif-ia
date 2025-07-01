import streamlit as st
import numpy as np
import os
import tempfile
from openai import OpenAI
import base64
import time

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Podcast Interactif IA",
    page_icon="🎙️",
    layout="wide"
)

# Configuration du titre et description
st.title("Podcast Interactif avec IA")
st.markdown("""
    Écoutez un podcast et posez des questions à n'importe quel moment.
    L'IA répondra avec la voix d'un des animateurs du podcast.
""")

# Récupération sécurisée de la clé API
if 'openai' in st.secrets:
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
else:
    # Fallback pour le développement local ou si la clé n'est pas configurée
    api_key = st.sidebar.text_input("Clé API OpenAI", type="password")
    client = OpenAI(api_key=api_key) if api_key else None

# Définition des variables de session
if 'podcast_path' not in st.session_state:
    st.session_state.podcast_path = None
if 'questions_answers' not in st.session_state:
    st.session_state.questions_answers = []
if 'audio_response' not in st.session_state:
    st.session_state.audio_response = None

# Sidebar pour télécharger le podcast et afficher les informations
st.sidebar.header("Configuration du podcast")

# Zone de téléchargement du podcast
uploaded_file = st.sidebar.file_uploader("Télécharger un podcast (MP3)", type=['mp3'])

if uploaded_file is not None:
    # Sauvegarde temporaire du fichier
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state.podcast_path = tmp_file.name
    
    st.sidebar.success(f"Podcast téléchargé: {uploaded_file.name}")

# Paramètres de voix
st.sidebar.header("Configuration de la voix IA")
voice_model = st.sidebar.selectbox(
    "Modèle de voix",
    ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
)

# Fonction pour générer l'audio TTS
def generate_audio_response(text, voice):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
            speed=1.0
        )
        
        # Sauvegarder l'audio dans un fichier temporaire
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        with open(temp_path, "wb") as f:
            f.write(response.content)
        
        return temp_path
    except Exception as e:
        st.error(f"Erreur lors de la génération audio: {str(e)}")
        return None

# Créer une section principale
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.header("Lecteur de Podcast")
    
    if st.session_state.podcast_path:
        # Afficher le lecteur audio (version simplifiée)
        st.audio(st.session_state.podcast_path)
        
        # Afficher la réponse audio si disponible
        if st.session_state.audio_response:
            st.subheader("Réponse de l'IA")
            st.audio(st.session_state.audio_response)
    else:
        st.info("Veuillez télécharger un podcast pour commencer.")

with main_col2:
    st.header("Poser une question")
    
    # Zone de texte pour saisir une question
    if st.session_state.podcast_path:
        # Saisie de la question par texte
        question = st.text_area("Tapez votre question ici :", height=100)
        
        if st.button("🔍 Poser la question"):
            if question:
                st.success(f"Question posée: {question}")
                
                # Traitement de la question avec OpenAI
                with st.spinner("L'IA prépare une réponse..."):
                    try:
                        # Générer la réponse textuelle avec OpenAI
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Tu es un expert francophone en géopolitique répondant à des questions sur le conflit Israël-Iran. Réponds en français de manière concise et factuelle."},
                                {"role": "user", "content": question}
                            ]
                        )
                        answer_text = response.choices[0].message.content
                        
                        # Générer l'audio de la réponse
                        with st.spinner("Génération de la réponse audio..."):
                            audio_path = generate_audio_response(answer_text, voice_model)
                            if audio_path:
                                st.session_state.audio_response = audio_path
                        
                        # Stocker la question et la réponse
                        st.session_state.questions_answers.append({
                            "question": question,
                            "answer": answer_text,
                            "position": 0,  # Simplification pour le MVP
                            "audio_path": audio_path
                        })
                        
                        # Afficher la réponse
                        st.success("Réponse obtenue!")
                        st.info(answer_text)
                        
                        # Forcer le rafraîchissement pour afficher l'audio
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la génération de la réponse: {str(e)}")
            else:
                st.warning("Veuillez entrer une question.")
        
        # Afficher l'historique des questions et réponses
        if st.session_state.questions_answers:
            st.subheader("Historique des questions")
            for i, qa in enumerate(st.session_state.questions_answers):
                with st.expander(f"Q{i+1}: {qa['question'][:50]}..."):
                    st.write(f"**Question:** {qa['question']}")
                    st.write(f"**Réponse:** {qa['answer']}")
                    if "audio_path" in qa and qa["audio_path"]:
                        st.audio(qa["audio_path"])

# Pied de page
st.markdown("---")
st.markdown("Podcast Interactif avec IA - Version MVP")
st.markdown("Développé avec Streamlit")

# Nettoyage des fichiers temporaires à la fermeture de l'application
def cleanup():
    if st.session_state.podcast_path and os.path.exists(st.session_state.podcast_path):
        try:
            os.unlink(st.session_state.podcast_path)
        except:
            pass
    
    # Nettoyer les fichiers audio temporaires
    for qa in st.session_state.questions_answers:
        if "audio_path" in qa and qa["audio_path"] and os.path.exists(qa["audio_path"]):
            try:
                os.unlink(qa["audio_path"])
            except:
                pass

# Enregistrer la fonction de nettoyage pour qu'elle s'exécute à la fermeture
import atexit
atexit.register(cleanup)
