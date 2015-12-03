from flask import Response, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import html
import flask_login
import json
import socket
import urllib.error
import urllib.parse
import urllib.request

from teine import (app, externals, settings,
                   episode_operations, audio_operations, photo_operations,
                   show_operations, user_operations)

app.secret_key = settings.SECRET_KEY

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return user_operations.get_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'GET' == request.method:
        if flask_login.current_user.is_authenticated():
            return _redirect_to_home()
        return render_template('signup.html')


@app.route('/user', methods=['GET', 'PUT', 'POST'])
def user():
    if 'GET' == request.method:
        if flask_login.current_user.is_authenticated:
            return json_response({
                'result': 'success',
                'user': flask_login.current_user.export()
            })
        else:
            return flask_login.current_app.login_manager.unauthorized()

    if 'PUT' == request.method:
        if flask_login.current_user.is_authenticated:
            args = request.get_json()
            if flask_login.current_user.user_id == args.get('user_id'):
                user = user_operations.update(**args)
                return json_response({
                    'result': 'success',
                    'user': user.export()
                })
            else:
                # someone else's profile
                raise ValueError
        else:
            return flask_login.current_app.login_manager.unauthorized()

    if 'POST' == request.method:
        args = request.get_json()
        user = None
        try:
            user = user_operations.signup(
                args.get('user_id'), args.get('password'), args.get('email'))
            flask_login.login_user(user)
            return json_response({
                'result': 'success',
                'user': user.export()
            })
        except user_operations.SignUpValidationException as e:
            return {
                'result': 'error',
                'message': e.message
            }, 500


@app.route('/validate-signup-entry', methods=['POST'])
def validateSignupEntry():
    if 'POST' == request.method:
        args = request.form
        try:
            user_operations.validateSignupEntryOrRaise(
                args.get('user_id'),
                args.get('password'),
                args.get('email'))
            return json_response({
                'result': 'success'
            })

        except user_operations.SignUpValidationException as e:
            return json_response({
                'result': 'error',
                'message': e.message
            })


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'POST' == request.method:
        args = request.form
        user = user_operations.get_by_credentials(
            args.get('username'), args.get('password'))
        if user:
            flask_login.login_user(user)
        return redirect(url_for('login'))

    if 'GET' == request.method:
        if flask_login.current_user.is_authenticated():
            return _redirect_to_home()
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


@app.route('/show', methods=['GET', 'POST', 'PUT'])
@flask_login.login_required
def show():
    if 'GET' == request.method:
        show_id = request.args['show_id']
        return json_response(
            show_operations.get_by_id(show_id).export(
                expand=['show_hosts', 'image']))

    user = flask_login.current_user
    in_data = request.get_json()

    if 'POST' == request.method:
        show = show_operations.create(user, **in_data)
        return json_response({
            'message': 'show created',
            'result': 'success',
            'show': show.export()
        })

    if 'PUT' == request.method:
        show = show_operations.update(user, **in_data)
        return json_response({
            'message': 'show updated',
            'result': 'success',
            'show': show.export()
        })


@app.route('/episode/new', methods=['GET'])
@flask_login.login_required
def page_create_episode():
    return page_episode(show_id=flask_login.current_user.primary_show_id())


@app.route('/episode/copy/<episode_id>', methods=['GET'])
def page_copy_episode(episode_id):
    return page_episode(episode_id=episode_id, copy_mode=True)


@app.route('/episode/<episode_id>', methods=['GET', 'DELETE'])
@flask_login.login_required
def page_load_episode(episode_id):
    if 'GET' == request.method:
        return page_episode(episode_id=episode_id)


def page_episode(show_id=None, episode_id=None, copy_mode=False):
    kwargs = dashboard_template_args(sidebar_episodes='active')
    if episode_id:
        kwargs['show_id'] = show_id
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
    result = kwargs.copy()
    result.update({
        'show_id': flask_login.current_user.primary_show_id() or 'new'
    })
    return result


@app.route('/episode', methods=['GET', 'POST', 'PUT', 'DELETE'])
@flask_login.login_required
def episode():
    if 'POST' == request.method:
        ep = episode_operations.create(**request.get_json())
        return json_response({
            'message': 'episode created',
            'result': 'success',
            'episode': ep.export()
        })

    if 'PUT' == request.method:
        ep = episode_operations.update(**request.get_json())
        return json_response({
            'message': 'episode updated',
            'result': 'success',
            'episode': ep.export()
        })

    if 'GET' == request.method:
        ep = episode_operations.get_by_id(request.args['episode_id'])
        return json_response({
            'result': 'success',
            'episode': ep.export(expand=['media', 'guests', 'links'])
        })

    if 'DELETE' == request.method:
        episode_operations.delete(request.form.get('episode_id'))
        return json_response({
            'message': 'episode deleted',
            'result': 'success'
        })


@app.route('/episodes', methods=['GET'])
@flask_login.login_required
def episodes():
    if 'GET' == request.method:
        show = show_operations.get_by_id(
            flask_login.current_user.primary_show_id())
        return json_response(map(
            lambda x: {'episode': x.export()}, show.episodes()))


@app.route('/media/list', methods=['GET'])
@flask_login.login_required
def page_media():
    kwargs = dashboard_template_args(sidebar_media='active')
    return render_template('dashboard-media.html', **kwargs)


@app.route('/media', methods=['POST', 'DELETE'])
@flask_login.login_required
def media():
    if 'POST' == request.method:
        media = audio_operations.create(
            flask_login.current_user, request.files['file'])
        return json_response({
            'message': 'new audio uploaded',
            'result': 'success',
            'media': media.export()
        })

    if 'DELETE' == request.method:
        audio_operations.delete(request.form.get('media_id'))
        return json_response({
            'message': 'audio deleted',
            'result': 'success'
        })


@app.route('/media/<media_id>', methods=['GET'])
@flask_login.login_required
def download_media(media_id):
    return redirect(
        urllib.parse.urljoin(
            settings.S3_HOST, '%s/%s' % (settings.S3_BUCKET_NAME, media_id)))


@app.route('/media-list', methods=['GET'])
@flask_login.login_required
def retrieve_media_list():
    filter_param = request.args.get('filter')
    media_list = audio_operations.get_by_user(
        flask_login.current_user,
        include_used=filter_param == 'used' or False,
        include_unused=filter_param == 'unused' or False)
    return json_response(map(
        lambda x: x.export(episode_summary=True), media_list))


@app.route('/photo', methods=['DELETE'])
@flask_login.login_required
def photo():
    photo_operations.delete(request.form.get('photo_id'))
    return json_response({
        'message': 'photo deleted',
        'result': 'success'
    })


@app.route('/photo-list', methods=['GET'])
@flask_login.login_required
def photo_list():
    photos = photo_operations.get_by_user(flask_login.current_user)
    return json_response({
        'result': 'success',
        'photos': map(lambda x: x.export(), photos)
    })


@app.route('/photos', methods=['GET'])
@flask_login.login_required
def page_photos():
    kwargs = dashboard_template_args(sidebar_photos='active')
    return render_template('dashboard-photos.html', **kwargs)


@app.route('/photo/<photo_id>', methods=['GET'])
@flask_login.login_required
def download_photo(photo_id):
    return redirect(
        urllib.parse.urljoin(
            settings.S3_HOST, '%s/%s' % (settings.S3_BUCKET_NAME, photo_id)))


@app.route('/upload-photo', methods=['POST'])
@flask_login.login_required
def upload_photo():
    photo = photo_operations.create(
        flask_login.current_user, request.files['file'])
    return json_response({
        'message': 'photo uploaded',
        'result': 'success',
        'photo': photo.export()
    })


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


def sanitized_json(d):
    if isinstance(d, list):
        return [sanitized_json(x) for x in d]
    if isinstance(d, map):
        return sanitized_json(list(d))
    if isinstance(d, dict):
        result = dict()
        for k, v in [(k, v) for k, v in d.items() if d.get(k)]:
            result[k] = sanitized_json(v)
        return result
    return sanitized_output(str(d))


def json_response(data):
    return Response(
        json.dumps(sanitized_json(data)), mimetype='application/json')


def _redirect_to_home():
    '''
    Redirects to the "home" page when logged in
    '''
    return redirect(url_for('page_profile'))
