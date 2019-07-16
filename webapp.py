#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, abort, escape, flash
from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from modules.settings import VACS_LIMIT, AUTH_COL
from modules.storage import DataStorage
from modules.auth import User


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
app.config['SECRET_KEY'] = 'VFfihUSDY873r1e(*&DE(s89d*(*&#*Q$fgsdfv286749wdyu59dhX!@'

login_manager = LoginManager()
login_manager.init_app(app)

# MongoDb for app data
db = DataStorage()


def get_user(filter_dict):
    user = db.get_docs(AUTH_COL, _filter=filter_dict, limit=1)
    if user:
        user = user[0]
    return user


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


@app.route('/board')
@login_required
def board():
    return render_template('board.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = get_user(filter_dict={'email': email})
    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))

    db.add_doc(AUTH_COL, {'email': email, 'name': name, 'password': generate_password_hash(password, method='sha256')})
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
    return redirect(url_for('board'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
