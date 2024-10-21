import os
import re
from PyPDF2 import PdfReader
from docx import Document
import chardet

# Define the input directory for source files
input_directory = "data/input/"

# Define the output directory and file path for the result
output_directory = "data/output/"
output_file = os.path.join(output_directory, "polish_words.txt")

# Define Polish diacritical characters
polish_chars = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"

# Regular expression to find words containing any Polish character but no digits
polish_pattern = re.compile(rf"\b\w*[{'|'.join(polish_chars)}]\w*\b")

# Set to store unique words
unique_words = set()

# Function to extract text from PDF files
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""

# Function to extract text from DOCX files
def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except:
        return ""

# Function to extract text from TXT files with automatic encoding detection
def extract_text_from_txt(file_path):
    try:
        with open(file_path, "rb") as file:  # Open file in binary mode
            raw_data = file.read()
            result = chardet.detect(raw_data)  # Detect encoding
            encoding = result['encoding']  # Get the detected encoding

        # Open the file with the detected encoding
        with open(file_path, "r", encoding=encoding) as file:
            text = file.read()
        return text
    except:
        return ""

# Function to process files in the input directory
def process_files(input_directory):
    for root, dirs, files in os.walk(input_directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            text = ""

            if file_name.endswith(".txt"):
                text = extract_text_from_txt(file_path)
            elif file_name.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            elif file_name.endswith(".docx"):
                text = extract_text_from_docx(file_path)
            else:
                continue

            # Find words containing any Polish character
            found_words = polish_pattern.findall(text)
            for word in found_words:
                # Convert letters to lowercase
                word = word.lower()
                # Remove digits from words
                cleaned_word = re.sub(r'\d+', '', word)
                # Add the word to the set if it is not empty and contains no digits
                if cleaned_word:
                    unique_words.add(cleaned_word)

# Call the function to process files
process_files(input_directory)

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Write the unique words to the output file, sorted alphabetically
with open(output_file, "w", encoding="utf-8") as file:
    for word in sorted(unique_words):
        file.write(word + "\n")

print(f"Found words saved to: {output_file}")
