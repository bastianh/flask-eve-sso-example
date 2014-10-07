import os

from flask import Flask, request, session, render_template, url_for, redirect
from flask_oauthlib.client import OAuth


app = Flask(__name__)

oauth = OAuth()
evesso = oauth.remote_app('evesso', app_key='EVESSO')

app.secret_key = os.environ.get("APP_SECRET", "SOMETHING_SECRET")

app.config['EVESSO'] = dict(
    consumer_key=os.environ.get("EVESSO_CLIENT_ID", "YOUR_EVESSO_CLIENT_ID"),
    consumer_secret=os.environ.get("EVESSO_SECRET_KEY", "YOUR_EVESSO_SECRET_KEY"),
    base_url='https://sisilogin.testeveonline.com/oauth/',
    access_token_url='https://sisilogin.testeveonline.com/oauth/token',
    access_token_method='POST',
    authorize_url='https://sisilogin.testeveonline.com/oauth/authorize',
)

oauth.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/login")
def login():
    return evesso.authorize(callback=url_for('authorized', _external=True, _scheme="https"))


@app.route('/callback')
def authorized():
    resp = evesso.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, Exception):
        return 'Access denied: error=%s' % str(resp)

    session['evesso_token'] = (resp['access_token'], '')

    verify = evesso.get("verify")
    session['character'] = verify.data
    return redirect(url_for("index"))


@evesso.tokengetter
def get_evesso_oauth_token():
    return session.get('evesso_token')


if __name__ == "__main__":
    app.run(debug=True)