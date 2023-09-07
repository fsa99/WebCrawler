import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import threading
import concurrent.futures

class ImageDownloader:
    def __init__(self, download_directory):
        self.download_directory = download_directory

    def download_image(self, url, filename):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(os.path.join(self.download_directory, filename), 'wb') as file:
                file.write(response.content)
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False

class WebPageParser:
    def __init__(self, url, download_directory):
        self.url = url
        self.download_directory = download_directory
        self.image_downloader = ImageDownloader(download_directory)

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
            print(f"Failed to parse image links: {e}")
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
                        future = executor.submit(self.download_images, image_url, width, height)
                        futures.append(future)
                except Exception as e:
                    print(f"Failed to parse_Downloade_links: {e}")
                    return []

            # 等待所有下载任务完成
            concurrent.futures.wait(futures)

    def download_images(self, image_url, width, height):
        try:
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
                print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Failed to download image {image_url}: {e}")


def get_total_pages(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
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
        else:
            return 0
    else:
        return 0

def download_images_from_multiple_pages(base_url, download_directory, total_pages):
    for page in range(1, total_pages + 1):
        url = f"{base_url}&page={page}"
        parser = WebPageParser(url, download_directory)
        image_links = parser.parse_image_links()
        parser.parse_Downloade_links(image_links)

def main():
    base_url = 'https://wallhaven.cc/user/ThorRagnarok/uploads'
    download_directory = 'downloaded_images'
    total_pages = get_total_pages(base_url)
    if total_pages > 0:
        download_images_from_multiple_pages(base_url, download_directory, total_pages)
    else:
        print("No pages to download.")

if __name__ == "__main__":
    main()
