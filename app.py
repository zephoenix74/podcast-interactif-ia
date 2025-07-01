
import streamlit as st
import os
import tempfile
from pathlib import Path
import time
import numpy as np
import wave
import contextlib
import io
import soundfile as sf
from pydub import AudioSegment
import speech_recognition as sr
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

# Définition des variables de session
if 'podcast_path' not in st.session_state:
    st.session_state.podcast_path = None
if 'podcast_duration' not in st.session_state:
    st.session_state.podcast_duration = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'questions_answers' not in st.session_state:
    st.session_state.questions_answers = []

# Fonction pour obtenir la durée d'un fichier audio
def get_audio_duration(file_path):
    with contextlib.closing(wave.open(file_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


# Configuration de l'API OpenAI (à remplacer par votre clé)
api_key = st.sidebar.text_input("Clé API OpenAI", type="password")
client = OpenAI(api_key=api_key) if api_key else None

# Sidebar pour télécharger le podcast et afficher les informations
st.sidebar.header("Configuration du podcast")

# Zone de téléchargement du podcast
uploaded_file = st.sidebar.file_uploader("Télécharger un podcast (MP3)", type=['mp3'])

if uploaded_file is not None:
    # Sauvegarde temporaire du fichier
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state.podcast_path = tmp_file.name
    
    # Obtenir la durée du podcast
    audio = AudioSegment.from_mp3(st.session_state.podcast_path)
    st.session_state.podcast_duration = len(audio) / 1000.0  # Convertir en secondes
    
    st.sidebar.success(f"Podcast téléchargé: {uploaded_file.name}")
    st.sidebar.info(f"Durée: {st.session_state.podcast_duration:.2f} secondes")

# Paramètres de voix
st.sidebar.header("Configuration de la voix IA")
voice_model = st.sidebar.selectbox(
    "Modèle de voix",
    ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
)

# Créer une section principale
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.header("Lecteur de Podcast")
    
    if st.session_state.podcast_path:
        # Afficher le lecteur audio
        st.audio(st.session_state.podcast_path)
        
        # Contrôles du podcast
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Lecture"):
                st.session_state.is_playing = True
        with col2:
            if st.button("⏸️ Pause"):
                st.session_state.is_playing = False
        with col3:
            if st.button("🔄 Redémarrer"):
                st.session_state.current_position = 0
                st.session_state.is_playing = False
                
        # Position actuelle (simulée)
        progress = st.slider(
            "Position dans le podcast", 
            0.0, 
            float(st.session_state.podcast_duration), 
            float(st.session_state.current_position),
            step=1.0
        )
        st.session_state.current_position = progress
        
        # Afficher le temps actuel
        st.text(f"Position actuelle: {int(st.session_state.current_position // 60):02d}:{int(st.session_state.current_position % 60):02d}")
    else:
        st.info("Veuillez télécharger un podcast pour commencer.")

with main_col2:
    st.header("Poser une question")
    
    # Option pour enregistrer une question
    if st.session_state.podcast_path:
        if st.button("🎤 Enregistrer une question"):
            with st.spinner("Enregistrement en cours... Parlez maintenant"):
                # Simulation d'enregistrement pour le MVP
                # Dans une implémentation réelle, utilisez le microphone ici
                # En utilisant par exemple speech_recognition
                time.sleep(2)  # Simuler l'enregistrement
                
                # Pour le MVP, nous allons simuler une question
                question = "Quelle est la position actuelle d'Israël dans ce conflit?"
                st.session_state.is_playing = False  # Mettre en pause le podcast
                
                st.success(f"Question enregistrée: {question}")
                
                # Traitement de la question (simulation pour MVP)
                if api_key:
                    with st.spinner("L'IA prépare une réponse..."):
                        # Simulation de l'appel à l'API OpenAI
                        answer_text = "Selon les informations les plus récentes, Israël maintient sa position défensive tout en répondant aux provocations. Le gouvernement israélien a déclaré qu'il continuera à protéger ses frontières et ses citoyens face aux menaces régionales."
                        
                        # Dans une implémentation réelle, on générerait l'audio via l'API OpenAI TTS
                        # response = client.audio.speech.create(
                        #     model="tts-1",
                        #     voice=voice_model,
                        #     input=answer_text
                        # )
                        
                        # Stocker la question et la réponse
                        st.session_state.questions_answers.append({
                            "question": question,
                            "answer": answer_text,
                            "position": st.session_state.current_position
                        })
                else:
                    st.error("Veuillez entrer une clé API OpenAI valide pour obtenir une réponse.")
        
        # Afficher l'historique des questions et réponses
        if st.session_state.questions_answers:
            st.subheader("Historique des questions")
            for i, qa in enumerate(st.session_state.questions_answers):
                with st.expander(f"Q{i+1}: {qa['question'][:50]}... (@{int(qa['position']//60):02d}:{int(qa['position']%60):02d})"):
                    st.write(f"**Question:** {qa['question']}")
                    st.write(f"**Réponse:** {qa['answer']}")


# Fonction pour reconnaître la parole à partir d'un enregistrement audio
def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        st.info("En écoute... Parlez maintenant")
        audio = recognizer.listen(source)
        
    try:
        return recognizer.recognize_google(audio, language="fr-FR")
    except sr.RequestError:
        return "Erreur de connexion à l'API de reconnaissance vocale"
    except sr.UnknownValueError:
        return "Impossible de reconnaître la parole"

# Fonction pour générer une réponse à partir de l'API OpenAI
def generate_answer(client, question, context="Podcast sur le conflit Israël-Iran"):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Tu es un expert en géopolitique répondant à des questions sur le {context}. Réponds de manière concise et factuelle."},
                {"role": "user", "content": question}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération de la réponse: {str(e)}"

# Fonction pour convertir le texte en parole avec la voix choisie
def text_to_speech(client, text, voice_model):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_model,
            input=text
        )
        
        # Convertir la réponse en bytes pour la lecture
        audio_data = io.BytesIO(response.content)
        return audio_data
    except Exception as e:
        return None

# Fonction pour mixer l'audio de la réponse avec le podcast
def insert_answer_in_podcast(podcast_path, answer_audio, position):
    # Charger le podcast original
    podcast = AudioSegment.from_mp3(podcast_path)
    
    # Convertir la position en millisecondes
    pos_ms = position * 1000
    
    # Diviser le podcast en deux parties: avant et après la position
    podcast_before = podcast[:pos_ms]
    podcast_after = podcast[pos_ms:]
    
    # Charger l'audio de la réponse
    answer = AudioSegment.from_file(answer_audio)
    
    # Combiner les trois segments: avant + réponse + après
    new_podcast = podcast_before + answer + podcast_after
    
    # Sauvegarder le nouveau podcast
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    new_podcast.export(output_path, format="mp3")
    
    return output_path

# Code pour implémenter l'enregistrement réel du microphone (à décommenter pour l'implémentation finale)
def real_record_question():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with st.spinner("Préparation du microphone..."):
        question = recognize_speech_from_mic(recognizer, microphone)
    
    if question and question not in ["Erreur de connexion à l'API de reconnaissance vocale", "Impossible de reconnaître la parole"]:
        st.success(f"Question enregistrée: {question}")
        return question
    else:
        st.error(f"Problème avec l'enregistrement: {question}")
        return None

# Fonction pour créer une version interactive du podcast avec toutes les réponses
def create_interactive_podcast(podcast_path, questions_answers, client, voice_model):
    # Charger le podcast original
    podcast = AudioSegment.from_mp3(podcast_path)
    
    # Trier les questions par position
    sorted_qa = sorted(questions_answers, key=lambda x: x['position'])
    
    # Insérer les réponses une par une
    current_podcast = podcast
    offset = 0  # Pour ajuster les positions après chaque insertion
    
    for qa in sorted_qa:
        # Générer l'audio de la réponse
        answer_text = qa['answer']
        answer_audio = text_to_speech(client, answer_text, voice_model)
        
        if answer_audio:
            # Convertir BytesIO en fichier temporaire
            temp_answer = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_answer.write(answer_audio.getvalue())
            temp_answer.close()
            
            # Charger l'audio de la réponse
            answer_segment = AudioSegment.from_mp3(temp_answer.name)
            
            # Calculer la position ajustée
            adjusted_position = qa['position'] * 1000 + offset
            
            # Diviser le podcast
            podcast_before = current_podcast[:adjusted_position]
            podcast_after = current_podcast[adjusted_position:]
            
            # Combiner avec la réponse
            current_podcast = podcast_before + answer_segment + podcast_after
            
            # Mettre à jour l'offset pour les prochaines insertions
            offset += len(answer_segment)
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_answer.name)
    
    # Sauvegarder le podcast interactif final
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    current_podcast.export(output_path, format="mp3")
    
    return output_path


# Ajout d'un onglet pour les fonctionnalités avancées
tab1, tab2 = st.tabs(["Podcast Interactif", "Fonctionnalités Avancées"])

with tab1:
    # Le contenu existant de l'interface principale reste ici
    pass  # Le contenu précédent serait placé ici

with tab2:
    st.header("Fonctionnalités Avancées")
    
    # Créer un podcast interactif complet
    if st.session_state.podcast_path and st.session_state.questions_answers and api_key:
        if st.button("🔄 Générer un podcast interactif complet"):
            with st.spinner("Création du podcast interactif en cours..."):
                # Simuler la création du podcast pour le MVP
                time.sleep(3)
                
                st.success("Podcast interactif généré avec succès!")
                st.info("Dans la version finale, cette fonction créerait un nouveau fichier MP3 avec toutes les questions et réponses intégrées aux bons moments.")
                
                # Afficher un exemple de téléchargement (simulé pour le MVP)
                st.download_button(
                    label="📥 Télécharger le podcast interactif",
                    data=open(st.session_state.podcast_path, "rb").read(),  # Dans le MVP, on renvoie simplement le podcast original
                    file_name="podcast_interactif.mp3",
                    mime="audio/mp3"
                )
    else:
        if not st.session_state.podcast_path:
            st.warning("Veuillez d'abord télécharger un podcast.")
        elif not st.session_state.questions_answers:
            st.warning("Posez au moins une question avant de générer un podcast interactif.")
        elif not api_key:
            st.warning("Une clé API OpenAI valide est nécessaire pour cette fonctionnalité.")
    
    # Options de configuration avancées
    st.subheader("Configuration avancée")
    
    # Paramètres du modèle
    gpt_model = st.selectbox(
        "Modèle GPT",
        ["gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    
    # Paramètres de la synthèse vocale
    col1, col2 = st.columns(2)
    with col1:
        speed = st.slider("Vitesse de la voix", 0.5, 2.0, 1.0, step=0.1)
    with col2:
        pitch = st.slider("Tonalité de la voix", 0.5, 2.0, 1.0, step=0.1)
    
    # Contexte personnalisé pour le podcast
    podcast_context = st.text_area(
        "Contexte du podcast (pour améliorer les réponses de l'IA)",
        "Podcast de 3 minutes sur le conflit Israel-Iran, couvrant les origines, les développements récents et les implications géopolitiques."
    )
    
    # Options d'export
    st.subheader("Options d'export")
    
    export_format = st.radio(
        "Format d'export",
        ["MP3", "WAV", "OGG"],
        horizontal=True
    )
    
    export_quality = st.select_slider(
        "Qualité audio",
        options=["Basse (64kbps)", "Moyenne (128kbps)", "Haute (256kbps)", "Très haute (320kbps)"],
        value="Moyenne (128kbps)"
    )
    
    # Analyse des questions
    st.subheader("Analyse des questions")
    
    if st.session_state.questions_answers:
        # Afficher un graphique des positions des questions
        positions = [qa["position"] for qa in st.session_state.questions_answers]
        
        # Créer un histogramme simple des positions des questions
        hist_values = np.histogram(
            positions, 
            bins=10, 
            range=(0, st.session_state.podcast_duration)
        )[0]
        
        st.bar_chart(hist_values)
        st.caption("Distribution des questions dans le podcast")
        
        # Afficher les questions les plus fréquentes (simulé pour le MVP)
        st.write("**Thèmes des questions:**")
        st.info("Dans la version finale, cette section afficherait une analyse des thèmes des questions posées.")

# Pied de page
st.markdown("---")
st.markdown("Podcast Interactif avec IA - Version MVP")
st.markdown("Développé avec Streamlit et OpenAI")

# Nettoyage des fichiers temporaires à la fermeture de l'application
def cleanup():
    if st.session_state.podcast_path and os.path.exists(st.session_state.podcast_path):
        os.unlink(st.session_state.podcast_path)

# Enregistrer la fonction de nettoyage pour qu'elle s'exécute à la fermeture
import atexit
atexit.register(cleanup)
