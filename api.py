from flask import Flask, jsonify, request, g
from flask_cors import CORS

from application.worker import Worker
from core.base_alg_object import BaseAlgObject
from core.db_instance import DBInstance
from core.token_helper import TokenHelper

app = Flask(__name__)
cors = CORS(app, origins='*')
app.config['SECRET_KEY'] = 'css-secret-key'


class Main:
    logger = BaseAlgObject.logger
    logger.info(f'Starting CSS App')
    worker = Worker()
    session = {}

    @classmethod
    def start(cls):
        cls.worker.init()
        app.run(debug=True)


@app.before_request
def db_connect():
    g.db = DBInstance
    g.db.connect()


@app.teardown_request
def db_disconnect(exception=None):
    g.db.disconnect()


@app.route('/login', methods=['POST'], )
def login():
    username = request.json['username']
    password = request.json['password']
    if request.method == 'POST':
        result = Main.worker.login(username, password)
        return jsonify(result)


@app.route('/sms_templates', methods=['GET'])
def sms_templates():
    if request.method == 'GET':
        authorization_header = request.headers.get('Authorization')
        token_res = TokenHelper.check_token(authorization_header[7:])
        if token_res['status'] != 'ok':
            return jsonify(token_res)
        else:
            result = Main.worker.get_sms_templates()
            return jsonify(result)


@app.route('/pdf_templates', methods=['GET', 'POST'])
def pdf_templates():
    authorization_header = request.headers.get('Authorization')
    token_res = TokenHelper.check_token(authorization_header[7:])
    if token_res['status'] != 'ok':
        return jsonify(token_res)
    else:
        if request.method == 'GET':
            result = Main.worker.get_pdf_templates()
            for file in result:
                file['template_data'] = file['template_data'].decode()
            return jsonify(result)
        if request.method == 'POST':
            file = request.files['file']
            file_bytes = file.read()
            file_name = file.filename
            if file_name != '':
                result = Main.worker.create_pdf_template(file_name, file_bytes)
                return jsonify(result)


@app.route('/filled_pdf_template/<template_id>', methods=['POST'])
def filled_pdf_template(template_id):
    authorization_header = request.headers.get('Authorization')
    token_res = TokenHelper.check_token(authorization_header[7:])
    if token_res['status'] != 'ok':
        return jsonify(token_res)
    else:
        if request.method == 'POST':
            form_data = request.json
            result = Main.worker.fill_pdf_templates(template_id, form_data)
            return jsonify(result)


@app.route('/user', methods=['POST'])
def user():
    user_data = request.json
    if request.method == 'POST':
        result = Main.worker.create_user(user_data)
        return jsonify(result)


if __name__ == '__main__':
    Main.start()
