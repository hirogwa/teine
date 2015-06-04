from flask import Flask, Response, render_template, request, redirect
from bs4 import BeautifulSoup
import json
import os
import urllib.error
import urllib.parse
import urllib.request

import externals
import models
import settings
import s3_store

app = Flask(__name__)


@app.route('/show/<show_id>', methods=['GET', 'POST'])
def show_editor(show_id):
    if 'GET' == request.method:
        if show_id == 'new':
            return render_template('show.html')
        else:
            return render_template('show.html', show_id=show_id)

    if 'POST' == request.method:
        # TODO
        user = models.User.create_test_user()
        show = models.Show.create_new(user, **request.get_json())
        show.save()
        return json_response(show.export())


@app.route('/show_data', methods=['GET'])
def show_data():
    if 'GET' == request.method:
        show_id = request.args['show_id']
        # TODO
        user = models.User.create_test_user()
        show = models.Show.get_by_id(show_id, user)
        return json_response(show.export())


@app.route('/episode', methods=['GET', 'POST'])
def episode():
    if 'POST' == request.method:
        print(request.form)
        print(request.args)
        print(request.get_json())
        return 'post_data'

    if 'GET' == request.method:
        return render_template('episode.html')


@app.route('/media', methods=['POST'])
def media():
    if 'POST' == request.method:
        uploaded_file = request.files['file']

        temp_f = temp_filepath(uploaded_file.filename)

        uploaded_file.save(temp_f)
        s3_store.set_key_public_read(uploaded_file.filename, temp_f)

        return json_response({
            'result': 'success'
        })


@app.route('/media/<media_id>', methods=['GET'])
def retrieve_media(media_id):
    return redirect(
        urllib.parse.urljoin(
            settings.S3_HOST, '%s/%s' % (settings.S3_BUCKET_NAME, media_id)))


@app.route('/link-info', methods=['GET'])
def link_info():
    try:
        req = urllib.request.Request(request.args['url'], method='GET')
        resp = urllib.request.urlopen(req)
    except ValueError:
        return json_response({
            'result': 'error',
            'reason': 'bad url'
        })
    except urllib.error.URLError:
        result = {
            'result': 'error',
            'reason': 'no exist'
        }
        return json_response(result)

    if resp.status == 200:
        content = resp.read()
        soup = BeautifulSoup(content)
        title = soup.title
        result = {
            'result': 'success',
            'title': title.string if title else ''
        }
    else:
        result = {
            'result': 'error',
            'response_code': 'resp.status'
        }
    return json_response(result)


@app.route('/personality', methods=['GET', 'POST'])
def personality():
    if 'GET' == request.method:
        pass

    if 'POST' == request.method:
        pass


@app.route('/twitter-user', methods=['GET'])
def twitter_user():
    user = externals.twitter_user(request.args['screen_name'])
    return json_response({
        'name': user.get('name'),
        'description': user.get('description'),
        'profile_image_url_original': (
            user.get('profile_image_url').replace('_normal', '_400x400'))
    })


@app.route('/twitter-user-search', methods=['GET'])
def twitter_user_search():
    users = externals.twitter_user_search(request.args['q'])
    return json_response(
        users
    )


@app.route('/ping', methods=['GET'])
def ping():
    return 'sup'


@app.route('/explorer', methods=['GET'])
def explorer():
    return render_template('explorer.html')


def temp_filepath(filename):
    if not os.path.exists(settings.TEMP_FILES_DIR):
        os.makedirs(settings.TEMP_FILES_DIR)
    return os.path.join(settings.TEMP_FILES_DIR, filename)


def json_response(dict_data):
    return Response(json.dumps(dict_data), mimetype='application/json')


if __name__ == '__main__':
    app.debug = True
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
