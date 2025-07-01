import streamlit as st
import numpy as np
import os
import tempfile
from openai import OpenAI

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

# Clé API OpenAI directement dans le code (pour le MVP uniquement)
OPENAI_API_KEY = "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"  # Remplacez par votre clé
client = OpenAI(api_key=OPENAI_API_KEY)

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
        # Utilisez GPT pour générer la réponse mais pas TTS
        # Simulation de TTS pour le MVP
        st.warning("Synthèse vocale désactivée dans cette version du MVP. Réponse textuelle uniquement.")
        return None
    except Exception as e:
        st.error(f"Erreur lors de la génération audio: {str(e)}")
        return None

# Créer une section principale
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.header("Lecteur de Podcast")
    
    if st.session_state.podcast_path:
        # Afficher le lecteur audio
        st.audio(st.session_state.podcast_path)
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
                        
                        # Stocker la question et la réponse
                        st.session_state.questions_answers.append({
                            "question": question,
                            "answer": answer_text
                        })
                        
                        # Afficher la réponse
                        st.success("Réponse obtenue!")
                        st.info(answer_text)
                        
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

# Enregistrer la fonction de nettoyage pour qu'elle s'exécute à la fermeture
import atexit
atexit.register(cleanup)
