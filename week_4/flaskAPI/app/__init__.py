from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return {'message': 'Rewards optimizer API is running.'}

    return app
