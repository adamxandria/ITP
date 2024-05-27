# Importing Required Libraries

# For Frontend (Provides Interface) and Deployment
import streamlit as st

# requests is used to get access to the website or in other words connect to the website
import requests

# Beautiful Soup 4 is a Python library that makes it easy to scrape information from web pages.
# It provides Pythonic idioms for iterating, searching, and modifying the parse tree.
# The library sits atop an HTML or XML parser.
from bs4 import BeautifulSoup

# For Rendering in Zip File
import zipfile

# Importing os module to get size of zip file and limit it so that it stops after a certain limit is reached
import os

# Importing openpyxl to handle Excel files
from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage

# Set a maximum size for the zip file in bytes
MAX_ZIP_FILE_SIZE = 1024 * 1024 * 100  # 100 MB

# Set a maximum number of files to include in the zip file
MAX_ZIP_FILE_COUNT = 50

# Adding Title
st.title("Web Scraper")

# Adding Subheader
st.subheader("Web Scraper for ITP Project")

# For writing Text we use text function
st.text("Enter Website Link and Get Text and Images from it.")

# Getting Input from User
try:
    link = st.text_input("Enter Website Link")
    from urllib.parse import urlparse

    # Parse the URL
    parsed_url = urlparse(link)

    # Split the domain by dots and get the first part
    # For name after https
    domain_name = parsed_url.netloc.split('.')[0]

    # If the Website has www in the start instead of domain name
    if domain_name == 'www':
        domain_name = parsed_url.netloc.split('.')[1]

    st.write("Domain Name:", domain_name.capitalize())

except:
    st.write("Please Give Valid URL")


# Send an HTTP request to the URL of the webpage we want to access
# Defining Function for Requesting Access to link/Establishing Connection
def establish_Connection(link):
    try:
        # Connecting to Website
        r = requests.get(link)
        # Create a BeautifulSoup object and parse the HTML content
        # lxml is capable of parsing both HTML and XML Content
        soup = BeautifulSoup(r.content, 'lxml')
        # Returning Soup object to use it later
        return soup

    except:
        st.write(f"Connection to {link} cannot be established. Try with another Website")


# Scraping Text data from Website and rendering in a text file
def save_to_file(text, fname):
    if text is not None:
        st.download_button(
            label="Download Text File",
            data=text,
            file_name=fname,
            key="download_button",
        )
    else:
        st.write("Website has No Data!!")


# Function for Printing Data Scraped
def button_Print(text, statement):
    if text is not None:
        # Button for user to see data scraped without downloading
        # Create a button, that when clicked, shows a text
        if st.button(statement):
            st.write(text)


# Function for Link Checking
def link_Check(link):
    # For Image Link
    if link.endswith('jpeg') or link.endswith('jpg') or link.endswith('png') or link.endswith('svg') or link.endswith('webp'):
        st.write("This is an Image File.")
        return "img"

    # For Normal Link
    else:
        return 1


# Defining Functions of Web Scraping

# Function 1
# Getting Embedded Links from a Website
def embedded_links(link):
    try:
        if link_Check(link) == 1:
            # Establishing Connection
            soup = establish_Connection(link)

            # Find all the links on the webpage
            links = soup.find_all('a')

            if links is not None:
                # To Store Embedded link
                embed_link = []

                # Iterating through the links
                for link in links:
                    # Creating an object and storing links
                    href = link.get('href')

                    # To ensure we are scraping the link
                    if href is not None and not href.startswith("#"):
                        # Writing links to text file
                        embed_link.append(href)

                # Option to download the text file
                if embed_link is not None and embed_link != []:
                    if utility == 'Embedded Links':
                        fname = domain_name.capitalize() + "_Embedded_links_Website.txt"
                        save_to_file('\n'.join(embed_link), fname)

                        # Button for the user to see data scraped without downloading
                        # Create a button, that when clicked, shows text
                        button_Print('\n'.join(embed_link), "See Embedded Links")
                    else:
                        return embed_link

                else:
                    if utility == 'Embedded Links':
                        st.write("Website Has No Embedded Links!!")
                    return ""
            else:
                if utility == 'Embedded Links':
                    st.write("Website Has No Embedded Links!!")

    except:
        st.write("Website Has No Embedded Links!!")


# Adding Variables for Visited Links so that we do not visit them again while scraping
visited_links = []


# Function 2
# Getting Main Website Text Data
def main_website_text_Data(link):
    global visited_links

    try:
        if link_Check(link) == 1:
            if link not in visited_links:
                soup = establish_Connection(link)

                # Extract all the text from the webpage
                text = soup.get_text()

                # Option to download the text file
                if text is not None:
                    if utility == 'Main Website Text Data':
                        fname = domain_name.capitalize() + "_Main_Website_Data.txt"
                        save_to_file(text, fname)

                        button_Print(text, "See Scraped Data")
                    else:
                        return text

                elif utility == 'Main Website Text Data':
                    st.write("Website Has No Data!!")
                    return ""

                else:
                    return ""

                visited_links.append(link)
            else:
                return ""

    except:
        visited_links.append(link)
        if utility == 'Main Website Text Data':
            st.write("Website does not have any Text Data!!")
        return ""


# Function 3
# Function for Getting Main Website Data along with Embedded Links Data
def main_website_text_embedded_link_text_Data(link):
    global visited_links
    web_text = []

    try:
        if link_Check(link) == 1:
            if link not in visited_links:
                # Adding Main website data
                web_text += main_website_text_Data(link)

                # Here we will directly use our functions instead of rewriting codes
                link = embedded_links(link)

                if link is not None:
                    for l in link:
                        web_text.append(main_website_text_Data(l))

                if web_text is not None and web_text != [""]:
                    if utility == 'Main Website Text Data along with Embedded Links Text Data':
                        fname = domain_name.capitalize() + "_Main_Website_Text_Data_Embedded_Links_Text_Data.txt"
                        save_to_file('\n'.join(web_text), fname)

                        # Button for the user to see data scraped without downloading
                        # Create a button that, when clicked, shows text
                        button_Print('\n'.join(web_text), "See Scraped Data")
                    else:
                        return web_text
                else:
                    st.write("Website has no Data!!")
                    return ""
            else:
                return ""

    except:
        visited_links.append(link)
        return ""


# Function 4
# Function for Getting Complete Website Data along with Embedded Links Data
# This also Fetches Data of Links embedded within the embedded links
def complete_text_data(link):
    try:
        if link_Check(link) == 1:
            complete_text = []

            main_website_text_Data(link)
            visited_links.append(link)

            links = embedded_links(link)

            if links is not None:
                for l in links:
                    complete_text.append(main_website_text_embedded_link_text_Data(l))

            if complete_text is not None:
                if utility == 'Complete Website Text Data':
                    fname = domain_name.capitalize() + "_Complete_Website_Text_Data.txt"
                    save_to_file('\n'.join(complete_text), fname)
                    button_Print('\n'.join(complete_text), "See Scraped Data")
                else:
                    return ""

            else:
                st.write("Website has no Text Data!!")
                return ""

    except:
        st.write("An error occurred or the website has no data!!")
        return ""


# Function for downloading Image
def download_Image(link, name, directory):
    try:
        response = requests.get(link)
        image_path = os.path.join(directory, name + ".jpg")
        with open(image_path, 'wb') as f:
            f.write(response.content)
    except:
        pass

# Function to create and download a ZIP file
def create_zip(directory, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(directory):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))
    zipf.close()

# Button to Download Zip File which contains Images Downloaded
def download_button_Image():
    try:
        with open('downloaded_images.zip', 'rb') as f:
            st.download_button('Download ZIP', f,
                               file_name=domain_name.capitalize() + '_Zip_File_Image.zip',
                               mime='application/zip')
    except:
        st.write("Website has No Image Files.")

# Function to save image URLs and paths to Excel
def save_images_to_excel(image_data, excel_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Images"
    
    # Add headers
    sheet.append(["Image Name", "Image URL", "Image Path"])

    for data in image_data:
        sheet.append(data)

    # Save the workbook
    workbook.save(excel_path)

# Function 5
# Function for Getting Main Website Image Data along with Embedded Links Image Data
def main_download_Image_Files(link):
    try:
        soup = establish_Connection(link)

        if soup is not None:
            # Find all the image tags on the webpage
            image_tags = soup.find_all('img')

            # To store image links
            image_links = []
            image_data = []

            if image_tags is not None:
                # Iterating through the image tags
                for img in image_tags:
                    # Creating an object and storing image links
                    src = img.get('src')

                    # Ensure the link is valid
                    if src is not None and not src.startswith("#"):
                        # Complete the URL if it is relative
                        if not src.startswith('http'):
                            src = "https://www.pmo.gov.sg" + src
                        image_links.append(src)

                if image_links is not None and image_links != []:
                    directory = 'downloaded_images'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    for img_link in image_links:
                        name = img_link.split('/')[-1].replace(" ", "_").split('.')[0]  # Extract name without extension
                        img_link = img_link.replace(' ', '%20')
                        download_Image(img_link, name, directory)
                        image_path = os.path.join(directory, name + ".jpg")
                        image_data.append([name, img_link, image_path])
                    zip_name = 'downloaded_images.zip'
                    create_zip(directory, zip_name)
                    download_button_Image()
                    save_images_to_excel(image_data, "downloaded_images.xlsx")
    except:
        st.write("An Error Occurred or Website has no Image Files.")


# Function 6
# Function for Downloading Complete Website Image Data along with Embedded Links Data
# This also Fetches Image Data of Links embedded within the embedded links
def complete_download_Image_Files(link):
    try:
        global visited_links

        link_type = link_Check(link)

        if link_type == "img" and link not in visited_links:
            name = link.split('/')[-1].replace(" ", "_").split('.')[0]  # Extract name without extension
            link = link.replace(' ', '%20')
            download_Image(link, name, 'downloaded_images')
            image_data.append([name, link, os.path.join('downloaded_images', name + ".jpg")])

        elif link not in visited_links and not link_type == "img":
            soup = establish_Connection(link)

            if soup is not None:
                # Find all the links on the webpage
                links = soup.find_all('img')

                if links is not None:
                    # To Store Embedded link
                    embed_link = []

                    # Iterating through the links
                    for link in links:
                        # Creating an object and storing links
                        src = link.get('src')

                        # To ensure we are scraping the link
                        if src is not None and not src.startswith("#"):
                            # Writing links to text file
                            embed_link.append(src)

                if embed_link is not None and embed_link != [""]:
                    directory = 'downloaded_images'
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    for l in embed_link:
                        if link_Check(l) == "img":
                            name = l.split('/')[-1].replace(" ", "_").split('.')[0]  # Extract name without extension
                            l = l.replace(' ', '%20')
                            download_Image(l, name, directory)
                            image_data.append([name, l, os.path.join(directory, name + ".jpg")])
                        else:
                            download_Image_Files(l)
                    zip_name = 'downloaded_images.zip'
                    create_zip(directory, zip_name)
                    download_button_Image()
                    save_images_to_excel(image_data, "downloaded_images.xlsx")
        else:
            pass
    except:
        st.write("An Error Occurred or Website has No Image Files.")


# Function to remove files after download button is clicked
def remove_files(fname):
    try:
        os.remove(fname)
    except:
        pass


# Main Function for Code
if __name__ == "__main__":

    # First argument takes the title of the Selection Box
    # Second argument takes options
    utility = st.selectbox("Utility: ",
                           ['Embedded Links', 'Main Website Text Data',
                            'Main Website Text Data along with Embedded Links Text Data',
                            'Complete Website Text Data',
                            'Download Image Files From Main Website', 'Download All Image Files From Website'])

    # Selecting Function according to utility
    if utility == 'Embedded Links':
        embedded_links(link)

    elif utility == 'Main Website Text Data':
        main_website_text_Data(link)

    elif utility == 'Complete Website Text Data':
        complete_text_data(link)

    elif utility == 'Main Website Text Data along with Embedded Links Text Data':
        main_website_text_embedded_link_text_Data(link)

    elif utility == 'Download Image Files From Main Website':
        main_download_Image_Files(link)
        remove_files('downloaded_images.zip')

    else:
        complete_download_Image_Files(link)
        remove_files('downloaded_images.zip')

    # For Closing Button
    # Function to handle app closure and file removal
    # Check a condition to close the app
    try:
        if st.button("Close App"):
            st.experimental_clear_cache()
            # Close the app
            st.stop()
    except:
        pass
