# -*- choding : utf-8 -*-

from enum import unique
from types import MethodDescriptorType
from typing import Text
from flask import Flask, request, abort,render_template,make_response,redirect
from datetime import datetime 

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    PostbackEvent, PostbackTemplateAction, TemplateSendMessage,
    ButtonsTemplate, FollowEvent, MessageAction, RichMenu, RichMenuArea,
    RichMenuBounds, RichMenuSize, URIAction, actions, messages
)
from linebot.models.template import CarouselColumn, CarouselTemplate
from werkzeug.utils import validate_arguments
from unipa_automation import getInfoFromUnipa,check_login
import os
import json
import dotenv 
import requests
dotenv.load_dotenv("./data/.env")

app = Flask(__name__)
app.secret_key = os.environ["secret"]
# カレントディレクトリのenvfileを使用

UserID = os.environ["USERID"]
PassWord = os.environ["PASS"]
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])



@app.route("/user/<user_id>")
def userlog(user_id):
    username = GetDisplayName(user_id)
    # 初めて使う場合のニックネームの設定
    resp= make_response(render_template('index.html',username=username))
    max_age= 60*60*24*3
    resp.set_cookie("username",value=str(user_id),max_age=max_age)
    return resp

@app.route("/try_login",methods=["POST"])
def try_login():
   # cookieで情報を保存しておく
   user = request.form["username"]
   pas = request.form["password"]
   eml = request.form["email"]
   slb = request.form["slabel"]
   user_info = {"user":str(user),"pass":str(pas),"email":str(eml),"slabel":str(slb)}
   # cookieで保存(30日間保存)
   resp = make_response(render_template("index.html"))
   max_age = 60*60*24*30
   resp.set_cookie("user_info",value=json.dumps(user_info),max_age=max_age)
   return render_template("mypage.html")

@app.route("/check_login")
def checklog():
   # ログイン情報の確認
   username=request.cookies.get("username")
   user_info = request.cookies.get("user_info")
   jsn = json.loads(user_info)
   print(jsn)
   userID = jsn["user"]
   PassWord = jsn["pass"]
   # ここ↓で止まってしまう

   if check_login(userID,PassWord):
      return redirect("/try_login")
   else:
      return redirect(f"/user/{username}")  
    
# webhook用コールバック関数
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# メッセージを受け取った時のアクション
@handler.add(MessageEvent, message=TextMessage)
def send_infomation(event):
    user_id = event.source.user_id
    
    if event.message.text == '課題は？':
        df_rest = getInfoFromUnipa(userID=UserID, PassWord=PassWord)
        rest_list=["残りの課題はこちらです"]
        for _,v in df_rest.iterrows():
            kadai = v["課題名"]
            sime = v["課題提出終了日時"]
            state=v["ステータス"]
            rest_list.append(f"課題名 : {kadai}\n締切日 : {sime}\nステータス : {state}\n")
        rest_homework="\n".join(rest_list)
        line_bot_api.push_message(
        to=user_id,
        messages=TextSendMessage(text=rest_homework)
        )
    elif event.message.text=="ボタン":
        send_button(event=event,user_id=user_id)
    elif event.message.text=="イベント":
        show_carousel(user_id)
    else:
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text=event.message.text+"は理解不能")
        )

# 友達追加・ブロック解除時のアクション
@handler.add(FollowEvent)
def on_follow(event):
    return 

# ボタンの反応があった時のアクション
@handler.add(PostbackEvent)
def on_postback(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    postback_msg = event.postback.data

    if postback_msg == "is_show=1":
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text="is_showオプション1を選択")
        )
    elif postback_msg == "is_show=0":
        line_bot_api.push_message(
            to = user_id,
            messages=TextSendMessage(text="is_showオプション0を選択")
        )
    else:
        line_bot_api.push_message(
            to=user_id,
            messages=TextSendMessage(text=postback_msg)
        )

# ログインサイトにcookieを保存
@app.route("/try_login",methods=["POST"])
def try_login():
   user = request.form["username"]
   pas = request.form["password"]
   eml = request.form["email"]
   slb = request.form["slabel"]
   user_info = {"user":str(user),"pass":str(pas),"email":str(eml),"slabel":str(slb)}
   # cookieで保存(30日間保存)
   resp = make_response(render_template("index.html"))
   max_age = 60*60*24*30
   resp.set_cookie("user_info",value=json.dumps(user_info),max_age=max_age)
   return render_template("mypage.html")

def cookie_check():
   try:
      user_info = request.cookies.get("user_info")
      print(user_info)
      return user_info
   except:
      return None


# ボタンテンプレート生成
def send_button(event,user_id):
    message_template=ButtonsTemplate(
        text="Please select",
        title="select!",
        actions=[
            PostbackTemplateAction(
                label="ON",
                data="is_show=1"
            ),
            URIAction(
                label="get LOGIN!",
                uri=f"https://cef1-210-137-33-126.ngrok.io/user/{user_id}"
            )
        ]
    )
    # ボタンテンプレートを選択して送信
    line_bot_api.push_message(
        to=user_id,
        messages=TemplateSendMessage(
            alt_text="Buttons template",
            template=message_template
        )
    )

# カーセルのテスト
def show_carousel(user_id):
    # メッセージテンプレートの内容(collumn)を作成
    carousel_collumns=[
        CarouselColumn(
            text=value,
            title = value+"通知",
            actions=[
                PostbackTemplateAction(
                    label="ON",
                    data=value+"1",
                ),
                PostbackTemplateAction(
                    label="OFF",
                    data=value+"0",
                )
            ]
        ) for key,value in (zip(
            ("取引所","取引所","取引所","取引所","取引所"),
            ("Binance","kuCoin","Hupbipro","Ploniex","Bittrex")
        ))
    ]
    # メッセージテンプレート作成
    message_template = CarouselTemplate(columns=carousel_collumns)
    line_bot_api.push_message(
        to=user_id,
        messages=TemplateSendMessage(alt_text="carousel template",template=message_template)
    )   


# ユーザーidから表示名を取得
def GetDisplayName(user_id):
    access = os.environ["CHANNEL_ACCESS_TOKEN"]
    headers = {
        "Authorization": f"Bearer {access}"
    }
    response = requests.get(f"https://api.line.me/v2/bot/profile/{user_id}",headers=headers)
    return response

if __name__ == "__main__":
    app.run(port=8000)