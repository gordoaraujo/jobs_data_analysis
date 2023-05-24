import requests
from bs4 import BeautifulSoup
import pandas as pd
import string

def clean_job_keywords(job_keywords):
    L = []
    for keyword in job_keywords:
        L.append(keyword.lower().replace(" ", "%20"))
    return L

def get_data_one_job(job_box):

    try:
        title = job_box.find("a").find("span", {"class" : "VacancySerpItemUpdated___StyledText2-sc-i0986f-4"}).text
    except AttributeError:
        title = ""
    info_box = job_box.find_all("p", {"class" : "Text__span-sc-1lu7urs-12"})
    try:
        pub_date = info_box[0].find("span").text.split(": ")[1]
    except IndexError:    
        pub_date = ""
    try:
        location = info_box[1].text
    except IndexError:
        location = ""
    try:    
        workload = info_box[2].text
    except IndexError:
        workload = ""
    try:    
        job_type = info_box[3].text
    except IndexError:
        job_type = ""
    try:
        company = info_box[4].text
    except IndexError:
        company = ""
    try:
        job_link = "https://www.jobs.ch" + job_box.find("a").get("href")
    except AttributeError:
        job_link = ""

    D = {
        "title" : title,
        "publication_date" : pub_date,
        "location" : location,
        "workload" : workload,
        "job_type" : job_type,
        "company" : company,
        "job_link" : job_link
    }

    return D

def df_all_jobs(all_jobs):
    df = pd.DataFrame()
    for one_job in all_jobs:
        j = get_data_one_job(one_job)
        df = pd.concat([df, pd.DataFrame(j, index = [0])], ignore_index = True)
    return df

def df_full_data(searched_jobs):
    
    job_positions_keys = clean_job_keywords(searched_jobs)

    errors = []
    df_all = pd.DataFrame()
    
    for job in job_positions_keys:
        try:
            url = f"https://www.jobs.ch/en/vacancies/?term={job}"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            pgs = int(soup.find("span", {"data-cy" : "page-count"}).text.split()[-1])
            
            df_jobs = pd.DataFrame()
            for i in range(1, pgs + 1):
                i_url = f"https://www.jobs.ch/en/vacancies/?page={i}&term={job}"
                i_page = requests.get(i_url)
                i_soup = BeautifulSoup(i_page.content, "html.parser")
                job_postings = i_soup.find("div", {"class" : "SearchVacancyListSeparatorDecoratorComponent___StyledGrid-sc-qlhh5h-0"})
                all_jobs = job_postings.find_all("article", {'data-cy': 'serp-item'})
                df_jobs_page = df_all_jobs(all_jobs)
                df_jobs = pd.concat([df_jobs, df_jobs_page], ignore_index = True)
            
            df_jobs["keyword"] = job.replace("%20", " ")
            df_all = pd.concat([df_all, df_jobs], ignore_index = True)

        except AttributeError:
            # cjob = job.replace("%20", " ")
            print(f"{job.replace('%20', ' ')} not found")
            errors.append(job.replace('%20', ' '))
    
    return {"results" : df_all, "errors" : errors}