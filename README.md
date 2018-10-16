# IMDB TV-SERIES NOTIFICATION
 
## PROJECT DESCRIPTION:

The script imdb.py asks for email address and list of favorite TV series for multiple users as input.
The prompt is as follows: 
Email address: 
TV Series: 

Input data is stored in MySQL dB table(s). A single email is sent to the input email address with all the appropriate response for every TV series. The content of the mail depends on the following use cases: 
* Exact date is mentioned for next episode. 
* Only year is mentioned for next season. 
* All the seasons are finished and no further details are available.

The script reminder.py checks the current database and if an episode of any series is to be streamed on the next day then an email is sent to the user.

## PRE-REQUISITES:
1.	Python 3.3 or up
2.	Install mysql :  (step for installing it on linux (Redhat) OS)
a.	yum install mysql mysql-client mysql-server
b.	service mysqld start
3.	Install MySQL Connector / mysqldb (does not work with python 3.3 or up)
4.	Install BeautifulSoup: pip install beautifulsoup4
5.	Install IMDB: pip install imdbPy


## USE OF ABOVE LIBRARIES:

1.	MySQL – It’s a special-purpose programming language to interact with the data stored in tables.
2.	MySQL Connector – It is a driver for connecting to a MySQL database server.
3.	BeautifulSoup – It is a Python library for pulling data out of HTML and XML files.
4.	IMDbPY – It is a Python package useful to retrieve and manage the data of the IMDb movie database.


## HOW DOES IS WORK:

imdb.py
When the code is run the terminal asks for email id and list of favorite tv series, separated by commas and they’ll receive a mail which will contain the details about the next release of the show or if the series has completed. Details about the whole process:
1.	Their input data is stored in a database and it is checked with imdb database, if the series exitis it will search for the last season and then to the episode which is not released yet. This is done through web scraping.
2.	Mailing is done through ansible and only gmail accounts can be taken into account. Make sure that you have enabled receiving mails from less secured devices. 
3. In the mail method, email id, username and password is to be provided by admin i.e from whose account the mails are to be forwarded.

reminder.py
Database will be checked everyday and if the next episode is supposed to stream the next day for a particular tv series then an email will be sent to the users informing them about the same 

Mail will be shown in this format : ![alt text](https://raw.githubusercontent.com/Mansi1301/Innovaccer-Reminder/master/gmail.png)

