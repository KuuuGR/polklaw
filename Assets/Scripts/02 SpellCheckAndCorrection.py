import subprocess

# Paths to input and output files
input_file = "data/input/polish_words.txt"
output_file = "data/output/filtered_and_corrected_words.txt"

# List to store filtered and corrected words
filtered_corrected_words = []

# Function to check spelling using Hunspell
def check_spelling(word):
    # Run Hunspell with the Polish dictionary
    process = subprocess.run(["hunspell", "-d", "pl_PL"], input=word, text=True, capture_output=True)
    output = process.stdout.splitlines()

    # Ignore lines with the Hunspell version info
    output = [line for line in output if not line.startswith("Hunspell")]

    # If output is empty, return the original word
    if not output:
        return word

    # Analyze Hunspell results
    if output[0].startswith("&"):
        # The word is incorrect, check suggestions
        suggestions = output[0].split(":")[-1].split(", ")
        if suggestions:
            # Display only cases where correction occurred
            print(f"Incorrect word: {word}, suggested correction: {suggestions[0]}")
            return suggestions[0]  # Return the first suggested correction
        else:
            return None  # No suggestion, remove the word
    else:
        # Return the correct word unchanged
        return word

# Read the input file and process each word
with open(input_file, "r", encoding="utf-8") as file:
    words = file.readlines()

# Counter for processed words
processed_count = 0

# Check each word
for word in words:
    word = word.strip().lower()  # Remove whitespace and convert to lowercase
    corrected_word = check_spelling(word)
    if corrected_word:
        filtered_corrected_words.append(corrected_word)

    # Increment the processed word counter
    processed_count += 1

    # Display a message every 100 words processed
    if processed_count % 100 == 0:
        print(f"Processed {processed_count} words...")

# Write the filtered and corrected words to the output file
with open(output_file, "w", encoding="utf-8") as file:
    for word in sorted(set(filtered_corrected_words)):  # Remove duplicates and sort
        file.write(word + "\n")

print(f"Filtered and corrected file saved as: {output_file}")
print(f"Total number of words processed: {processed_count}")
