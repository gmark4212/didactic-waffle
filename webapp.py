from flask import Flask, jsonify, request, abort
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


@app.route('/api/skills/', methods=['GET'])
def get_top_skills():
    search = request.args.get('search')
    if bool(search) and len(search) > 2:
        top = db.fetch_top_skills(search)
        return jsonify({'data': top})
    else:
        return abort(400)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
