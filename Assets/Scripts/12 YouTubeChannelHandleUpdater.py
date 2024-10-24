import re
import os
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
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to get the YouTube handle from the channel URL
def get_channel_handle(video_url, driver):
    driver.get(video_url)
    try:
        # Wait for the handle link element to load and extract the text
        handle_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/@")]'))
        )
        channel_handle = handle_element.get_attribute('href').split('/')[-1]

        # Ensure that the handle starts with only one '@' symbol
        if not channel_handle.startswith('@'):
            channel_handle = f'@{channel_handle}'
    except Exception as e:
        print(f"Error finding channel handle for {video_url}: {e}")
        channel_handle = "Handle not found"
    return channel_handle

# Function to process a list of video URLs and update channel details
def process_urls(urls, driver, output_file):
    with open(output_file, 'a', encoding='utf-8') as updated_file:
        for channel_name, video_url in urls:
            # Get the YouTube channel handle by visiting the video URL
            channel_handle = get_channel_handle(video_url, driver)

            # Avoid adding extra '@' if already present in handle
            if not channel_handle.startswith('@'):
                channel_handle = '@' + channel_handle

            # Write the updated line with the channel handle immediately
            updated_file.write(f"Channel Name: {channel_name} -> URL: {video_url} --> {channel_handle}\n")
            updated_file.flush()
            print(f"Updated: {channel_name} --> {channel_handle}")

            # Optional sleep to avoid rate-limiting or blocking by YouTube
            time.sleep(1)

# Main script to read input file, process URLs in batches, and write progress to a resume file
def update_channel_details(input_file, output_file, batch_size=10):
    driver = setup_driver()

    # Load previously processed URLs (if resume file exists)
    resume_file = output_file + '.resume'
    processed_urls = set()
    if os.path.exists(resume_file):
        with open(resume_file, 'r', encoding='utf-8') as resume:
            processed_urls.update(line.strip() for line in resume.readlines())

    # Regular expression to match the channel name and URL pattern
    pattern = re.compile(r'Channel Name: (.*?) -> URL: (https://www\.youtube\.com/watch\?v=[0-9A-Za-z_-]{11})')

    # Read the input file line by line
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Prepare a list of URLs for batch processing
    urls_to_process = []
    processed_count = 0
    for line in lines:
        match = pattern.search(line)
        if match:
            channel_name = match.group(1)
            video_url = match.group(2)

            # Skip already processed URLs
            if video_url in processed_urls:
                continue

            urls_to_process.append((channel_name, video_url))

            # Process in batches of `batch_size`
            if len(urls_to_process) == batch_size:
                process_urls(urls_to_process, driver, output_file)
                processed_count += len(urls_to_process)
                print(f"Processed {processed_count} URLs so far...")
                with open(resume_file, 'a', encoding='utf-8') as resume_out:
                    for _, url in urls_to_process:
                        resume_out.write(url + "\n")
                urls_to_process = []

    # Process any remaining URLs that didn't complete a batch
    if urls_to_process:
        process_urls(urls_to_process, driver, output_file)
        processed_count += len(urls_to_process)
        print(f"Processed {processed_count} URLs so far...")
        with open(resume_file, 'a', encoding='utf-8') as resume_out:
            for _, url in urls_to_process:
                resume_out.write(url + "\n")

    driver.quit()
    print(f"Channel details updated and written to {output_file}")

# File paths for input and output
input_file = "data/input/channel_details.txt"
output_file = "data/output/updated_channel_details.txt"

# Run the update process
if __name__ == "__main__":
    update_channel_details(input_file, output_file)
