from flask import Response, jsonify
from mongoengine import connect
from pymongo.errors import OperationFailure
from dotenv import load_dotenv
import os

class DBParametersError(Exception):
    def __init__(self) -> None:
        super().__init__('Failed to retrieve the enviroment variables to connect to the DB')

class DB():
    _MONGODB_USERNAME = None
    _MONGODB_PASSWORD = None
    _MONGODB_CLUSTER = None
    _MONGODB_DB = None
    _MONGODB_COLLECTION = None
    def __init__(self) -> None:
        self._load_envs()
        try:
            connect(host="mongodb+srv://cluster.a7nme.mongodb.net"
                , db=self._MONGODB_DB
                , username=self._MONGODB_USERNAME
                , password=self._MONGODB_PASSWORD)
        except OperationFailure as err:
            print ('--> Could not connect to the DB')
            raise Exception('Could not connect to the DB')
        print('Connecting to the db...')


    def _load_envs(self):
        load_dotenv()
        self._MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
        self._MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
        self._MONGODB_CLUSTER = os.getenv('MONGODB_CLUSTER')
        self._MONGODB_DB = os.getenv('MONGODB_DB')
        self._MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION')

        if not all([self._MONGODB_USERNAME, self._MONGODB_PASSWORD, self._MONGODB_CLUSTER, self._MONGODB_DB, self._MONGODB_COLLECTION]):
            raise DBParametersError()

def connect_to_db() -> None:
    try:
        db = DB()
    except:
        raise DBParametersError
        print('--> Could not connect to the DB')
        resp = jsonify({
            'msg': 'Could not connect to the DB',
            'error': True,
            'data': None
        })
        resp.status_code = 500
        return resp