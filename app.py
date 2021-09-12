from enum import unique
from flask import Flask, request, abort
import os,dotenv
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
from unipa_automation import getInfoFromUnipa
# 環境ファイルの読み込み
dotenv.load_dotenv("./info/.env")

app = Flask(__name__)
# カレントディレクトリのenvfileを使用

UserID = os.environ["USERID"]
PassWord = os.environ["PASS"]
CHANNEL_ACCESS_TOKEN=os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEl_SECRET=os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEl_SECRET)

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
    app.run(port=8000)