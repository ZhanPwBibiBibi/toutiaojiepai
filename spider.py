import json
import os
from multiprocessing.pool import Pool
from urllib.parse import urlencode
import requests
import re
import hashlib

from requests import RequestException


def get_index_page(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
    }
    url = "http://www.toutiao.com/search_content/?" + urlencode(data)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5)" +
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('Loading index page error.')
        return None


def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item['article_url']


def get_details_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5)" +
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"}
    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('Loading details page error.')
        return None


def parse_details_page(html):
    pattern = re.compile('var gallery = (.*?);', re.S)
    pic = re.search(pattern, html)
    if pic:
        data = json.loads(pic.group(1))
        if 'sub_images' in data.keys():
            images = [item["url"] for item in data["sub_images"]]
            for image in images:
                download_images(image)
            return {
                "images": images
            }


def write_to_file(line):
    with open("image.txt", 'a') as f:
        f.write(str(line))
        f.close()


def download_images(url):
    response = requests.get(url)
    try:
        if response.status_code == 200:
            save_images(response.content)
        return None
    except RequestException:
        print('Loading picture error.')
        return None


def save_images(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), hashlib.md5(content), 'jpg')
    with open(file_path, 'wb') as f:
        f.write(content)
        f.close()


def main(offset):
    html = get_index_page(offset, "街拍")
    for url in parse_page_index(html):
        if 'group' in url:
            details_html = get_details_page(url)
            parse_details_page(details_html)
            if parse_details_page(details_html):
                write_to_file(str(parse_details_page(details_html)) + '\n')


if __name__ == '__main__':
    main(0)
    # pool = Pool()
    # pool.map(main, [i*20 for i in range(10)])
