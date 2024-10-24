import re
import os
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
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to get the YouTube handle from the channel URL
def get_channel_handle(video_url, driver):
    """
    Extracts and returns the YouTube channel handle from a given video URL using Selenium.
    
    Args:
        video_url (str): URL of the YouTube video.
        driver (webdriver.Chrome): Selenium WebDriver instance.
    
    Returns:
        str: Extracted channel handle or an error message if not found.
    """
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

# Function to update the channel details file with handles
def update_channel_details(input_file, output_file):
    """
    Reads the input file, extracts YouTube channel handles, and writes updated information to the output file.
    
    Args:
        input_file (str): Path to the file containing YouTube video URLs.
        output_file (str): Path to the output file to save updated channel details.
    """
    driver = setup_driver()

    # Regular expression to match the channel name and URL pattern
    pattern = re.compile(r'Channel Name: (.*?) -> URL: (https://www\.youtube\.com/watch\?v=[0-9A-Za-z_-]{11})')

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_file, 'w', encoding='utf-8') as updated_file:
        for line in lines:
            match = pattern.search(line)
            if match:
                channel_name = match.group(1)
                video_url = match.group(2)

                # Get the YouTube channel handle by visiting the video URL
                channel_handle = get_channel_handle(video_url, driver)

                # Avoid adding extra '@' if already present in handle
                if not channel_handle.startswith('@'):
                    channel_handle = '@' + channel_handle

                # Write the updated line with the channel handle
                updated_file.write(f"Channel Name: {channel_name} -> URL: {video_url} --> {channel_handle}\n")
                print(f"Updated: {channel_name} --> {channel_handle}")
            else:
                # Write the original line if it doesn't match the pattern
                updated_file.write(line)

    driver.quit()
    print(f"Channel details updated and written to {output_file}")

# File paths for input and output
input_file = "data/input/channel_details.txt"
output_file = "data/output/updated_channel_details.txt"

# Run the update process
if __name__ == "__main__":
    update_channel_details(input_file, output_file)
