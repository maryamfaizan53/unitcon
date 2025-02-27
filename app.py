import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ✅ Set Page Configuration (Should be the first command)
st.set_page_config(page_title="AI-Powered Unit Converter", page_icon="🔄", layout="centered")

# ✅ Load API Key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()  # Stop the app if API key is missing
else:
    genai.configure(api_key=api_key)

# ✅ Apply Basic Custom CSS for Styling
st.markdown(
    """
    <style>
        body { font-family: Arial, sans-serif; }
        .stApp { background-color: #f5f5f5; }
        .title { color: #6A0DAD; text-align: center; font-size: 32px; font-weight: bold; }
        .stButton>button { background-color: #6A0DAD; color: white; font-size: 16px; padding: 8px; }
        .stNumberInput>div>div>input { background-color: white; color: black; }
        .stSelectbox>div>div>div { color: black; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ App Title with Styling
st.markdown("<h1 class='title'>🔄 AI-Powered Unit Converter</h1>", unsafe_allow_html=True)

# ✅ Sidebar for Inputs
st.sidebar.header("Conversion Settings")

# Define unit types and their respective units
unit_type = st.sidebar.selectbox("Select Unit Type", ["Length", "Weight", "Temperature", "Speed", "Time", "Area", "Volume"])
input_value = st.sidebar.number_input("Enter Value", min_value=0.0, format="%.2f")

conversion_units = {
    "Length": ["Meters", "Kilometers", "Miles", "Feet", "Inches", "Yards", "Centimeters", "Millimeters"],
    "Weight": ["Kilograms", "Grams", "Pounds", "Ounces", "Tonnes"],
    "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
    "Speed": ["Meters per second", "Kilometers per hour", "Miles per hour"],
    "Time": ["Seconds", "Minutes", "Hours", "Days", "Weeks"],
    "Area": ["Square meters", "Square kilometers", "Square feet", "Acres", "Hectares", "Square miles"],
    "Volume": ["Liters", "Milliliters", "Gallons", "Cubic meters"]
}

# Update unit selection based on the selected unit type
if unit_type:
    from_unit = st.sidebar.selectbox("From", conversion_units[unit_type])
    to_unit = st.sidebar.selectbox("To", conversion_units[unit_type])
else:
    st.warning("Please select a unit type first.")

# ✅ Manual Conversion Function
def manual_conversion(value, from_unit, to_unit):
    conversion_factors = {
        "Meters_Kilometers": 0.001,
        "Kilometers_Meters": 1000,
        "Miles_Kilometers": 1.60934,
        "Kilometers_Miles": 1 / 1.60934,
        "Feet_Meters": 0.3048,
        "Meters_Feet": 1 / 0.3048,
        "Inches_Feet": 1 / 12,
        "Feet_Inches": 12,
        "Yards_Meters": 0.9144,
        "Meters_Yards": 1 / 0.9144,
        "Kilograms_Grams": 1000,
        "Grams_Kilograms": 1 / 1000,
        "Kilograms_Pounds": 2.20462,
        "Pounds_Kilograms": 1 / 2.20462,
        "Ounces_Grams": 28.3495,
        "Grams_Ounces": 1 / 28.3495,
        "Celsius_Fahrenheit": lambda x: (x * 9/5) + 32,
        "Fahrenheit_Celsius": lambda x: (x - 32) * 5/9,
        "Celsius_Kelvin": lambda x: x + 273.15,
        "Kelvin_Celsius": lambda x: x - 273.15,
        "Meters per second_Kilometers per hour": 3.6,
        "Kilometers per hour_Meters per second": 1 / 3.6,
        "Miles per hour_Kilometers per hour": 1.60934,
        "Kilometers per hour_Miles per hour": 1 / 1.60934,
        "Seconds_Minutes": 1 / 60,
        "Minutes_Seconds": 60,
        "Minutes_Hours": 1 / 60,
        "Hours_Minutes": 60,
        "Hours_Days": 1 / 24,
        "Days_Hours": 24,
        "Weeks_Days": 7,
        "Days_Weeks": 1 / 7,
        "Square meters_Square kilometers": 1 / 1e6,
        "Square kilometers_Square meters": 1e6,
        "Square feet_Square meters": 0.092903,
        "Square meters_Square feet": 1 / 0.092903,
        "Acres_Square meters": 4046.86,
        "Square meters_Acres": 1 / 4046.86,
        "Hectares_Square meters": 10000,
        "Square meters_Hectares": 1 / 10000,
        "Square miles_Square kilometers": 2.58999,
        "Square kilometers_Square miles": 1 / 2.58999,
        "Liters_Milliliters": 1000,
        "Milliliters_Liters": 1 / 1000,
        "Liters_Gallons": 0.264172,
        "Gallons_Liters": 1 / 0.264172,
        "Liters_Cubic meters": 0.001,
        "Cubic meters_Liters": 1000
    }

    key = f"{from_unit}_{to_unit}"
    if key in conversion_factors:
        factor = conversion_factors[key]
        return factor(value) if callable(factor) else value * factor
    return None

# ✅ Gemini AI Integration for Advanced Conversions
def gemini_conversion(value, from_unit, to_unit):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Convert {value} {from_unit} to {to_unit}. Provide only the numerical result."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini AI Error: {e}")
        return None

# ✅ Convert Button
if st.button("🔄 Convert", help="Click to convert the units"):
    if from_unit != to_unit:
        manual_result = manual_conversion(input_value, from_unit, to_unit)
        if manual_result is not None:
            st.success(f"Manual Conversion: {manual_result:.2f} {to_unit}")
        else:
            st.warning("Manual conversion not available. Using Gemini AI...")
            gemini_result = gemini_conversion(input_value, from_unit, to_unit)
            if gemini_result:
                st.success(f"Gemini AI Conversion: {gemini_result} {to_unit}")
            else:
                st.error("Conversion failed. Please try again.")
    else:
        st.warning("Please select different units.")

# ✅ Footer
author = "Maryam Faizan"
version = "1.0"
st.markdown(f"---\n✨ Made by {author} ❤️ using Streamlit & Google Gemini AI (v{version})")
