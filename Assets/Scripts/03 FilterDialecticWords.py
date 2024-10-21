import re

# Paths to input and output files
input_file = "data/input/filtered_and_corrected_words.txt"
output_file = "data/output/dialectic_words.txt"

# Definition of Polish diacritical characters
polish_chars = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"

# Minimum word length to keep (adjust this value as needed)
min_word_length = 3

# Regular expression to find words containing any Polish diacritical character
polish_pattern = re.compile(rf"[{polish_chars}]")

# Dictionary to store unique words while preserving original capitalization
unique_words = {}

# Read the input file and process each word
with open(input_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Process each line and split into words
for line in lines:
    # Split the line into words using split(), which separates by spaces and newlines
    words = line.split()
    for word in words:
        word = word.strip()  # Remove surrounding whitespace
        if len(word) >= min_word_length and polish_pattern.search(word):  # Keep words of sufficient length that contain a Polish character
            lower_word = word.lower()  # Convert word to lowercase for comparison
            if lower_word not in unique_words:
                # If lowercase version doesn't exist, add the word with original capitalization
                unique_words[lower_word] = word
            else:
                # If lowercase version exists, preserve the capitalized version if available
                if word[0].isupper():
                    unique_words[lower_word] = word

# Write the filtered words to the output file
with open(output_file, "w", encoding="utf-8") as file:
    for word in sorted(unique_words.values()):  # Sort words alphabetically
        file.write(word + "\n")

print(f"Filtered file has been saved as: {output_file}")
print(f"Total number of filtered words: {len(unique_words)}")
