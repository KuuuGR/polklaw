import yt_dlp as youtube_dl
import os
import re

# Function to get video URLs for a given YouTube channel
def get_channel_videos(channel_url, output_file, processed_channels_file):
    # Configuration for yt_dlp
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    video_urls = []  # List to store video URLs

    try:
        # Create a yt_dlp instance
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Fetch the info for the channel/playlist
            info_dict = ydl.extract_info(channel_url, download=False)
            
            # Check if 'entries' is in the info_dict
            if 'entries' in info_dict:
                # Iterate through each video in the channel/playlist
                for i, video in enumerate(info_dict['entries'], start=1):
                    # Append the video URL to the list
                    video_urls.append(f'https://www.youtube.com/watch?v={video["id"]}')
                    
                    # Every 1000 addresses, write to file and clear the list to save memory
                    if i % 1000 == 0:
                        with open(output_file, "a", encoding="utf-8") as file:  # 'a' mode for append
                            for url in video_urls:
                                file.write(url + "\n")
                        print(f"Added {i} video URLs to {output_file}")
                        video_urls = []  # Reset the list after saving
    except Exception as e:
        print(f"Error processing channel: {channel_url}, Error: {e}")
        return False

    # Write any remaining video URLs to the file
    if video_urls:
        with open(output_file, "a", encoding="utf-8") as file:  # Append mode to not overwrite
            for url in video_urls:
                file.write(url + "\n")
        print(f"Added the final batch of {len(video_urls)} video URLs to {output_file}")

    total_videos = len(info_dict.get('entries', [])) if 'entries' in info_dict else 0
    print(f"Saved a total of {total_videos} video URLs to {output_file}")
    return True

# Main function to process channels from input file
def process_channels(input_handles_file, output_file, processed_channels_file):
    # Load previously processed channels (if any)
    processed_channels = set()
    if os.path.exists(processed_channels_file):
        with open(processed_channels_file, 'r', encoding='utf-8') as processed_file:
            processed_channels.update(line.strip() for line in processed_file.readlines())

    # Read the input file with handles
    with open(input_handles_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    total_channels = len(lines)
    processed_count = 0

    for line in lines:
        match = re.match(r'Channel Name: (.*?) -> (.*)', line)
        if match:
            channel_name = match.group(1)
            channel_handle = match.group(2)

            # Skip already processed channels
            if channel_handle in processed_channels:
                processed_count += 1
                continue

            # Form the channel URL
            channel_url = f'https://www.youtube.com/{channel_handle}/videos'

            # Process channel videos
            success = get_channel_videos(channel_url, output_file, processed_channels_file)

            # Update processed channels list
            if success:
                with open(processed_channels_file, 'a', encoding='utf-8') as processed_file:
                    processed_file.write(channel_handle + "\n")

            processed_count += 1
            print(f"Processed {processed_count}/{total_channels} channels")

if __name__ == "__main__":
    input_handles_file = "channel_handles_output.txt"
    output_file = "movies.txt"
    processed_channels_file = "processed_channels.txt"

    process_channels(input_handles_file, output_file, processed_channels_file)
