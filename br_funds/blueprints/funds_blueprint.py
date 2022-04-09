from http import HTTPStatus
import re
from flask import Blueprint, Response, request, jsonify

from br_funds.quote.quotes import get_latest_quote, get_quotes
from br_funds.utils import convert_to_xml, validate_url_params
# from ..utils import add_funds, get_all_funds, get_fund
from ..funds.funds import add_funds, get_all_funds, get_fund

funds_blueprint = Blueprint('funds_blueprint', __name__)

@funds_blueprint.route('/funds/', methods=['GET', 'POST'])
def route_funds() -> Response:
    if request.method == 'GET':
        resp = get_all_funds()
        return resp

    if request.method == 'POST':
        request_data = request.get_json()
        resp = add_funds(request_data['cnpjs'])
        return resp

    return None

@funds_blueprint.route('/funds/<cnpj>', methods=['GET'])
def route_funds_get(cnpj: str):

    resp = get_fund(cnpj)
    return resp

@funds_blueprint.route('/funds/<cnpj>/quote/', methods=['GET'])
def route_funds_get_quote(cnpj: str) -> Response:
    # cnpj = '08.968.733/0001-26'
    # Artesanal 09.625.909/0001-00 09625909000100
    if not validate_url_params(request.args):
        resp = jsonify({
            'msg': 'Invalid values for the URL parameters',
            'error': True,
            'data': None
        })
        resp.status_code = HTTPStatus.BAD_REQUEST
        return resp

    print(request.args.get('format', default='JSON', type=str))
    param_format = request.args.get('format', default='JSON', type=str).upper()
    print(f'param ---> {param_format}')

    resp = get_latest_quote(cnpj)

    if param_format == 'XML':
        return convert_to_xml(resp)
    
    return resp