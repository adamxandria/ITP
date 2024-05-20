from bs4 import BeautifulSoup
import requests
import csv
import os

# Send a request to the website
page_to_scrape = requests.get("https://www.pmo.gov.sg/The-Cabinet")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

# Find all 'li' elements since each 'li' represents a cabinet member's data
cabinet_members = soup.findAll("li")

# Create a directory for the downloaded images if it doesn't already exist
if not os.path.exists('downloaded_images'):
    os.makedirs('downloaded_images')

# Open the CSV file for writing
with open("scraped_data.csv", "w", newline='') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(["Name", "Title", "Image URL", "Local Image Path"])
    
    # Iterate over each cabinet member
    for member in cabinet_members:
        # Safely extracting the name
        name_div = member.find("div", attrs={"class": "field-content"})
        name = name_div.text.strip() if name_div else 'No name found'
        
        # Safely extracting the title
        title_p = member.find("p")
        title = title_p.text.strip() if title_p else 'No title found'
        
        # Safely extracting and downloading the image URL
        image_tag = member.find("img")
        if image_tag and image_tag.has_attr('src'):
            image_url = "https://www.pmo.gov.sg" + image_tag['src']
            image_response = requests.get(image_url)
            image_path = f'downloaded_images/{name.replace(" ", "_")}.jpg'
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
        else:
            image_url = 'No image found'
            image_path = 'No image downloaded'
        
        # Print and write to CSV
        print(name + " - " + title + " - " + image_url + " - " + image_path)
        writer.writerow([name, title, image_url, image_path])
