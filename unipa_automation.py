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
import re
import pandas as pd
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
   # ポップアップメッセージを削除するため
   options.add_experimental_option('excludeSwitches', ['enable-logging'])
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

   # 曜日を取得
   week = driver.find_element_by_class_name('dateDisp').text
   week = re.search(r'\((.+)\)', week).group(1)

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

#    # 次の授業が押せなくなったら終了
#    while True:
#       time.sleep(1)
#       # 講義名を取得する
#       lecture = driver.find_element_by_class_name('cpTgtName').text
#       lecture = re.search(r'[0-9]+(.+) ((.+))', lecture).group(1)
#       print(lecture)
#       # 何の科目か知りたい場合
#       # subject = re.search(r'[0-9]+(.+) ((.+))', lecture).group(2)

#       # 課題提出状況を確認する
#       elements = driver.find_elements_by_css_selector(".ui-button-text.ui-c")
#       # もっとスマートな方法があれば...
#       for element in elements:
#          if element.text == '課題提出':
#                element.click()
#                break

#       # 2ページ以上の可能性があるので考慮する必要がある
#       i = 0
#       dfs = []
#       while True:
#          time.sleep(1)
#          i += 1
#          try:
#                driver.find_element_by_xpath(f'//*[@id="funcForm:gakKdiTstList_paginator_bottom"]/span[4]/span[{i}]').click()
#          except:
#                break
#          # 選択した講義の課題が残っているのかを調べるためにデータフレームにする
#          table = driver.find_element_by_css_selector("#funcForm\:gakKdiTstList > div.ui-datatable-tablewrapper > table")
#          html = table.get_attribute('outerHTML')
#          df_table = pd.read_html(html)
#          dfs.append(df_table[0])
#       # データフレームから必要な情報を取得する
#       if len(dfs) >= 2:
#          df = pd.concat(dfs)
#       elif len(dfs) == 1:
#          df = dfs[0]
#       else:
#         df = pd.DataFrame(columns = ['課題グループ名', '課題名', '種別', '承認状態', 'コース', '目次', '課題提出開始日時', '課題提出終了日時',
#        '提出方法', 'ステータス', '未提出', '提出回数', '再提出回数', '再提出期限', '提出日時', '点数', '未確認',
#        'Good', 'No good', '他の提出者'])
#       # 未提出の課題数を取得する
#       print(len(df[df['未提出'] == "○"]))
    
      
#       #　次の授業があるかを判定
#       if driver.find_elements_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right') == []:
#          break
#       # 次の授業を押す
#       driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right').click()

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