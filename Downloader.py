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
   savepath = savepathroot + o.netloc + o.path
   if re.search(r"/$", savepath):
      savepath += "index.html"
   savedir = os.path.dirname(savepath)

   if os.path.exists(savepath): return savepath

   if not os.path.exists(savedir):
      print("mkdir=", savedir)
      try:
          makedirs(savedir)
      except FileNotFoundError:
          print("ディレクトリ作成失敗:", savedir)

   try:
      print("download=", url)
      ext = os.path.splitext(savepath)[1]
      # URL末尾に拡張子が存在しない場合はhtmlファイルとして保存
      if ext == "":
          savepath += ".html"
      urlretrieve(url, savepath)
      time.sleep(1)
      return savepath
   except:
      print("ダウンロード失敗:", url)
      return None

def analize_html(url, root_url):
   savepath = download_file(url)
   if savepath is None: return
   if savepath in test_files: return
   test_files[savepath] = True
   print("analize_html=", url)

   if const.DL_ROOT_NAME in url:
       with open(os.path.abspath(url), mode='rb') as f:
           char_code = cchardet.detect(f.read())["encoding"]
   else:
       char_code = cchardet.detect(requests.get(url).content)["encoding"]
   html = open(savepath, "r", encoding=char_code).read()
   links = enum_links(html, url)
   for link_url in links:
      if link_url.find(root_url) != 0:
         if not re.search(r".css$", str(link_url)): continue

      if re.search(r".(html|htm)$", str(link_url)):
         analize_html(link_url, root_url)
         continue

      link_url = download_file(link_url)

      if re.search(r".(html|htm)$", str(link_url)):
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
           url = row["URL"]
           url_convert(url)
           analize_html(url, url)