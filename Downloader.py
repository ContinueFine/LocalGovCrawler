from bs4 import BeautifulSoup
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.request import urlretrieve
from os import makedirs
import os.path, time, re
import requests
import cchardet
import const
import csv
import traceback

import logging_config
from logging import getLogger
log = getLogger(__name__)

const.DL_ROOT_NAME = "CrawlerDownload"
test_files = {}

def enum_links(html, base):
   soup = BeautifulSoup(html, "html.parser")
   links = soup.select("link[rel='stylesheet']")
   links += soup.select("a[href]")
   result = []

   for a in links:
      href = a.attrs['href']
      url = urljoin(base, href)
      result.append(url)
   return result

def download_file(url):
   o = urlparse(url)
   savepathroot = "../" + const.DL_ROOT_NAME + "/"
   replace_path = re.sub(r'[\\|:|?|"|<|>|\|]', '-', o.path)
   savepath = savepathroot + o.netloc + replace_path
   if re.search(r"/$", savepath):
      savepath += "index.html"
   savedir = os.path.dirname(savepath)

   if os.path.exists(savepath): return savepath

   if not os.path.exists(savedir):
      log.info("mkdir=" + savedir)
      try:
          makedirs(savedir)
      except FileNotFoundError:
          traceback.print_exc()
          log.warning("ディレクトリ作成失敗:" + savedir)

   try:
      log.info("download=" + url)
      ext = os.path.splitext(savepath)[1]
      # URL末尾に拡張子が存在しない場合はhtmlファイルとして保存
      if ext == "":
          savepath += ".html"
      opener = urllib.request.build_opener()
      opener.addheaders = [('User-agent', 'Mozilla/5.0')]
      urllib.request.install_opener(opener)
      urlretrieve(url, savepath)
      time.sleep(1)
      return savepath
   except:
      traceback.print_exc()
      log.warning("ダウンロード失敗:" + url)
      return None

def analize_html(url, root_url):
   savepath = download_file(url)
   if savepath is None: return
   if savepath in test_files: return
   test_files[savepath] = True
   log.info("analize_html=" + url)

   if const.DL_ROOT_NAME in url:
       with open(os.path.abspath(url), mode='rb') as f:
           char_code = cchardet.detect(f.read())["encoding"]
   else:
       char_code = cchardet.detect(requests.get(url).content)["encoding"]
   html = open(savepath, "r", encoding=char_code, errors='ignore').read()
   links = enum_links(html, url)
   for link_url in links:
      if link_url.find(root_url) != 0:
         if not re.search(r".(css|pdf)$", str(link_url)): continue

      if re.search(r".(html|htm)$", str(link_url)):
         analize_html(link_url, root_url)
         continue

      link_url = download_file(link_url)

      if link_url is not None:
          if link_url.find(root_url) == 0 and re.search(r".(html|htm)$", str(link_url)):
              analize_html(link_url, root_url)
              continue

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def url_convert(url):
    if not is_ascii(url):
       parsed_link = urllib.parse.urlsplit(url)
       # queryにascii以外の文字が含まれている場合
       parsed_link = parsed_link._replace(query=urllib.parse.quote(parsed_link.query))
       url = parsed_link.geturl()
    return url

if __name__ == "__main__":
   csv_file = open("target_url_list.csv", "r", encoding="ms932", errors="", newline="" )
   f = csv.DictReader(csv_file)
   for row in f:
       if row["TargetFlag"] == "1":
           log.info("【" + row["LocalGovernmentName"] + "】")
           sp = row["URL"].split("|")
           start = time.time()
           for target_url in sp:
              url = target_url
              url_convert(url)
              # 階層パスまでをルートURLとする
              root_url = os.path.dirname(url)
              analize_html(url, root_url)
           log.debug("実行時間:" + row["LocalGovernmentName"] + ":" + str(time.time()-start))