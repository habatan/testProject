# -*- coding: utf-8 -*-
# このファイルを編集する
# ユニパの情報取得を自動化していく
# 事前にselenium一式とchromedriverが必要
from selenium.webdriver import Chrome,ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# 例外処理用の便利なライブラリ
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import pandas as pd 
import time 
import requests 
import os 
import dotenv
# カレントディレクトリのenvfileを使用
dotenv.load_dotenv("./info/.env")

# sysを使ってuserIDとpassはターミナルの引数にしてもええかも(もしくはjsonファイルかtxtファイルにする)
UserID = os.environ["USERID"]
PassWord = os.environ["PASS"]
token = os.environ["TOKEN"]

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
   # 課題提出フォームに飛ぶ
   driver.find_element_by_css_selector('#funcForm\:j_idt329\:1\:j_idt331').click()
   time.sleep(2)

   #　授業名と残りの課題数
   class_name =[]
   rest_task = []
   df_list =[]
   # 前の授業に戻るボタン
   btn = driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-left')
   # 戻る段階(flag=0)進む段階(flag=1)とする
   flag = 0
   while btn:
      time.sleep(1)
      # 授業名取得
      name = driver.find_element_by_css_selector('.cpTgtName').text[6:-9].replace("\n","")
      if name not in class_name:
         class_name.append(name)
         # 未提出選択をclick
         driver.find_element_by_css_selector('.ui-chkbox-icon.ui-icon.ui-icon-blank.ui-c').click()
         # 検索ボタンをクリック
         driver.find_element_by_css_selector('.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only.btnSearch.btnAltColorSearch.btnL').click()
         # 残りの課題数を確認
         time.sleep(1.5)
         num_task = driver.find_elements_by_css_selector(".ui-paginator-current")
         # dataframeの作成
         html= driver.page_source
         df = pd.read_html(html)
         df_list.append(df[1])
         # リストに押し込む
         rest_task.append(num_task[1].text)
      # ラストの場合終了
      if flag ==2:
         driver.close()
         break
      # 次のページへ遷移
      btn.click()
      time.sleep(1)
      try:
         if flag==0:
            # 戻るボタン
            btn = driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-left')
         else:
            # 進むボタン
            btn = driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right')        
      except:
         # 戻るボタン->進むボタン切り替え
         if flag==0:
            flag = 1
            btn = driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right')
         # 最後は"進むボタン"->ラスト切り替え
         else:
            btn = True
            flag = 2
   # ここからdataframeの整形
   all_df = pd.concat(df_list)
   rest_task_df=all_df[(all_df["課題名"]!="対象データがありません。")&(all_df["未提出"]=="○")]
   rest_task_df.sort_values("課題提出終了日時")

   # とりあえず送れるようにする
   start = ["課題名 : 課題提出日時"]
   for i,v in rest_task_df.iterrows():
      start.append(f'{v["課題名"]} : {v["課題提出終了日時"]}')
   text="\n".join(start)
   # まとめたtextを送信
   print(sendMessage(text))

      
# linenotify通知関数
def sendMessage(msg:str)->str:
   # linenotfy通知系apiをたたく
   URL="https://notify-api.line.me/api/notify"
   payload = {
      "message":msg
   }
   headers={
      "Authorization":"Bearer "+token
   }
   response=requests.post(URL,params=payload,headers=headers)
   return response.text


if __name__ == "__main__":
   main()