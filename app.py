import logging
import os

from flask import Flask, abort, redirect, render_template, request, url_for

import core
import tl

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/main', methods=['GET'])
def show_main():
    user_repo = core.UserRepository()
    users = user_repo.get_all()

    return render_template('main.html', users=users)


@app.route('/request_consent', methods=['GET'])
def request_consent():
    user_repo = core.UserRepository()

    user_id = request.args.get('user_id')
    if user_id is None:
        return ('missing user_id', 400)

    if user_repo.get_by_id(user_id) is None:
        logger.warn(f'request consent for unknown user_id={user_id}')
        return abort(404)

    state = core.encode_state(user_id)
    consent_link = tl.generate_auth_link(CLIENT_ID, REDIRECT_URI, state)
    return redirect(consent_link)


@app.route('/callback', methods=['POST'])
def handle_callback():
    # check if this user exists
    state = request.form['state']
    user_id = core.decode_state(state)

    user_repo = core.UserRepository()

    if user_repo.get_by_id(user_id) is None:
        logger.error(f'got code for unknown user_id={user_id}')
        return abort(404)

    # exchange the access code
    code = request.form['code']
    tokens = tl.exchange_code(code, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    # extract token info
    token_info = tl.token_info(tokens.access)

    token_repo = core.TokenRepository()
    token_repo.store(user_id, token_info['provider'], tokens)

    return redirect(url_for('show_main'))


def extract_summary(user, user_tokens):
    def to_summary_row(user_token):
        accounts = tl.list_accounts(user_token.access_token)
        return {
            'provider': user_token.provider.name,
            'num_accounts': len(accounts)
        }

    accounts_summary = [to_summary_row(ut) for ut in user_tokens]

    return {'user_name': user.name, 'accounts_summary': accounts_summary}


@app.route('/summary/<user_id>', methods=['GET'])
def list_user_summary(user_id):
    token_repo = core.TokenRepository()
    user_tokens = token_repo.get_by_id(user_id)

    if len(user_tokens) == 0:
        return render_template('no_consent.html', user_id=user_id)

    user_repo = core.UserRepository()
    user = user_repo.get_by_id(user_id)
    if user is None:
        logger.error(f'user summary for unknown user_id={user_id}')
        return abort(404)

    summary = extract_summary(user, user_tokens)
    return render_template('user_summary.html', summary=summary)
