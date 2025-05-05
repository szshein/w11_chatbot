import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def parsing_job(job):
    try:
        job_name = job.find('a', {'data-algolia-event-name':'click_job'}).text.strip()
    except AttributeError:
        job_name = 'N/A'
    
    try:
        comp_name = job.find('a', {'data-algolia-event-name':'click_page'}).text.strip()
    except AttributeError:
        comp_name = 'N/A'
    
    try:
        job_desc = job.find('div', {'class':'JobSearchItem_description__si5zg'}).text.strip()
    except AttributeError:
        job_desc = 'N/A'
    
    job_tags = [t.text.strip() for t in job.select('div.Tags_wrapper__UQ34T > div')]

    return [job_name, comp_name, job_desc, job_tags]

def crawl_jobs():
    try:
        # 檢查並創建 'pages' 資料夾（如果不存在）
        if not os.path.exists('pages'):
            os.makedirs('pages')

        data = []
        for p in range(1, 50):
            url = f'https://www.cake.me/jobs/%E5%AF%A6%E7%BF%92?locale=zh-TW&page={p}'
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            jobs = soup.select('div.JobSearchHits_list__3UtHp > div')
            
            for job in jobs:
                data.append(parsing_job(job))
            
            time.sleep(3)

        # 儲存爬取的資料到 CSV
        df = pd.DataFrame(data, columns=['job_name', 'comp_name', 'job_desc', 'job_tags'])
        df.to_csv('pages/jobsthousands.csv', index=False, encoding='utf-8-sig')  # 儲存到 'pages' 資料夾

    except KeyboardInterrupt:
        print("爬蟲被中斷，請稍後再試！")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    crawl_jobs()
