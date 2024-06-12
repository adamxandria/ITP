import pandas as pd
import requests
import os

# Load the dataset
file_path = 'anjing.csv'  # Update this with your actual file path
data = pd.read_csv(file_path)

# Directory to save the images
save_dir = 'dataset'
os.makedirs(save_dir, exist_ok=True)

def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f'Successfully downloaded {save_path}')
    except requests.exceptions.RequestException as e:
        print(f'Failed to download {url}: {e}')


for index, row in data.iterrows():
    image_url = row['image']
    image_id = row['id']  # Or any unique identifier for the image
    save_path = os.path.join(save_dir, f'{image_id}.jpg')
    download_image(image_url, save_path)
