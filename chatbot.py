import streamlit as st
import boto3
import pandas as pd
from io import StringIO
from groq import Groq
import requests

# Initialize Groq client
client = Groq(api_key="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")
LOGGING_URL = "http://127.0.0.1:5000/log"
# Function to fetch CSV from S3 bucket
def fetch_csv_from_s3(bucket_name, file_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id="AKIA4LX5DJ3TX55YO3V7",  # Your access key
        aws_secret_access_key="KbMiPB/OC7RHPdnKf8ii6+IqFIHTj3XqgtQjBg/i",  # Your secret key
        region_name="us-east-1"  # Your region
    )
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_data = obj['Body'].read().decode('utf-8')
        return StringIO(csv_data)
    except Exception as e:
        st.error(f"Error fetching CSV file: {e}")
        return None

# Function to interact with the Llama model
def interact_with_llama(user_input, data_sample):
    # Format the prompt
    content = f"Look at the CSV data here: {data_sample}. Instruction: {user_input}. Please answer the question regarding the input by the user. Dont' include number of rows in the response ever."
    
    # Query the Llama model
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": content
        }],
        model="llama3-8b-8192",
    )
    
    # Extract the response from the model
    response = chat_completion.choices[0].message.content
    return response

# Streamlit app interface
def main():
    st.title("Streamlit Chatbot using Llama Model")
    st.write("Interact with the Llama model and analyze your data in real time!")

    # Upload CSV or fetch from S3
    st.sidebar.header("Data Input")
    data_option = st.sidebar.selectbox("Choose data source:", ["Upload CSV", "Fetch from S3"])

    # Use session state to store the dataset and sample data
    if "df" not in st.session_state:
        st.session_state.df = None
    if "data_sample" not in st.session_state:
        st.session_state.data_sample = None

    # Handle data upload or fetch
    if data_option == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.df.columns = st.session_state.df.columns.str.strip()  # Strip extra spaces
            st.session_state.data_sample = st.session_state.df.head(40).to_string()  # Use first 40 rows as sample
            st.sidebar.write("Sample Data:")
            st.sidebar.write(st.session_state.df.head(5))  # Show preview of data
    elif data_option == "Fetch from S3":
        bucket_name = st.sidebar.text_input("S3 Bucket Name", "space-datas")
        file_key = st.sidebar.text_input("S3 File Key", "cassini.csv")
        if st.sidebar.button("Fetch CSV"):
            file_data = fetch_csv_from_s3(bucket_name, file_key)
            if file_data:
                st.session_state.df = pd.read_csv(file_data)
                st.session_state.df.columns = st.session_state.df.columns.str.strip()  # Strip extra spaces
                st.session_state.data_sample = st.session_state.df.head(100).to_string()  # Use first 40 rows as sample
                st.sidebar.write("Sample Data:")
                st.sidebar.write(st.session_state.df.head(5))  # Show preview of data

    # Ensure dataset is loaded before allowing chatbot interaction
    if st.session_state.df is not None:
        st.header("Chat with Llama Model")
        user_input = st.text_input("Enter your question:")
        if st.button("Submit"):
            data = {"action": "SUMMARY GENERATED", "model": "LLAMA 2 USED"}
            res = requests.post(LOGGING_URL, json=data)
            if user_input:
                with st.spinner("Processing..."):
                    try:
                        # Interact with the Llama model
                        response = interact_with_llama(user_input, st.session_state.data_sample)
                        st.success("Response:")
                        st.write(response)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a question to proceed.")
    else:
        st.warning("Please upload or fetch a dataset first to enable chatbot interaction.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
