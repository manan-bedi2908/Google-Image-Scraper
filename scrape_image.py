# Importing the necessary libraries
import os
import time
import requests
from selenium import webdriver

# Function to extract the images from the Google Images
def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 0.5):

    # Function to scroll till last
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # Custom Search URL
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # Get the url of the searched query on Google Images
    wd.get(search_url.format(q = query))

    image_urls = set()
    image_count = 0
    results = 0

    # Extract images until we reach number of images we want
    while image_count < max_links_to_fetch:

        scroll_to_end(wd)
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_of_results = len(thumbnail_results)

        print(f"Found: {number_of_results} search results. Extracting links from {results}:{number_of_results}")

        for img in thumbnail_results[results:number_of_results]:

            # Get all the photos and click on it one by one
            try:
                img.click()
                time.sleep(sleep_between_interactions)

            except Exception as e:
                continue

            # Extract the image url from the html image's tag src attribute
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for img in actual_images:
                if img.get_attribute('src') and 'http' in img.get_attribute('src'):
                    image_urls.add(img.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return

            # Load more images if needed
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        results = len(thumbnail_results)

    return image_urls


def save_images(folder_path:str,url:str, counter):

    # Get the content of the url (i.e. actual image)
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"Error - Could not download {url} - {e}")

    # Open the pic in write byte mode
    try:
        f = open(os.path.join(folder_path, 'pic' + "_" + str(counter) + ".jpg"), 'wb')
        f.write(image_content)
        f.close()
        print(f"Success - saved {url} - as {folder_path}")

    except Exception as e:
        print(f"Error occured - Could not save {url} - {e}")

# Function will go to google images and search the specified image and call fetch_images_urls to get the urls and save
def search_and_download(search_term: str, driver_path: str, target_path='./images', number_of_images=10):

    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    # If the path does not exist, it will create the directory
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Open Chrome as executable and call fetch_image_urls
    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_of_images, wd=wd, sleep_between_interactions=0.5)

    counter = 0

    # Save all the images in the directory inside the respective searched image folder
    for pic in res:
        save_images(target_folder, pic, counter)
        counter += 1



DRIVER_PATH = './chromedriver'      # Chrome Driver of My Version
search_term = input("Enter what you wish to download: ")
number_of_images = int(input("How many images do you want to download: "))

search_and_download(search_term=search_term, driver_path=DRIVER_PATH, number_of_images = number_of_images)