import requests
import json

class LoginManager:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        try:
            # 构建登录数据
            login_data = {
                "username": self.username,
                "password": self.password
            }

            # 设置请求头
            headers = {
                "Content-Type": "application/json;charset=UTF-8"
            }

            # 发送POST请求
            response = self.session.get(self.base_url, headers=headers)

            # 检查响应状态码
            if response.status_code == 200:
                # 登录成功，提取Authorization头部的值
                authorization = response.headers.get("Authorization")
                return authorization
            else:
                print(f"Failed to login. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Login error: {str(e)}")
            return None



def TP_ProcessReport_Data(_barcode):
    # 发送HTTP GET请求
    url = "http://10.3.15.148:8861/api/ProcessReport"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3VzZXJkYXRhIjoie1widXNlcl9pZFwiOjEsXCJjb21wYW55X2lkXCI6MSxcInN5c3RlbV9pZFwiOjAsXCJkZXBhcnRtZW50X2lkXCI6MixcImRlcGFydG1lbnRfbmFtZVwiOm51bGwsXCJ1c2VyX25hbWVcIjpcIueuoeeQhuWRmFwiLFwidXNlcl9waG9uZVwiOm51bGx9IiwiaHR0cDovL3NjaGVtYXMubWljcm9zb2Z0LmNvbS93cy8yMDA4LzA2L2lkZW50aXR5L2NsYWltcy9yb2xlIjoiW3tcInZhbHVlXCI6MSxcImxhYmVsXCI6XCJBRE1JTlwifV0iLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2dyb3Vwc2lkIjoiW3tcInZhbHVlXCI6MSxcImxhYmVsXCI6XCLlroHms6LkvJjlvrfmma5cIn1dIiwibmJmIjoxNjk0NjA4NjMyLCJleHAiOjE3MDAzNjg2MzIsImlzcyI6IlRQU3lzdGVtQXBpIiwiYXVkIjoiVFBTeXN0ZW1BcGkifQ.SsW1X8vS-Nmhiy4bjIHjZRkY-zTZJQ3G_kd21TNY9Ik"
    params = {
        "cx_id": 37,
        "barcode": _barcode,
        "page": 1,
        "size": 20
    }
    headers = {
    "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, params=params, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析JSON数据
        json_data = response.json()

        # 在这里，你可以处理JSON数据，例如访问其中的字段
        # 例如，访问JSON中的某个字段：
        # value = json_data["key"]

        # 输出整个JSON数据
        print(json.dumps(json_data, indent=4))
    else:
        print(f"请求失败，状态码：{response.status_code}")


if __name__ == "__main__":
    # 
    # login_url = 'http://10.3.15.148:8865/fonts/element-icons.535877f5.woff'  # 替换为实际登录页面的URL
    # username = 'admin'
    # password = 'tp1234'
    
    # login_manager = LoginManager(login_url, username, password)
    # authorization = login_manager.login()
    
    # if authorization:
    #     TP_ProcessReport_Data("P1523003-00-C:SAL523221000022")
    TP_ProcessReport_Data("P1523003-00-C:SAL523221000022")
