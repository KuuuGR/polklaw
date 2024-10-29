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
def get_channel_handle(video_url, driver, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            driver.get(video_url)
            
            # First attempt: Try to find the handle link element with @ format
            try:
                handle_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/@")]'))
                )
                channel_handle = handle_element.get_attribute('href').split('/')[-1]
            
            # If not found, proceed to another attempt
            except:
                # Second attempt: Try to find an element like <yt-formatted-string> with nested <a>
                handle_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//yt-formatted-string[@id="text"]//a'))
                )
                channel_handle = handle_element.get_attribute('href').split('/')[-1]

            return channel_handle

        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {video_url}: {e}")
            attempt += 1
            time.sleep(2)  # Wait before retrying

    # If all retries fail, return failure
    return "Handle not found"

# Function to process channels and update details with resume capability
def process_channels_with_resume(input_file, output_file, resume_file):
    driver = setup_driver()

    while True:
        # Load previously processed channels (if resume file exists)
        processed_channels = set()
        if os.path.exists(resume_file):
            with open(resume_file, 'r', encoding='utf-8') as resume:
                processed_channels.update(line.strip() for line in resume.readlines())

        # Regular expression to match the channel name and URLS pattern
        pattern = re.compile(r'Channel Name: (.*?) -> URLS: \[(.*?)\]')

        # Read the input file line by line
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        has_failed = False

        with open(output_file, 'a', encoding='utf-8') as out_file, \
             open(resume_file, 'a', encoding='utf-8') as resume_out:

            for line in lines:
                match = pattern.search(line)
                if match:
                    channel_name = match.group(1)
                    urls = match.group(2).split(', ')

                    # Skip already processed channels
                    if channel_name in processed_channels:
                        continue

                    # Try to get the channel handle from one of the URLs
                    channel_handle = "Handle not found"
                    for url in urls:
                        channel_handle = get_channel_handle(url, driver)
                        if channel_handle != "Handle not found":
                            break

                    # Write the result to the output file
                    if channel_handle == "Handle not found":
                        has_failed = True
                        out_file.write(f"Channel Name: {channel_name} -> failed\n")
                    else:
                        out_file.write(f"Channel Name: {channel_name} -> {channel_handle}\n")
                    out_file.flush()

                    # Update the resume file
                    resume_out.write(channel_name + "\n")
                    resume_out.flush()

                    print(f"Processed: {channel_name} -> {channel_handle}")

                    # Optional sleep to avoid rate-limiting or blocking by YouTube
                    time.sleep(1)

        # If there are no failed attempts left, break the retry loop
        if not has_failed:
            break

    driver.quit()
    print(f"Channel handles updated and written to {output_file}")

# File paths for input, output, and resume
input_file = "combined_channel_details.txt"
output_file = "channel_handles_output.txt"
resume_file = "resume.txt"

# Run the update process
if __name__ == "__main__":
    process_channels_with_resume(input_file, output_file, resume_file)
