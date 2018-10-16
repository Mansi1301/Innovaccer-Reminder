
# coding: utf-8

# In[1]:


import mysql.connector
from bs4 import BeautifulSoup

from imdb import IMDb
import urllib.request as urllib2

import subprocess as sp
import requests

import schedule
import time

connection=mysql.connector.connect(user='root',password='Mansi@1301',host='localhost',auth_plugin='mysql_native_password') 

cursor=connection.cursor()

#creating database
cursor.execute("Create database if not exists aIMDB") 
cursor.execute("Use aIMDB")

#creating table
cursor.execute("Create table if not exists input_from_users(email_id varchar(100), tv_show varchar(500))") 

#it will let users to get informed on a day before their series is starting 
def reminder():
    try:
        from imdb import IMDb
        import urllib.request as urllib2
    except Exception:
        return ("Error: You must install the imdbpy library to use this action.")
    x=0
    while x!=count:
        series_name=data_of_user[x][1].split(',')
        length=len(series_name)
        j=0
        while j!=length:
            #checking the existing series with IMDB database and fetching the series id
            tv_series= IMDb()
            tv_series_name = tv_series.search_movie(series_name[j])[0]
            series_id= tv_series.get_imdbID(tv_series_name)
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
                continue
            else:
                flag=0
                for i in temp_release_date:
                    date_break=i.split(" ")
                    date_break[1]=month.get(date_break[1])
                    if datetime.date(int(date_break[2]),int(date_break[1]),int(date_break[0])) > datetime.date(int(today[0]),int(today[1]),int(today[2])):
                        flag=1
                        break
            
                if flag==1:
                    #comparing the current date with release date and if the difference is 1 then mail is to be sent
                    a=datetime.date(int(date_break[2]),int(date_break[1]),int(date_break[0]))-datetime.date(int(today[0]),int(today[1]),int(today[2]))

                    if(a.days==1):
                        Status="Your fav series {} is streaming tomorrow".format(series_name[j])
                        mail(data_of_user[x][0],Status)
                    else:
                        continue
                else:
                    continue


            j=j+1
        x=x+1

#mailing is done through ansible --> email will be sent to the user on
#their respective email address 
#it takes only account of only gmail
def mail(id,Status): 
    fh=open("/output/mail.yml","w")
    fh.write("""
    - hosts: localhost
      tasks:
       - mail:
           body: {}
           from: 'xyz@gmail.com'
           username: 'xyz@gmail.com'
           password: "xyz"
           subject: "Notification for your fav tv series"
           to: {}
           host: smtp.gmail.com
           port: 587
    """.format(Status,id))
    fh.close()

    sp.getoutput("sudo ansible-playbook /output/mail.yml")

email_address=input("Email address: ") #user input
TV_series=input("TV Series: ")

params=(email_address,TV_series.lower())
cursor.execute("Insert into input_from_users(email_id,tv_show) values (%s,%s)",params)

cursor.execute("select * from input_from_users")
data_of_user=cursor.fetchall()

#separating tv series name
data=data_of_user[len(data_of_user)-1]
series_name_by_user=data[1].split(',') 


count_row=cursor.execute("select count(*) from input_from_users")
count_row=cursor.fetchall()
count = count_row[0][0]

folder_check=sp.getstatusoutput("sudo mkdir /output")
if 0 in folder_check:
    sp.getoutput("sudo mkdir /output")



#scheduling so that it will check everyday if any tv series will be streaming the next day
schedule.every().day.at("10:00").do(reminder)
while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute
connection.commit()

