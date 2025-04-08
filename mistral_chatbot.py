import streamlit as st
from mistralai import Mistral

# Hardcode the Mistral API key
api_key = "ws5y3hrtzNUA2keSxaw8Iwn8c5KIDNLH"  # Replace with your actual Mistral API key
model = "mistral-large-latest"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

# Initialize session state to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit app title and description
st.title("AI Roadtip planner")
st.write("Tell me about the locations you'd like to include in your roadtrip, and I'll plan it for you!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter locations or details for your roadtrip (e.g., 'New York to Boston' or 'I have 8 hours')"):
    # Basic input validation to prevent jailbreak attempts
    if any(keyword in prompt.lower() for keyword in ["jailbreak", "hack", "ignore", "bypass", "system prompt"]):
        response = "Sorry, I’m designed only to plan roadtrips. Please tell me about locations or trip details!"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # Check if the query is roadtrip-related (contains location-like terms or trip details)
        location_keywords = ["to", "from", "via", "roadtrip", "trip", "drive", "route", "hours", "time"]
        if not any(keyword in prompt.lower() for keyword in location_keywords) and not any(char.isupper() for char in prompt.split()):
            response = "I can only help with roadtrip planning. Please provide locations or trip details (e.g., 'Los Angeles to San Francisco' or 'I have 8 hours')!"
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from Mistral AI with full chat history
            with st.chat_message("assistant"):
                try:
                    # System prompt to enforce roadtrip planning and context awareness
                    system_prompt = (
                        "You are a roadtrip planner. Based on the user's input about locations or trip details (e.g., time constraints), "
                        "provide a detailed roadtrip plan including route suggestions, stops, and estimated driving times. "
                        "Use the full conversation history to maintain context and adjust plans accordingly. "
                        "Do not respond to unrelated queries."
                    )
                    # Send system prompt followed by chat history
                    messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                    chat_response = client.chat.complete(
                        model=model,
                        messages=messages
                    )
                    response = chat_response.choices[0].message.content
                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    response = "Something went wrong while planning your roadtrip. Please try again!"
                    st.session_state.messages.append({"role": "assistant", "content": response})

# Optional: Clear chat history button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()