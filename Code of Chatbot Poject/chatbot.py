from __future__ import unicode_literals

import os
import sys
import redis

import random
import requests
from argparse import ArgumentParser
from bs4 import BeautifulSoup

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
    )
from linebot.exceptions import (
    InvalidSignatureError
    )
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage,VideoSendMessage,PostbackTemplateAction,
    MessageTemplateAction,URITemplateAction
)

from linebot.utils import PY3

# Init redis (ZHAN YUMIN)
HOST = "redis-13885.c82.us-east-1-2.ec2.cloud.redislabs.com"
PWD = "IKNUEeoxuV5d2PvQZ6OKZ9SKupbZykSi"
PORT = "13885" 

redis1 = redis.Redis(host=HOST, password=PWD, port=PORT)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handle_TextMessage(event)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'


#Crawl news (ZHNA YUMIN)
def get_News():

    url="https://www.news-medical.net/category/Healthcare-News.aspx"
    whoPage = requests.get(url)
    who = BeautifulSoup(whoPage.text, 'lxml')
    who_layout = who.find('div',{'class':'posts publishables-list-wrap first-item-larger'})
    who_list = who_layout.find_all('div', {'class': 'row'})

    list_news = []
    for news in who_list:
    
        img_obj = news.find('div',{'class':'col-xs-3'})
        content_obj = news.find('div',{'class':'col-xs-9'})
        if img_obj and content_obj:
            news_link = img_obj.find('a')
            link_addr = 'https://www.news-medical.net'+news_link['href']
            news_imgUrl = img_obj.find('img')
            news_title = content_obj.find('h3')
            news_content = content_obj.find('p',{'class':'hidden-xs item-desc'})
            news_title_text = news_title.get_text()
            news_content_text = news_content.get_text()
            if len(news_title_text )> 38:
                news_title_text = news_title_text[0:37]
                news_title_text += '..'

            if len(news_content_text )>38:
                news_content_text = news_content_text[0:37]
                news_content_text+='..'

            list_news.append([link_addr,news_imgUrl['src'],news_title_text,news_content_text])
    return list_news

#Read date from redis(ZHAN YUMIN)
def read_redis():
    if redis1.ttl('hot_news') < 0:
        news_list = get_News()
        for new in news_list:
            redis1.sadd("hot_news_link", new[0])
            redis1.sadd("hot_news_img", new[1])
            redis1.sadd("hot_news_title", new[2])
            redis1.sadd("hot_news_intro", new[3])
        redis1.expire("hot_news_link", 21600)
        redis1.expire("hot_news_title", 21600)
        redis1.expire("hot_news_img", 21600)
        redis1.expire("hot_news_intro", 21600)

    hot_news_link = redis1.smembers('hot_news_link')
    hot_news_img = redis1.smembers('hot_news_img')
    hot_news_title = redis1.smembers('hot_news_title')
    hot_news_intro = redis1.smembers('hot_news_intro')
    return [list(hot_news_link),list(hot_news_img),list(hot_news_title),list(hot_news_intro)]



# Handler function for Text Message
def handle_TextMessage(event):
# Check if user want to know news (ZHAN YUMIN)
    if 'news' == event.message.text.lower():
        hot_news = read_redis()
        message = TemplateSendMessage(
            alt_text='Hot news about the coronavirus',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=str(hot_news[1][0],encoding='utf-8'),
                        title=str(hot_news[2][0],encoding='utf-8'),
                        text=str(hot_news[3][0],encoding='utf-8'),
                        actions=[
                            URIAction(
                                uri=str(hot_news[0][0],encoding='utf-8'), 
                                label='View More')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=str(hot_news[1][1],encoding='utf-8'),
                        title=str(hot_news[2][1], encoding='utf-8'),
                        text=str(hot_news[3][1], encoding='utf-8'),
                        actions=[
                            URIAction(
                                uri=str(hot_news[0][1], encoding='utf-8'), 
                                label='View More')
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=str(hot_news[1][2], encoding='utf-8'),
                        title=str(hot_news[2][2], encoding='utf-8'),
                        text=str(hot_news[3][2], encoding='utf-8'),
                        actions=[
                            URIAction(
                                uri=str(hot_news[0][2], encoding='utf-8'), 
                                label='View More')
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            message
        )

    else:# ZHOU XI HANG
        GOOGLE_API_KEY = 'AIzaSyAH5qFJ9JfgCdblC-6Y282wFMxCXA6TeHM' # due to confidentiality, it will not be published on GitHub

        address = event.message.text
        addurl = 'https://maps.googleapis.com/maps/api/geocode/json?key={}&address={}&sensor=false'.format(GOOGLE_API_KEY,address)

        #get current location
        addressReq = requests.get(addurl)
        addressDoc = addressReq.json()
        lat = addressDoc['results'][0]['geometry']['location']['lat']
        lng = addressDoc['results'][0]['geometry']['location']['lng']
    
        #get pharmacies around this location
        pharmacySearch = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=pharmacy&language=en-US'.format(GOOGLE_API_KEY,lat,lng)
        pharmacyReq = requests.get(pharmacySearch)
        nearby_pharmacy_dict = pharmacyReq.json()

        #put the searching result into top20_pharmacy as a list
        top20_pharmacy = nearby_pharmacy_dict['results']
        res_num = (len(top20_pharmacy))

        #get the pharmacy whose rating is beyond 3 
        bravo=[]
        for i in range(res_num):
            try:
                if top20_pharmacy[i]['rating'] >= 3.9:
                    print('rating',top20_pharmacy[i]['rating'])
                    bravo.append(i)
            except:
                KeyError
        # if all pharmacies' rating are lower than 3, randomly choose one
        if len(bravo) < 0:
            content = 'there is no pharmacies around'
            pharmacy = random.choice(top20_pharmacy) 
        #or choose from bravo list
        else:
            pharmacy = top20_pharmacy[random.choice(bravo)] 
        
        #check the photo of this pharmacy
        if pharmacy.get('photos') is None:
            thumbnail_image_url = None
        else:
        #if has photos, choose one
            photo_reference = pharmacy['photos'][0]['photo_reference']
            photo_width = pharmacy['photos'][0]['width']
            thumbnail_image_url = 'https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth={}'.format(GOOGLE_API_KEY,photo_reference,photo_width)
    

        rating = 'no rating' if pharmacy.get('rating') is None else pharmacy['rating']
        address = 'No info' if pharmacy.get('vicinity') is None else pharmacy['vicinity']
        details = pharmacy['name']
        #the url of current map
        map_url = "http://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(lat=pharmacy['geometry']['location']['lat'],long=pharmacy["geometry"]['location']['lng'],place_id=pharmacy['place_id'])
        print(pharmacy['name'])

        #reply template
        buttons_template = TemplateSendMessage(
            alt_text = pharmacy['name'],
            template = ButtonsTemplate(
                thumbnail_image_url = thumbnail_image_url,
                title = 'Recommended for you',
                text = details,
                actions = [
                    URITemplateAction(
                        label='Go',
                        uri = map_url,
                    ),
                ]
            ) 
        )

        line_bot_api.reply_message(
            event.reply_token,
            buttons_template
        )

# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

# Handler function for Image Message
def handle_ImageMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice image!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice video!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	TextSendMessage(text="Nice file!")
    )

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
