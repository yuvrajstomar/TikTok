from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re, time, os, xlrd

def convert_str_to_number(x):
    '''Magical method to convert K to 1000s '''
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

def extract_hashtags(text):
    '''Wonderful method to seamlessly extract hashtags'''
    hashtag_list = [] 
    for word in text.split(): 
        if word[0] == '#': 
            hashtag_list.append(word[1:]) 
    return hashtag_list

def configure():
    '''Configure selenium webdriver'''
    #https://musicallydown.com/?ref=more
    #https://snaptik.app/

    GECKODRIVER_PATH = '/usr/local/bin/geckodriver'
    WINDOW_SIZE = "1920,1080"

    firefox_options = Options()
    firefox_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    # firefox_options.add_argument("--headless")
    firefox_options.add_argument("--incognito")
    driver = webdriver.Firefox(executable_path = GECKODRIVER_PATH, options = firefox_options)
    return driver

def get_main_url_list(driver, urls):
    '''Returns main user profile url'''
    main_profile_urls = []
    for url in urls:
        driver.get(url)
        time.sleep(1)
        user_profile = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[1]/a[2]')
        url = user_profile.get_attribute('href')
        main_profile_urls.append(url)
    return main_profile_urls

def list_user_metadata(driver, urls):
    '''Returns metadata specific to a video'''
    
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

        caption_xpath = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[2]')
        hashtag_list = extract_hashtags(caption_xpath.text)

        print(f"URL: {url}\nLikes: {likes}\nComments: {comments}\nShares: {shares}\nHashTags: {hashtag_list}")
        

def list_user_video_urls(driver, url):
    '''Returns a list of video ids for specified tiktok user id'''
    driver.get(url)
    videos_xpath_element = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/main/div[2]/div[1]')
    html_inside = videos_xpath_element.get_attribute('innerHTML')
    soup = BeautifulSoup(html_inside, 'html.parser')
    user_vid_list = []
    for link in soup.findAll('a'):
        user_vid_list.append(link.get('href'))
    return user_vid_list

def download_video(driver, tiktok_video_url):
    '''Downloads specified video id to disk'''
    driver.get("https://musicallydown.com/?ref=more")
    search_field = driver.find_element_by_xpath('//*[@id="link_url"]')
    search_field.send_keys(tiktok_video_url)
    search_field.send_keys(Keys.ENTER)
    time.sleep(1)
    download_button = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/a[1]')
    download_button.click()

def parse_excel(filepath):
    '''Reads tiktok campaign videos from spreadsheet and returns'''
    workbook = xlrd.open_workbook(filepath)
    worksheet = workbook.sheet_by_index(0)
    first_row = []
    for col in range(worksheet.ncols - 1):
        first_row.append(worksheet.cell_value(0, col))
    data = []
    for row in range(1, worksheet.nrows):
        col = 3
        data.append(worksheet.cell_value(row, col))
    return(data)

def extract_tiktok_userid(first_user_video_url):
    '''Extracts and returns userid from first user video'''
    start = first_user_video_url.find('@')
    end = first_user_video_url.find('/', start)
    tiktok_user_id = first_user_video_url[start:end]
    return tiktok_user_id

def extract_unique_video_ids(user_vid_list):
    '''Extracts and returns unique video ids for each tiktok user'''
    video_ids = []
    for user_vid in user_vid_list:
        start = user_vid.find('o/') + 2
        end = len(user_vid)
        vid_id = user_vid[start:end]
        video_ids.append(vid_id)
    return video_ids

def dump_videos(driver, user_tiktok_dict):
    '''Takes userid and creates subdirectories for each videoid'''
    user_identifier = list(user_tiktok_dict.keys())[0]
    print(f"Processing Tiktok Profile: {user_identifier}")
    user_videos_urls = list(user_tiktok_dict.values())[0]
    parent_dir = os.getcwd()
    directory = user_identifier
    path = os.path.join(parent_dir, directory) 
    os.mkdir(path)
    os.chdir(path)
    for video in user_videos_urls:
        print(f"Downloading Video: {video}")
        download_video(driver, video)
        time.sleep(2)


if __name__ == "__main__":
    
    filepath = 'source.xlsx'
    total_url_list = parse_excel(filepath)
    sample_urls = total_url_list[0:1]
    
    driver = configure()
    profile_url_list = get_main_url_list(driver, sample_urls)
    
    for profile_url in profile_url_list:
        user_vid_list = list_user_video_urls(driver, profile_url)
        first_user_video_url = user_vid_list[0]
        tiktok_user_id = extract_tiktok_userid(first_user_video_url)
        user_tiktok_dict = {tiktok_user_id: user_vid_list}
        dump_videos(driver, user_tiktok_dict)
        # video_ids = extract_unique_video_ids(user_vid_list)

    
    # for video in user_vid_list:
    #     download_video(driver, video)
    #     time.sleep(3)

    # print(user_vid_list)
    # list_user_metadata(driver, user_vid_list)

    # for video in user_vid_list[0]
    #     print(video)