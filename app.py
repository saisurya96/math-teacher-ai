import streamlit as st
from math_teacher_ai import MathTeacherAI
import os

st.title("Math Teacher AI")

# Initialize the MathTeacherAI
if 'math_ai' not in st.session_state:
    st.session_state.math_ai = MathTeacherAI()

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize image state and processed state
if 'image_uploaded' not in st.session_state:
    st.session_state.image_uploaded = False
if 'image_processed' not in st.session_state:
    st.session_state.image_processed = False  # Ensures image is processed only once



# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  # Simply render the content as text, without any LaTeX detection

# Only allow image upload once and process it
if not st.session_state.image_uploaded:
    uploaded_file = st.file_uploader("Upload an image of an equation (once)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        st.session_state.image_uploaded = True
        st.session_state.image_file = uploaded_file

        # Save the file temporarily
        with open("temp_image.png", "wb") as f:
            f.write(uploaded_file.getvalue())

        # Process the image only if it hasn't been processed yet
        if not st.session_state.image_processed:
            with st.spinner("Analyzing the image..."):
                # Assuming response contains content (no LaTeX detection)
                response = st.session_state.math_ai.process_query("What's this equation about?", "user_session", "temp_image.png")

            # Add assistant response to chat history, but only once
            if not any(msg["content"] == response for msg in st.session_state.messages):
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Display the response
                with st.chat_message("assistant"):
                    st.markdown(response)

            # Mark the image as processed to avoid duplicate responses
            st.session_state.image_processed = True

        # Clean up the temporary file
        os.remove("temp_image.png")

# Accept user input for follow-up questions
if prompt := st.chat_input("What's your math question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response (no need to reprocess image)
    response = st.session_state.math_ai.process_query(prompt, "user_session")

    # Append and display the response as plain text
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
