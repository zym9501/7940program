# INTRODUCTION
This project will create a Line bot, which may contain follow factor:

* It will works as a public health care helper (instead of personal health care).
* It may contains some constraints below:
* The bot will be able to differentiate at least 2 different types of queries and give 2 different types of responses.
* The bot will use a redis server to store some persistent information.
* The bot may use consume another service other than redis.
* The bot will be running on Heroku, or an equivalent cloud.
* The design concept of the bot may be applicable to our society while the content (e.g. answer of questions, reported data) need not to be accurate, most updated, nor comprehensive.
* The bot will use git for version controls.
* The LINE bot will be written only with Python and its library.

## news api 
The first one we want to create is a reponses of public health care news, it may alow customes can konw the news happended recently. In preliminary investigation, We want to use [news api] or [google news api]. [new api] can provide new in josn when we apply in url.get; And [google news api] can return the results of key word in google. In this program we want bot return the top 3 daily news about health in CHINA. But there are still some problems. In [news api] we don't kown if it can work without registion. And [google news api] is an abandoned servers though it still works now.

```
In conclution we prefer using [news api], we will try to build connect with heroku and new api fristly.
```

## XXX api
Another one we want to do is......