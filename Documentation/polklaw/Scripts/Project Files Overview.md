
# General

Most of the collected data corpus and Python scripts are stored in the **Assets** folder.

# Text Files

## 1. Dictionary

The file `slownik.txt` contains a dictionary of collected Polish words. Each word must contain at least one Polish national character. This file is used to search for YouTube videos that contain these Polish words.

## 2. Polish Video Addresses

The search method yielded video URLs totaling about 120MB (unpacked, this is 562MB). After removing duplicates and repacking, the file is now 64MB. To save space in this GitHub repository, only the URLs that contain Polish transcriptions are included. This file can be used in the future to extract channel names, remove further duplicates, and gather more videos from channels with at least one transcription. So far, the corpus obtained from these videos is approximately 1GB of text.

# Python Scripts

## 1. **ExtractPolishWords.py**

### Description:

This script processes `.pdf`, `.docx`, and `.txt` files from the input directory to extract words containing Polish diacritical characters. It then removes any words containing digits, converts them to lowercase for comparison, and saves the unique words in an output file, sorted alphabetically.

### Input:

- `.pdf`, `.docx`, and `.txt` files located in `data/input/`.

### Output:

- `polish_words.txt` (located in `data/output/`): A text file containing unique Polish words with diacritical characters, sorted alphabetically.

### Key Features:

- Handles multiple file types (`.pdf`, `.docx`, `.txt`).
- Detects and extracts words with Polish diacritical characters.
- Removes digits from words and eliminates duplicates.
- Saves the unique words in alphabetical order.
## 2. **SpellCheckAndCorrection.py**

### Description:

This script processes a list of Polish words from an input file, checks their spelling using the Hunspell tool with a Polish dictionary, and applies corrections where necessary. Incorrect words are either corrected based on the first suggested fix or removed if no suggestion is available. The corrected words are then saved in an output file, with duplicates removed and the words sorted alphabetically.

### Input:

- `polish_words.txt` (located in `data/input/`): A text file containing Polish words.

### Output:

- `filtered_and_corrected_words.txt` (located in `data/output/`): A text file containing filtered and corrected Polish words, sorted alphabetically and without duplicates.

### Key Features:

- Utilizes Hunspell for spelling checks and corrections.
- Handles `.txt` files.
- Outputs a cleaned, deduplicated, and sorted list of words.

---
### Optional: **FilterPolishVerbs.py**

#### Description:

This script processes a list of Polish words, identifies verbs using the spaCy language model for Polish, and either converts them to their base form (lemma) or keeps the original form. The filtered verbs are then deduplicated and saved to an output file.

#### Input:

- `dialectic_words.txt` (located in `data/input/`): A text file containing Polish words to be processed.

#### Output:

- `filtered_verbs.txt` (located in `data/output/`): A text file containing filtered Polish verbs, sorted alphabetically and without duplicates.

#### Key Features:

- Uses the spaCy language model to identify and process Polish verbs.
- Option to convert verbs to their base form (lemma).
- Removes duplicates while preserving capitalization.
- Outputs a sorted list of verbs.

---
## 3. **FilterDialecticWords.py**

### Description:

This script processes a list of Polish words from an input file and filters them to retain words containing Polish diacritical characters. It ensures that words are of a certain minimum length and removes duplicates while preserving original capitalization. The final filtered and sorted words are saved to an output file.

### Input:

- `filtered_and_corrected_words.txt` (located in `data/input/`): A text file containing pre-processed Polish words.

### Output:

- `dialectic_words.txt` (located in `data/output/`): A text file containing filtered Polish words that include diacritical characters, sorted alphabetically.

### Key Features:

- Retains words that contain Polish diacritical characters.
- Removes duplicates while preserving the original capitalization.
- Outputs a sorted list of words.



## 4. **YouTubeChannelSearch.py**

### Description:

This script processes a list of search queries from a dictionary file, uses `yt_dlp` to search YouTube for videos matching the query, and collects video URLs. The collected URLs are saved to an output file, and the dictionary is updated to remove the processed words.

### Input:

- `dictionary.txt` (located in `data/input/`): A text file containing search queries (one per line).

### Output:

- `collected_links.txt` (located in `data/output/`): A text file containing the collected YouTube video URLs.

### Key Features:

- Uses `yt_dlp` to search YouTube based on search queries.
- Collects and saves video URLs for each search query.
- Automatically updates the dictionary file after processing each query.
- Handles multiple search queries from the dictionary file.
## 5. **SortYouTubeLinks.py**

### Description:

This script reads a file containing YouTube video links, counts occurrences of each link, and outputs two files: one with the unique sorted links and another with the top 16 most duplicated links.

### Input:

- `collected_links.txt` (located in `data/output/YouTubeChannelSearch/`): A text file containing YouTube video links.

### Output:

- `sorted_links.txt` (located in `data/output/YouTubeChannelSearch/`): A text file containing the sorted unique YouTube video links.
- `top_16_duplicates.txt` (located in `data/output/YouTubeChannelSearch/`): A text file containing the top 16 most duplicated YouTube video links along with their occurrence counts.

### Key Features:

- Reads a list of YouTube video links from an input file.
- Counts occurrences of each link and sorts them alphabetically.
- Outputs the sorted list of unique links.
- Identifies and saves the top 16 most duplicated links.
## 6. **.**
