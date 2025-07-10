import streamlit as st
import os
import tempfile
import requests
import json

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
if 'questions_answers' not in st.session_state:
    st.session_state.questions_answers = []
if 'audio_response' not in st.session_state:
    st.session_state.audio_response = None

# Configuration des clés API dans la barre latérale
st.sidebar.header("Configuration de l'API")
elevenlabs_api_key = st.sidebar.text_input("Clé API ElevenLabs", type="password")

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

# Réponses prédéfinies pour les questions fréquentes sur le conflit Israël-Iran
predefined_responses = {
    "iran": "Le conflit entre l'Iran et Israël est complexe et remonte à plusieurs décennies. L'Iran ne reconnaît pas l'État d'Israël et soutient des groupes comme le Hezbollah et le Hamas qui s'opposent à Israël. De son côté, Israël considère le programme nucléaire iranien comme une menace existentielle. Les tensions récentes incluent des accusations mutuelles d'attaques et parfois des confrontations militaires directes.",
    
    "attaque": "En avril 2024, l'Iran a lancé une attaque directe contre Israël, impliquant environ 300 drones et missiles, dont la plupart ont été interceptés. Cette attaque était une réponse à une frappe israélienne sur le consulat iranien à Damas, qui a tué plusieurs officiers iraniens. Cet incident représente une escalade significative dans les tensions entre les deux pays.",
    
    "nucleaire": "Le programme nucléaire iranien est au cœur des tensions avec Israël. L'Iran affirme que son programme est pacifique et destiné à la production d'énergie, tandis qu'Israël et plusieurs pays occidentaux soupçonnent l'Iran de chercher à développer des armes nucléaires. Ces préoccupations ont conduit à des sanctions internationales contre l'Iran et à des actions clandestines attribuées à Israël pour ralentir le programme nucléaire iranien.",
    
    "états-unis": "Les États-Unis jouent un rôle important dans ce conflit. Ils sont un allié proche d'Israël et maintiennent des sanctions économiques contre l'Iran. L'administration américaine a condamné l'attaque iranienne d'avril 2024 et a aidé Israël à intercepter les missiles. Cependant, les États-Unis ont également appelé à la retenue pour éviter une escalade régionale majeure.",
    
    "hezbollah": "Le Hezbollah est un groupe armé et politique libanais soutenu par l'Iran. Il constitue une menace significative pour Israël depuis sa frontière nord. Le groupe possède un arsenal important de missiles et de drones, et a été impliqué dans plusieurs conflits avec Israël. Le soutien de l'Iran au Hezbollah est l'un des aspects clés du conflit indirect entre l'Iran et Israël.",
    
    "histoire": "Les tensions entre l'Iran et Israël se sont intensifiées après la révolution islamique iranienne de 1979. Avant cette date, sous le règne du Shah, l'Iran et Israël entretenaient des relations relativement cordiales. Depuis, l'Iran a adopté une position hostile envers Israël, le qualifiant de 'petit Satan' et appelant régulièrement à sa destruction. Ce sont des rivalités géopolitiques et idéologiques profondes qui structurent ce conflit.",
    
    "default": "Cette question touche à un aspect important du conflit Israël-Iran. Ce conflit implique des tensions historiques, religieuses et géopolitiques complexes. L'Iran ne reconnaît pas l'État d'Israël et soutient des groupes qui s'y opposent, tandis qu'Israël considère le programme nucléaire iranien et les proxys soutenus par l'Iran comme des menaces existentielles. Les tensions récentes incluent des échanges d'accusations et parfois des attaques directes ou indirectes."
}

# Fonction pour générer une réponse textuelle simple basée sur des mots-clés
def generate_simple_response(question):
    question_lower = question.lower()
    
    # Vérifier si la question contient des mots-clés connus
    for keyword, response in predefined_responses.items():
        if keyword in question_lower:
            return response
    
    # Réponse par défaut si aucun mot-clé n'est trouvé
    return predefined_responses["default"]

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

# Créer une section principale
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.header("Lecteur de Podcast")
    
    if st.session_state.podcast_path:
        # Message pour l'utilisateur concernant la pause manuelle
        st.warning("⚠️ Veuillez mettre le podcast en pause manuellement avant de poser une question.")
        
        # Afficher le lecteur audio
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
        question = st.text_area("Tapez votre question ici :", height=100, 
                                placeholder="Exemple: Pourquoi l'Iran a attaqué Israël?")
        
        if st.button("🔍 Poser la question"):
            if question:
                st.success(f"Question posée: {question}")
                
                # Générer une réponse simple basée sur des mots-clés
                answer_text = generate_simple_response(question)
                
                # Vérifier que la clé API ElevenLabs est disponible
                if not elevenlabs_api_key:
                    st.error("Veuillez entrer votre clé API ElevenLabs pour générer la réponse audio.")
                else:
                    # Générer l'audio de la réponse avec ElevenLabs
                    with st.spinner("Génération de la réponse audio..."):
                        audio_path = generate_audio_response(answer_text, voice_id, elevenlabs_api_key)
                        if audio_path:
                            st.session_state.audio_response = audio_path
                
                # Stocker la question et la réponse
                st.session_state.questions_answers.append({
                    "question": question,
                    "answer": answer_text,
                    "audio_path": st.session_state.audio_response
                })
                
                # Afficher la réponse
                st.success("Réponse obtenue!")
                st.info(answer_text)
                
                # Forcer le rafraîchissement pour afficher l'audio
                st.rerun()
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
st.markdown("Développé avec Streamlit et ElevenLabs")

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
