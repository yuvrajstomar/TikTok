from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re, time, os

def convert_str_to_number(x):
    '''magical method to convert K to 1000s '''
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

def configure():
    '''configure selenium webdriver'''
    #https://musicallydown.com/?ref=more
    #https://snaptik.app/

    # CHROMEDRIVER_PATH = '/home/kraken/Desktop/chromedriver_linux64/chromedriver'
    # CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
    GECKODRIVER_PATH = '/usr/local/bin/geckodriver'
    WINDOW_SIZE = "1920,1080"

    firefox_options = Options()
    firefox_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--incognito")
    driver = webdriver.Firefox(executable_path = GECKODRIVER_PATH, options = firefox_options)
    return driver

def get_url(driver):
    '''Get user profile url'''
    driver.get("https://vm.tiktok.com/t8ULrA/")
    time.sleep(2)
    user_profile = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[1]/a[2]')
    url = user_profile.get_attribute('href')
    return url

def list_user_metadata(driver, urls):
    '''returns metadata specific to a video'''
    
    print(f"\nScraping Metadata...\n")
    
    for url in urls:
        print(f"Parsing URL: {url}")
        driver.get(url)

        likes_xpath = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[4]/div[2]/div[1]/strong')
        likes = convert_str_to_number(likes_xpath.text)

        comments_xpath = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[4]/div[2]/div[2]/strong')
        comments = convert_str_to_number(comments_xpath.text)

        shares_xpath = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[4]/div[2]/div[3]/strong')
        shares = convert_str_to_number(shares_xpath.text)
        print(f"URL: {url}\nLikes: {likes}\nComments: {comments}\nShares: {shares}\n")

def list_user_video_urls(driver, url):
    '''returns a list of video ids for specified tiktok user id'''
    driver.get(url)
    videos_xpath_element = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/main/div[2]/div[1]')
    html_inside = videos_xpath_element.get_attribute('innerHTML')
    soup = BeautifulSoup(html_inside, 'html.parser')
    user_vid_list = []
    for link in soup.findAll('a'):
        user_vid_list.append(link.get('href'))
    return user_vid_list

def download_video(driver, tiktok_video_id):
    '''downloads specified video id to disk'''
    driver.get("https://musicallydown.com/?ref=more")
    search_field = driver.find_element_by_xpath('//*[@id="link_url"]')
    search_field.send_keys(tiktok_video_id)
    search_field.send_keys(Keys.ENTER)
    download_button = driver.find_element_by_xpath('//*[@id="welcome"]/div/div[2]/div[2]/a[1]')
    download_button.click()

if __name__ == "__main__":
    driver = configure()
    url = get_url(driver)
    user_vid_list = list_user_video_urls(driver, url)
    # print(user_vid_list)
    # user_vid_list = user_vid_list[:]
    # for video in user_vid_list:
    #     download_video(driver, video)
    #     time.sleep(3)

    print(user_vid_list)
    list_user_metadata(driver, user_vid_list)

    # for video in user_vid_list[0]
    #     print(video)

'''
<a href="https://www.tiktok.com/@jugglinjosh/video/6898091882652486918" class="jsx-3109748587 video-feed-item-wrapper"><span class="lazyload-wrapper"><div class="jsx-828470630 image-card" style="border-radius: 0px; background-image: url(&quot;https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/022bd1bcb0c74a2bbeb1f1117cdb0839?x-expires=1606467600&amp;x-signature=EBWO4iKRmSskdqukz%2FC70njrPbI%3D&quot;);"><div class="jsx-1778455663 video-card default"><div class="jsx-1778455663 video-card-mask"><div class="jsx-1036923518 card-footer normal no-avatar"><div class="jsx-1036923518 video-bottom-info"><svg class="like-icon" width="18" height="18" viewBox="0 0 48 48" fill="#fff" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M16 10.554V37.4459L38.1463 24L16 10.554ZM12 8.77702C12 6.43812 14.5577 4.99881 16.5569 6.21266L41.6301 21.4356C43.5542 22.6038 43.5542 25.3962 41.6301 26.5644L16.5569 41.7873C14.5577 43.0012 12 41.5619 12 39.223V8.77702Z"></path></svg><strong class="jsx-1036923518 video-count">69.2K</strong></div></div></div></div></div></span></a>
'''
