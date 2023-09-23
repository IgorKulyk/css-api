from flask import Flask, jsonify, request

from application.worker import Worker
from core.base_alg_object import BaseAlgObject

app = Flask(__name__)
app.config['SECRET_KEY'] = 'css-secret-key'


class Main:
    # Simulated user data (for simplicity)
    logger = BaseAlgObject.logger
    logger.info(f'Starting CSS App')
    worker = Worker()
    session = {}

    @classmethod
    def start(cls):
        cls.worker.init()
        app.run(debug=True)


@app.route('/login', methods=['POST'])
def login():
    # result = {'status': 'ok', 'message': ''}
    if request.method == 'POST':
        result = Main.worker.get_sms_templates()
        return jsonify(result)

@app.route('/sms_templates', methods=['GET'])
def sms_templates():
    # result = {'status': 'ok', 'message': ''}
    if request.method == 'GET':
        result = Main.worker.get_sms_templates()
        return jsonify(result)


@app.route('/user', methods=['POST'])
def user():
    # result = {'status': 'ok', 'message': ''}
    user_data = request.json
    print(f"user data: {user_data}")
    if request.method == 'POST':
        result = Main.worker.create_user(user_data)
        return jsonify(result)


if __name__ == '__main__':
    Main.start()
