from flask import Blueprint, jsonify
from bson.objectid import ObjectId

root_blueprint = Blueprint('root_bluprint', __name__)

@root_blueprint.route('/')
def root():
    return jsonify(msg='This is the root / endpoint... and there is nothing here...'
        , version='v1'
    )