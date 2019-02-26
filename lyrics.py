import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import json
import re
import os
import sys
from Config import *

def get_content(url):
    try:
        content = requests.get(url, headers=HEADERS).text
        return content
    except:
        print('request error')
        sys.exit()

def get_singer(content):
    soup = BeautifulSoup(content, 'lxml')
    singer_name = ''.join(soup.title.text.split('-')[0].strip().split())
    link_list = soup.find('ul', class_='f-hide').find_all('a')
    song_list = []
    for tag in link_list:
        song_id = tag.get('href').split('=')[-1]
        song_name_raw = ''.join(tag.get_text().strip().split())
        song_name = validateTitle(song_name_raw)
        song_list.append([song_id, song_name])
    return singer_name, song_list

def save_lyric(song, singer, dir_path):
    song_id = song[0]
    song_name = song[1]
    song_file = os.path.join(dir_path, song_name + ".txt")
    if os.path.exists(song_file):
        print("{}-{} 已存在.".format(song_name, singer))
        return
    lyric_link = "http://music.163.com/api/song/lyric?" + "id=" + song_id + "&lv=-1&kv=-1&tv=-1"
    lyric_html = json.loads(get_content(lyric_link))
    try:
        lyric_raw = lyric_html["lrc"]['lyric']
        regex = re.compile('\s?\[.*\]\s?')
        lyric = re.split(regex, lyric_raw)
        with open(song_file, 'w+', encoding='utf-8') as f:
            for line in lyric:
                if '作词' in line or '作曲' in line or not line:
                    continue
                f.write(str(line) + '\n')
        print("{}-{} 写入完成.".format(song[1], singer))
    except:
        print('lyric parser error {}'.format(song_name))

def singer_crawler(singer_id):
    singer_url = "https://music.163.com/artist?id=" + str(singer_id)
    content = get_content(singer_url)
    singer, song_list = get_singer(content)
    singer_dir = os.path.join('./lyric_dir', singer)
    if not os.path.exists(singer_dir):
        os.makedirs(singer_dir)
    print("{} 歌曲数 {}".format(singer, len(song_list)))
    for i, song in enumerate(song_list):
        print("{} {}/{}".format(singer, str(i+1), str(len(song_list))))
        save_lyric(song, singer, singer_dir)

def validateTitle(title): #处理非法文件名
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

if __name__ == '__main__':
    print('Task Num :', len(TASKS))
    pool = Pool(processes=P_NUM)
    for task in TASKS:
        pool.apply_async(singer_crawler, (task,))
    pool.close()
    pool.join()