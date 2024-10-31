import os
import time
import random
import streamlit as st

from typing import List, Dict, Any

from webreader.reader import read_website
from webreader.analysis import get_website_summary, get_gpt_response
from webreader.utils import format_website_data

os.system('playwright install')
os.system('playwright install-deps')

# Get the website data
def get_data(url: str) -> str:
    data = read_website(url)
    formatted_data = format_website_data(data)
    return formatted_data


def get_summary(formatted_data: str) -> str:
    summary = get_website_summary(formatted_data)
    return summary


def get_response() -> str:
    internal_messages = st.session_state.internal_messages
    return get_gpt_response(internal_messages)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for private chat history
if "internal_messages" not in st.session_state:
    st.session_state.internal_messages = []

# Initialize session state for question
if "website_data" not in st.session_state:
    st.session_state.website_data = None


st.title("Web Reader")

# Move file uploader and clear chat button to sidebar
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.internal_messages = []
        st.session_state.website_data = None
        st.sidebar.empty()
        
    openai_api_key = st.text_input("OpenAI API Key:")
    if st.button("Save API Key"):
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            st.sidebar.success("API Key saved successfully!")
        else:
            st.sidebar.error("Please enter your OpenAI API key.")

    website_url = st.text_input("Enter a website URL:")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.sidebar.button("Generate summary"):
    if not os.environ["OPENAI_API_KEY"]:
        st.error("Please enter your OpenAI API key.")
    else:
        with st.spinner("Getting website data..."):
            website_data = get_data(website_url)
        st.sidebar.success("Website data retrieved successfully!")

        with st.spinner("Generating summary..."):
            website_summary_response = get_summary(website_data)
        st.sidebar.success("Website summary generated successfully!")


        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in website_summary_response:
                element = chunk.choices[0].delta.content
                # element = chunk
                if element is not None:
                    full_response += element
                    message_placeholder.markdown(full_response)
                    time.sleep(0.025)
            
            message_placeholder.markdown(full_response)

        st.session_state.internal_messages.append({
            "role": "assistant",
            "content": full_response
        })

        st.session_state.internal_messages.append({
            "role": "assistant",
            "content": full_response
        })

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })


# Chat input
if user_input := st.chat_input("How can I help you?"):
    if user_input:
        # Show the user input
        with st.chat_message("user"):
            st.write(user_input)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.internal_messages.append({"role": "user", "content": user_input})
        
        # Call dummy endpoint
        with st.spinner("Generating response..."):
            response = get_response() # Stream the response

        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in response:
                element = chunk.choices[0].delta.content
                # element = chunk
                if element is not None:
                    full_response += element
                    message_placeholder.markdown(full_response)
                    time.sleep(0.025)
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.internal_messages.append({"role": "assistant", "content": full_response})        
    else:
        st.warning("Please enter a message.")


