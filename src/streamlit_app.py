import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(page_title="Ask AI About Your Data", page_icon="🤖")

# Constants from environment
FASTAPI_URL = os.getenv("API_BASE_URL", "http://localhost:5599")


def main():
    # Header
    st.title("🤖 Ask AI About Your Data")
    st.write(
        "Upload your CSV file and ask questions in natural language to get AI-powered insights!")

    # Check backend status
    if not check_backend_status():
        st.error(
            "❌ Backend is not accessible. Make sure FastAPI server is running on localhost:8000")
        return
    else:
        st.success("✅ Backend is running!")

    # File upload
    st.subheader("📁 Upload Your CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    # Display file preview if uploaded
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(
                f"✅ File uploaded successfully! ({df.shape[0]} rows, {df.shape[1]} columns)")
            st.subheader("📊 Data Preview")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

    # Question input
    st.subheader("🤔 Ask Your Question")
    question = st.text_area(
        "What would you like to know about your data?",
        placeholder="e.g., What is the average sales amount?",
        height=100
    )

    # Submit button
    if st.button("🚀 Ask AI", type="primary"):
        if uploaded_file is None:
            st.error("❌ Please upload a CSV file first!")
        elif not question.strip():
            st.error("❌ Please enter a question!")
        else:
            with st.spinner("🤖 AI is analyzing your data..."):
                result = send_request_to_backend(uploaded_file, question)

                if result:
                    display_results(result)
                else:
                    st.error("❌ Failed to get response from backend.")


def check_backend_status():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get(f"{FASTAPI_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False


def send_request_to_backend(uploaded_file, question):
    """Send request to FastAPI backend"""
    try:
        # Step 1: Upload the file first
        uploaded_file.seek(0)
        files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}

        upload_response = requests.post(
            f"{FASTAPI_URL}/upload",
            files=files,
            timeout=30
        )

        if upload_response.status_code != 200:
            st.error(
                f"Upload failed: {upload_response.status_code} - {upload_response.text}")
            return None

        upload_result = upload_response.json()
        file_id = upload_result["file_id"]

        # Step 2: Ask the question with the file_id
        question_response = requests.post(
            f"{FASTAPI_URL}/answer",
            json={
                "file_id": file_id,
                "question": question
            },
            timeout=300
        )

        if question_response.status_code == 200:
            return question_response.json()
        else:
            st.error(
                f"Backend error: {question_response.status_code} - {question_response.text}")
            return None

    except requests.exceptions.ConnectionError:
        st.error(
            f"❌ Cannot connect to backend. Make sure FastAPI server is running on {FASTAPI_URL}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timeout. The analysis is taking too long.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def display_results(result):
    """Display the results from the backend"""
    st.subheader("🎯 AI Analysis Results")

    # Main answer
    st.write("**Answer:**")
    st.info(result.get("answer", "No answer provided"))


if __name__ == "__main__":
    main()
