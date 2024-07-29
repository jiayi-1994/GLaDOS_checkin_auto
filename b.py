import requests
import time
import random
from datetime import datetime, timedelta
from hashlib import md5 as md5Encode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----固定变量区----
marketingId = '1816854086004391938'

# 任务数和线程数
tasks_num = 100  # 运行 100 次
threads_num = 5  # 最大线程数 5 个

# ----自定义变量区----
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3eF8xNDQ5MjYyMjQ0MDE3MTIzMzMxIiwiaWF0IjoxNzIyMjMxNTk4fQ.3cdudwO1YaS7SJXaaKVpnEBb197vsuQR0Vr-9RMragKTtkmO9dZzB8KrRxg7Ox_Neq5hfzL3ulPw2YDoaXGVQA'

# 预定义的 User-Agent 列表
user_agents = [
    # Android设备
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; ONEPLUS A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36',

    # iOS设备
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1'
]


def get_headers():
    return {
        'Access-Token': token,
        'Referer': 'https://mxsa-h5.mxbc.net/',
        'Host': 'mxsa.mxbc.net',
        'Origin': 'https://mxsa-h5.mxbc.net',
        'User-Agent': random.choice(user_agents),
        'Content-type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
    }


def exchange(secret_word, round):
    try:
        url = 'https://mxsa.mxbc.net/api/v1/h5/marketing/secretword/confirm'
        param = f'marketingId={marketingId}&round={round}&s=2&secretword={secret_word}c274bac6493544b89d9c4f9d8d542b84'
        m = md5Encode(param.encode("utf8"))
        sign = m.hexdigest()
        body = {
            "secretword": secret_word,
            "sign": sign,
            "marketingId": marketingId,
            "round": round,
            "s": 2
        }
        headers = get_headers()
        res = requests.post(url, headers=headers, json=body)
        response_text = res.text
        print(f'任务执行: {response_text}')

        if "阻断" in response_text or "安全威胁" in response_text:
            print("检测到访问被阻断，终止本时间段的访问")
            return False

        time.sleep(random.uniform(1, 3))
        return True
    except Exception as e:
        print(f'任务失败: {e}')
        return True


def get_secret_word():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    driver = webdriver.Chrome(options=options)
    driver.get("https://mxsa-h5.mxbc.net/#/flash-sale-words?needToken=2&marketingId=1816854086004391938")

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '本场口令：')]"))
        )
        keyword = element.text.split("本场口令：")[1].strip()
        print("口令:", keyword)
        return keyword
    except:
        print("未找到口令或加载超时")
        return None
    finally:
        driver.quit()


def threading_run(tasks, threads, round):
    secret_word = get_secret_word()
    if not secret_word:
        print("无法获取口令，任务终止")
        return False

    def task():
        return exchange(secret_word, round)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(task) for _ in range(tasks)]
        for future in as_completed(futures):
            try:
                result = future.result()
                if not result:
                    print("检测到阻断，停止所有任务")
                    executor.shutdown(wait=False)
                    return False
            except Exception as e:
                print(f"任务执行出错: {e}")

    print(f"所有 {tasks} 个任务已完成")
    return True


def get_current_round():
    now = datetime.now()
    return f"{now.hour:02d}:00"


def start_task():
    while True:
        now = datetime.now()
        if 11 <= now.hour < 21:
            current_round = get_current_round()
            print(f"开始执行 {current_round} 的任务")

            start_time = time.time()
            task_result = False
            if now.hour > 15:
                task_result = threading_run(tasks_num, threads_num, current_round)
            end_time = time.time()

            if not task_result:
                print(f"{current_round} 的任务因阻断而提前终止，用时 {end_time - start_time:.2f} 秒")
            else:
                print(f"{current_round} 的任务执行完毕，用时 {end_time - start_time:.2f} 秒")

            next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            wait_time = (next_hour - datetime.now()).total_seconds()

            if wait_time > 0:
                print(f"等待到下一个整点 {next_hour.strftime('%H:%M')}，还需 {wait_time:.2f} 秒")
                time.sleep(wait_time)
        elif now.hour >= 21:
            print("今日任务已结束")
            next_run = now.replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=1)
            wait_time = (next_run - now).total_seconds()
            print(f"等待到明天上午11点，还需 {wait_time:.2f} 秒")
            time.sleep(wait_time)
        else:
            next_run = now.replace(hour=11, minute=0, second=0, microsecond=0)
            wait_time = (next_run - now).total_seconds()
            print(f"等待到上午11点，还需 {wait_time:.2f} 秒")
            time.sleep(wait_time)


if __name__ == '__main__':
    start_task()
