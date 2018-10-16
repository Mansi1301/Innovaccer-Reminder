
# coding: utf-8

# In[6]:


import mysql.connector
from bs4 import BeautifulSoup

import subprocess as sp
import requests

connection=mysql.connector.connect(user='root',password='Mansi@1301',host='localhost',auth_plugin='mysql_native_password')

cursor=connection.cursor()

#creating database
cursor.execute("Create database if not exists IMDB")
cursor.execute("Use IMDB")

#creating table
cursor.execute("Create table if not exists input_from_users(email_id varchar(100), tv_show varchar(500))")

def scrapper(series_name_by_user):
    try:
        from imdb import IMDb
        import urllib.request as urllib2
    except Exception:
        return ("Error: You must install the imdbpy library to use this action.")
    
    #checking the existing series with IMDB database and fetching the series id
    for j in series_name_by_user:
        try:
            tv_series= IMDb()
            tv_series_name = tv_series.search_movie(j)[0]
            series_id= tv_series.get_imdbID(tv_series_name)
        except Exception:
            return ("ERROR: " + j + " not found.")


        web_page = requests.get("https://www.imdb.com/title/tt{}".format(series_id))
        soup = BeautifulSoup(web_page.content,'html.parser')
        name_box=soup.findAll('div',attrs={'class':'seasons-and-year-nav'})
        value=[]
        
        #fetching the last season number
        for i in name_box:
            value=i.text.strip()
        value=value.split("\xa0\xa0\n")
        temp=value[0].split("\n")
        name=temp[len(temp)-1]

        #fetching the release dates for all episodes of that season 
        npage = requests.get("https://www.imdb.com/title/tt{0}/episodes?season={1}&ref_=tt_eps_sn_{1}".format(series_id,name))
        soup = BeautifulSoup(npage.content,'html.parser')
        name_box=soup.findAll('div',attrs={'class':'airdate'})

        release_date=[]
        for i in name_box:
            release_date.append(i.text.strip())
        
        temp_release_date=release_date
        original_length=len(release_date)

        #removing the non-existing values
        while '' in temp_release_date:
            temp_release_date.remove('')
        temp_length=len(temp_release_date)

        month={"Jan.":1,"Feb.":2,"Mar.":3,"Apr.":4,"May":5,"Jun.":6,"Jul.":7,"Aug.":8,"Sep.":9,"Oct.":10,"Nov.":11,"Dec.":12}

        #extracting the current date
        from datetime import date
        import datetime
        today=str(date.today())
        today=today.split("-")

        if len(release_date[0].split()) == 1:
            Status="The next season begins in {}".format(release_date[0])
        else:
            flag=0
            for i in temp_release_date:
                date_break=i.split(" ")
                date_break[1]=month.get(date_break[1])
                if datetime.date(int(date_break[2]),int(date_break[1]),int(date_break[0])) > datetime.date(int(today[0]),int(today[1]),int(today[2])):
                    flag=1
                    break
            if flag==0:
                if temp_length<original_length:
                    Status="Latest episode was released on {}/{}/{}".format(date_break[2],date_break[1],date_break[0])
                else:
                    Status="The show has finished streaming all its episodes"
            else:
                Status="Next episode airs on {}/{}/{}".format(date_break[2],date_break[1],date_break[0])


        fh.write("""
        Tv series name: {}
        Status: {}\n""".format(j,Status))


    fh.write("id: {}".format(email_address))    
    fh.close()
    return ("True")

def mail():
    fh=open("/output/mail.yml","w")
    fh.write("""
    - hosts: localhost
      tasks:
       - include_vars: "/output/mail_output.yml"
       - mail:
           body: "{{var}}"
           from: 'xyz@gmail.com'
           username: 'xyz@gmail.com'
           password: "xyz"
           subject: "Reminder for your Favorite TV Shows"
           to: '{{id}}'
           host: smtp.gmail.com
           port: 587
    """)
    fh.close()

    sp.getoutput("sudo ansible-playbook /output/mail.yml")

email_address=input("Email address: ")
TV_series=input("TV Series: ")

params=(email_address,TV_series.lower())
cursor.execute("Insert into input_from_users(email_id,tv_show) values (%s,%s)",params)

cursor.execute("select * from input_from_users")
data_of_user=cursor.fetchall()

data=data_of_user[len(data_of_user)-1]
series_name_by_user=data[1].split(',')


folder_check=sp.getstatusoutput("sudo mkdir /output")
if 0 in folder_check:
    sp.getoutput("sudo mkdir /output")

fh=open('/output/mail_output.yml','w')
fh.write("var: |")

result=scrapper(series_name_by_user)
if result == "True":
    mail()
else:
    print(result)
connection.commit()

