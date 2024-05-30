import pandas as pd
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException

# Path to the CSV file
csv_file = 'dataset_facebook-photos-scraper.csv'
# Folder where images will be saved
save_folder = 'downloaded_images'

# Create the directory if it doesn't exist
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Load the CSV file
data = pd.read_csv(csv_file)

# Create a requests session
session = requests.Session()
# Retry strategy
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
# Mount it for both http and https usage
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

# Process each image URL starting from row 65 (index 64)
for index, row in data.iterrows():
    if index >= 65:  # Start from row 66
        url = row['image']  # Replace 'image' with your actual column name
        file_name = os.path.join(save_folder, f'image_{index}.jpg')

        try:
            # Send a GET request to the image URL
            response = session.get(url, verify=False)  # Set verify=False if you need to bypass SSL verification
            if response.status_code == 200:
                # Write the image to a file
                with open(file_name, 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Failed to retrieve image from {url} with status code {response.status_code}")
        except RequestException as e:
            print(f"An error occurred while trying to retrieve {url}: {str(e)}")

print("Download completed.")
