import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import concurrent.futures
import time
import logging

# 创建一个日志记录器
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

# 创建一个文件处理器，将日志写入到文件中
file_handler = logging.FileHandler("log.txt")
file_handler.setLevel(logging.INFO)

# 创建一个格式化器，定义日志的格式
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器中
logger.addHandler(file_handler)

# 图片下载器类
class ImageDownloader:
    def __init__(self, download_directory):
        self.download_directory = download_directory

    def check_file_exists(self, directory, filename):
        # 获取目录下的所有文件和子目录
        for root, dirs, files in os.walk(directory):
            if filename in files:
                return True  # 文件存在
        return False  # 文件不存在
    
    # 下载图片
    def download_images(self, image_url, width, height):
        try:
            img_exist = self.check_file_exists(self.download_directory, image_url.split('/')[-1])
            if not img_exist:
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = response.content
                filename = os.path.basename(image_url)
                if width > height:
                    folder = 'PC_images'
                else:
                    folder = 'iphone_images'
                folder_path = os.path.join(self.download_directory, folder)
                os.makedirs(folder_path, exist_ok=True)
                with open(os.path.join(folder_path, filename), 'wb') as f:
                    f.write(image_data)
                    message_info = f"Downloaded {filename}"
                    logger.info(message_info)
                    print(message_info)
            else:
                message_info = f"{image_url.split('/')[-1]} 已经下载过了"
                logger.info(message_info)
                print(message_info)
        except Exception as e:
            message_error = f"Failed to download image {image_url}: {e}"
            logger.error(message_error)
            print(message_error)


class WebPageParser:
    def __init__(self, url, downloader):
        self.url = url
        self.download_directory = downloader.download_directory
        self.image_downloader = downloader.download_images

    def parse_image_links(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            image_links = []
            for a_tag in soup.find_all('a', class_='preview'):
                image_links.append(a_tag['href'])
            return image_links
        except Exception as e:
            message_error = f"Failed to parse image links: {e}"
            logger.error(message_error)
            print(message_error)
            return []

    def parse_Downloade_links(self, image_links):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # 使用多线程下载
            futures = []
            for image_link in image_links:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
                    response = requests.get(image_link, headers=headers)
                    response.raise_for_status()
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')
                    image_element = soup.find('img', {'id': 'wallpaper'})
                    if image_element:
                        image_url = image_element.get('src')
                        width = int(image_element.get('data-wallpaper-width', 0))
                        height = int(image_element.get('data-wallpaper-height', 0))
                        future = executor.submit(self.image_downloader, image_url, width, height)
                        futures.append(future)
                except Exception as e:
                    message_error = f"Failed to parse_Downloade_links: {e}"
                    logger.error(message_error)
                    print(message_error)
                    return []

            # 等待所有下载任务完成
            concurrent.futures.wait(futures)

def get_total_pages(url):
    """
    获取总页数

    Args:
        url (str): 页面的URL

    Returns:
        int: 总页数,如果无法获取则返回0
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # 找到包含页码信息的元素，提取总页数
        pagination_element = soup.find('ul', class_='pagination')
        if pagination_element:
            data_pagination = pagination_element.get('data-pagination')
            if data_pagination:
                total_pages = int(data_pagination.split(':')[1].split(',')[0])
                return total_pages
    except requests.exceptions.RequestException as e:
        message_error = f"Error occurred while getting total pages: {e}"
        logger.error(message_error)
        print(message_error)
    return 0

def download_images_from_multiple_pages(base_url, downloader, total_pages):
    """
    从多个页面下载图片

    Args:
        base_url (str): 页面的基本URL
        downloader (Downloader): 图片下载器对象
        total_pages (int): 总页数

    Returns:
        None
    """
    for page in range(1, total_pages + 1):
        url = f"{base_url}?page={page}"
        parser = WebPageParser(url, downloader)
        try:
            image_links = parser.parse_image_links()
            parser.parse_Downloade_links(image_links)
        except ConnectionResetError as e:
            message_error = f"Error occurred while parsing and downloading images from url {url}: {e}"
            logger.error(message_error)
            print(message_error)
        time.sleep(20)

def main():
    base_url = 'https://wallhaven.cc/user/ThorRagnarok/uploads'
    downloader = ImageDownloader('downloaded_images')
    total_pages = get_total_pages(base_url)
    if total_pages > 0:
        download_images_from_multiple_pages(base_url, downloader, total_pages)
    else:
        message_info = "No pages to download."
        logger.info(message_info)
        print(message_info)

if __name__ == "__main__":
    main()
