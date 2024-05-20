from bs4 import BeautifulSoup
import requests
import csv

# Send a request to the website
page_to_scrape = requests.get("https://www.pmo.gov.sg/The-Cabinet")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

# Find all names and titles
names = soup.findAll("div", attrs={"class": "field-content"})
titles = soup.findAll("div", attrs={"class": "row qna"})

# Open the CSV file for writing
with open("scraped_data.csv", "w", newline='') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(["Name", "Title"])
    
    # Write the data rows
    for name, title in zip(names, titles):
        print(name.text.strip() + " - " + title.text.strip())
        writer.writerow([name.text.strip(), title.text.strip()])
