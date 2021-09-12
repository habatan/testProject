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

# unipaのURL
URL = "https://unipa.u-hyogo.ac.jp/uprx/"
# driverのオプション設定
def getInfoFromUnipa(userID:str,PassWord:str):
   options = ChromeOptions()
   # chromedriverを作成
   options.headless = True
   driver = Chrome(options=options)
   driver.get(URL)
   WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="loginForm:userId"]')))

   # UserIDやPasswordの入力及び送信
   input_element_key1 = driver.find_element_by_xpath('//*[@id="loginForm:userId"]')
   input_element_key2 = driver.find_element_by_xpath('//*[@id="loginForm:password"]')
   botton = driver.find_element_by_xpath('//*[@id="loginForm:loginButton"]')
   input_element_key1.send_keys(userID)
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
      
   # 戻る段階(flag=0)進む段階(flag=1)とする
   flag = 0
   # 戻るボタンの有無を確認(月曜日の場合)
   try:
      btn=driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-left')
   except:
      btn = driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right')
      flag = 1

   while btn:
      time.sleep(1)
      # 授業名取得
      lecture = driver.find_element_by_css_selector('.cpTgtName').text[6:-9].replace("\n","")
      if lecture not in class_name:
         class_name.append(lecture)
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
         print(lecture+": "+num_task[1].text)
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
            # 進むボタンがあるか確認(金曜日か土曜日の場合)
            try:
               btn = driver.find_element_by_css_selector('.ui-button-icon-left.ui-icon.ui-c.fa.fa-fw.fa-caret-right')
               flag = 1
            except:
               driver.close()
               break     
         # 最後は"進むボタン"->ラスト切り替え
         else:
            btn = True
            flag=2
            
   # ここからdataframeの整形
   dfs = pd.concat(df_list)
   rest_task_df=dfs[(dfs["課題名"]!="対象データがありません。")&(dfs["未提出"]=="○")]
   rest_task_df.sort_values("課題提出終了日時")   
   return rest_task_df
