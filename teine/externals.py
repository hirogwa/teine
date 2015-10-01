from requests_oauthlib import OAuth1Session
import base64
import json
import urllib.parse
import urllib.request

from teine import settings


def twitter_user(screen_name):
    params = urllib.parse.urlencode({
        'screen_name': screen_name
    })
    req = urllib.request.Request(
        '%s?%s' % (settings.TWITTER_URL_USER_SHOW, params))
    req.add_header('Authorization', 'Bearer %s' % twitter_app_only_token)
    resp = urllib.request.urlopen(req)
    return response_to_dict(resp)


def twitter_user_search(query):
    params = urllib.parse.urlencode({
        'q': query
    })

    oauth_session = create_oauth_session()
    resp = oauth_session.get(settings.TWITTER_URL_USER_SEARCH, params=params)
    if resp.status_code != 200:
        print ("status code: %s" % resp.status_code)
        return None
    return json.loads(resp.text)


def get_twitter_app_only_token():
    concated = '%s:%s' % (
        urllib.parse.quote_plus(settings.TWITTER_CONSUMER_KEY),
        urllib.parse.quote_plus(settings.TWITTER_CONSUMER_SECRET))

    auth_header_str = base64.b64encode(str.encode(concated)).decode('utf-8')

    req = urllib.request.Request(
        settings.TWITTER_URL_TOKEN,
        data=b'grant_type=client_credentials', method='POST')
    req.add_header('Authorization', 'Basic %s' % auth_header_str)
    req.add_header(
        'Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')

    resp = urllib.request.urlopen(req)
    return response_to_dict(resp).get('access_token')


def create_oauth_session():
    return OAuth1Session(
        settings.TWITTER_CONSUMER_KEY,
        settings.TWITTER_CONSUMER_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_SECRET
    )


def response_to_dict(resp):
    return json.loads(
        resp.read().decode(resp.headers.get_content_charset()))

twitter_app_only_token = get_twitter_app_only_token()
