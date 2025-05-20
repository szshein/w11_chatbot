import requests
import pandas as pd
import os
import time

def crawl_104_jobs(pages=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        'Referer': 'https://www.104.com.tw/jobs/search/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }

    url = "https://www.104.com.tw/jobs/search/list"
    all_jobs = []

    for page in range(1, pages + 1):
        params = {
            "ro": 0,  # 全職、兼職、實習都要
            "keyword": "實習",
            "mode": "l",
            "order": 11,  # 最新排序
            "asc": 0,     # 降序
            "page": page
        }

        try:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                jobs = data.get('data', {}).get('list', [])
                if not jobs:
                    print(f"第 {page} 頁無職缺，結束爬取")
                    break
                all_jobs.extend(jobs)
                print(f"✅ 成功爬取第 {page} 頁，共獲得 {len(jobs)} 筆職缺")
            else:
                print(f"❌ 第 {page} 頁請求失敗，狀態碼：{resp.status_code}")
        except Exception as e:
            print(f"⚠️ 第 {page} 頁發生錯誤：{e}")

        time.sleep(2)

    return all_jobs

def save_jobs_to_csv(jobs, filename='pages/104_jobs.csv'):
    if not os.path.exists('pages'):
        os.makedirs('pages')

    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"📁 已儲存 {len(jobs)} 筆職缺資料到 {filename}")

if __name__ == "__main__":
    job_list = crawl_104_jobs(10)
    save_jobs_to_csv(job_list)
