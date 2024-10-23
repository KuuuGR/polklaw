import os

def combine_text_files(input_directory="data/input/", 
                       output_file_name="data/output/combined_output.txt"):
    """
    Combines all text files from the input directory into a single output file.

    :param input_directory: Directory where input text files are located.
    :param output_file_name: Path and name of the output file where the combined content will be written.
    """
    # Ensure the input directory exists
    if not os.path.exists(input_directory):
        print(f"The directory {input_directory} does not exist.")
        return

    # Get all .txt files in the folder
    text_files = [file for file in os.listdir(input_directory) if file.endswith(".txt")]

    if not text_files:
        print(f"No .txt files found in {input_directory}.")
        return

    # Open the output file for writing
    with open(output_file_name, 'w', encoding='utf-8') as output_file:
        for file_name in text_files:
            file_path = os.path.join(input_directory, file_name)

            # Read the content of each text file
            with open(file_path, 'r', encoding='utf-8') as input_file:
                content = input_file.read()

            # Write the content to the output file, followed by an empty line
            output_file.write(content)
            output_file.write("\n\n")  # Separate each file's content by an empty line

    print(f"All text files have been combined into {output_file_name}")

if __name__ == "__main__":
    combine_text_files()
