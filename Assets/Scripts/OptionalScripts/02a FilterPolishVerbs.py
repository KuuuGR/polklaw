import spacy

# Load the Polish language model
nlp = spacy.load("pl_core_news_sm")

# Paths to input and output files
input_file = "data/input/dialectic_words.txt"
output_file = "data/output/filtered_verbs.txt"

# List to store filtered and corrected words
filtered_corrected_words = []

# Control variable: whether to change to the base form (lemma)
use_base_form = True  # Set to False to keep the original form from the input file

def check_if_verb_spacy(word, use_base_form):
    # Analyze the word using spaCy
    doc = nlp(word)
    for token in doc:
        if token.pos_ == "VERB":
            if use_base_form:
                print(f"Verb: {word}, base form: {token.lemma_}")
                return token.lemma_  # Return the base form (e.g., "czytać")
            else:
                print(f"Verb: {word}, keeping the original form")
                return word  # Return the original form (e.g., "czytałem")
    return None  # Return None if the word is not a verb

# Read the input file and process each word
with open(input_file, "r", encoding="utf-8") as file:
    words = file.readlines()

# Check each word
for word in words:
    word = word.strip().lower()  # Remove whitespace and convert to lowercase
    verb_form = check_if_verb_spacy(word, use_base_form)
    if verb_form:
        filtered_corrected_words.append(verb_form)  # Add only verbs in the correct form

# Remove duplicates, ignoring case
unique_words = {}
for word in filtered_corrected_words:
    lower_word = word.lower()
    # Keep only unique forms, preferring capitalized forms if they exist
    if lower_word not in unique_words or word[0].isupper():
        unique_words[lower_word] = word

# Write the unique words to the output file
with open(output_file, "w", encoding="utf-8") as file:
    for word in sorted(unique_words.values()):  # Remove duplicates and sort alphabetically
        file.write(word + "\n")

print(f"Filtered and corrected file saved as: {output_file}")
print(f"Total number of processed verbs: {len(filtered_corrected_words)}")
