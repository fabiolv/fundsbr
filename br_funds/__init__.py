from flask import Flask
from .blueprints.root_blueprint import root_blueprint
from .blueprints.funds_blueprint import funds_blueprint

def create_app(config_object='br_funds.settings'):
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    app.register_blueprint(root_blueprint)
    app.register_blueprint(funds_blueprint)

    return app