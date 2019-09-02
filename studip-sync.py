#!/bin/python3
import requests
from bs4 import BeautifulSoup
import re
import os
import urllib

username    =   ''
password    =   ''
folder      =   ''

login_url           =   'https://studip.tu-braunschweig.de/index.php?again=yes'
courses_url         =   'https://studip.tu-braunschweig.de/dispatch.php/my_courses'
file_list_url       =   'https://studip.tu-braunschweig.de/dispatch.php/course/files/flat?cid='
course_details      =   'https://studip.tu-braunschweig.de/dispatch.php/course/details/?cid='

sane_folder_names   =   1
sane_file_names     =   1

custom_names = {
        'enter course id here':     'custom name here'
        }

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
	if re.match(r'.*\..{4,}', title):
		title = title.replace('.', '', 1)
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
    match = re.match(r'(^https:\/\/studip\.tu-braunschweig\.de\/seminar_main\.php\?auswahl=\w{32}$)', link)
    if match:
        id = []
        id = link.rsplit("=")
        id = str(id[-1])
        courses.append(id)

print('entering the mainframe')
for id in courses:
    f = s.get(file_list_url + id)
    t = s.get(course_details + id)
    soup = BeautifulSoup(f.text, 'html.parser')
    semester = ' ' + re.findall(r'([A-Z][a-z][A-Z][a-z]\s[0-9]{4})', t.text)[0]

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

