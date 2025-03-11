import streamlit as st
import io
import re
import pdfplumber
from docx import Document
from collections import Counter

def extract_text_from_pdf(file):
    """Extracts text from a PDF file."""
    try:
        with pdfplumber.open(file) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file):
    """Extracts text from a DOCX file."""
    try:
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def preprocess_text(text):
    """Preprocesses text for analysis."""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    return text

def analyze_resume(file, job_description):
    """Analyzes a resume against a job description."""

    file_type = file.type
    if "pdf" in file_type:
        resume_text = extract_text_from_pdf(file)
    elif "docx" in file_type:
        resume_text = extract_text_from_docx(file)
    else:
        st.error("Unsupported file type. Please upload a PDF or DOCX file.")
        return

    if not resume_text:
        return

    resume_text = preprocess_text(resume_text)
    job_description = preprocess_text(job_description)

    resume_words = resume_text.split()
    job_words = job_description.split()

    resume_word_counts = Counter(resume_words)
    job_word_counts = Counter(job_words)

    matched_words = set(resume_words) & set(job_words)
    matched_word_counts = {word: resume_word_counts[word] for word in matched_words}

    total_job_words = len(job_words)
    total_resume_words = len(resume_words)

    if total_job_words > 0:
        match_percentage = (len(matched_words) / total_job_words) * 100
    else:
        match_percentage = 0.0

    return matched_words, matched_word_counts, match_percentage

def main():
    st.title("Resume ATS Scanner")

    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    job_description = st.text_area("Enter the job description")

    if uploaded_file and job_description:
        if st.button("Analyze Resume"):
            results = analyze_resume(uploaded_file, job_description)

            if results:
                matched_words, matched_word_counts, match_percentage = results

                st.subheader("Analysis Results:")
                st.write(f"Match Percentage: {match_percentage:.2f}%")

                if matched_words:
                    st.write("Matched Words:")
                    for word, count in matched_word_counts.items():
                        st.write(f"- {word}: {count} times")
                else:
                    st.write("No matching keywords found.")
            else:
                st.write("An error occured during analysis.")

if __name__ == "__main__":
    main()