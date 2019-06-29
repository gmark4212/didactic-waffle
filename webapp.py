from flask import Flask, jsonify, request, abort, escape
from flask import render_template
from modules.storage import DataStorage


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
db = DataStorage()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/skills/', methods=['GET'])
def get_top_skills():
    search = escape(request.args.get('search'))
    if bool(search) and len(search) > 2:
        top = db.fetch_top_skills(search)
        return jsonify({'data': top})
    else:
        return abort(400)


@app.route('/api/v1/ref/skills/', methods=['GET'])
def get_skills_ref():
    return jsonify({'data': db.get_skills_ref()})


@app.route("/api/v1/vacancies/<string:skill>", methods=['GET'])
def fetch_vacs_for_skill(skill):
    skill = escape(skill)
    if request.method == 'GET':
        return jsonify({'data': db.get_vacancies_by_skill(skill)})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
