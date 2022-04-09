from http import HTTPStatus
from typing import List
from flask import Response, jsonify
from br_funds.database import DB, DBParametersError, connect_to_db
from br_funds.models.quote_model import Quote
from br_funds.utils import InvalidCNPJError, validate_cnpj


def get_quotes(cnpj: str, from_date: str='1900-01-01', to_date: str='9999-12-31') -> List:
    try:
        connect_to_db()
    except DBParametersError:
        raise DBParametersError

    results = list()
    for quote in Quote.objects(CNPJ=cnpj, DATA__gte=from_date, DATA__lt=to_date).order_by('-DATA'):
        result = quote.to_mongo().to_dict()
        result['_id'] = str(result['_id'])
        results.append(result)

    return results

def get_latest_quote(cnpj: str) -> Response:
    try:
        cnpj = validate_cnpj([cnpj])[0]
    except InvalidCNPJError as err:
        print(f'--> Invalid CNPJ: {cnpj}')
        resp = jsonify({
            'msg': str(err),
            'error': True,
            'data': None
        })
        resp.status_code = HTTPStatus.BAD_REQUEST
        return resp

    try:
        # results = get_quotes(cnpj, from_date='2021-06-01', to_date='2021-06-18')
        results = get_quotes(cnpj)
    except DBParametersError:
        print('--> Could not connect to the DB')
        resp = jsonify({
            'msg': 'Could not connect to the DB',
            'error': True,
            'data': None
        })
        resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return resp

    if not results:
        print('dentro de if results')
        resp = jsonify({
            'msg': f'Could not find any quotes for the fund {cnpj}',
            'records': 0,
            'error': True,
            'data': None
        })
        resp.status_code = HTTPStatus.NOT_FOUND
        return resp

    resp = jsonify({
        'msg': f'Latest quote for the fund {cnpj}',
        'records': 1,
        'data': results[0]
    })

    return resp
