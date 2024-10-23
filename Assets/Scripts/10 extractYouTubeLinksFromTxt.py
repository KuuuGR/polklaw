import re
from collections import defaultdict

def extractYouTubeLinks(inputFile="data/input/combinedOutput.txt", outputFile="data/output/uniqueYouTubeLinks.txt"):
    """
    Extracts unique YouTube video URLs from an input file, counts duplicates, 
    and writes the unique, sorted links to an output file.
    
    :param inputFile: Path to the input file containing lines with YouTube URLs.
    :param outputFile: Path to the output file where unique, sorted URLs will be saved.
    """
    youtubeLinks = defaultdict(int)  # Dictionary to count occurrences of each URL

    # Regular expression to match YouTube video URLs
    youtubeUrlPattern = re.compile(r"(https://www\.youtube\.com/watch\?v=[0-9A-Za-z_-]{11})")

    # Read through the input file and count occurrences of YouTube URLs
    with open(inputFile, 'r', encoding='utf-8') as file:
        for line in file:
            match = youtubeUrlPattern.search(line)
            if match:
                youtubeLinks[match.group(1)] += 1  # Increment the count for this URL

    # Sort the unique YouTube links
    sortedLinks = sorted(youtubeLinks.keys())

    # Write the sorted, unique links to the output file
    with open(outputFile, 'w', encoding='utf-8') as file:
        for link in sortedLinks:
            file.write(link + "\n")

    # Print summary of duplicates
    duplicateCount = sum(count - 1 for count in youtubeLinks.values() if count > 1)
    print(f"Collected {len(sortedLinks)} unique YouTube links.")
    print(f"Found {duplicateCount} duplicate entries.")

if __name__ == "__main__":
    extractYouTubeLinks()
