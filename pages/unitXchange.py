import streamlit as st
import streamlit.components.v1 as components
import requests

# Initialize session state for history and clear button if not already done
if 'history' not in st.session_state:
    st.session_state.history = []
if 'clear_clicked' not in st.session_state:
    st.session_state.clear_clicked = False

def clear_history_callback():
    st.session_state.clear_clicked = True

# Cache the currency API response for 10 minutes
@st.cache_data(ttl=600)
def fetch_currency_rates():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        return response.json().get("rates", {})
    except Exception as e:
        st.error("Error fetching currency rates")
        return {}

# Conversion functions
def distance_converter(from_unit, to_unit, value):
    units = {
        "Meters": 1,
        "Kilometers": 1000,
        "Feet": 0.3048,
        "Miles": 1609.34,
        "Yards": 0.9144,
        "Inches": 0.0254
    }
    return value * units[from_unit] / units[to_unit]

def temperature_converter(from_unit, to_unit, value):
    if from_unit == "Celsius" and to_unit == "Fahrenheit":
        return (value * 9/5) + 32
    elif from_unit == "Fahrenheit" and to_unit == "Celsius":
        return (value - 32) * 5/9
    return value

def weight_converter(from_unit, to_unit, value):
    units = {
        "Kilograms": 1,
        "Grams": 0.001,
        "Pounds": 0.453592,
        "Ounces": 0.0283495,
        "Stones": 6.35029
    }
    return value * units[from_unit] / units[to_unit]

def pressure_converter(from_unit, to_unit, value):
    units = {
        "Pascals": 1,
        "Hectopascals": 100,
        "Kilopascals": 1000,
        "Bar": 100000,
        "Atmospheres": 101325
    }
    return value * units[from_unit] / units[to_unit]

def currency_converter(from_unit, to_unit, value, rates):
    return value * rates[to_unit] / rates[from_unit]

def time_converter(from_unit, to_unit, value):
    units = {
        "Seconds": 1,
        "Minutes": 60,
        "Hours": 3600,
        "Days": 86400,
        "Weeks": 604800,
        "Months": 2628000
    }
    return value * units[from_unit] / units[to_unit]

def volume_converter(from_unit, to_unit, value):
    units = {
        "Liters": 1,
        "Milliliters": 0.001,
        "Gallons": 3.78541,
        "Cups": 0.236588,
        "Cubic Meters": 1000
    }
    return value * units[from_unit] / units[to_unit]

def area_converter(from_unit, to_unit, value):
    units = {
        "Square Meters": 1,
        "Square Kilometers": 1e6,
        "Acres": 4046.86,
        "Hectares": 10000
    }
    return value * units[from_unit] / units[to_unit]

def speed_converter(from_unit, to_unit, value):
    units = {
        "Meters per second": 1,
        "Kilometers per hour": 0.277778,
        "Miles per hour": 0.44704,
        "Knots": 0.514444
    }
    return value * units[from_unit] / units[to_unit]

def data_converter(from_unit, to_unit, value):
    units = {
        "Bytes": 1,
        "Kilobytes": 1024,
        "Megabytes": 1024**2,
        "Gigabytes": 1024**3,
        "Terabytes": 1024**4
    }
    return value * units[from_unit] / units[to_unit]

# Fetch real-time currency rates
currency_rates = fetch_currency_rates()

# Enhanced CSS styling
st.markdown(
    """
    <style>
    /* Global background & font */
    .stApp {
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Title styling */
    .title {
        text-align: center;
        font-size: 48px;
        color:green;
        font-weight: 800;
        background: linear-gradient(120deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 30px 0;
        padding: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        font-size: 32px;
        font-weight: 600;
        color: #1a73e8;
        margin: 25px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Converter card container */
    .converter-container {
        background: green;
        padding: 1px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 30px auto;
        max-width: 900px;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Input fields styling */
    .stSelectbox {
       color:green;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stNumberInput {
       color:green;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* History container styling */
    .history {
        background: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 15px;
        margin-top: 30px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .history-item {
        padding: 12px;
        margin: 8px 0;
        background: rgba(240, 242, 246, 0.5);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        transform: translateX(5px);
        background: rgba(240, 242, 246, 0.8);
    }
    
    /* Button styling */
    .stButton>button {
        
       
        padding: 12px 30px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(76, 175, 80, 0.3);
    }
    
    /* Category icons */
    .category-icon {
        font-size: 24px;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    /* Success message styling */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid #4CAF50;
        border-radius: 10px;
        padding: 16px;
        color: #2e7d32;
    }
    
    /* Formula display styling */
    .formula {
        background: rgba(33, 150, 243, 0.1);
        padding: 1px;
        border-radius: 10px;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
        border-left: 4px solid #2196F3;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .title {
            font-size: 36px;
        }
        .subtitle {
            font-size: 24px;
        }
        .converter-container {
            padding: 20px;
            margin: 15px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Title with animation
st.markdown("""
    <div class='title'>
        🔄 UnitXchange  
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>
        Your all-in-one solution for quick and accurate unit conversions
    </p>
""", unsafe_allow_html=True)

# Wrap the conversion UI in a container card
st.markdown("<div class='converter-container'>", unsafe_allow_html=True)

# Category selection with icons
category_icons = {
    "Distance": "📏",
    "Temperature": "🌡️",
    "Weight": "⚖️",
    "Pressure": "🎯",
    "Currency": "💱",
    "Time": "⏰",
    "Volume": "🧪",
    "Area": "📐",
    "Speed": "🚀",
    "Data": "💾"
}

# Updated list of categories
categories = ["Distance", "Temperature", "Weight", "Pressure", "Currency", "Time", "Volume", "Area", "Speed", "Data"]
category = st.selectbox(
    "Select Category",
    categories,
    format_func=lambda x: f"{category_icons[x]} {x}"
)

# Unit options for each category
unit_options = {
    "Distance": ["Meters", "Kilometers", "Feet", "Miles", "Yards", "Inches"],
    "Temperature": ["Celsius", "Fahrenheit"],
    "Weight": ["Kilograms", "Grams", "Pounds", "Ounces", "Stones"],
    "Pressure": ["Pascals", "Hectopascals", "Kilopascals", "Bar", "Atmospheres"],
    "Currency": ["USD", "EUR", "INR", "JPY", "GBP", "AUD", "PKR"],
    "Time": ["Seconds", "Minutes", "Hours", "Days", "Weeks", "Months"],
    "Volume": ["Liters", "Milliliters", "Gallons", "Cups", "Cubic Meters"],
    "Area": ["Square Meters", "Square Kilometers", "Acres", "Hectares"],
    "Speed": ["Meters per second", "Kilometers per hour", "Miles per hour", "Knots"],
    "Data": ["Bytes", "Kilobytes", "Megabytes", "Gigabytes", "Terabytes"]
}

from_unit = st.selectbox("From", unit_options[category])
to_unit = st.selectbox("To", unit_options[category])
value = st.number_input("Enter Value", min_value=0.0, format="%.2f")

# Center the convert button
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
convert_button = st.button("Convert")
st.markdown("</div>", unsafe_allow_html=True)

if convert_button:
    if category == "Distance":
        result = distance_converter(from_unit, to_unit, value)
        factor = distance_converter(from_unit, to_unit, 1)
        st.write(f"📏 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Temperature":
        result = temperature_converter(from_unit, to_unit, value)
        if from_unit == "Celsius" and to_unit == "Fahrenheit":
            formula = f"({value}°C × 9/5) + 32 = {result:.2f}°F"
        elif from_unit == "Fahrenheit" and to_unit == "Celsius":
            formula = f"({value}°F - 32) × 5/9 = {result:.2f}°C"
        else:
            formula = f"{value}°{from_unit} = {result:.2f}°{to_unit}"
        st.write(f"🌡️ Formula: {formula}")
    elif category == "Weight":
        result = weight_converter(from_unit, to_unit, value)
        factor = weight_converter(from_unit, to_unit, 1)
        st.write(f"⚖️ Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Pressure":
        result = pressure_converter(from_unit, to_unit, value)
        factor = pressure_converter(from_unit, to_unit, 1)
        st.write(f"🎯 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Currency":
        result = currency_converter(from_unit, to_unit, value, currency_rates)
        factor = currency_converter(from_unit, to_unit, 1, currency_rates)
        st.write(f"💱 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
        st.write("Note: Currency rates are fetched in real-time")
    elif category == "Time":
        result = time_converter(from_unit, to_unit, value)
        factor = time_converter(from_unit, to_unit, 1)
        st.write(f"⏰ Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Volume":
        result = volume_converter(from_unit, to_unit, value)
        factor = volume_converter(from_unit, to_unit, 1)
        st.write(f"🧪 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Area":
        result = area_converter(from_unit, to_unit, value)
        factor = area_converter(from_unit, to_unit, 1)
        st.write(f"📐 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Speed":
        result = speed_converter(from_unit, to_unit, value)
        factor = speed_converter(from_unit, to_unit, 1)
        st.write(f"🚀 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    elif category == "Data":
        result = data_converter(from_unit, to_unit, value)
        factor = data_converter(from_unit, to_unit, 1)
        st.write(f"💾 Formula: {value} {from_unit} × {factor:.4f} = {result:.2f} {to_unit}")
    
    # Enhanced result display
    st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: rgba(76, 175, 80, 0.1); border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);'>
            <span style='font-size: 24px; color: #2e7d32; font-weight: 500;'>
                {value} {from_unit} = {result:.2f} {to_unit}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    st.session_state.history.append(f"{value} {from_unit} → {result:.2f} {to_unit}")

st.markdown("</div>", unsafe_allow_html=True)  # End of converter container

# Enhanced History Display - FIXED VERSION
st.markdown("""
    <div style='margin-top: 30px;'>
        <h2 style='color: #1a73e8; font-size: 28px; margin-bottom: 20px;'>
            🕒 Recent Conversions
        </h2>
    </div>
""", unsafe_allow_html=True)

# Check if clear was clicked and clear the history
if st.session_state.clear_clicked:
    st.session_state.history = []
    st.session_state.clear_clicked = False
    st.success("Conversion history cleared!")
    st.rerun()

# Display history and buttons - FIXED to eliminate white space
if st.session_state.history:
    # Container for history items
    history_container = st.container()
    with history_container:
        st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.9); 
                        padding: 2px; 
                        border-radius: 15px; 
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); 
                        border: 1px solid rgba(255, 255, 255, 0.18);
                        margin-bottom: 20px;'>
        """, unsafe_allow_html=True)
        
        for item in st.session_state.history[::-1][:10]:
            st.markdown(f"""
                <div style='padding: 12px;
                            margin: 8px 0;
                            background: rgba(240, 242, 246, 0.5);
                            border-radius: 8px;
                            transition: all 0.3s ease;
                            border: 1px solid rgba(0, 0, 0, 0.05);'>
                    ➜ {item}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Buttons for history actions
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗑️ Clear History", on_click=clear_history_callback)
    with col2:
        if category == "Currency" and st.button("🔄 Refresh Rates"):
            currency_rates = fetch_currency_rates()
            st.success("Currency rates updated!")
else:
    # No empty space between heading and info message
    st.markdown("""
        <div style='background: rgba(240, 248, 255, 0.9); 
                    padding: 20px; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); 
                    border: 1px solid rgba(230, 240, 250, 0.8);
                    margin-top: 10px;
                    margin-bottom: 10px;'>
            <p style='text-align: center; color: #1a73e8; font-size: 24px;'>
                No conversions yet. Start converting to build your history!
            </p>
        </div>
    """, unsafe_allow_html=True)

