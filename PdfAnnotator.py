import os
import re
import requests
import PyPDF2
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Set your Hugging Face API Key
ACCESS_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxx"


# Define annotation labels
ANNOTATION_LABELS = [
    "Deep Learning",
    "Computer Vision",
    "Reinforcement Learning",
    "Natural Language Processing",
    "Optimization"
]

# Hugging Face API URL and headers
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


def extract_title_abstract(pdf_path):
    title, abstract = "Title not found", "Abstract not found"
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            page = reader.pages[0]
            text = page.extract_text() or ""
            if text:
                lines = text.split("\n")
                for line in lines:
                    if line.strip():
                        title = line.strip()
                        break
                # Attempt to locate "abstract" in the text
                abstract_index = text.lower().find("abstract")
                if abstract_index != -1:
                    abstract_text = text[abstract_index:].strip()
                    abstract_text = re.sub(r'abstract[:\s]*', '', abstract_text, flags=re.IGNORECASE)
                    abstract = abstract_text[:500]  # Limit abstract size to 500 chars
    except Exception as e:
        print(f"Error extracting PDF text from {pdf_path}: {e}")
    return title, abstract


def classify_paper(title, abstract, labels):
    text = f"Title: {title}\n\nAbstract: {abstract}"
    payload = {"inputs": text, "parameters": {"candidate_labels": labels}}

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        if "labels" in result:
            return result["labels"][0]  # Return highest-confidence category
    except requests.exceptions.RequestException as e:
        print(f"Error classifying paper: {e}")
    return "Unclassified"

def process_pdfs_in_folder(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the selected folder.")
        return

    # Hardcoded output directory path
    output_folder = r"C:\Users\Kashish\Desktop\NeurIPS_PythonScrapper"
    csv_file = os.path.join(output_folder, "annotated_papers.csv")

    # Check if file already exists to handle headers
    file_exists = os.path.isfile(csv_file)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        print(f"\nProcessing: {pdf_file}")

        # Extract title and abstract
        title, abstract = extract_title_abstract(pdf_path)
        print(f"Extracted Title: {title}")
        print(f"Extracted Abstract: {abstract}")

        # Classify the paper
        annotation = classify_paper(title, abstract, ANNOTATION_LABELS)
        print(f"Annotation Label: {annotation}")

        # Create a DataFrame for a single PDF
        df = pd.DataFrame(
            [[pdf_file, title, abstract, annotation]],
            columns=["PDF File", "Title", "Abstract", "Annotation"]
        )

        # Append data to CSV immediately (mode="a")
        df.to_csv(
            csv_file, mode="a", index=False, header=not file_exists
        )
        file_exists = True  # Ensures headers won't be written again
        print(f"Data saved for {pdf_file}")

    print(f"\nAll processed PDFs have been annotated. Results saved to: {csv_file}")

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root Tkinter window
    # Ask user to select a folder
    folder_path = filedialog.askdirectory(title="Select a folder containing PDFs")
    if not folder_path:
        print("No folder selected. Exiting...")
        return

    print(f"\nProcessing PDFs in folder: {folder_path}")
    process_pdfs_in_folder(folder_path)

if __name__ == "__main__":
    main()
