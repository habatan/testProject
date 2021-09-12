from enum import unique
from flask import Flask, request, abort
import os

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
    RichMenuBounds, RichMenuSize, URIAction
)
import dotenv
from unipa_automation import getInfoFromUnipa

app = Flask(__name__)
# カレントディレクトリのenvfileを使用
dotenv.load_dotenv("./info/.env")

UserID = os.environ["USERID"]
PassWord = os.environ["PASS"]
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

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
        df_rest = getInfoFromUnipa(UserID=UserID, PassWord=PassWord)
        # df_rest=df[(df["課題名"]!="対象データがありません。")&(df["未提出"]=="○")]
        rest_homework=[]
        for work_name in df_rest['講義名'].unique():
            rest_homework.append(work_name)
            rest_homework.append('----------')
            for lecture_name in df_rest[df_rest['講義名']==work_name]["課題名"]:
                rest_homework.append(lecture_name)
            rest_homework.append('======================')
        rest_homework = "\n".join(rest_homework)
        line_bot_api.push_message(
        to=user_id,
        messages=TextSendMessage(text=rest_homework)
        )
    else:
        line_bot_api.push_message(
        to=user_id,
        messages=TextSendMessage(text='申し訳ございませんがご利用できません')
        )

# 友達追加・ブロック解除時のアクション
@handler.add(FollowEvent)
def on_follow(event):
    return

# ボタンなどの反応があった時のアクション
@handler.add(PostbackEvent)
def on_postback(event):
    return
    
if __name__ == "__main__":
    app.run(host="localhost", port=8000)