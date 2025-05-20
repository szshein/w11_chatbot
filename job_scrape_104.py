import requests
import pandas as pd
import os

def crawl_104_jobs(pages=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'Referer': 'https://www.104.com.tw/',
        'Accept': 'application/json',
    }

    all_jobs = []

    for page in range(1, pages + 1):
        url = f'https://www.104.com.tw/jobs/search/list?ro=0&page={page}'
        resp = requests.get(url, headers=headers)

        if resp.status_code == 200:
            try:
                jobs = resp.json()['data']['list']
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"解析第 {page} 頁失敗: {e}")
        else:
            print(f"第 {page} 頁請求失敗，狀態碼: {resp.status_code}")

    return all_jobs

def save_jobs_to_csv(jobs, filename='pages/104_jobs.csv'):
    if not os.path.exists('pages'):
        os.makedirs('pages')

    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"已儲存 {len(jobs)} 筆職缺資料到 {filename}")

if __name__ == "__main__":
    job_list = crawl_104_jobs(pages=5)
    save_jobs_to_csv(job_list)
