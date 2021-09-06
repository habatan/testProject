# -*- coding: utf-8 -*-
# このファイルを編集する
# ユニパの情報取得を自動化していく
# 事前にselenium一式とchromedriverが必要
from requests.api import head
from selenium.webdriver import Chrome,ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# 例外処理用の便利なライブラリ
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from datetime import datetime
import time 
import requests 
import os 
import dotenv
import re
# カレントディレクトリのenvfileを使用
dotenv.load_dotenv("./info/.env")

# sysを使ってuserIDとpassはターミナルの引数にしてもええかも(もしくはjsonファイルかtxtファイルにする)
UserID = os.environ["USERID"]
PassWord = os.environ["PASS"]

# unipaのURL
URL = "https://unipa.u-hyogo.ac.jp/uprx/"
# driverのオプション設定
def main():
   options = ChromeOptions()
   options.headless = True
   # chromedriverを作成
   driver = Chrome(options=options)
   driver.get(URL)
   WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="loginForm:userId"]')))

   # UserIDやPasswordの入力及び送信
   input_element_key1 = driver.find_element_by_xpath('//*[@id="loginForm:userId"]')
   input_element_key2 = driver.find_element_by_xpath('//*[@id="loginForm:password"]')
   botton = driver.find_element_by_xpath('//*[@id="loginForm:loginButton"]')
   input_element_key1.send_keys(UserID)
   input_element_key2.send_keys(PassWord)
   botton.send_keys(Keys.RETURN)
   time.sleep(2)

   # クラスプロファイルを探索しに行く
   driver.find_element_by_xpath('//*[@id="funcForm:j_idt361:j_idt518:j_idt524"]/p').click()

   #繰り返し方は要注意
   for _ in range(2):
      # 講義名を取得する
      lecture = driver.find_element_by_class_name('cpTgtName').text
      lecture = re.search(r'[0-9]+(.+) ((.+))', lecture).group(1)
      # 何の科目か知りたい場合
      # subject = re.search(r'[0-9]+(.+) ((.+))', lecture).group(2)

      # 課題提出状況を確認する
      elements = driver.find_elements_by_css_selector(".ui-button-text.ui-c")
      # もっとスマートな方法があれば...
      for element in elements:
         if element.text == '課題提出':
               element.click()
               break

      # 2ページ以上の可能性があるので考慮する必要がある
      i = 0
      while True:
         i += 1
         try:
               driver.find_element_by_xpath(f'//*[@id="funcForm:gakKdiTstList_paginator_bottom"]/span[4]/span[{i}]').click()
         except:
               break
         # 選択した講義の課題が残っているのかを調べる
         work_names = driver.find_elements_by_class_name('ui-commandlink ui-widget')
               
      #次の授業を押す
      driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right').click()


# envfileから情報を入手することを想定
token = os.environ["TOKEN"]

# linenotify通知関数
def sendMessage(msg:str)->str:
   # linenotfy通知系apiをたたく
   URL="https://notify-api.line.me/api/notify"
   payload = {
      "message":msg
   }
   headers={
      "Aouthorization":"Bearer "+token
   }
   response=requests.post(URL,params=payload,headers=headers)
   return response.text


if __name__ == "__main__":
   main()
