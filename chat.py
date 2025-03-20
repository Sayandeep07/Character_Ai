import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()  # Stop execution if API key is missing

# Initialize the Generative AI model
my_llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.3)

# Set Streamlit page configuration
st.set_page_config(page_title="Character AI", page_icon="💀", layout="centered")

# Apply custom CSS
st.markdown(
    """
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
        }
        .stApp {
            background: #121212;
        }
        .stChatMessage {
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .stChatMessage.user {
            background-color: #444;
            text-align: left;
        }
        .stChatMessage.assistant {
            background-color: #007ACC;
            text-align: left;
        }
        .sidebar .sidebar-content {
            background: #222;
            color: white;
        }
        .stButton > button {
            background: #007ACC;
            color: white;
            border-radius: 8px;
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
    character_name = st.text_input("Character name", value=st.session_state.get("character_name", ""))

    my_prompt = PromptTemplate.from_template(
        "you are {character_name}, a fictional character, and you have the personality of {character_name}. Answer as if you are the character being asked by the fan: {question}"
    )

# Display chat history
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["message"])

# Chat input and sidebar for character selection
user_prompt = st.chat_input("Ask me")

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
