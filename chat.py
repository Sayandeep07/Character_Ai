import streamlit as st
from langchain_google_genai 
import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
import os
from dotenv import load_dotenv
import speech_recognition as sr 

def recognize_speech():
    # Initialize recognizer
    recognizer = sr.Recognizer()
    # Use microphone as source
    with sr.Microphone() as source:
        st.info("Adjusting for ambient noise. Please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        st.info("Listening... Speak now!")
        try:
            # Capture audio and recognize using Google Speech Recognition
            audio_data = recognizer.listen(source)
            st.info("Recognizing...")
            text = recognizer.recognize_google(audio_data)
            st.success(f"Recognized: {text}")
            return text  # Return the recognized text
        except sr.UnknownValueError:
            st.warning("Sorry, could not understand the audio.")
            return None # Return None on error
        except sr.RequestError:
            st.error("Could not request results. Check your internet connection.")
            return None # Return None on error

if __name__ == "__main__":
    # The direct call is removed from here, as it's part of the Streamlit flow now.
    pass

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()  # Stop execution if API key is missing

# Initialize the Generative AI model
my_llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.7)

# Set Streamlit page configuration
st.set_page_config(page_title="Character AI", page_icon="🤖", layout="centered")

# Apply custom neon CSS with gradient background
st.markdown(
    """
    <style>
        html, body {
        height: 100vh;
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460) !important;
        background-attachment: fixed;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background: transparent !important;
    }
        .stChatMessage {
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .stChatMessage.user {
            background: rgba(255, 0, 150, 0.3);
            border-left: 4px solid #ff00ff;
            text-align: left;
        }
        .stChatMessage.assistant {
            background: rgba(0, 255, 255, 0.3);
            border-left: 4px solid #00ffff;
            text-align: left;
        }
        .sidebar .sidebar-content {
            background: rgba(20, 20, 20, 0.8);
            color: white;
        }
        .stButton > button {
            background: linear-gradient(90deg, #ff00ff, #00ffff);
            color: white;
            border-radius: 8px;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0px 0px 10px rgba(255, 0, 255, 0.8);
        }
        .stButton > button:hover {
            box-shadow: 0px 0px 15px rgba(0, 255, 255, 1);
        }
        .stTextInput > div > div > input {
            background: rgba(0, 0, 0, 0.7);
            color: white;
            border: 2px solid #ff00ff;
            border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.header("Character AI")
st.subheader("Chat with your character")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to reset chat
def reset_chat():
    st.session_state.chat_history = []
    st.session_state.character_name = ""

# Sidebar for character selection
with st.sidebar:
    if st.button("New Chat"):
        reset_chat()

    st.title("Choose the Character")
    character_name = st.selectbox("Character name", ["Sukuna", "Doraemon", "Trump", "Elon Musk","Taylor Swift"], index=0)

    my_prompt = PromptTemplate.from_template(
        """
        You are {character_name}, a well-known and iconic character with a distinct personality.
        Stay completely in character and respond in an engaging, humorous, and natural way.
        If you're Gojo, be charming, confident, and witty. If you're Sukuna, be menacing but sarcastically funny.
        If you're Doraemon, be kind and wise, with a touch of childlike wonder. If you're Trump, be bold and over-the-top.
        If you're Cat, be playful and mischievous, as a talking cat would be.
        Your responses should be highly entertaining, full of personality, and as if you are truly the character.
        The fan asks: {question}
        """
    )

# Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["message"])

# Voice input button outside the text input check
voice_input_button = st.button("🎙️ Speak Now")

# Handle text input OR voice input
user_prompt = st.chat_input("Ask me")

if voice_input_button:
    # If voice button was clicked, attempt speech recognition
    recognized_text = recognize_speech()
    if recognized_text:
        user_prompt = recognized_text # Use recognized text as the prompt
    else:
        # Keep user_prompt as None if recognition failed, so it doesn't proceed
        user_prompt = None 

# Process the prompt if it exists (either from text input or successful voice recognition)
if user_prompt:
    st.chat_message("user").markdown(user_prompt)

    chain = LLMChain(llm=my_llm, prompt=my_prompt)
    input_data = {'character_name': character_name, 'question': user_prompt}

    try:
        response = chain.invoke(input=input_data)
        text_result = response["text"]
    except Exception as e:
        text_result = "Sorry, I couldn't process your request. Please try again later."
        st.error(text_result)

    with st.chat_message("assistant"):
        st.markdown(text_result)

    st.session_state.chat_history.append({"role": "user", "message": user_prompt})
    st.session_state.chat_history.append({"role": "assistant", "message": text_result})

    st.session_state.character_name = character_name
    
