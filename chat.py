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
    st.title("Choose the Character")
    
    # New Chat button
    if st.button("New Chat"):
        reset_chat()
    
    # Character name input
    character_name = st.text_input("Character name", value=st.session_state.get("character_name", ""))

    # Create the prompt template without series name
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
    
    # Initialize LLM Chain
    chain = LLMChain(
        llm=my_llm,
        prompt=my_prompt
    )

    # Pass input data to LLM Chain
    input_data = {
        'character_name': character_name,
        'question': user_prompt
    }

    # Generate response
    try:
        response = chain.invoke(input=input_data)
        text_result = response["text"]
    except Exception as e:
        text_result = "Sorry, I couldn't process your request. Please try again later."
        st.error(text_result)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(text_result)

    # Add user and assistant messages to chat history
    st.session_state.chat_history.append({"role": "user", "message": user_prompt})
    st.session_state.chat_history.append({"role": "assistant", "message": text_result})

    # Update character name in session state
    st.session_state.character_name = character_name
