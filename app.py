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

# Définition des variables de session
if 'podcast_path' not in st.session_state:
    st.session_state.podcast_path = None
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'current_position' not in st.session_state:
    st.session_state.current_position = 0
if 'questions_answers' not in st.session_state:
    st.session_state.questions_answers = []

# Configuration de l'API OpenAI
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
                st.success("Podcast mis en pause")
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
    
    # Zone de texte pour saisir une question
    if st.session_state.podcast_path:
        # Saisie de la question par texte (en attendant de résoudre les problèmes audio)
        question = st.text_area("Tapez votre question ici (MVP) :", height=100)
        
        if st.button("🔍 Poser la question"):
            if question:
                # Mettre en pause le podcast
                st.session_state.is_playing = False
                
                st.success(f"Question posée: {question}")
                
                # Traitement de la question avec OpenAI si la clé API est disponible
                if api_key:
                    with st.spinner("L'IA prépare une réponse..."):
                        try:
                            # Générer la réponse textuelle avec OpenAI
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "Tu es un expert en géopolitique répondant à des questions sur le conflit Israël-Iran. Réponds de manière concise et factuelle."},
                                    {"role": "user", "content": question}
                                ]
                            )
                            answer_text = response.choices[0].message.content
                            
                            # Dans un MVP complet, on convertirait cette réponse en audio avec la voix choisie
                            # Puis on l'intégrerait au podcast
                            
                            # Stocker la question et la réponse
                            st.session_state.questions_answers.append({
                                "question": question,
                                "answer": answer_text,
                                "position": st.session_state.current_position
                            })
                            
                            # Afficher la réponse
                            st.success("Réponse obtenue!")
                            st.info(answer_text)
                            
                            # Dans un MVP complet: générer l'audio de la réponse
                            st.warning("Dans la version complète, cette réponse serait convertie en audio avec la voix choisie.")
                            
                        except Exception as e:
                            st.error(f"Erreur lors de la génération de la réponse: {str(e)}")
                else:
                    # Réponse simulée si pas de clé API
                    answer_text = "Pour comprendre pourquoi l'Iran a attaqué Israël, il faut considérer plusieurs facteurs historiques et géopolitiques. Les tensions entre ces deux pays remontent à plusieurs décennies, avec l'Iran qui considère Israël comme un ennemi idéologique. L'attaque récente peut être vue comme une escalade dans ce conflit de longue date, potentiellement déclenchée par des actions spécifiques d'Israël ou comme une manœuvre stratégique de l'Iran pour renforcer sa position régionale."
                    
                    st.session_state.questions_answers.append({
                        "question": question,
                        "answer": answer_text,
                        "position": st.session_state.current_position
                    })
                    
                    st.info(answer_text)
                    st.warning("Note: Cette réponse est simulée. Entrez une clé API OpenAI pour des réponses réelles.")
            else:
                st.warning("Veuillez entrer une question.")
        
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
