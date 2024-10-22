import multiprocessing
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_transcriptions(input_file, output_file, resume_file, batch_size=1000):
    # Read the resume file to get processed URLs
    if os.path.exists(resume_file):
        with open(resume_file, 'r', encoding='utf-8') as file:
            processed_urls = set(line.strip() for line in file.readlines())
    else:
        processed_urls = set()

    # Read the input file and filter out already processed URLs
    with open(input_file, 'r', encoding='utf-8') as file:
        video_urls = [url.strip() for url in file.readlines() if url.strip() not in processed_urls]

    video_count = len(video_urls)
    print(f"Total videos to process: {video_count}")

    # Open the output and resume files for writing
    with open(output_file, 'a', encoding='utf-8') as out_file, open(resume_file, 'a', encoding='utf-8') as resume_out_file:
        for index, url in enumerate(video_urls, start=1):
            if index % batch_size == 1:
                print(f"\nProcessing batch: {index // batch_size + 1}")
                print(f"{index} of {video_count} videos processed so far")

            try:
                # Extract video ID from the URL
                video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
                if not video_id_match:
                    print(f"Invalid URL format: {url}")
                    continue
                video_id = video_id_match.group(1)
                print(f"Processing video {index} of {video_count}: {video_id}")

                # Fetch transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pl'])

                # If there is no transcript, skip to the next video
                if not transcript:
                    print(f"No Polish transcript available for URL: {url}")
                    continue

                # Convert transcript to a plain text string
                transcription_text = '\n'.join([item['text'] for item in transcript])

                # Write the URL and transcription to the output file
                out_file.write(f"URL: {url}\nTranscription:\n{transcription_text}\n\n")

                # Mark as processed by adding to the resume file
                resume_out_file.write(url + "\n")
                resume_out_file.flush()  # Immediately write to the resume file to save progress

                # Update processed URLs set
                processed_urls.add(url)

                # Remove processed URLs from the input file in batches
                if index % batch_size == 0 or index == video_count:
                    print(f"\nBatch of {batch_size} URLs processed, updating input file...\n")
                    update_input_file(input_file, processed_urls)

            except Exception as e:
                # Skip any URLs that fail without logging the failure
                print(f"No Polish transcript found or failed to process: {url}")
                continue

def update_input_file(input_file, processed_urls):
    """
    Remove processed URLs from the input file.
    """
    # Read all lines from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Keep only unprocessed URLs
    with open(input_file, 'w', encoding='utf-8') as file:
        for line in lines:
            if line.strip() not in processed_urls:
                file.write(line)

    print("Input file updated to remove processed URLs.")

def process_file(input_file, output_file, resume_file):
    extract_transcriptions(input_file, output_file, resume_file)

def split_input_file(input_file, num_chunks):
    """
    Split the input file into num_chunks smaller files.
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    chunk_size = len(lines) // num_chunks
    for i in range(num_chunks):
        chunk_file = f"{input_file}_part_{i}.txt"
        with open(chunk_file, 'w', encoding='utf-8') as chunk:
            chunk.writelines(lines[i * chunk_size: (i + 1) * chunk_size])

    print(f"File split into {num_chunks} parts.")

if __name__ == "__main__":
    # Define paths
    base_path = 'data/input/YouTubeChannelSearch/'
    
    # Main input file
    input_file = base_path + 'video_urls.txt'
    output_file = base_path + 'transcriptions.txt'
    resume_file = base_path + 'resume_file.txt'

    # Step 1: Split the input file into smaller chunks
    split_input_file(input_file, num_chunks=10)

    # Step 2: Prepare file paths for each process
    num_parts = 10  # Number of parts to split into
    files = [
        (f"{input_file}_part_{i}.txt", 
         f"{output_file}_part_{i}.txt", 
         f"{resume_file}_part_{i}.txt")
        for i in range(num_parts)
    ]

    # Step 3: Launch multiprocessing to handle each file part
    processes = []
    for file_set in files:
        p = multiprocessing.Process(target=process_file, args=file_set)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("All parts processed.")
