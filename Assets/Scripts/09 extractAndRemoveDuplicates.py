import re

def extractAndRemoveDuplicates(inputFile="data/input/combinedOutput.txt", outputFile="data/output/uniqueTranscriptions.txt"):
    """
    Extracts blocks of YouTube URLs and transcriptions from the input file, removes duplicates, 
    and writes unique blocks to the output file.
    
    :param inputFile: Path to the input file containing URL + transcription blocks.
    :param outputFile: Path to the output file where unique blocks will be saved.
    """
    blockPattern = re.compile(r"(URL: https://www\.youtube\.com/watch\?v=[0-9A-Za-z_-]{11})\nTranscription:\n(.*?)\n\n", re.DOTALL)
    uniqueBlocks = set()

    # Read the entire input file
    with open(inputFile, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all blocks of URL + Transcription
    blocks = blockPattern.findall(content)

    with open(outputFile, 'w', encoding='utf-8') as outFile:
        for block in blocks:
            url = block[0]
            transcription = block[1].strip()  # Remove extra newlines or spaces around transcriptions
            fullBlock = f"{url}\nTranscription:\n{transcription}"

            # Add block to set if it hasn't been seen before
            if fullBlock not in uniqueBlocks:
                uniqueBlocks.add(fullBlock)
                # Write the unique block to the output file
                outFile.write(f"{fullBlock}\n\n")

    print(f"Removed duplicates and wrote {len(uniqueBlocks)} unique blocks to {outputFile}")

if __name__ == "__main__":
    extractAndRemoveDuplicates()