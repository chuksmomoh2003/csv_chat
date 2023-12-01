#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import openai
from io import StringIO
import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv

# Load .env file
load_dotenv(find_dotenv(), override=True)

# Initialize 'data_file' in session state
st.session_state['data_file'] = st.session_state.get('data_file', None)

# Initialize system prompt template
prompt_template = ""

# Application title
st.markdown(
    """
    <h1 style="color: blue; text-align: right; 
        font-size: 48px; 
        text-shadow: 2px 2px 2px LightBlue;">Data to text</h1> 
    <hr/>
    """,
    unsafe_allow_html=True,
)

# Sidebar for API key input
with st.sidebar:
    api_key = st.text_input('OpenAI API Key:', type='password', value=os.getenv('OPENAI_API_KEY', ''))
    if api_key:
        openai.api_key = api_key
    else:
        st.error("Please enter your OpenAI API key.")

    chosen_file = st.file_uploader("Choose a file")
    if chosen_file is not None:
        if st.session_state.data_file != chosen_file:
            st.session_state.data_file = chosen_file

            # Convert to a string-based IO
            stringio = StringIO(chosen_file.getvalue().decode("utf-8"))

            # Read file in chunks
            chunk_size = 1000  # Define the size of each chunk
            data_chunks = pd.read_csv(StringIO(stringio.read()), chunksize=chunk_size)

            # Process each chunk (for demonstration, we just print the first chunk)
            for chunk in data_chunks:
                # Normally, you would process and store each chunk here
                st.dataframe(chunk)
                #break  # Remove this break statement to process all chunks

            # Update the system prompt
            prompt_template = """
            The data has been loaded and processed in chunks.
            """
            st.session_state.messages = [{"role": "system", "content": prompt_template}]

# Initialize 'messages' in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": prompt_template}]

# Chat input and processing
if query := st.chat_input("Enter your query:"):
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Ensure API key is set before making API calls
    if openai.api_key:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            temperature=0
        )

        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
            st.session_state.messages.append(response.choices[0].message)

        # Download the latest response
        st.download_button(
            label="Download result",
            data=response.choices[0].message.content,
            file_name='result.txt',
            mime='text/plain'
        )
    else:
        st.error("OpenAI API key is not set. Please enter your API key.")


# In[ ]:




