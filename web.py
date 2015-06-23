from flask import Flask, Response, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import html
import flask_login
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
import uuid

import externals
import models
import settings
import s3_store

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return models.User.get_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'POST' == request.method:
        args = request.form
        username = args.get('username')
        password = args.get('password')
        user = models.User.get_by_credentials(username, password)
        if user:
            flask_login.login_user(user)
        return redirect(url_for('login'))

    if 'GET' == request.method:
        if flask_login.current_user.is_authenticated():
            return redirect(url_for('dashboard'))
        return render_template('login.html')


@app.route('/logout', methods=['GET'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET'])
@flask_login.login_required
def dashboard():
    kwargs = dashboard_template_args(sidebar_show='active')
    return render_template('dashboard-show.html', **kwargs)


@app.route('/show/new', methods=['GET'])
@flask_login.login_required
def page_create_show():
    return page_show()


@app.route('/show/<show_id>', methods=['GET'])
@flask_login.login_required
def page_load_show(show_id):
    return page_show(show_id, {'result': request.args.get('updated')})


def page_show(show_id=None, updated=None):
    kwargs = dashboard_template_args(sidebar_show='active')
    if show_id:
        kwargs['show_id'] = show_id
        kwargs['updated'] = updated
    return render_template('dashboard-show.html', **kwargs)


@app.route('/profile', methods=['GET'])
@flask_login.login_required
def page_profile():
    kwargs = dashboard_template_args(sidebar_profile='active')
    kwargs['user_id'] = flask_login.current_user.user_id
    return render_template('dashboard-profile.html', **kwargs)


@app.route('/profile-data', methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    if 'GET' == request.method:
        return json_response({
            'result': 'success',
            'user': flask_login.current_user.export()
        })
    if 'POST' == request.method:
        userData = models.User(**request.get_json())
        if flask_login.current_user.user_id == userData.user_id:
            return json_response({
                'result': 'success',
                'user': userData.save().export()
            })
        else:
            raise ValueError


@app.route('/show', methods=['GET', 'POST'])
@flask_login.login_required
def show():
    if 'GET' == request.method:
        user = flask_login.current_user
        show = models.Show.get_by_id(user.get_show_id()).load_hosts()
        return json_response(show.export())

    if 'POST' == request.method:
        user = flask_login.current_user
        in_data = request.get_json()

        in_data['show_host_ids'] = list(map(
            lambda x: get_personality(x).personality_id,
            in_data.get('show_hosts')))

        if in_data['show_id']:
            show = models.Show(owner_user_id=user.user_id, **in_data)
        else:
            show = models.Show.create_new(
                owner_user_id=user.user_id, **in_data)
        show.save()
        return json_response({
            'result': 'success',
            'show': show.export()
        })


@app.route('/show-image', methods=['GET', 'POST'])
@flask_login.login_required
def upload_show_image():
    image_id = flask_login.current_user.get_show_id()
    if 'POST' == request.method:
        uploaded_file = request.files['file']
        temp_f = temp_filepath(uploaded_file.filename)
        uploaded_file.save(temp_f)

        s3_store.set_key_public_read(image_id, temp_f)

        return json_response({
            'result': 'success',
            'image_id': image_id
        })

    if 'GET' == request.method:
        return redirect(
            urllib.parse.urljoin(
                settings.S3_HOST,
                '%s/%s' % (settings.S3_BUCKET_NAME, image_id)))


@app.route('/episode/new', methods=['GET'])
@flask_login.login_required
def page_create_episode():
    return page_episode()


@app.route('/episode/copy/<episode_id>', methods=['GET'])
def page_copy_episode(episode_id):
    return page_episode(episode_id, True)


@app.route('/episode/<episode_id>', methods=['GET', 'DELETE'])
@flask_login.login_required
def page_load_episode(episode_id):
    if 'GET' == request.method:
        return page_episode(episode_id)
    if 'DELETE' == request.method:
        ep = models.Episode.get_by_id(episode_id)
        if ep.media_id:
            ep.media.dissociate_episode().save()
        ep.delete()
        return json_response({
            'result': 'success'
        })


def page_episode(episode_id=None, copy_mode=False):
    kwargs = dashboard_template_args(sidebar_episodes='active')
    if episode_id:
        kwargs['episode_id'] = episode_id
        kwargs['copy_mode'] = 'true' if copy_mode else 'false'
    return render_template('dashboard-episode.html', **kwargs)


@app.route('/episode-list', methods=['GET'])
@flask_login.login_required
def episode_list():
    kwargs = dashboard_template_args(
        sidebar_episodes='active', notify=request.args.get('notify'))
    return render_template('dashboard-episode-list.html', **kwargs)


@flask_login.login_required
def dashboard_template_args(**kwargs):
    user = flask_login.current_user
    result = {
        'show_id': user.get_show_id() or 'new'
    }
    for k, v in kwargs.items():
        result[k] = v
    return result


def get_personality(g):
    user = flask_login.current_user
    return models.Personality.find_by_twitter(
        g.get('alias'), user.get_show_id(), True, **g)


@app.route('/episode', methods=['GET', 'POST'])
@flask_login.login_required
def episode():
    if 'POST' == request.method:
        in_data = request.get_json()
        user = flask_login.current_user

        in_data['guest_ids'] = list(map(
            lambda x: get_personality(x).personality_id,
            in_data.get('guests')))
        in_data['links'] = map(
            lambda x: models.Link(**x), in_data.get('links'))

        ep_id = in_data.get('episode_id')
        if ep_id:
            ep = models.Episode(show_id=user.get_show_id(), **in_data)
            original = models.Episode.get_by_id(ep_id)
            if original.media_id != ep.media_id and original.media_id:
                original_model = models.Media.get_by_id(original.media_id)
                original_model.dissociate_episode().save()
        else:
            ep = models.Episode.create_new(
                show_id=user.get_show_id(), **in_data)

        if ep.media_id:
            model = models.Media.get_by_id(ep.media_id)
            model.associate_episode(ep.episode_id).save()

        ep.save()

        return json_response({
            'result': 'success',
            'episode': ep.export()
        })

    if 'GET' == request.method:
        ep = models.Episode.get_by_id(request.args['episode_id'])
        result = {
            'episode': ep.export()
        }
        if ep.media_id:
            result['media'] = models.Media.get_by_id(ep.media_id).export()
        return json_response(result)


@app.route('/episodes', methods=['GET'])
@flask_login.login_required
def episodes():
    if 'GET' == request.method:
        return json_response(list(map(
            lambda x: x.export(), models.Episode.get_list())))


@app.route('/upload-media', methods=['POST'])
@flask_login.login_required
def upload_media():
    uploaded_file = request.files['file']
    temp_f = temp_filepath(uploaded_file.filename)

    user = flask_login.current_user
    uploaded_file.save(temp_f)
    media_info = {
        'content_type': uploaded_file.headers.get('Content-Type'),
        'size': os.stat(temp_f).st_size
    }
    media = models.Media.create_new(
        user.user_id, uploaded_file.filename, **media_info)

    s3_store.set_key_public_read(media.media_id, temp_f)
    media.save()

    return json_response({
        'result': 'success',
        'media': media.export()
    })


@app.route('/delete-media', methods=['POST'])
@flask_login.login_required
def delete_media():
    media_id = request.form['media_id']
    media = models.Media.get_by_id(media_id)
    if media:
        media.delete()
        result = {
            'result': 'success'
        }
    else:
        result = {
            'result': 'error',
            'reason': 'media not found'
        }
    return json_response(result)


@app.route('/media', methods=['GET'])
@flask_login.login_required
def page_media():
    kwargs = dashboard_template_args(sidebar_media='active')
    return render_template('dashboard-media.html', **kwargs)


@app.route('/media/<media_id>', methods=['GET'])
@flask_login.login_required
def download_media(media_id):
    return redirect(
        urllib.parse.urljoin(
            settings.S3_HOST, '%s/%s' % (settings.S3_BUCKET_NAME, media_id)))


@app.route('/media-list', methods=['GET'])
@flask_login.login_required
def retrieve_media_list():
    media_list = models.Media.get_list(flask_login.current_user.user_id)
    filter_param = request.args.get('filter')
    if filter_param == 'unused':
        media_list = filter(
            lambda x: not x.associated_with_episode(), media_list)
    if filter_param == 'used':
        media_list = filter(
            lambda x: x.associated_with_episode(), media_list)
    return json_response(map(
        lambda x: x.export_with_episode_summary(), media_list))


@app.route('/link-info', methods=['GET'])
@flask_login.login_required
def link_info():
    try:
        req = urllib.request.Request(request.args['url'], method='GET')
        resp = urllib.request.urlopen(req, timeout=5)

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
    except ValueError:
        result = {
            'result': 'error',
            'reason': 'bad url'
        }
    except urllib.error.URLError:
        result = {
            'result': 'error',
            'reason': 'no exist'
        }
    except socket.timeout:
        result = {
            'result': 'error',
            'reason': 'timeout'
        }

    return json_response(result)


@app.route('/personality', methods=['GET', 'POST'])
@flask_login.login_required
def personality():
    if 'GET' == request.method:
        pass

    if 'POST' == request.method:
        pass


@app.route('/twitter-user', methods=['GET'])
@flask_login.login_required
def twitter_user():
    user = externals.twitter_user(request.args['screen_name'])
    return json_response({
        'name': user.get('name'),
        'description': user.get('description'),
        'profile_image_url_original': (
            user.get('profile_image_url').replace('_normal', '_400x400'))
    })


@app.route('/twitter-user-search', methods=['GET'])
@flask_login.login_required
def twitter_user_search():
    users = externals.twitter_user_search(request.args['q'])
    return json_response(
        users
    )


@app.route('/ping', methods=['GET'])
def ping():
    print(request.form)
    print(request.args)
    print(request.get_json())
    return 'sup'


@app.route('/explorer', methods=['GET'])
def explorer():
    return render_template('explorer.html')


def temp_filepath(filename):
    if not os.path.exists(settings.TEMP_FILES_DIR):
        os.makedirs(settings.TEMP_FILES_DIR)
    return os.path.join(settings.TEMP_FILES_DIR, filename)


def sanitized_output(d):
    if isinstance(d, dict):
        result = dict()
        for k, v in d.items():
            result[k] = sanitized_output(v)
        return result
    if isinstance(d, list):
        return [sanitized_output(x) for x in d]
    if isinstance(d, str):
        return html.escape(d)


def json_response(data):
    if type(data) is map:
        data = list(data)
    data = sanitized_output(data)
    return Response(json.dumps(data), mimetype='application/json')


if __name__ == '__main__':
    app.debug = True
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
