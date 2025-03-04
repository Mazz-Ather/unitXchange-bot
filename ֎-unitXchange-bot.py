import os
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Gemini-Pro!",
    page_icon="֎",  # Favicon emoji
    layout="wide",  # Changed to wide for better layout
)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-2.0-flash')

# Add this constant for the chat history file
CHAT_HISTORY_FILE = "chat_histories.json"

def get_chat_title(prompt):
    """Generate a short title from the first question"""
    # Remove any special characters and extra spaces
    clean_prompt = re.sub(r'[^\w\s]', '', prompt)
    # Get first 30 characters
    title = clean_prompt[:30].strip()
    # Add ellipsis if longer than 30 characters
    if len(clean_prompt) > 30:
        title += "..."
    return title if title else "New Chat"

def is_conversion_question(text):
    """Check if the question is about unit conversion with strict validation"""
    # Define valid units and their variations
    valid_units = {
        'length': ['kilometer', 'kilometre', 'meter', 'metre', 'centimeter', 'centimetre', 
                  'millimeter', 'millimetre', 'mile', 'yard', 'foot', 'feet', 'inch', 'km', 
                  'm', 'cm', 'mm', 'mi', 'yd', 'ft', 'in'],
        'weight': ['kilogram', 'kilo', 'gram', 'milligram', 'pound', 'ounce', 'kg', 'g', 'mg', 
                  'lb', 'oz', 'ton', 'tonne'],
        'temperature': ['celsius', 'fahrenheit', 'kelvin', '°c', '°f', 'k'],
        'volume': ['liter', 'litre', 'milliliter', 'millilitre', 'gallon', 'quart', 
                  'pint', 'cup', 'l', 'ml', 'gal', 'qt', 'pt'],
        'time': ['second', 'minute', 'hour', 'day', 'week', 'month', 'year',
                'sec', 'min', 'hr', 'yr']
    }
    
    # Flatten the units list
    all_units = [unit for category in valid_units.values() for unit in category]
    
    # Convert text to lowercase and remove extra spaces
    text = ' '.join(text.lower().split())
    
    # Add spaces after numbers if missing
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    
    # Check for strict conversion patterns with more variations
    conversion_patterns = [
        # Standard patterns with spaces
        r'convert\s+(\d+(?:\.\d+)?)\s*([a-zA-Z°]+)\s+(?:to|into|in)\s+([a-zA-Z°]+)',
        r'how\s+many\s+([a-zA-Z°]+)\s+(?:are|is)\s+(?:in|there\s+in)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z°]+)',
        r'what\s+is\s+(\d+(?:\.\d+)?)\s*([a-zA-Z°]+)\s+(?:to|in|into)\s+([a-zA-Z°]+)',
        r'change\s+(\d+(?:\.\d+)?)\s*([a-zA-Z°]+)\s+(?:to|into|in)\s+([a-zA-Z°]+)',
        
        # Patterns without spaces between number and unit
        r'convert\s+(\d+(?:\.\d+)?)([a-zA-Z°]+)\s+(?:to|into|in)\s+([a-zA-Z°]+)',
        r'how\s+many\s+([a-zA-Z°]+)\s+(?:are|is)\s+(?:in|there\s+in)\s+(\d+(?:\.\d+)?)([a-zA-Z°]+)',
        r'what\s+is\s+(\d+(?:\.\d+)?)([a-zA-Z°]+)\s+(?:to|in|into)\s+([a-zA-Z°]+)',
        r'change\s+(\d+(?:\.\d+)?)([a-zA-Z°]+)\s+(?:to|into|in)\s+([a-zA-Z°]+)'
    ]
    
    for pattern in conversion_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            # Extract units (removing any numbers) and check if they're valid
            units = []
            for group in groups:
                if group:
                    # Remove numbers and clean the unit
                    clean_unit = re.sub(r'[\d\s.]', '', group.lower())
                    if any(valid_unit in clean_unit for valid_unit in all_units):
                        units.append(clean_unit)
            
            if len(units) >= 2:  # Must have at least two different units
                return True
    
    return False

def generate_conversion_response(prompt, temperature):
    """Generate a response for conversion questions based on temperature"""
    if temperature == 0:
        # Strict mode: Only exact conversion questions with minimal response
        if not is_conversion_question(prompt):
            return "Invalid format. Use:\n'Convert X units to units'"
        else:
            # Create a strict prompt for the model
            strict_prompt = (
                "Respond with ONLY the number and unit. "
                "No explanations, no additional text. "
                "Example format: '1000 grams' or '100 meters'. "
                "Question: " + prompt
            )
            response = st.session_state.chat_session.send_message(strict_prompt).text
            
            # Clean the response to ensure it's just numbers and units
            cleaned_response = re.sub(r'[^0-9\s.a-zA-Z°]', '', response)
            # Extract just the first number and unit
            match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z°]+)', cleaned_response)
            if match:
                return f"{match.group(1)} {match.group(2)}"
            return cleaned_response.strip()
    else:
        # Creative mode: Detailed responses with formulas and explanations
        if any(keyword in prompt.lower() for keyword in ['convert', 'how many', 'what is']):
            conversion_formulas = {
                ('kilo', 'gram'): {
                    'formula': '1 kilogram = 1000 grams',
                    'explanation': 'Multiply kilograms by 1000 to get grams'
                },
                ('meter', 'centimeter'): {
                    'formula': '1 meter = 100 centimeters',
                    'explanation': 'Multiply meters by 100 to get centimeters'
                },
                ('celsius', 'fahrenheit'): {
                    'formula': '°F = (°C × 9/5) + 32',
                    'explanation': 'First multiply by 9/5, then add 32'
                },
                ('mile', 'kilometer'): {
                    'formula': '1 mile ≈ 1.60934 kilometers',
                    'explanation': 'Multiply miles by 1.60934 to get kilometers'
                }
            }

            text = prompt.lower()
            for (unit1, unit2), info in conversion_formulas.items():
                if unit1 in text and unit2 in text:
                    response = (
                        f"🔢 **Formula:**\n{info['formula']}\n\n"
                        f"📝 **How to Convert:**\n{info['explanation']}\n\n"
                        f"🎯 **Your Result:**\n"
                     )
                    result = st.session_state.chat_session.send_message(prompt).text
                    return response + result

            # If no specific formula found, give a creative response
            return (
                "🔄 Let me help you with that conversion!\n\n" +
                st.session_state.chat_session.send_message(
                    prompt + "\nProvide a detailed explanation with the conversion."
                ).text
            )
        else:
            return "I only handle conversion questions! Try asking something like 'convert 5 kilometers to miles' 🔄"

# Add custom CSS
st.markdown("""
<style>
    .stChat {
        padding: 20px;
    }
    .stChatMessage {
       
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .stChatInput {
        position: fixed;
        bottom: 0;
        width: 100%;
        padding-bottom: 1000px;
        padding: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .chat-history-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-history-item:hover {
        background-color: #f0f0f0;
    }
    .delete-btn {
        color: red;
        cursor: pointer;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Add these functions at the top after imports
def save_chats_to_file():
    """Save all chat histories to file"""
    chat_data = {}
    for chat_id, chat_info in st.session_state.chat_histories.items():
        chat_data[chat_id] = {
            "name": chat_info["name"],
            "history": chat_info["history"]
        }
    
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_data, f)

def load_chats_from_file():
    """Load all chat histories from file"""
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Modify the session state initialization
if "chat_histories" not in st.session_state:
    # Load existing chats from file when starting
    st.session_state.chat_histories = load_chats_from_file()
    
if "current_chat_id" not in st.session_state:
    # Set current chat to the first available chat, or None if no chats exist
    chat_ids = list(st.session_state.chat_histories.keys())
    st.session_state.current_chat_id = chat_ids[0] if chat_ids else None
if "new_chat_created" not in st.session_state:
    st.session_state.new_chat_created = False

# Add sidebar for settings and chat history
with st.sidebar:
    st.title("⚙️ Settings")
    model_type = st.selectbox(
        "Select Model",
        ["gemini-1.5-flash", "gemini-2.0-flash"],
        index=1
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    st.markdown("""
    ### Temperature Guide:
    - **0.0**: Only responds to valid unit conversion questions
    - **1.0**: Responds to conversion questions with creative answers
    - Other questions will be ignored
    """)
    
    # New Chat Button
    if st.button("➕ New Chat"):
        new_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.chat_histories[new_chat_id] = {
            "name": "New Chat",
            "history": []
        }
        st.session_state.current_chat_id = new_chat_id
        st.session_state.new_chat_created = True
        save_chats_to_file()  # Save after creating new chat
        st.rerun()
    
    st.markdown("### Chat History")
    
    # Display chat history
    for chat_id, chat_data in st.session_state.chat_histories.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(chat_data["name"], key=f"select_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}"):
                del st.session_state.chat_histories[chat_id]
                save_chats_to_file()  # Save after deletion
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

# Update model configuration
model = gen_ai.GenerativeModel(model_type)
model.temperature = temperature

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

def save_chat_history(history, chat_id):
    """Save chat history to both session state and file"""
    if chat_id not in st.session_state.chat_histories:
        st.session_state.chat_histories[chat_id] = {
            "name": "New Chat",
            "history": []
        }
    
    chat_data = []
    for message in history:
        chat_data.append({
            "role": message.role,
            "text": message.parts[0].text
        })
    
    st.session_state.chat_histories[chat_id]["history"] = chat_data
    # Save to file after updating session state
    save_chats_to_file()

def load_chat_history(chat_id):
    """Load chat history for a specific chat"""
    if chat_id in st.session_state.chat_histories:
        chat_data = st.session_state.chat_histories[chat_id]["history"]
        history = []
        for message in chat_data:
            if message["role"] == "user":
                history.append({"role": "user", "parts": [message["text"]]})
            else:
                history.append({"role": "model", "parts": [message["text"]]})
        return history
    return []

# Initialize or load chat session
if "chat_session" not in st.session_state or st.session_state.current_chat_id is None:
    # Only create a new chat if there are no chats at all
    if not st.session_state.chat_histories and "chat_session" not in st.session_state:
        new_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.chat_histories[new_chat_id] = {
            "name": "New Chat",
            "history": []
        }
        st.session_state.current_chat_id = new_chat_id
        save_chats_to_file()  # Save the new chat immediately
    
    # If we have a current_chat_id, load its history
    if st.session_state.current_chat_id:
        saved_history = load_chat_history(st.session_state.current_chat_id)
        st.session_state.chat_session = model.start_chat(history=saved_history)
else:
    # This ensures chat session is reloaded when switching chats
    current_chat_id = st.session_state.current_chat_id
    saved_history = load_chat_history(current_chat_id)
    st.session_state.chat_session = model.start_chat(history=saved_history)

# Display the chatbot's title on the page
st.title("֎ unitXchange - Bot")

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask me anything...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Update chat title for new chats or if it's still "New Chat"
    if (st.session_state.new_chat_created or 
        st.session_state.chat_histories[st.session_state.current_chat_id]["name"] == "New Chat"):
        chat_title = get_chat_title(user_prompt)
        st.session_state.chat_histories[st.session_state.current_chat_id]["name"] = chat_title
        st.session_state.new_chat_created = False
        save_chats_to_file()  # Save the updated title immediately

    # Generate appropriate response based on temperature and question type
    response = generate_conversion_response(user_prompt, temperature)

    # Display the response
    with st.chat_message("assistant"):
        st.markdown(response)
        
    # Save updated chat history
    save_chat_history(st.session_state.chat_session.history, st.session_state.current_chat_id)