#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, abort, escape, flash, json
from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from modules.settings import VACS_LIMIT, AUTH_COL, CONFIRM_SEC_TO_EXPIRE, SITE_URL, ADS_COL
from modules._sensitive import SECRET, EMAIL_CONFIRM_SALT, MAIL_PASSWORD
from modules.storage import DataStorage
from modules.auth import User
from modules.payment import StripePay


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    ))


app = CustomFlask(__name__)
app.config['TESTING'] = False
app.config['SECRET_KEY'] = SECRET
app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'noreply@skoglee.com'
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@skoglee.com'


mail = Mail(app)
mail.init_app(app)

serializer = URLSafeTimedSerializer(SECRET)

login_manager = LoginManager()
login_manager.init_app(app)

# MongoDb for app data
db = DataStorage()
# stripe payment obj
stripe = StripePay()


def get_user(filter_dict):
    user = db.get_docs(AUTH_COL, _filter=filter_dict, limit=1)
    if user:
        user = user[0]
    return user


def get_confirmation_token(email):
    return serializer.dumps(email, EMAIL_CONFIRM_SALT)


@login_manager.user_loader
def load_user(email):
    db_user = get_user(filter_dict={'email': email})
    if not db_user:
        return None
    return User(db_user)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/skills/', methods=['GET'])
def api_get_top_skills_with_vacs():
    search = escape(request.args.get('search'))
    if bool(search) and len(search) > 2:
        top = db.fetch_top_skills(search, VACS_LIMIT)
        db.get_skill_details(top)
        return jsonify({'data': top})
    else:
        return abort(400)


@app.route('/api/v1/ref/skills/', methods=['GET'])
def api_get_skills_ref():
    return jsonify(db.get_skills_ref())


@app.route("/api/v1/vacancies/<string:skill>", methods=['GET'])
def api_fetch_vacs_for_skill(skill):
    if request.method == 'GET':
        skill = escape(skill)
        return jsonify({'data': db.get_vacancies_by_skill(skill)})


@app.route('/api/v1/topskills/<string:position>', methods=['GET'])
def api_get_top_skills_no_vacs(position):
    if request.method == 'GET':
        position = escape(position)
        if bool(position) and len(position) > 2:
            top = db.fetch_top_skills(position, no_vacs=True)
            return jsonify({'data': top})


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    email = escape(request.form.get('email'))
    name = escape(request.form.get('name'))
    password = escape(request.form.get('password'))

    if not email:
        flash('You should fill email')
        return redirect(url_for('signup'))

    if not password:
        flash('You should fill password')
        return redirect(url_for('signup'))

    user_exist = get_user(filter_dict={'email': email})
    if user_exist:
        flash(f'Email address {email} already exists')
        return redirect(url_for('signup'))

    db.add_doc(AUTH_COL, {'active': False, 'email': email, 'name': name,
                          'password': generate_password_hash(password, method='sha256')})

    token = get_confirmation_token(email)
    link = SITE_URL + url_for('confirm_email', token=token, external=True)
    msg = Message('[Skoglee.com] Please confirm your account', sender='noreply@skoglee.com', recipients=[email])
    msg.html = f'<p>To gain access to all functions of your Skoglee advertisement account confirm your email ' \
        f'clicking this link </p><p><a href="{link}">{link}</a></p>'

    try:
        mail.send(msg)
    except Exception:
        redirect(url_for('srv_error'))
    return redirect(url_for('login'))


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    db_user = get_user(filter_dict={'email': email})

    if not db_user or not check_password_hash(db_user['password'], password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(User(db_user))
    flash('Logged in successfully.')
    return redirect(url_for('account'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt=EMAIL_CONFIRM_SALT, max_age=CONFIRM_SEC_TO_EXPIRE)
        db_user = get_user(filter_dict={'email': email})
        if db_user:
            db.update_doc(AUTH_COL, _filter={'email': email}, set_dict={'active': True})
    except SignatureExpired:
        return redirect(url_for('page_not_found'))
    except BadSignature:
        return redirect(url_for('page_not_found'))
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def srv_error(e):
    return render_template('500.html'), 500


@app.route("/campaign/fetch", methods=['POST'])
@login_required
def fetch_campaign():
    if request.method == 'POST':
        if not request.json or not current_user.active:
            abort(400)
        query = request.get_json()
        if query.get('request', None) == 'campaign':
            data = db.get_docs(collection_name=ADS_COL, _filter={'email': current_user.email})
            camp = data[0].get('campaign', None)
            if camp:
                return jsonify(camp)
        abort(400)


@app.route('/campaign/save', methods=['POST'])
@login_required
def save_campaign():
    if request.method == 'POST':
        if not request.json or not current_user.active:
            abort(400)
        db.delete_docs(_filter={'email': current_user.email}, collection_name=ADS_COL)
        db.add_doc(collection_name=ADS_COL, data={
            'email': current_user.email,
            'campaign': request.json,
            'paid': campaign_is_paid()
        })
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/account/customer/", methods=['GET'])
@login_required
def get_customer():
    if request.method == 'GET':
        if not current_user.active:
            abort(400)
        return jsonify({
            'name': current_user.name,
            'email': current_user.email,
            'stripe_id': current_user.stripe_id,
            'paid': campaign_is_paid()
        })
    abort(400)


def campaign_is_paid():
    last_payment = stripe.is_current_campaign_paid(current_user.email)
    return last_payment['campaign_is_paid']


@app.route('/payment/success')
@login_required
def successful_payment():
    if not current_user.active:
        abort(400)
    email = current_user.email
    if email:
        customer_ids = stripe.get_customer_ids(email, limit=1)
        if customer_ids:
            stripe_id = customer_ids[0]
            if stripe_id:
                db.update_doc(AUTH_COL, _filter={'email': email}, set_dict={'stripe_id': stripe_id})
                db.update_doc(ADS_COL, _filter={'email': email}, set_dict={'paid': campaign_is_paid()})
            return render_template('success.html')
    abort(400)


@app.route('/payment/cancel')
@login_required
def cancelled_payment():
    if not current_user.active:
        abort(400)
    return render_template('cancel.html')


@app.route("/account/payment/history/", methods=['GET'])
@login_required
def get_payment_history():
    if request.method == 'GET':
        if not current_user.active:
            abort(400)
        charges = stripe.get_history(current_user.email, limit=100)
        return jsonify(charges)
    abort(400)


if __name__ == '__main__':
    app.run()
