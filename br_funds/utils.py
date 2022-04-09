from http import HTTPStatus
import sys
from flask import jsonify, Response, request
import re
from string import digits
from typing import List, Tuple
from .funds.load_funds import load_funds_data
from .models.fund_model import Fund
from .database import DB

class InvalidCNPJError(Exception):
    def __init__(self, cnpj) -> None:
        super().__init__(f'Invalid CNPJ: {cnpj}')
        self.fund = cnpj

def validate_cnpj(cnpjs: list) -> list:
    symbols = '-./'
    regex = re.compile('^[0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}\-[0-9]{2}$')
    new_cnpjs = list()

    if not cnpjs:
        raise InvalidCNPJError(str(cnpjs))
    
    for cnpj in cnpjs:
        print(cnpj)
        for digit in cnpj:
            if digit not in symbols and digit not in digits:
                raise InvalidCNPJError(cnpj)
        
        if '-' not in cnpj and '/' not in cnpj and '-' not in cnpj:
            # Numeric CNPJ given, so converting...
            cnpj = f'{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'

        if not regex.match(cnpj):
            raise InvalidCNPJError(cnpj)
        
        new_cnpjs.append(cnpj)

    return new_cnpjs

def funds_exist(list_of_funds: List, existing_funds: List) -> List:
    '''Returns a list of error messages when fund is not in the results loaded by pandas'''
    messages = list()
    existing_cnpjs = [fund['CNPJ'] for fund in existing_funds]
    for fund in list_of_funds:
        if fund not in existing_cnpjs:
            messages.append(f'Fund with CNPJ {fund} not found in the registry')

    return messages

def validate_url_params(args) -> bool:
    param_format = args.get('format', default='JSON', type=str)

    if param_format.upper() not in ['JSON', 'XML']:
        return False

    return True

def convert_to_xml(resp: Response) -> Response:
    resp_dict = resp.get_json()
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<quote>'
    print('----> converting to XML')
    for key, value in resp_dict.items():
        if isinstance(value, dict): # This should be recursive...
            xml += f'<{key}>\n'
            for subkey, subvalue in value.items():
                xml += f'\t<{subkey}>{subvalue}</{subkey}>\n'
            xml += f'</{key}>\n'
        else:
            xml += f'<{key}>{value}</{key}>\n'
    xml += '</quote>'

    print(xml)

    resp_xml = Response(xml, mimetype='text/xml', status=HTTPStatus.OK)
    return resp_xml



def get_all_funds() -> Response:
    try:
        db = DB()
    except:
        print('Could not connect to the DB')
        resp = jsonify({
            'msg': 'Could not connect to the DB',
            'error': True,
            'data': None            
        })
        resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return resp

    all_funds = [fund.to_mongo().to_dict() for fund in Fund.objects]
    for fund in all_funds:
        fund['_id'] = str(fund['_id'])

    print(all_funds)
    resp = jsonify({
        'msg': 'All funds in the DB',
        'records': len(all_funds),
        'data': all_funds
    })
    return resp

def add_funds(cnpjs: list) -> Response:
    results = list()
    try:
        funds_list = validate_cnpj(cnpjs)
    except InvalidCNPJError as error:
        print('Invalid CNPJ')
        resp = jsonify({
            'msg': f'{error}',
            'error': True,
            'data': cnpjs
        })
        resp.status_code = 400
        return resp
    
    try:
        db = DB()
    except:
        print('Could not connect to the DB')
        resp = jsonify({
            'msg': 'Could not connect to the DB',
            'error': True,
            'data': None            
        })
        resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return resp
    
    funds_info = load_funds_data(funds_list)
    
    msg = funds_exist(funds_list, funds_info)
    if msg:
        print('One or more funds were not found')
        resp = jsonify({
            'msg': 'One or more funds were not found',
            'error': True,
            'data': msg
        })
        resp.status_code = HTTPStatus.NOT_FOUND
        return resp

    for record in funds_info:
        fund = Fund(**record)
        try:
            result = fund.save()
            print(f'Saved {fund.CNPJ}')
            results.append(str(result.id))
        except:
            e = sys.exc_info()
            print('Exception -->', e)
            print(f'{fund.CNPJ} not saved...')
            resp = jsonify({
                'msg': f'Error while adding {fund.CNPJ} to the DB',
                'error': True,
                'data': str(e[1])
            })
            resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            return resp

    resp = jsonify({
        'msg': 'Records added',
        'records': len(results),
        'data': results
    })
    resp.status_code = HTTPStatus.CREATED

    return resp

def get_fund(cnpj: str) -> Response:
    print('CNPJ Received ---->', cnpj)
    try:
        fund_cnpj = validate_cnpj([cnpj])[0]
    except InvalidCNPJError as error:
        print('Invalid CNPJ')
        resp = jsonify({
            'msg': f'{error}',
            'error': True,
            'data': [cnpj]
        })
        resp.status_code = HTTPStatus.BAD_REQUEST
        return resp

    try:
        db = DB()
    except:
        print('Could not connect to the DB')
        resp = jsonify({
            'msg': 'Could not connect to the DB',
            'error': True,
            'data': None            
        })
        resp.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        return resp

    funds = Fund.objects(CNPJ=fund_cnpj)
    if not funds or len(funds) != 1:
        print(f'---> Fund {cnpj} not found')
        resp = jsonify({
            'msg': f'Fund {cnpj} ({fund_cnpj}) not found',
            'error': True,
            'data': [cnpj]
        })
        resp.status_code = HTTPStatus.NOT_FOUND
        return resp
    
    for record in funds:
        fund = record.to_mongo().to_dict()
        fund['_id'] = str(fund['_id'])
        resp = jsonify({
            'msg': f'Fund: {fund["CNPJ"]}',
            'records': len(funds),
            'data': fund
        })
        return resp

if __name__ == '__main__':
    # print(ascii_letters)
    # l = validate_cnpj(['21.917.184/0001-29', '21.917.206/0001-50', '42.730.627/0001-48', '11222333444455'])
    # add_funds(['11222333444455'])
    # print(l)
    # validate_cnpj([''])
    pass