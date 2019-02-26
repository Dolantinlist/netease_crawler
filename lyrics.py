import requests
from bs4 import BeautifulSoup
import json
import re
import os
from Config import *

def get_content(url):
    try:
        content = requests.get(url, headers=HEADERS).text
        return content
    except:
        print('request error')

def get_singer(content):
    soup = BeautifulSoup(content, 'lxml')