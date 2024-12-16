import streamlit as st
import requests
import pandas as pd
from io import StringIO  # Correct import for StringIO

# Set the API base URL
BASE_URL = "https://api.astrocats.space"

# Function to fetch data from the API
def fetch_data(endpoint, params=None, format='json'):
    url = f"{BASE_URL}/{endpoint}"
    if format != 'json':
        params = params or {}
        params['format'] = format
    
    try:
        # Bypass SSL certificate verification
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        
        if format == 'csv':
            # Use StringIO from io module to read CSV data
            return pd.read_csv(StringIO(response.text))
        elif format == 'tsv':
            return pd.read_csv(StringIO(response.text), sep='\t')
        else:
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# Streamlit UI
def app():
    st.title('Open Astronomy Catalog API Interface')

    # Query Selection
    query_type = st.selectbox("Select the query type", ["Catalog", "Object Info", "Photometry", "Spectra"])

    if query_type == "Catalog":
        object_name = st.text_input("Enter Object Name")
        quantity = st.text_input("Enter Quantity (e.g., redshift, photometry, etc.)")
        attribute = st.text_input("Enter Attribute (e.g., magnitude, time, etc.)")
        argument = st.text_input("Enter Argument (optional, e.g., ra=10:42:16.88&dec=-24:13:12.13)")

        if st.button("Search"):
            endpoint = f"catalog/{object_name}/{quantity}/{attribute}"
            params = {arg.split('=')[0]: arg.split('=')[1] for arg in argument.split('&')} if argument else {}
            data = fetch_data(endpoint, params)

            if data:
                st.write(data)

    elif query_type == "Object Info":
        object_name = st.text_input("Enter Object Name")

        if st.button("Get Object Info"):
            data = fetch_data(f"{object_name}/redshift")
            if data:
                # Extract the redshift data and format it neatly
                if object_name in data:
                    redshift_data = data[object_name]["redshift"]
                    # Create a DataFrame for neat display
                    redshift_df = pd.DataFrame(redshift_data)
                    st.write(f"Redshift values for {object_name}:")
                    st.write(redshift_df)
                else:
                    st.write("No redshift data found for this object.")

    elif query_type == "Photometry":
        object_name = st.text_input("Enter Object Name")
        attribute = st.text_input("Enter Attribute (e.g., magnitude, e_magnitude, band)")

        if st.button("Get Photometry Data"):
            data = fetch_data(f"{object_name}/photometry/{attribute}")
            if data:
                st.write(data)

    elif query_type == "Spectra":
        object_name = st.text_input("Enter Object Name")

        if st.button("Get Spectra Data"):
            data = fetch_data(f"{object_name}/spectra/time+data")
            if data:
                st.write(data)

    # Query Examples Section
    st.header("Example Queries")

    # Example of querying the API
    st.subheader("ALL SUPERNOVA RELATED EVENTS")
    if st.button("Run"):
        data = fetch_data("catalog/sne", format='csv')
        st.write(data)

    st.subheader("2. Redshifts of Objects within 5° Radius of Given Coordinates")
    if st.button("Run Example 2"):
        params = {"ra": "10:42:16.88", "dec": "-24:13:12.13", "radius": "18000", "format": "csv", "redshift": ""}
        data = fetch_data("catalog/sne/redshift", params=params, format='csv')
        st.write(data)

if __name__ == "__main__":
    app()
