from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import csv, re, time, os, xlrd

def convert_str_to_number(x):
    """Magical method to convert K to 1000s """
    total_stars = 0
    num_map = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    if x.isdigit():
        total_stars = int(x)
    elif (x == "Share"):
        total_stars = 0
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

def extract_hashtags(text):
    """Wonderful method to seamlessly extract hashtags"""
    hashtag_list = []
    for word in text.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    return hashtag_list

def configure():
    """Configure selenium webdriver"""
    fp = webdriver.FirefoxProfile()
    fp.set_preference('browser.download.manager.showWhenStarting', False)
    fp.set_preference('browser.helperApps.neverAsk.openFile', 'video/mp4')
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk', 'video/mp4')
    fp.set_preference('browser.helperApps.alwaysAsk.force', False)
    fp.set_preference('browser.download.manager.alertOnEXEOpen', False)
    fp.set_preference('browser.download.manager.focusWhenStarting', False)
    fp.set_preference('browser.download.manager.useWindow', False)
    fp.set_preference('browser.download.manager.showAlertOnComplete', False)
    fp.set_preference('browser.download.manager.closeWhenDone', False)
    GECKODRIVER_PATH = '/usr/local/bin/geckodriver'
    WINDOW_SIZE = "1920,1080"
    firefox_options = Options()
    firefox_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--incognito")
    driver = webdriver.Firefox(fp, executable_path = GECKODRIVER_PATH, options = firefox_options)
    return (fp, driver, firefox_options)

def get_main_url_list(driver, urls):
    """Returns main user profile url"""
    main_profile_urls = []
    for url in urls:
        print(url)
        try:
            driver.get(url)
            user_profile = driver.find_element_by_xpath(
                '//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[1]/a[2]')
            url = user_profile.get_attribute('href')
            main_profile_urls.append(url)
        except NoSuchElementException:
            print("Video currently unavailable")
    return main_profile_urls

def list_user_metadata(driver, user_tiktok_dict):
    """Returns metadata specific to a video"""
    current_profile_tiktok_list = []
    tiktok_user_id = list(user_tiktok_dict.keys())[0]
    user_videos_urls = list(user_tiktok_dict.values())[0]
    print(f"\nScraping Metadata for Tiktok User: {tiktok_user_id}...\n")
    for url in user_videos_urls:
        vid_id = extract_video_id(url)
        print(f"Parsing URL: {url}")
        driver.get(url)
        likes_xpath = driver.find_element_by_xpath(
            '//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[4]/div[2]/div[1]/strong')
        likes = convert_str_to_number(likes_xpath.text)
        comments_xpath = driver.find_element_by_xpath(
            '//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[4]/div[2]/div[2]/strong')
        comments = convert_str_to_number(comments_xpath.text)
        shares_xpath = driver.find_element_by_xpath(
            '//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[4]/div[2]/div[3]/strong')
        print(f"Shares: {shares_xpath.text}")
        shares = convert_str_to_number(shares_xpath.text)
        print(f"URL: {url}\nLikes: {likes}\nComments: {comments}\nShares: {shares}\n")
        caption_xpath = driver.find_element_by_xpath(
            '//*[@id="main"]/div[2]/div[2]/div/div/main/div/div[1]/span[1]/div/div[1]/div[2]')
        hashtag_list = extract_hashtags(caption_xpath.text)
        print(f"URL: {url}\nLikes: {likes}\nComments: {comments}\nShares: {shares}\nHashTags: {hashtag_list}")
        tiktok_current_user_dict = {'tiktok_user_id': tiktok_user_id, 'video_id': vid_id, 'likes': likes, 'comments': comments, 'shares': shares, 'hashtags': hashtag_list}
        print(f"TikTok Video: {tiktok_current_user_dict}")
        current_profile_tiktok_list.append(tiktok_current_user_dict)
        
    return current_profile_tiktok_list

def list_user_video_urls(driver, url):
    """Returns a list of video ids for specified tiktok user id"""
    driver.get(url)
    videos_xpath_element = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/main/div[2]/div[1]')
    html_inside = videos_xpath_element.get_attribute('innerHTML')
    soup = BeautifulSoup(html_inside, 'html.parser')
    user_vid_list = []
    for link in soup.findAll('a'):
        user_vid_list.append(link.get('href'))
    return user_vid_list

def download_video(driver, tiktok_video_url):
    """Downloads specified video id to disk"""
    driver.get("https://musicallydown.com/?ref=more")
    search_field = driver.find_element_by_xpath('//*[@id="link_url"]')
    search_field.send_keys(tiktok_video_url)
    time.sleep(1)
    search_field.send_keys(Keys.ENTER)
    time.sleep(1)
    download_button = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/a[1]')
    download_button.click()
    
def parse_excel(filepath):
    """Reads tiktok campaign videos from spreadsheet and returns"""
    workbook = xlrd.open_workbook(filepath)
    worksheet = workbook.sheet_by_index(0)
    first_row = []
    for col in range(worksheet.ncols - 1):
        first_row.append(worksheet.cell_value(0, col))
    data = []
    for row in range(1, worksheet.nrows):
        col = 3
        data.append(worksheet.cell_value(row, col))
    return (data)

def extract_tiktok_userid(first_user_video_url):
    """Extracts and returns userid from first user video"""
    start = first_user_video_url.find('@')
    end = first_user_video_url.find('/', start)
    tiktok_user_id = first_user_video_url[start:end]
    return tiktok_user_id

def extract_video_id(user_vid):
    """Extracts and returns unique video id for each user video url"""
    start = user_vid.find('o/') + 2
    end = len(user_vid)
    vid_id = user_vid[start:end]
    return vid_id

def dump_videos(fp, driver, user_tiktok_dict, firefox_options):
    """Takes userid and creates subdirectories for each video_id"""
    user_identifier = list(user_tiktok_dict.keys())[0]
    print(f"Processing Tiktok Profile: {user_identifier}")
    user_videos_urls = list(user_tiktok_dict.values())[0]
    parent_dir = os.getcwd()
    directory = user_identifier
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    os.chdir(path)
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--incognito")
    fp.set_preference('browser.download.folderList', 2)
    fp.set_preference('browser.download.dir', path)
    driver = webdriver.Firefox(fp, options = firefox_options)
    for video in user_videos_urls:
        print(f"Downloading Video: {video}")
        download_video(driver, video)
    os.chdir(parent_dir)

if __name__ == "__main__":
    master_tiktok_list = []
    filepath = 'source.xlsx'
    total_url_list = parse_excel(filepath)
    sample_urls = total_url_list[0:8]
    fp, driver, firefox_options = configure()
    profile_url_list = get_main_url_list(driver, sample_urls)
    for profile_url in profile_url_list:
        user_vid_list = list_user_video_urls(driver, profile_url)
        first_user_video_url = user_vid_list[0]
        tiktok_user_id = extract_tiktok_userid(first_user_video_url)
        user_tiktok_dict = {tiktok_user_id: user_vid_list}
        #dump_videos(fp, driver, user_tiktok_dict, firefox_options)
        current_profile_tiktok_list = list_user_metadata(driver, user_tiktok_dict)
        master_tiktok_list.append(current_profile_tiktok_list)
        
        
        
        
    
