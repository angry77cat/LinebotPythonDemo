# import 必要的函式庫
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
import os
import requests
import json

line_bot_api = LineBotApi(os.getenv('ChannelAccessToken'))
parser = WebhookParser(os.getenv('ChannelSecret'))
# print(os.getenv('ChannelSecret'))

def get_answer(message_text):
    
    url = "https://dogidogi.azurewebsites.net/qnamaker/knowledgebases/a2c5c87b-7005-413b-aa58-0af23bcf8f8e/generateAnswer"

    # 發送request到QnAMaker Endpoint要答案
    response = requests.post(
                   url,
                   json.dumps({'question': message_text}),
                   headers={
                       'Content-Type': 'application/json',
                       'Authorization': 'EndpointKey f50c132b-2076-4576-b073-8e2c567d3f54'
                   }
               )

    data = response.json()

    try: 
        #我們使用免費service可能會超過限制（一秒可以發的request數）
        if "error" in data:
            return data["error"]["message"]
        #這裡我們預設取第一個答案
        answer = data['answers'][0]['answer']

        return answer

    except Exception:

        return "Error occurs when finding answer"

@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                answer = get_answer(event.message.text)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=answer)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()