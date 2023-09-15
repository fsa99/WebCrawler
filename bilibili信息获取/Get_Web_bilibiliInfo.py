import requests
from bs4 import BeautifulSoup
import json
import os
import re 
from urllib.parse import urljoin
from urllib.parse import urlparse

def scrape_bilibili_info(url):
    try:
        # 发送请求并获取网页内容
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}  # 请替换为您的用户代理
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html, 'html.parser')

        # # 创建一个目录来保存下载的图片
        # save_directory = 'downloaded_images'
        # os.makedirs(save_directory, exist_ok=True)

        # # 查找所有的img标签
        # img_tags = soup.find_all('img')

        # # 遍历每个img标签，获取图片URL并下载
        # for img_tag in img_tags:
        #     # 获取图片的 URL
        #     img_url = img_tag.get('src')
        #     # 如果 img_url 以 'data:' 开头，说明是 base64 编码的图片，跳过
        #     if img_url.startswith('data:'):
        #         continue
        #     # 合并图片的 URL
        #     img_url = urljoin(url, img_url)
        #     # 发送请求并保存图片
        #     img_response = requests.get(img_url)
        #     # 检查响应状态码，如果不是 200，则跳过
        #     if img_response.status_code != 200:
        #         continue
        #     # 提取图片文件名
        #     img_filename = os.path.basename(img_url)

        #     # 保存图片到下载目录
        #     with open(os.path.join(save_directory, img_filename), 'wb') as img_file:
        #         img_file.write(img_response.content)

        playinfo_script_tag = soup.find('script', text=re.compile(r'window\.__playinfo__\s*=\s*{.*?}'))
        script_tag = soup.find('script', text=re.compile(r'window\.__INITIAL_STATE__\s*=\s*{.*?};'))
        if script_tag:
            # 从 <script> 标签的文本中提取 JSON 数据
            script_text = script_tag.text
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', script_text, re.DOTALL)
            
            if match:
                # 提取 JSON 数据部分
                json_data = match.group(1)
                # 解析 JSON 数据为 Python 字典
                initial_state = json.loads(json_data)
                # 提取 "舞者"、"UP主" 和 "参演" 的信息
                staffDatas = initial_state.get("staffData", [])
                videoDatas = initial_state.get("videoData", [])
                dancers = []
                up_main = []
                performers = []
                for member in staffDatas:
                    title = member.get("title", "")
                    name = member.get("name", "")
                    if title == "舞者":
                        dancers.append(name)
                    elif title == "UP主":
                        up_main.append(name)
                    elif title == "参演":
                        performers.append(name)
                des = videoDatas.get("desc")  # 从字典中获取描述信息
                if des is not None and des != "":
                    desc = des  # 如果描述信息不为空，添加到 desc 列表中

        else:
            print("未找到包含 window.__INITIAL_STATE__ 的 <script> 标签")

        if playinfo_script_tag:
            # 从 <script> 标签的文本中提取 JSON 数据
            playinfo_script_text = playinfo_script_tag.text
            playinfo_match = re.search(r'window\.__playinfo__\s*=\s*({.*?})', playinfo_script_text, re.DOTALL)
            
            if playinfo_match:
                # 提取 JSON 数据部分
                playinfo_data = parse_json_with_error_handling(playinfo_match.group(1))
                # 获取 timelength
                timelength = playinfo_data["data"]["timelength"]
                video_format = playinfo_data["data"]["accept_format"]
                highest_resolution = playinfo_data["data"]["accept_description"]
            else:
                timelength = None
                video_format = None
                highest_resolution = None
        else:
            timelength = None
            video_format = None
            highest_resolution = None
        # 0、查找 meta 标签中的字符编码方式
        meta_tag = soup.find('meta')
        charset = meta_tag.get('charset')
        # 1、获取 <title> 标签中的值-视频的名字
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.strip()
        else:
            title = "Title not found"

        # 2、查找包含 itemprop="author" 的 <meta> 元素-UP主名字
        author_meta = soup.find('meta', {'itemprop': 'author'})
        if author_meta:
            author = author_meta.get('content')
        else:
            author = "Author not found"
        # 3、查找 JSON 数据中的 "accept_description" 列表-最高清晰度、视频格式
        # json_data = soup.find('script', type='application/ld+json')
        # if json_data:
        #     json_text = json_data.text
        #     json_dict = json.loads(json_text)
        #     accept_description = json_dict.get("accept_description", [])
        #     highest_resolution = accept_description[0] if accept_description else "Unknown"
        #     video_format = json_dict.get("data", {}).get("format", "Unknown")
        # else:
        #     highest_resolution = "Unknown"
        #     video_format = "Unknown"

        # 4、获取所有的 <a> 链接的 href 属性
        # links = soup.find_all('a')
        # hrefs = [link.get('href') for link in links]

        video_info = Bilibili_Video_Info(
            url=url,
            video_title=title,
            video_author=author,
            video_highest_resolution=highest_resolution,
            video_timelength=timelength,
            video_format=video_format,
            video_desc=desc,
            html_charset=charset,
            up_main_name=up_main,
            up_dancers=dancers,
            up_performers=performers
        )
        return video_info
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


class Bilibili_Video_Info:
    def __init__(self, url=None, video_title=None, video_author=None, video_highest_resolution=None, video_timelength=None, video_format=None, 
                 video_desc=None, html_charset=None, up_main_name=None, up_dancers=None, up_performers=None):
        self.url = url
        self.video_title = video_title
        self.video_author = video_author
        self.video_highest_resolution = video_highest_resolution
        self.video_timelength = video_timelength
        self.video_format = video_format
        self.video_desc = video_desc
        self.html_charset = html_charset
        self.up_main_name = up_main_name
        self.up_dancers = up_dancers
        self.up_performers = up_performers

    def to_json(self):
        # 将类属性转化为字典
        video_info_dict = {
            "url": self.url,
            "video_title": self.video_title,
            "video_author": self.video_author,
            "video_highest_resolution": self.video_highest_resolution,
            "video_format": self.video_format,
            "video_desc": self.video_desc,
            "html_charset": self.html_charset,
            "up_main_name": self.up_main_name,
            "up_dancers": self.up_dancers,
            "up_performers": self.up_performers
        }
        # 使用json.dumps将字典转化为JSON字符串
        return json.dumps(video_info_dict)


def parse_json_with_error_handling(json_data):
    result = None
    try:
        result = json.loads(json_data)
    except json.JSONDecodeError as e:
        # 如果解析出错，找到出错位置的索引并修复 JSON 数据
        error_index = e.pos
        corrected_json_data = json_data[:error_index] + json_data[error_index+1:]
        result = json.loads(corrected_json_data)
    return result


def milliseconds_to_time(milliseconds):
    milliseconds = milliseconds % 1000
    total_seconds = milliseconds // 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60

    time_format = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
    return time_format


# 定义一个函数来下载图片
def download_image(url, save_dir):
    response = requests.get(url)
    if response.status_code == 200:
        # 获取文件名
        filename = os.path.join(save_dir, os.path.basename(urlparse(url).path))
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"已下载图片: {url}")
    else:
        print(f"下载失败: {url}")

# 使用示例
if __name__ == "__main__":
    url = "https://www.bilibili.com/video/av317034760/?vd_source=7672ce71469c836046e24632cec55de9"
    result = scrape_bilibili_info(url)
    if 'error' in result:
        print("An error occurred:", result['error'])
    else:
        print("Title:", result['title'])
        print("Metas:", result['metas'])
        print("Hrefs:", result['hrefs'])
