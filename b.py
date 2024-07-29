# coding=utf-8
import requests
import threading
from hashlib import md5 as md5Encode
import time
from datetime import datetime

# ----固定变量区----
marketingId = "1816854086004391938"

# 任务数和线程数
tasks_num = 100  # 运行 100 次

# ----自定义变量区----
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3eF8xNDQ5MjYyMjQ0MDE3MTIzMzMxIiwiaWF0IjoxNzIyMjMxNTk4fQ.3cdudwO1YaS7SJXaaKVpnEBb197vsuQR0Vr-9RMragKTtkmO9dZzB8KrRxg7Ox_Neq5hfzL3ulPw2YDoaXGVQA"
round = "17:00"
secretword = "好一朵美丽的茉莉花"


headers = {
    "Access-Token": token,
    "Referer": "https://mxsa-h5.mxbc.net/",
    "Host": "mxsa.mxbc.net",
    "Origin": "https://mxsa-h5.mxbc.net",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.50(0x18003233) NetType/4G Language/zh_CN miniProgram/wx7696c66d2245d107",
    "Content-type": "application/json;charset=UTF-8",
}


def exchange():
    try:
        url = "https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm"
        param = f"marketingId={marketingId}&round={round}&s=2&secretword={secretword}c274bac6493544b89d9c4f9d8d542b84"
        m = md5Encode(param.encode("utf8"))
        sign = m.hexdigest()
        body = {
            "secretword": secretword,
            "sign": sign,
            "marketingId": marketingId,
            "round": round,
            "s": 2,
        }
        res = requests.post(
            url,
            headers=headers,
            json=body,
        )

        print(f"任务开始: {res.text}")

    except Exception as e:
        print(f"任务失败: {e}")




if __name__ == "__main__":
    try:
        cnt = 0
        round_time = datetime.strptime(round, "%H:%M").time()
        while True:
            # 获取当前时间并格式化为字符串
            current_time = datetime.now().time()
            if current_time >= round_time:
                print("到时间了", current_time)
                for _ in range(tasks_num):
                    exchange()
                    time.sleep(1)
                break
            else:
                if cnt % 600 == 0:
                    print("未到时间", current_time)
                cnt += 1
                time.sleep(0.1)  # 每 0.1 秒检查一次,不sleep会导致cpu占用过高
    except KeyboardInterrupt:
        print("手动停止-等待线程结束")
