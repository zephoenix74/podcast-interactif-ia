import streamlit as st
import numpy as np
import os
import tempfile

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

# Configuration de l'API OpenAI (à remplacer par votre clé)
api_key = st.sidebar.text_input("Clé API OpenAI", type="password")

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
            180.0,  # Supposons une durée maximale de 3 minutes (180 secondes)
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
            with st.spinner("Simulation d'enregistrement... (MVP)"):
                # Simulation d'enregistrement pour le MVP
                question = "Quelle est la position actuelle d'Israël dans ce conflit?"
                st.session_state.is_playing = False  # Mettre en pause le podcast
                
                st.success(f"Question simulée: {question}")
                
                # Traitement de la question (simulation pour MVP)
                with st.spinner("L'IA prépare une réponse... (simulé pour MVP)"):
                    # Simulation de réponse
                    answer_text = "Selon les informations disponibles, Israël maintient une position défensive tout en répondant aux provocations. Le gouvernement israélien a déclaré qu'il continuera à protéger ses frontières et ses citoyens face aux menaces régionales."
                    
                    # Stocker la question et la réponse
                    st.session_state.questions_answers.append({
                        "question": question,
                        "answer": answer_text,
                        "position": st.session_state.current_position
                    })
        
        # Afficher l'historique des questions et réponses
        if st.session_state.questions_answers:
            st.subheader("Historique des questions")
            for i, qa in enumerate(st.session_state.questions_answers):
                with st.expander(f"Q{i+1}: {qa['question'][:50]}... (@{int(qa['position']//60):02d}:{int(qa['position']%60):02d})"):
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
