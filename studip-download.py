#!/bin/python3
# This simple script will download all files of the studIP courses you are enlisted in.
# Basically it opens a Session with your universities StudIP and checks the overview of your courses,
# for the corresponding course id's. (This is a 32 character long string found at the end of the course url)
# It then gets all the file url's of each curses and downloads them in subfolders named according to either
# the name given by the university or your custom name specified in the custom_names dictionary.
# The semster of the course is appended because some courses can have equal names.
# This can be disabled if the append_semster variable is set to 0.
# You can exclude courses from downloading by adding their id to the excluded_courses list.

import requests
from bs4 import BeautifulSoup
import re
import os
import urllib

# Fill out the first 3 variables to login automaticly on execution.
# If one of these is not supplied, the script will prompt you to input the missing ones.

username    =   ''
password    =   ''
folder      =   ''

# Here you can supply the url's of your university, accordingly.

login_url           =   'https://studip.tu-braunschweig.de/index.php?again=yes'

# The following is the url of the course overview. This one is used to get the id's of your courses.
courses_url         =   'https://studip.tu-braunschweig.de/dispatch.php/my_courses'

# The next one should be overview of all your files of one of your courses WITHOUT the course id at the end of the url.
# Also the "Alle Datein Anzeigen" option MUST be chosen.
file_list_url       =   'https://studip.tu-braunschweig.de/dispatch.php/course/files/flat?cid='

# The last url is the "Details" tab of the course overview, where you can see the semester of the Course. Again WITHOUT the id.
# This is used to supply the semester and year since some courses have the same names.
course_details      =   'https://studip.tu-braunschweig.de/dispatch.php/course/details/?cid='

# If theses are set to 1, the script will remove all spaces, Umlaute and replace _ with -
# If they are set to 0, the names are not altered.
sane_folder_names   =   1
sane_file_names     =   1

# If the following is set to 0 the script will not supply the year and semester turn to the folder name wich can lead du ambiguities.
append_semester     =   1

# The script will check this dictionary and if a key matching to a course id is supplied, the folder
# for the specified course will be named according to the value mathing so said key.
custom_names = {
        'enter course id here':     'custom name here'
        }

# If you want to exclude courses write the id's in this list.
excluded_courses = ['course to exclude','another course to exclude']

if not username:
    username = input('username: ')
if not password:
    password = input('password: ')
if not folder:
    folder = input('download location: ')
login_data = {
        'loginname':            username,
        'password':             password,
        'security_token':       '',
        'login_ticket':         '',
        'login':                ''
}

if not folder[-1] == '/':
    folder = folder + '/'
if not os.path.exists(folder):
    os.mkdir(folder)

def sane_maker(title):
	title = title.lower()
	title = title.replace('ä', 'ae')
	title = title.replace('ö', 'oe')
	title = title.replace('ü', 'ue')
	title = title.replace('ß', 'ss')
	title = title.replace(' ', '-')
	title = title.replace('--', '-')
	title = title.replace('+', '-')
	title = title.replace('_', '-')
	return title

print('making login request')
s = requests.Session()
res = s.get(login_url)
cookies = dict(res.cookies)
soup = BeautifulSoup(res.content, 'html5lib')
login_data['security_token'] = soup.find('input', attrs={'name': 'security_token'})['value']
login_data['login_ticket'] = soup.find('input', attrs={'name': 'login_ticket'})['value']
res = s.post(login_url, data=login_data, cookies=cookies)

print('guess it succeeded idk tho')

d = s.get(courses_url)
courses_soup = BeautifulSoup(d.text, 'html.parser')
courses = []
for link in courses_soup.find_all('a'):
    link = (link.get('href'))
    match = re.match(r'(^https:\/\/studip\..*\.de\/seminar_main\.php\?auswahl=\w{32}$)', link)
    if match:
        id = []
        id = link.rsplit("=")
        id = str(id[-1])
        courses.append(id)

print('entering the mainframe')
for id in courses:
    if id in excluded_courses:
        continue
    f = s.get(file_list_url + id)
    soup = BeautifulSoup(f.text, 'html.parser')
    if append_semester:
        t = s.get(course_details + id)
        semester = ' ' + re.findall(r'([A-Z][a-z][A-Z][a-z]\s[0-9]{4})', t.text)[0]
    else:
        semester = ''

    if id in custom_names:
        subfolder = custom_names[id] + '/'
    else:
	    subfolder = soup.title.string
	    subfolder = subfolder.split(':')
	    subfolder = str(subfolder[-1])
	    subfolder = subfolder.split('-')
	    subfolder = subfolder[0].strip() + semester + '/'
    print('\n',  subfolder[:-1] ,'\n')
    if sane_folder_names:
        subfolder = sane_maker(subfolder)
    if not os.path.exists(folder + subfolder):
        os.mkdir(folder + subfolder)

    for link in soup.find_all('a'):
        link = (link.get('href'))
        match = re.match(r'(.*file_id=.*)',link)
        if match:
            filename = link.rsplit("=")
            filename = str(filename[-1])
            filename = urllib.parse.unquote(filename)
            if sane_file_names: 
                filename = sane_maker(filename)
            fullpath = folder + subfolder + filename
            if not os.path.exists(folder + subfolder + filename):
                print('     ' + subfolder + filename)
                file = s.get(link)
                with open(fullpath , 'wb') as f:
                    f.write(file.content)
