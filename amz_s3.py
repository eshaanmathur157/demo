import pandas as pd
import json
import plotly.express as px
import streamlit as st
import boto3
from io import StringIO
from groq import Groq
import requests
# Set up S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id="AKIA4LX5DJ3TX55YO3V7",  # Your access key
    aws_secret_access_key="KbMiPB/OC7RHPdnKf8ii6+IqFIHTj3XqgtQjBg/i",  # Your secret key
    region_name="us-east-1"  # Your region
)

bucket = 'space-datas'

# Directly set the API key here
client = Groq(api_key="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")

def generate_visualization_instruction(user_input, file):
    # Check if file is empty
    if file is None:
        st.error("The uploaded file is empty. Please upload a valid CSV file.")
        return None
    
    try:
        # Read the dataset
        df = pd.read_csv(file)
        if df.empty:
            st.error("The CSV file contains no data. Please upload a valid file.")
            return None
    except Exception as e:
        st.error(f"An error occurred while reading the CSV file: {e}")
        return None

    # Strip any leading/trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Show the column names to debug
    st.write(f"Columns in the uploaded CSV: {df.columns}")

    # Use the Llama model to generate instructions for the graph
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Generate a visualization based on the following CSV data: {df.head()}. Instruction: {user_input}. Please return the chart type, x column, and y column in a structured JSON format. The JSON should look like this: {{'chartType': 'chartType', 'xColumn': 'x-axis parameter from the instruction', 'yColumn': 'y-axis parameter from the instruction'}}. Dont say anything else please"
            }],
            model="llama3-8b-8192",
        )

        # Get the model's response
        response = chat_completion.choices[0].message.content
        st.write("Llama Model Response:", response)

        # Extract the JSON portion from the response (ignoring other text)
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        json_response = response[start_idx:end_idx]  # Extract only the JSON part
        response_data = json.loads(json_response)  # Parse the JSON response
        
        # Extract the fields with the correct capitalization
        chart_type = response_data.get("chartType", "scatter").lower().replace(" ", "")  # Default to scatter if not found
        x_col = response_data.get("xColumn", None)
        y_col = response_data.get("yColumn", None)

    except Exception as e:
        st.error(f"Error parsing Llama's response: {e}")
        return None

    # Print the chart type and columns chosen by the model
    st.write(f"Chart Type: {chart_type}")
    st.write(f"X Column: {x_col}")
    st.write(f"Y Column: {y_col}")
    
    # If chart type is valid, generate the plot
    if 'bubble' in chart_type:
        # Make sure the columns exist in the dataframe
        if x_col in df.columns and y_col in df.columns:
            # Filter out invalid or negative values for size
            valid_size_column = df[y_col].apply(lambda x: isinstance(x, (int, float)) and x >= 0)
            df_filtered = df[valid_size_column]
            
            # Plotting
            fig = px.scatter(df_filtered, x=x_col, y=y_col, size=df_filtered[y_col], title=f'Bubble plot between {x_col} and {y_col}')
            st.plotly_chart(fig)
        else:
            st.error(f"Columns '{x_col}' or '{y_col}' not found in the CSV data.")
    elif 'scatter' in chart_type:
        # Make sure the columns exist in the dataframe
        if x_col in df.columns and y_col in df.columns:
            fig = px.scatter(df, x=x_col, y=y_col, title=f'Scatter plot between {x_col} and {y_col}')
            st.plotly_chart(fig)
        else:
            st.error(f"Columns '{x_col}' or '{y_col}' not found in the CSV data.")
    elif 'line' in chart_type:
        if x_col in df.columns and y_col in df.columns:
            fig = px.line(df, x=x_col, y=y_col, title=f'Line plot between {x_col} and {y_col}')
            st.plotly_chart(fig)
    elif 'bar' in chart_type:
        if x_col in df.columns and y_col in df.columns:
            fig = px.bar(df, x=x_col, y=y_col, title=f'Bar chart between {x_col} and {y_col}')
            st.plotly_chart(fig)
    elif 'pie' in chart_type:
        if x_col in df.columns:
            fig = px.pie(df, names=x_col, title=f'Pie chart for {x_col}')
            st.plotly_chart(fig)
    elif 'histogram' in chart_type:
        if x_col in df.columns:
            fig = px.histogram(df, x=x_col, title=f'Histogram of {x_col}')
            st.plotly_chart(fig)
    elif 'box' in chart_type:
        if x_col in df.columns and y_col in df.columns:
            fig = px.box(df, x=x_col, y=y_col, title=f'Box plot between {x_col} and {y_col}')
            st.plotly_chart(fig)
    elif 'heatmap' in chart_type:
        if x_col in df.columns and y_col in df.columns:
            fig = px.density_heatmap(df, x=x_col, y=y_col, title=f'Heatmap between {x_col} and {y_col}')
            st.plotly_chart(fig)
    else:
        st.error(f"Unsupported chart type: {chart_type}")

# Streamlit UI
st.markdown(
    """
    <style>
    body {
        background: url('https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Ffree-photos-vectors%2Fspace&psig=AOvVaw1lJ-vgpzKl9gURs8W37yiE&ust=1734380933968000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCMj44M3OqooDFQAAAAAdAAAAABAJ') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Arial', sans-serif;
        color: white;
    }
    .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        padding: 20px;
        color: white;
    }
    .css-1d391kg h1 {
        font-size: 2em;
        text-align: center;
    }
    .stTextInput input {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    .stButton button {
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        border-radius: 5px;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add the new header text about supported datasets
st.markdown("""
    ### Datasets Supported:
    1. **Cassini**  
    The following fields are available for visualization:
    - Year
    - Time
    - Position
    - Serial
    - Radial Magnetic Field
    - Tangential Magnetic Field
    - Normal Magnetic Field
    - Average IMF Magnetic Field Magnitude

    2. **Pioneer7**  
    The following fields are available for visualization:
    - Heliocentric Distance (start of data interval)
    - Heliographic Inertial Latitude
    - HGI Longitude
    - IMF Radial Magnetic Field
    - IMF Tangential Magnetic Field
    - IMF Normal Magnetic Field
    - Magnetic Field Magnitude (average)
    - Proton Flow Speed
    - Proton Density
    3. **VOYAGER 2**
    Year: Year of recording
    - Day_of_Year: Day of the year (365 or 366 for leap years)
    - F1: Magnetic Field Magnitude (total magnetic field strength)
    - BR: Radial Component of the Magnetic Field (outward from the Sun)
    - BT: Tangential Component of the Magnetic Field (perpendicular to radial direction)
    - BN: Normal Component of the Magnetic Field (orthogonal to radial and tangential directions)
    - dF1: Rate of Change of Magnetic Field Magnitude (variability in total magnetic field)
    - dBR: Rate of Change of Radial Magnetic Field Component
    - dBT: Rate of Change of Tangential Magnetic Field Component
    - dBN: Rate of Change of Normal Magnetic Field Component
    """, unsafe_allow_html=True)

st.title('Dynamic Data Visualization from S3')
st.write("Enter the S3 file name and visualization instruction.")

file_name = st.text_input("Enter the source of data")
user_input = st.text_input("Enter your visualization instruction:")
LOGGING_URL = "http://127.0.0.1:5000/log"
if st.button("Generate Visualization"):
    data = {"action": "VISUALIZATION GENERATED", "model": "LLAMA 2 USED"}
    res = requests.post(LOGGING_URL, json=data)
    if file_name and user_input:
        # Retrieve the file from S3
        try:
            obj = s3.get_object(Bucket=bucket, Key=file_name + '.csv')
            data = obj['Body'].read().decode('utf-8')  # Read the file content
            
            # Create a file-like object
            file = StringIO(data)
            
            # Generate visualization
            generate_visualization_instruction(user_input, file)
        
        except Exception as e:
            st.error(f"Error retrieving the file from S3: {e}")
    else:
        st.warning("Please enter the file name and instruction.")

# Real-time space weather monitor button
if st.button("REAL TIME SPACE WEATHER MONITOR"):
    st.markdown("""
        <style>
        .real-time-button {
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 5px;
            padding: 12px;
            font-size: 16px;
            text-align: center;
        }
        .real-time-button:hover {
            background-color: rgba(0, 0, 0, 1);
        }
        </style>
        <a href="http://172.16.25.177:8052/" target="_blank">
            <button class="real-time-button">Go to Real-Time Space Weather Monitor</button>
        </a>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .chatbot-button {
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        border-radius: 5px;
        padding: 12px;
        font-size: 16px;
        text-align: center;
        display: block;
        margin: 20px auto;
        text-decoration: none;
    }
    .chatbot-button:hover {
        background-color: rgba(0, 0, 0, 1);
    }
    </style>
    <a href="http://172.16.25.177:9000" target="_blank" class="chatbot-button">HAVE MORE QUESTIONS ON THE STATIC DATA? USE THE CHATBOT</a>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .chatbot-button {
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        border-radius: 5px;
        padding: 12px;
        font-size: 16px;
        text-align: center;
        display: block;
        margin: 20px auto;
        text-decoration: none;
    }
    .chatbot-button:hover {
        background-color: rgba(0, 0, 0, 1);
    }
    </style>
    <a href="http://172.16.25.177:9001" target="_blank" class="chatbot-button">CLICK HERE FOR GETTING INFO ON SPACE EVENTS</a>
""", unsafe_allow_html=True)

