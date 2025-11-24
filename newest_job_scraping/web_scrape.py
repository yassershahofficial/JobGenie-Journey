from selenium import webdriver #Mandatory
from selenium.webdriver.chrome.options import Options #options for running selenium in background
from selenium.webdriver.chrome.service import Service #Mandatory
from webdriver_manager.chrome import ChromeDriverManager#Mandatory
import pandas as pd #labeled table for data analysis
import os
import sys

def get_app_path():
    if getattr(sys,'frozen',False):
        return os.path.dirname(sys.executable) #use this for executable mode: pyinstaller exe
    else:
        return os.path.dirname(os.path.abspath(__file__)) #use this for testing before executable
    
def find_any_element(element, xpaths):
    for xpath in xpaths:
        elements = element.find_elements(by="xpath", value=xpath)
        if elements:
            return elements[0]
    return None

#path
app_path = get_app_path()
output_path = os.path.join(app_path, 'output')

#for chrome driver setup
website = "https://my.jobstreet.com/jobs"

#headless mode - running without display
options = Options()
# options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(website)

jobs_links = driver.find_elements(by="xpath", value='//article')

dict_jobs_links = []

for num, job_link in enumerate(jobs_links):
    main = find_any_element(job_link, ['./div/a'])
    if main:
        link = main.get_attribute("href")
        dict_jobs_links.append({'no':num+1, 'link':link})

df_jobs_links = pd.DataFrame(dict_articles)

if not os.path.exists(output_path):
    os.makedirs(output_path)

df_jobs_links.to_csv(os.path.join(output_path,'all_articles.csv'), index=False)
print("complete extraction")

#input("Press Enter Key to close the browser...")
driver.quit()