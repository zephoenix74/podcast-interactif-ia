
import streamlit as st
import numpy as np
import os
import tempfile
from transformers import pipeline
import requests
import json
import io
import time
import base64
from pydub import AudioSegment
from pydub.playback import play

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

# Définition des variables de session
if 'podcast_path' not in st.session_state:
    st.session_state.podcast_path = None
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'questions_answers' not in st.session_state:
    st.session_state.questions_answers = []
if 'audio_response' not in st.session_state:
    st.session_state.audio_response = None
if 'audio_player_key' not in st.session_state:
    st.session_state.audio_player_key = 0

# Configuration des clés API dans la barre latérale (à remplacer par des secrets pour la production)
st.sidebar.header("Configuration des API")
elevenlabs_api_key = st.sidebar.text_input("Clé API ElevenLabs", type="password")
huggingface_api_key = st.sidebar.text_input("Clé API Hugging Face", type="password")

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

# Paramètres de voix ElevenLabs
st.sidebar.header("Configuration de la voix")
voice_options = {
    "Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Antoine": "ErXwobaYiN019PkySvjV",
    "Domi": "AZnzlk1XvdvUeBnXmlld",
    "Bella": "EXAVITQu4vr4xnSDxMaL",
    "Thomas": "GBv7mTt0atIp3Br8iCZE",
    "Nicole": "piTKgcLEGmPE4e6mEKli"
}
voice_name = st.sidebar.selectbox("Voix ElevenLabs", list(voice_options.keys()))
voice_id = voice_options[voice_name]

# Fonction pour générer une réponse texte avec Hugging Face
def generate_text_response(question, huggingface_api_key):
    try:
        API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-xxl"
        headers = {"Authorization": f"Bearer {huggingface_api_key}"}
        
        # Formater la question pour inclure le contexte du podcast
        formatted_question = f"Réponds en français à cette question sur le conflit Israël-Iran: {question}"
        
        payload = {
            "inputs": formatted_question,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()[0]["generated_text"]
    except Exception as e:
        st.error(f"Erreur lors de la génération de la réponse texte: {str(e)}")
        return "Je n'ai pas pu générer une réponse à votre question. Veuillez réessayer."

# Fonction pour générer l'audio avec ElevenLabs
def generate_audio_response(text, voice_id, api_key):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Sauvegarder l'audio dans un fichier temporaire
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
        else:
            st.error(f"Erreur API ElevenLabs: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la génération audio: {str(e)}")
        return None

# Fonctions pour la capture audio depuis le navigateur (avec Web Speech API)
def add_speech_recognition_js():
    st.markdown(
        """
        <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'fr-FR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        function startRecording() {
            recognition.start();
            document.getElementById('status').textContent = 'Écoute en cours...';
        }
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('result').value = transcript;
            document.getElementById('status').textContent = 'Enregistrement terminé';
            document.getElementById('submit-btn').click();
        };
        
        recognition.onerror = function(event) {
            document.getElementById('status').textContent = 'Erreur: ' + event.error;
        };
        </script>
        
        <button onclick="startRecording()">🎤 Poser une question oralement</button>
        <p id="status">Prêt à enregistrer</p>
        <input type="hidden" id="result">
        """,
        unsafe_allow_html=True
    )

# Créer une section principale
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.header("Lecteur de Podcast")
    
    if st.session_state.podcast_path:
        # Afficher le lecteur audio avec une clé unique pour forcer le rechargement
        st.audio(st.session_state.podcast_path, key=f"podcast_player_{st.session_state.audio_player_key}")
        
        # Afficher la réponse audio si disponible
        if st.session_state.audio_response:
            st.subheader("Réponse de l'IA")
            st.audio(st.session_state.audio_response, key=f"response_player_{st.session_state.audio_player_key}")
    else:
        st.info("Veuillez télécharger un podcast pour commencer.")

with main_col2:
    st.header("Poser une question")
    
    # Zone de texte pour saisir une question
    if st.session_state.podcast_path:
        # Ajout du JavaScript pour la reconnaissance vocale (ne fonctionne pas dans Streamlit Cloud)
        # add_speech_recognition_js()  # Décommentez pour essayer la reconnaissance vocale
        
        # Saisie de la question par texte (alternative à la reconnaissance vocale)
        question = st.text_area("Tapez votre question ici :", height=100, 
                                placeholder="Exemple: Pourquoi l'Iran a attaqué Israël?")
        
        # Bouton caché pour la soumission depuis JavaScript
        submit_btn = st.empty()
        
        if st.button("🔍 Poser la question", key="submit-btn") or submit_btn:
            if question:
                # Forcer la mise en pause du podcast en rechargeant le lecteur audio
                st.session_state.is_playing = False
                st.session_state.audio_player_key += 1  # Incrémenter pour forcer le rechargement
                
                st.success(f"Question posée: {question}")
                
                # Traitement de la question
                with st.spinner("L'IA prépare une réponse..."):
                    # Vérifier que les clés API sont disponibles
                    if not huggingface_api_key:
                        st.error("Veuillez entrer votre clé API Hugging Face.")
                    elif not elevenlabs_api_key:
                        st.error("Veuillez entrer votre clé API ElevenLabs.")
                    else:
                        try:
                            # Générer la réponse textuelle avec Hugging Face
                            answer_text = generate_text_response(question, huggingface_api_key)
                            
                            # Générer l'audio de la réponse avec ElevenLabs
                            with st.spinner("Génération de la réponse audio..."):
                                audio_path = generate_audio_response(answer_text, voice_id, elevenlabs_api_key)
                                if audio_path:
                                    st.session_state.audio_response = audio_path
                            
                            # Stocker la question et la réponse
                            st.session_state.questions_answers.append({
                                "question": question,
                                "answer": answer_text,
                                "position": st.session_state.current_position,
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
st.markdown("Développé avec Streamlit, ElevenLabs et Hugging Face")

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
