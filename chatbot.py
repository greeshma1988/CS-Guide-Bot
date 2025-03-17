import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
import time
import re

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
model = genai.GenerativeModel('models/gemini-1.5-flash')  # Using a flash model

# Define system prompt for the chatbot
SYSTEM_PROMPT = """
You are CSGuideBot, a specialized assistant for computer science engineering students and professionals.
Your expertise includes:
- Data structures and algorithms
- Programming languages (Python, Java, C++, etc.)
- Software engineering concepts
- System design
- Operating systems
- Database management
- Computer networks
- Technical interview preparation
- Career guidance in computer science

Provide concise, accurate, and helpful responses. Include code examples when relevant.
For interview questions, provide both the question and a well-structured answer.

IMPORTANT: You MUST ONLY answer questions related to computer science and software engineering.
"""

# Function to check if query is CS-related
def is_cs_related(query):
    # List of CS-related keywords
    cs_keywords = [
        "algorithm", "code", "program", "software", "data structure", "database", 
        "network", "operating system", "computer", "engineer", "development", 
        "java", "python", "c++", "javascript", "html", "css", "api", "backend", 
        "frontend", "fullstack", "interview", "leetcode", "complexity", "big o", 
        "cloud", "github", "git", "compiler", "debugging", "variable", "function",
        "class", "object", "inheritance", "polymorphism", "encapsulation", "abstraction",
        "recursion", "iteration", "sorting", "searching", "tree", "graph", "linked list",
        "stack", "queue", "hash table", "binary", "hex", "memory", "cpu", "gpu",
        "server", "client", "http", "https", "tcp", "ip", "dns", "rest", "soap", "json",
        "xml", "sql", "nosql", "agile", "scrum", "waterfall", "devops", "cicd", "testing",
        "unit test", "integration test", "system test", "browser", "web", "mobile", "app"
    ]
    
    # Check if any CS keyword is present in the query
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in cs_keywords)

# Ask Gemini if a query is CS-related (for ambiguous queries)
def verify_cs_topic(query):
    verification_prompt = f"""
    Determine if the following query is related to computer science, programming, software engineering, 
    or technical interviews. Answer with ONLY "Yes" or "No".
    
    Query: {query}
    
    Is this query related to computer science or software engineering? (Yes/No)
    """
    
    try:
        response = model.generate_content(verification_prompt)
        result = response.text.strip().lower()
        return "yes" in result
    except Exception:
        # Fall back to keyword matching if API call fails
        return is_cs_related(query)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! I'm CSGuideBot, your computer science engineering guide. How can I help you today? I can provide information on algorithms, programming concepts, system design, or help you prepare for technical interviews. Note that I'm specialized in computer science topics only."}
    ]

def main():
    st.title("CSGuideBot: CS Engineering Guide & Interview Prep")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't display system messages
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Get user input
    user_input = st.chat_input("Ask me about CS concepts, coding problems, or interview prep...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Show thinking indicator
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Thinking...")
            
            # First check if it's CS related
            is_related = is_cs_related(user_input)
            
            # If not obviously CS-related by keywords, double-check with the model
            if not is_related:
                is_related = verify_cs_topic(user_input)
            
            if is_related:
                try:
                    # Get only the content from messages (Gemini expects a simpler format)
                    formatted_messages = [
                        {"role": msg["role"], "parts": [msg["content"]]} 
                        for msg in st.session_state.messages
                        if msg["role"] in ["user", "assistant"]  # Skip system message for Gemini
                    ]
                    
                    # Insert system prompt as a user message at the beginning (Gemini workaround)
                    formatted_messages.insert(0, {
                        "role": "user", 
                        "parts": [f"You are acting as CSGuideBot with these instructions: {SYSTEM_PROMPT}. Respond to the upcoming messages accordingly."]
                    })
                    
                    # Generate response from Gemini
                    response = model.generate_content(formatted_messages)
                    assistant_response = response.text
                    
                    # Update placeholder with actual response
                    message_placeholder.write(assistant_response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    
                except Exception as e:
                    message_placeholder.write(f"I apologize, but I encountered an error: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
            else:
                # Not CS-related, provide a standard response
                not_cs_response = "I'm sorry, but I can only answer questions related to computer science and software engineering. Could you please ask me something about programming, algorithms, data structures, or other CS-related topics?"
                message_placeholder.write(not_cs_response)
                st.session_state.messages.append({"role": "assistant", "content": not_cs_response})

    # Run main chat interface
main()