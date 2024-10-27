
# General

Most of the collected data corpus and Python scripts are stored in the **Assets** folder.

# Text Files

## 1. Dictionary

The file `slownik.txt` contains a dictionary of collected Polish words. Each word must contain at least one Polish national character. This file is used to search for YouTube videos that contain these Polish words.

## 2. Polish Video Addresses

The search method yielded video URLs totaling about 120MB (unpacked, this is 562MB). After removing duplicates and repacking, the file is now 64MB. To save space in this GitHub repository, only the URLs that contain Polish transcriptions are included. This file can be used in the future to extract channel names, remove further duplicates, and gather more videos from channels with at least one transcription. So far, the corpus obtained from these videos is approximately 1GB of text.

## 3. uniqueYouTubeLinksWithPlTranscriptions.txt

This file contains 85,264 filtered YouTube links, selected from over 70 million addresses. Each link corresponds to a YouTube video that has a transcription available in Polish.

## 4. combined_channel_details.txt

- `combined_channel_details.txt` contains information about YouTube channels, including channel names and their associated video URLs.
- The file format follows the structure: `Channel Name: <channel_name> -> URLS: [<url1>, <url2>, ...]`.
- This dataset is used for further analysis, processing, and scraping operations to extract more information about the channels.
## 5. ,

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
## 6. **ExtractYouTubeTranscriptions.py**

### Description:

This script reads a list of YouTube video URLs from an input file, attempts to extract Polish transcriptions using the `youtube_transcript_api`, and writes the transcriptions to an output file. It keeps track of processed URLs using a resume file, allowing the script to resume where it left off if interrupted.

### Input:

- **`video_urls.txt`** (located in `data/input/`): A text file containing YouTube video URLs to process.

### Output:

- **`transcriptions.txt`** (located in `data/output/`): A text file containing the URLs and their corresponding Polish transcriptions.
- **`resume_file.txt`** (located in `data/output/`): A text file keeping track of processed URLs to prevent reprocessing.

### Key Features:

- Processes YouTube video URLs to extract Polish transcriptions.
- Handles batch processing with a customizable batch size.
- Updates the input file to remove processed URLs, ensuring efficiency.
- Can resume processing from where it left off using the resume file.
- Handles exceptions gracefully, skipping videos without available Polish transcriptions.
- Validates URL format before processing.

---
## 7. **MultiprocessYouTubeTranscriptions.py**

### Description:

This script processes a large input file of YouTube video URLs using multiprocessing. It splits the input file into smaller chunks and runs separate processes for each chunk to extract Polish transcriptions from YouTube videos. The script handles batch processing, resuming from the last processed URL, and updates the input file by removing processed URLs.

### Input:

- **`video_urls.txt`** (located in `data/input/YouTubeChannelSearch/`): A text file containing YouTube video URLs to process.

### Output:

- **`transcriptions.txt_part_[i]`** (located in `data/output/YouTubeChannelSearch/`): Text files containing the URLs and their corresponding Polish transcriptions for each chunk.
- **`resume_file_part_[i]`** (located in `data/output/YouTubeChannelSearch/`): Text files keeping track of processed URLs to prevent reprocessing.

### Key Features:

- Processes YouTube video URLs to extract Polish transcriptions in parallel using multiprocessing.
- Splits the input file into smaller chunks for more efficient processing.
- Handles batch processing and updates input file to remove processed URLs.
- Can resume processing from where it left off using resume files.
- Handles exceptions gracefully, skipping videos without available Polish transcriptions.
- Validates URL format before processing.

---
## 8. **CombineTextFiles.py**

### Description:

This script combines the content of all text files from a given directory into a single output file. Each file's content is separated by a blank line for clarity.

### Input:

- **`data/input/`**: Directory containing the `.txt` files to be combined.

### Output:

- **`data/output/combined_output.txt`**: The resulting output file where all the text content is written, with a blank line separating each file.

### Key Features:

- Reads all `.txt` files from the specified input directory.
- Combines the content of all text files into one output file.
- Ensures that the output file is updated even if no `.txt` files are found or if an error occurs.
## 9. **ExtractAndRemoveDuplicates.py**

### Description:

This script extracts blocks of YouTube URLs and transcriptions from an input file, removes duplicates, and writes the unique blocks to an output file.

### Input:

- **`data/input/combinedOutput.txt`**: A text file that contains multiple blocks of `URL + Transcription`.

### Output:

- **`data/output/uniqueTranscriptions.txt`**: A text file containing unique `URL + Transcription` blocks after duplicates have been removed.

### Key Features:

- Extracts and identifies `URL + Transcription` blocks from the input file.
- Removes duplicate blocks to ensure only unique ones are kept.
- Writes unique blocks to an output file.
- Provides a summary of how many unique blocks were written.
## 10. **ExtractYouTubeLinks.py**

###  Description:

This script extracts unique YouTube video URLs from an input file, counts any duplicate URLs, and writes the unique, sorted links to an output file.

### Input:

- **`data/input/combinedOutput.txt`**: A text file containing lines with YouTube URLs (in any format).

### Output:

- **`data/output/uniqueYouTubeLinks.txt`**: A file containing unique YouTube URLs, sorted alphabetically.

### Key Features:

- Extracts and counts YouTube video URLs from the input file.
- Writes unique URLs to an output file.
- Counts and reports duplicate entries.
- Provides a summary of the total unique URLs and duplicate entries.

---
## 11. **YouTubeChannelDetailsScraper.py**

### Overview

This script extracts channel details from a list of YouTube video URLs using Selenium WebDriver. It retrieves the channel name associated with each video and writes the output to specified files, ensuring that processed URLs are tracked for future resumability in case the script is interrupted.

### Features

- Extracts YouTube channel names from video URLs using Selenium WebDriver.
- Processes each video URL and writes channel details to an output file.
- Resumable processing with resume and failed log files.
- Automatically restarts the WebDriver after every 1000 URLs to handle memory usage efficiently.

### Requirements

- Python 3.x
- Selenium WebDriver
- WebDriver Manager for ChromeDriver installation

### Script Breakdown

#### 1. Setup Selenium WebDriver

The `setup_driver()` function configures the Selenium WebDriver with the following options:

- **Headless Execution**: Runs the browser without opening the UI.
- **No Sandbox & Disable GPU**: Improves stability and compatibility.
- **Disable Dev SHM Usage**: Helps overcome limited resource problems.
- **Auto-managed ChromeDriver**: Uses `webdriver_manager` for automatic ChromeDriver installation.

#### 2. Extract Channel Name

The `get_channel_name(video_url, driver)` function takes a video URL and uses Selenium to visit the URL and extract the channel name from the page:

- **Wait for Element**: Uses an explicit wait to ensure the channel name element is loaded before accessing it.
- **Handle Errors**: Prints an error message if the channel name cannot be found.

#### 3. Extract Channel Details

The `extract_channel_details(input_file, output_file, resume_file, failed_file)` function performs the following:

- **Resume from Progress**: Reads the resume file and failed URLs to skip already processed ones.
- **Loop through Video URLs**: Visits each YouTube video URL to extract channel names.
- **Restart Driver Periodically**: Quits and restarts the WebDriver every 800 videos to manage memory.
- **Writes Results to File**: Saves channel details to the output file and keeps track of processed and failed URLs.

### Usage Instructions

1. **Input File**: Prepare a file containing YouTube video URLs, one per line (e.g., `data/input/unique_youtube_links.txt`).
2. **Output File Paths**: Update the paths for input, output, resume, and failed files in the script.
3. **Run the Script**: Execute the script using Python.

### Example File Paths:

- **Input File**: `data/input/unique_youtube_links.txt`
- **Output File**: `data/output/channel_details.txt`
- **Resume File**: `data/output/resume.txt`
- **Failed File**: `data/output/failed.txt`

### Code Example

```
# File paths for input, output, and resume
input_file = "data/input/unique_youtube_links.txt"
output_file = "data/output/channel_details.txt"
resume_file = "data/output/resume.txt"
failed_file = "data/output/failed.txt"

# Run the extraction process
if __name__ == "__main__":
    extract_channel_details(input_file, output_file, resume_file, failed_file)
```

### Notes for Future Enhancements

- **Parallel Processing**: Adding multiprocessing could improve processing speed for a large number of URLs.
- **Error Handling**: Improve robustness for failed YouTube URL retrievals.
- **Rate Limiting**: Add more dynamic pauses or retries to prevent rate limiting by YouTube.
## 12.  **YouTubeChannelHandleUpdater.py**

###  Summary: 
This script extracts YouTube channel handles from a list of video URLs and updates the channel details in the specified output file. It uses Selenium for scraping and includes a batch processing mechanism to avoid overwhelming the browser or running into rate limits. Additionally, it features a resume mechanism to continue processing URLs from where it left off in case of failure, making it efficient for large datasets.

### Details:

- **Input:** File containing YouTube video URLs with channel names.
- **Output:** File containing updated channel details with YouTube handles.
- **Features:**
    - Headless browser for efficient scraping.
    - Batch processing with configurable batch size to control resource usage.
    - Resume capability to ensure continuity in case of interruptions.
    - Immediate file writes for progress tracking.
### Usage:

- Call `update_channel_details(input_file, output_file, batch_size=10)` to process the video URLs.
- The script writes the results in `updated_channel_details.txt` and keeps track of progress in a `.resume` file.

This script is helpful for managing large volumes of YouTube video metadata efficiently.

### Simplified Version for Fewer Files
A simplified version has been added as `12a_YoutubeChannelScraper.py` in the `OptionalScripts` folder.
## 13. **.**
