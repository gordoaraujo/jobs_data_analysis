import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import string
import collections
import time

# Adapted from https://github.com/lukebarousse/Data_Analyst_Streamlit_App_V1/blob/main/01_%F0%9F%9B%A0%EF%B8%8F_Skills.py
keywords_skills = {
    'airflow': 'Airflow', 'alteryx': 'Alteryx', 'aspnet': 'ASP.NET', 'atlassian': 'Atlassian', 
    'excel': 'Excel', 'powerbi': 'Power BI', 'tableau': 'Tableau', 'srss': 'SRSS', 'word': 'Word', 
    'unix': 'Unix', 'vue': 'Vue', 'jquery': 'jQuery', 'linuxunix': 'Linux / Unix', 'seaborn': 'Seaborn', 
    'microstrategy': 'MicroStrategy', 'spss': 'SPSS', 'visio': 'Visio', 'gdpr': 'GDPR', 'ssrs': 'SSRS', 
    'spreadsheet': 'Spreadsheet', 'aws': 'AWS', 'hadoop': 'Hadoop', 'ssis': 'SSIS', 'linux': 'Linux', 
    'sap': 'SAP', 'powerpoint': 'PowerPoint', 'sharepoint': 'SharePoint', 'redshift': 'Redshift', 
    'snowflake': 'Snowflake', 'qlik': 'Qlik', 'cognos': 'Cognos', 'pandas': 'Pandas', 'spark': 'Spark', 'outlook': 'Outlook'
}

# Adapted from https://github.com/lukebarousse/Data_Analyst_Streamlit_App_V1/blob/main/01_%F0%9F%9B%A0%EF%B8%8F_Skills.py
keywords_programming = {
    'sql' : 'SQL', 'python' : 'Python', 'r' : 'R', 'c':'C', 'c#':'C#', 'javascript' : 'JavaScript', 'js':'JS', 'java':'Java', 
    'scala':'Scala', 'sas' : 'SAS', 'matlab': 'MATLAB', 'c++' : 'C++', 'perl' : 'Perl','go' : 'Go',
    'typescript' : 'TypeScript','bash':'Bash','html' : 'HTML','css' : 'CSS','php' : 'PHP','powershell' : 'Powershell',
    'rust' : 'Rust', 'kotlin' : 'Kotlin','ruby' : 'Ruby','dart' : 'Dart','assembly' :'Assembly',
    'swift' : 'Swift','vba' : 'VBA','lua' : 'Lua','groovy' : 'Groovy','delphi' : 'Delphi','objectivec' : 'Objective-C',
    'haskell' : 'Haskell','elixir' : 'Elixir','julia' : 'Julia','clojure': 'Clojure','solidity' : 'Solidity',
    'lisp' : 'Lisp','f#':'F#','fortran' : 'Fortran','erlang' : 'Erlang','apl' : 'APL','cobol' : 'COBOL',
    'ocaml': 'OCaml','crystal':'Crystal','javascripttypescript' : 'JavaScript / TypeScript','golang':'Golang',
    'nosql': 'NoSQL', 'mongodb' : 'MongoDB','tsql' :'Transact-SQL','vba' : 'Visual Basic',
    'pascal':'Pascal', 'mongo' : 'Mongo', 'plsql' : 'PL/SQL','sass' :'SASS', 'vbnet' : 'VB.NET','mssql' : 'MSSQL'
}

keywords_python = {'tensorflow': 'TensorFlow', 'numpy': 'NumPy', 'scipy': 'SciPy',
 'pandas': 'Pandas', 'matplotlib': 'Matplotlib', 'keras': 'Keras', 'statsmodels': 'Statsmodels', 'scikitlearn': 'SciKit-Learn', 
 'pytorch': 'PyTorch', 'pycaret': 'PyCaret', 'scrapy': 'Scrapy', 'beautifulsoup': 'BeautifulSoup', 'xgboost': 'XGBoost', 
 'lightgbm': 'LightGBM', 'eli5': 'ELI5', 'theano': 'Theano', 'nupic': 'NuPIC', 'ramp': 'Ramp', 'pipenv': 'Pipenv',
 'bob': 'Bob', 'pybrain': 'PyBrain', 'caffe2': 'Caffe2', 'chainer': 'Chainer', 'seaborn': 'Seaborn', 'bokeh': 'Bokeh', 
 'plotly': 'Plotly', 'pydot': 'pydot'}


def clean_job_keywords(job_keywords):
    L = []
    for keyword in job_keywords:
        L.append(keyword.lower().replace(" ", "%20"))
    return L

def get_data_one_job(job_box):

    try:
        title = job_box.find("a").find("span", {"class" : "VacancySerpItemUpdated___StyledText2-sc-i0986f-4"}).text
    except AttributeError:
        title = np.nan
    info_box = job_box.find_all("p", {"class" : "Text__span-sc-1lu7urs-12"})
    try:
        pub_date = info_box[0].find("span").text.split(": ")[1]
    except IndexError:    
        pub_date = np.nan
    try:
        location = info_box[1].text
    except IndexError:
        location = np.nan
    try:    
        workload = info_box[2].text
    except IndexError:
        workload = np.nan
    try:    
        job_type = info_box[3].text
    except IndexError:
        job_type = np.nan
    try:
        company = job_box.find('div', {'class': 'gNMZoz'}).find('strong').text
    except AttributeError:
        company = np.nan
    # try:
        # company = info_box[4].text
    # except IndexError:
        # company = np.nan
    try:
        job_link = "https://www.jobs.ch" + job_box.find("a").get("href")
    except AttributeError:
        job_link = np.nan

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


def get_job_keywords(df):
    programming_count = []
    skills_count = []
    python_count = []
    errors = []

    job_urls = df["job_link"].values

    for i, ju in enumerate(job_urls):

        if i % 5 == 0:
            time.sleep(0.5)

        flag_1 = False
        flag_2 = False
        
        sec_page = requests.get(ju)
        sec_soup = BeautifulSoup(sec_page.content, "html.parser")
        
        try:
            job_desc = sec_soup.find("div", {"data-cy" : "vacancy-description"})
            job_desc_text = job_desc.text
            # print(job_desc)
        except AttributeError:
            job_desc_text = ""
            flag_1 = True
        
        if job_desc == None:
            try:
                job_desc = sec_soup.find("iframe", {"data-cy" : "detail-vacancy-iframe-content"}).find_next()
                job_desc_text = job_desc.text
                # print(job_desc)
            except AttributeError:
                job_desc_text = ""
                flag_2 = True
        
        if flag_1 and flag_2:
            errors.append(ju)

        job_desc_text = job_desc_text.translate(job_desc_text.maketrans("", "", '!"$%&\'()*,-./:;<=>?@[\\]^_`{|}~'))
        job_desc_text = job_desc_text.lower()
        job_desc_words = job_desc_text.split()
        # job_desc_words = set(job_desc_text)

        for word in job_desc_words:
            if word in keywords_programming.keys():
                programming_count.append(word)
            if word in keywords_skills.keys():
                skills_count.append(word)
            if word in keywords_python.keys():
                python_count.append(word)
    
    programming_summary = collections.Counter(programming_count)
    skills_summary = collections.Counter(skills_count)
    python_summary = collections.Counter(python_count)
    
    return {"programming_summary" : programming_summary, "skills_summary" : skills_summary, "python_summary" : python_summary, "errors" : errors}