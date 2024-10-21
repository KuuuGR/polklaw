import os

# Folder path and file names
folder_path = "data/output/YouTubeChannelSearch"
input_file_path = os.path.join(folder_path, "collected_links.txt")
sorted_links_file = os.path.join(folder_path, "sorted_links.txt")
top_16_duplicates_file = os.path.join(folder_path, "top_16_duplicates.txt")

# Step 1: Read all links and count occurrences
link_counts = {}
with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        link = line.strip()  # Remove any leading/trailing whitespace and newlines
        if link:  # If the line is not empty
            if link in link_counts:
                link_counts[link] += 1  # Increment count for this link
            else:
                link_counts[link] = 1  # Initialize count for this link

# Step 2: Sort and write unique links to sorted_links.txt
sorted_unique_links = sorted(link_counts.keys())  # Sort links alphabetically

with open(sorted_links_file, "w", encoding="utf-8") as sorted_file:
    for link in sorted_unique_links:
        sorted_file.write(link + "\n")

print(f"Unique sorted links have been saved to: {sorted_links_file}")

# Step 3: Find and write the top 16 most duplicated links
top_16_links = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)[:16]  # Get top 16 by count

with open(top_16_duplicates_file, "w", encoding="utf-8") as top_file:
    for link, count in top_16_links:
        top_file.write(f"{count} duplicates - {link}\n")

print(f"Top 16 duplicated links have been saved to: {top_16_duplicates_file}")

# Print summary of results
print(f"Total unique links: {len(sorted_unique_links)}")
print("Top 16 most duplicated links:")
for link, count in top_16_links:
    print(f"{count} duplicates - {link}")
