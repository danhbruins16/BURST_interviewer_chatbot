$ pip install -r requirements.txt

import streamlit as st
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# Streamlit title and description
st.title("AI-Led Quantum Physics Interview Bot")
st.write(
    "This chatbot will interview graduate students about their experiences studying quantum physics. "
    "To use this app, you need to provide an OpenAI API key."
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Initialize OpenAI client and chatbot model
    client = OpenAI(api_key=openai_api_key)
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key=openai_api_key)

    # Define the system prompt for the chatbot
    SYSTEM_PROMPT = (
        "You are a qualitative researcher conducting interviews with graduate students specializing in quantum physics. "
        "Your goal is to understand their experiences, challenges, and perspectives on the field. Follow these instructions: "
        "1. Guide the interview in a non-directive way. Let the respondent bring up relevant topics. "
        "2. Ask open-ended follow-up questions to clarify and deepen their responses. "
        "3. Avoid suggesting answers or being judgmental."
    )

    # Define pre-determined questions about quantum physics
    PRE_DETERMINED_QUESTIONS = [
        "What inspired you to study quantum physics?",
        "Can you describe your current research focus in quantum physics?",
        "What do you find most challenging about studying quantum physics?",
        "How do you see quantum physics evolving in the next decade?",
        "Can you share a significant breakthrough or insight you had in your studies?"
    ]

    # Define a function to dynamically generate follow-up questions based on user responses
    def ask_follow_up(response):
        follow_up_prompt = PromptTemplate(
            template=(
                "You are a researcher conducting a qualitative interview. Based on the response: '{response}', "
                "generate a thoughtful follow-up question to delve deeper into the respondent's perspective."
            ),
            input_variables=["response"]
        )
        return llm(follow_up_prompt.format(response=response))

    # Create a session state variable to store the chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Introduction and respondent details
    name = st.text_input("Please enter your name:")
    if name:
        st.write(f"Hello, {name}! Let's begin the interview.")

        # Display pre-determined questions
        for i, question in enumerate(PRE_DETERMINED_QUESTIONS, 1):
            st.subheader(f"Question {i}")
            user_response = st.text_area(f"{question}", key=f"q{i}")

            if user_response:
                # Store and display the current prompt
                st.session_state.messages.append({"role": "user", "content": user_response})
                with st.chat_message("user"):
                    st.markdown(user_response)

                # Generate and display a follow-up question
                follow_up_question = ask_follow_up(user_response)
                st.write("Follow-up Question:")
                st.write(follow_up_question)

                # Store the assistant's response
                st.session_state.messages.append({"role": "assistant", "content": follow_up_question})

        # End of interview summary
        st.subheader("Summary")
        st.write(
            "Thank you for participating in this interview! If you'd like, you can provide feedback below on how well "
            "the interview captured your thoughts."
        )
        feedback = st.radio(
            "How well does this interview reflect your experiences?",
            ("Poorly", "Partially", "Well", "Very Well"),
            index=2
        )
        st.write(f"Your feedback: {feedback}")

        # Option to download responses
        if st.button("Download Responses"):
            responses = "\n".join([
                f"Q{i+1}: {question}\nA{i+1}: {st.session_state.messages[2*i]['content']}\nFollow-up: {st.session_state.messages[2*i+1]['content']}"
                for i, question in enumerate(PRE_DETERMINED_QUESTIONS)
            ])
            st.download_button("Download", data=responses, file_name="interview_responses.txt")
