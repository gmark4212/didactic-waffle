from flask import Flask, jsonify, request, abort
from jinja2 import Template
from modules.storage import DataStorage

app = Flask(__name__)
db = DataStorage()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/skills/', methods=['GET'])
def get_top_skills():
    search = request.args.get('search')
    if bool(search) and len(search) > 3:
        top = db.fetch_top_skills(search)
        return jsonify({'data': top})
    else:
        return abort(400)



if __name__ == '__main__':
    app.run()
