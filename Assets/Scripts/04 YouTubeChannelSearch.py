import yt_dlp as youtube_dl
import os

# Paths to dictionary and output file
dictionary_file = "data/input/dictionary.txt"
output_file = "data/output/collected_links.txt"

def get_channel_videos(search_query, output_file):
    # Configuration for yt_dlp
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    video_urls = []  # List to store video URLs
    search_url = f'https://www.youtube.com/results?search_query={search_query.replace(" ", "+")}'

    # Create a yt_dlp instance
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Fetch the info for the search query URL
            info_dict = ydl.extract_info(search_url, download=False)
            
            # Check if 'entries' is in the info_dict
            if 'entries' in info_dict:
                # Iterate through each video in the search results
                for video in info_dict['entries']:
                    # Append the video URL to the list
                    video_urls.append(f'https://www.youtube.com/watch?v={video["id"]}')
        except Exception as e:
            print(f"Error fetching info for query '{search_query}': {e}")

    # Write the search query and video URLs to the output file
    with open(output_file, "a", encoding="utf-8") as file:
        file.write(f"Search Query: {search_query}\n")
        for url in video_urls:
            file.write(url + "\n")
        file.write("\n")  # Newline for separation

    print(f"Saved {len(video_urls)} video URLs for query '{search_query}' to {output_file}")

def process_dictionary_and_collect_links(dictionary_file, output_file):
    # Read all words from the dictionary file
    if not os.path.exists(dictionary_file):
        print(f"Dictionary file '{dictionary_file}' not found.")
        return

    with open(dictionary_file, "r", encoding="utf-8") as file:
        words = file.readlines()

    words = [word.strip() for word in words if word.strip()]  # Remove empty lines

    # Process each word in the dictionary
    for word in words:
        print(f"Processing query for word: {word}")
        get_channel_videos(word, output_file)

    # After processing, update the dictionary to remove used words
    # (all words that have been queried)
    with open(dictionary_file, "w", encoding="utf-8") as file:
        # Write back only the words that haven't been used
        remaining_words = [w for w in words if w not in words]
        file.write("\n".join(remaining_words))

if __name__ == "__main__":
    # Start processing dictionary and collecting links
    process_dictionary_and_collect_links(dictionary_file, output_file)
