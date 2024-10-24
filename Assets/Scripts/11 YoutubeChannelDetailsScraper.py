import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Function to set up the Selenium WebDriver
def setup_driver():
    """
    Sets up and returns a Selenium WebDriver instance with Chrome options for headless execution.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    chrome_options.add_argument("--no-sandbox")  # Required for running as root user
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering
    chrome_options.add_argument("--remote-debugging-port=9222")  # Optional

    # Initialize WebDriver with options and auto-managed ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to get channel name from a YouTube video URL
def get_channel_name(video_url, driver):
    """
    Extracts and returns the channel name from a given YouTube video URL using Selenium.
    
    Args:
        video_url (str): URL of the YouTube video.
        driver (webdriver.Chrome): Selenium WebDriver instance.
    
    Returns:
        str: Extracted channel name or an error message if not found.
    """
    driver.get(video_url)
    try:
        # Wait for the channel name element to be visible and extract the text
        channel_name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//ytd-channel-name[@id="channel-name"]//a'))
        )
        channel_name = channel_name_element.text.strip()
    except Exception as e:
        print(f"Error finding channel name for {video_url}: {e}")
        channel_name = "Channel name not found"
    return channel_name

# Function to extract channel details without transcriptions
def extract_channel_details(input_file, output_file, resume_file, failed_file):
    """
    Extracts channel details from a list of YouTube video URLs and writes results to output files.
    
    Args:
        input_file (str): Path to the file containing YouTube video URLs.
        output_file (str): Path to the output file to save channel details.
        resume_file (str): Path to the resume file to track processed URLs.
        failed_file (str): Path to the file to save URLs that failed to process.
    """
    # Initialize variables
    processed_urls = set()
    failed_urls = set()

    # Check if resume file exists to continue from where it left off
    if os.path.exists(resume_file):
        with open(resume_file, 'r', encoding='utf-8') as resume:
            processed_urls.update(line.strip() for line in resume.readlines())

    # Load the failed URLs if any exist
    if os.path.exists(failed_file):
        with open(failed_file, 'r', encoding='utf-8') as failed:
            failed_urls.update(line.strip() for line in failed.readlines())

    # Read all video URLs from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        video_urls = file.readlines()

    total_videos = len(video_urls)
    print(f"Total videos to process: {total_videos}")

    # Set up the Selenium WebDriver once for the entire session
    driver = setup_driver()

    # Open output files for appending and error handling
    with open(output_file, 'a', encoding='utf-8') as out_file, \
         open(resume_file, 'a', encoding='utf-8') as resume_out, \
         open(failed_file, 'a', encoding='utf-8') as failed_out:

        # Process each video URL
        for index, url in enumerate(video_urls, start=1):
            url = url.strip()  # Remove any leading/trailing whitespace

            # Restart the WebDriver after every 1000 videos to avoid memory issues
            if index % 1000 == 0:
                driver.quit()
                driver = setup_driver()

            # Skip URLs already processed or failed
            if url in processed_urls or url in failed_urls:
                continue

            # Print progress
            print(f"Processing video {index} of {total_videos}: {url}")

            # Validate URL format
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
            if not video_id_match:
                print(f"Invalid video URL: {url}")
                failed_out.write(url + "\n")
                failed_out.flush()
                continue

            # Get channel name
            channel_name = get_channel_name(url, driver)

            # If channel name is retrieved, write to output file
            if channel_name != "Channel name not found":
                out_file.write(f"Channel Name: {channel_name} -> URL: {url}\n")
                out_file.flush()
                # Update resume file to mark as processed
                resume_out.write(url + "\n")
                resume_out.flush()
            else:
                # If channel name retrieval failed, mark it as failed
                failed_out.write(url + "\n")
                failed_out.flush()

            # Print status update
            print(f"Processed {index}/{total_videos} videos.")

            # Optional sleep to avoid being blocked by YouTube or triggering rate limits
            time.sleep(1)

    # Close the driver after processing all URLs
    driver.quit()
    print("Processing complete. Check the output files for results.")

# File paths for input, output, and resume
input_file = "data/input/unique_youtube_links.txt"
output_file = "data/output/channel_details.txt"
resume_file = "data/output/resume.txt"
failed_file = "data/output/failed.txt"

# Run the extraction process
if __name__ == "__main__":
    extract_channel_details(input_file, output_file, resume_file, failed_file)
