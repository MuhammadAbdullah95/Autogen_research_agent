import streamlit as st
import os
from dotenv import load_dotenv
from research_agent.agents import ResearchAgent
from research_agent.data_loader import DataLoader


load_dotenv()

print("ok")


st.title("🤖🔍📚 Virtual Research Assistant")

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("groq api key is missing. Please add it to your environment variable")
    st.stop()

agents = ResearchAgent(groq_api_key)

data_loader = DataLoader()


query = st.text_input("Enter a research topic:")
