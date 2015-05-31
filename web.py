from flask import Flask, Response, render_template, request, redirect
import json
import os
import urllib.parse

import externals
import settings
import s3_store

app = Flask(__name__)


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


@app.route('/twitter-user', methods=['GET'])
def twitter_user():
    user = externals.twitter_user(request.args['screen_name'])
    return json_response({
        'name': user.get('name'),
        'description': user.get('description'),
        'profile_image_url': (
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
