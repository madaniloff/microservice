import bs4
import requests
import io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import os
import time 
from curses.ascii import isdigit

first = 1
while True:
    time.sleep(2)
    #Get input from file
    f = open("input-text.txt", "r")
    with open("input-text.txt") as f:
        firstline = f.readline()
        if (firstline != ''):
            tempkey = firstline
        secondline = f.readline()
        if (firstline != '' and isdigit(secondline[0])):
            tempnumber = int(secondline) 
        thirdline = f.readline()
        tempdirectory = thirdline
        #Check if key and number have changed
        if (first == 0 and key != tempkey and number != tempnumber):
            key = tempkey
            number = tempnumber
            directory = tempdirectory
            input = 1
        elif (first == 1):
            key = tempkey
            number = tempnumber
            directory = tempdirectory
            input = 1
        else:
            wd.quit()

    #Path for the chrome web driver
    PATH = os.getcwd()
    PATH += "/chromedriver"
    #Prevent webdriver from displaying
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--remote-debugging-port=9222")
    service = Service(PATH)
    wd = webdriver.Chrome(service=service, options=options)

    def get_images(wd, delay, max_images):
        #Scroll down to the bottom of the google images page
        def scroll_down(wd):
            wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)

        #Google images url for the keyword
        url = "https://www.google.com/search?q="+ key +"&sxsrf=ALiCzsb73hGk4yTwU7ynoghs3hdLx_g2VA:1651547361456&source=lnms&tbm=isch&sa=X&ved=2ahUKEwi8uLyurcL3AhWACjQIHU9jAh8Q_AUoAXoECAIQAw&biw=1958&bih=1003&dpr=0.95"
        wd.get(url)

        #Ensure there are no duplicate urls
        image_urls = set()
        skips = 0

        while len(image_urls) + skips < max_images:
            scroll_down(wd)

            #Get all the images with a common class name
            thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")

            #Go through the images and try to click on them
            for img in thumbnails[len(image_urls) + skips: max_images]:
                try:
                    img.click()
                    time.sleep(delay)
                except:
                    continue

                #Get the source of the selected images
                images = wd.find_elements(By.CLASS_NAME, "n3VNCb")
                for image in images:
                    #If we encounter the same image
                    if image.get_attribute('src') in image_urls:
                        #If we have to skip an image, increment the max_images to get the 
                        #proper number of images
                        max_images += 1
                        skips += 1
                        break

                    #If the source for the image is valid, add it to image_urls
                    if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                        image_urls.add(image.get_attribute('src'))

            return image_urls

    #Function to download images
    def download_image(download_path, url, file_name):
        #Allows HTTP get request to url to get image content
        image_content = requests.get(url).content 
        #Save image as a bytesIO datatype
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = download_path + file_name
        #Save the image
        with open(file_path, "wb") as f: 
            #Save image as a JPEG or convert to JPEG
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(f, "JPEG")

    #Proceed if the input is valid
    if (input == 1):
        urls = get_images(wd, 1, number)
        for i, url in enumerate(urls):
            download_image(directory, url, (str(i)+'.jpg'))

        input = 0
        first = 0
        wd.quit()
