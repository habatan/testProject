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
import datetime
import time 
import requests 
import os 
import dotenv
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

   # 事前に今日の曜日を確認する必要がある
   d = datetime.today().weekday()+1
   count_class=[]
   # 曜日とscccelectorの規則を確認
   for c in range(1,6):
      if c == d:
         continue
      driver.find_element_by_css_selector(f'#funcLeftForm\:yobiPanel{c}_toggler > span').click()
      classes = driver.find_elements_by_css_selector(f'#funcLeftForm\:yobiPanel{c}_content > div.classList')
      count_class.append(len(classes))
      time.sleep(1)


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
