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
import time 
import requests 
import os 
import dotenv
# カレントディレクトリのenvfileを使用
dotenv.load_dotenv("./info/.env")

############編集を行う###############
UserID = "{ userid }"
PassWord = "{ pass }"
####################################

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

   # 掲示板を探しに行く
   WebDriverWait(driver,timeout=15).until(EC.presence_of_element_located((By.XPATH,'//*[@id="menuForm:mainMenu"]/ul/li[1]/a')))
   driver.find_element_by_xpath('//*[@id="menuForm:mainMenu"]/ul/li[1]/a').click()
   WebDriverWait(driver,timeout=15).until(EC.presence_of_element_located((By.XPATH,'//*[@id="funcForm:tabArea"]/ul/li[5]/a')))
   driver.find_element_by_xpath('//*[@id="funcForm:tabArea"]/ul/li[5]/a').click()

   # 25件を超える場合に全表示を使う
   if driver.find_element_by_xpath('//*[@id="funcForm:tabArea:4:j_idt403"]'):
      driver.find_element_by_xpath('//*[@id="funcForm:tabArea:4:j_idt403"]').click()
   else:
      pass
   div_class = driver.find_elements_by_class_name('alignRight')
   # 今の段階だと特定の課題のみしか抜き出せない
   print(div_class)

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
