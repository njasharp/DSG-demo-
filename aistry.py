import os
import streamlit as st
from typing import Dict, Optional
from groq import Groq
from gtts import gTTS  # For text-to-speech
import tempfile

# Streamlit page configuration
st.set_page_config(layout="wide", page_title="Dynamic Perspective Story Generator", initial_sidebar_state="expanded")

# Supported models
SUPPORTED_MODELS: Dict[str, str] = {
    "Llama 3.2 1B (Preview)": "llama-3.2-1b-preview",
    "Llama 3 70B": "llama3-70b-8192",
    "Llama 3 8B": "llama3-8b-8192",
    "Llama 3.1 70B": "llama-3.1-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Mixtral 8x7B": "mixtral-8x7b-32768",
    "Gemma 2 9B": "gemma2-9b-it",
    "LLaVA 1.5 7B": "llava-v1.5-7b-4096-preview",
    "Llama 3.2 3B (Preview)": "llama-3.2-3b-preview",
    "Llama 3.2 11B Vision (Preview)": "llama-3.2-11b-vision-preview"
}

MAX_TOKENS: int = 1000

# Initialize Groq client with API key
@st.cache_resource
def get_groq_client() -> Optional[Groq]:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables. Please set it and restart the app.")
        return None
    return Groq(api_key=groq_api_key)

client = get_groq_client()

# Sidebar - Story Parameters
st.sidebar.image("p1.jpg")
st.sidebar.title("Dynamic Story Generator")

# New Topic Input at the Top
st.sidebar.subheader("Enter a Story Topic")
story_topic = st.sidebar.text_input("Topic (e.g., 'adventure', 'discovery', 'solitude')")

st.sidebar.subheader("Choose a Perspective")
perspective = st.sidebar.selectbox(
    "Select Perspective",
    ["Ant", "Bird", "Wind", "Cloud", "Tree", "Rock", "Shadow", "Raindrop", "Spider", "Grain of Sand"]
)

st.sidebar.subheader("Select Story Elements")
time_of_day = st.sidebar.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
weather = st.sidebar.selectbox("Weather", ["Sunny", "Cloudy", "Rainy", "Windy", "Stormy"])
environment = st.sidebar.selectbox("Environment", ["Forest", "City", "Desert", "Beach", "Mountain"])
interaction = st.sidebar.text_input("What will your perspective interact with? (e.g., a leaf, a building, etc.)")

# Sidebar - Model Configuration
st.sidebar.subheader("Model Configuration")
selected_model = st.sidebar.selectbox("Choose an AI Model", list(SUPPORTED_MODELS.keys()))

# Sidebar - Temperature Slider
st.sidebar.subheader("Temperature")
temperature = st.sidebar.slider("Set temperature for response variability:", min_value=0.0, max_value=1.0, value=0.7)

# Story Prompt Template
story_template = f"""
You are observing the world as a {perspective}. It is {time_of_day}, and the weather is {weather}. 
You are in a {environment} environment. As you move through this space, describe your interaction with {interaction}.
Make sure to include elements that reflect the topic of {story_topic}. 
Focus on sensory observations such as sights, sounds, and textures, and reflect on the experience from your unique perspective.
"""

# Initialize session state for selected agent and agent output
if 'agent_output' not in st.session_state:
    st.session_state.agent_output = None

# Function to get response from Groq API
def get_groq_response(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=SUPPORTED_MODELS[selected_model],
            messages=[
                {"role": "system", "content": "You are a creative AI story generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error: {e}")
        return ""

# Function to generate audio from text
def generate_audio(text: str):
    with st.spinner("Generating audio..."):
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name

# Submit button to generate the story
if st.sidebar.button("Generate Story"):
    if client:
        st.session_state.agent_output = get_groq_response(story_template)
    else:
        st.error("Groq client not initialized.")

# Main content area
st.image("p2.png")
st.title("Dynamic Perspective Story Generator")

st.write("### Generated Story:")
if st.session_state.agent_output:
    st.write(st.session_state.agent_output)
    
    # Button to generate audio from the generated story
    if st.button("Convert to Audio"):
        audio_file = generate_audio(st.session_state.agent_output)
        st.audio(audio_file)
else:
    st.info("Enter parameters in the sidebar and click 'Generate Story' to create a dynamic perspective-based story.")

# Footer
st.info("Story Generator by dw")
