from http import HTTPStatus
import sys
from flask import jsonify, Response
from .load_funds import load_funds_data
from ..models.fund_model import Fund
from ..database import DB
from ..utils import validate_cnpj, InvalidCNPJError, funds_exist

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
            'data': [f'{error.fund}']
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
            # The current behavior is to abort execution if there's an error
            # if the list of funds is not unique (already exists in the DB)
            # it will fail for everything.
            # If we test for the MongoEngine exception here, it creates a dependency on the DB type,
            # a solution might to send the error to db object to evaluate.
            # If the error is because a key duplication, ignore and continue
            e = sys.exc_info()
            print('Exception -->', e)
            print(f'{fund.CNPJ} not saved...')
            resp = jsonify({
                'msg': f'Error while adding {fund.CNPJ} to the DB',
                'error': True,
                'data': [str(e[1]), record]
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

    # Example body:
    # {
    #   "cnpjs": [
    #     "26.673.556/0001-32",
    #     "21.917.184/0001-29",
    #     "21.917.206/0001-50",
    #     "36.014.016/0001-09",
    #     "31.533.459/0001-84",
    #     "09.625.909/0001-00",
    #     "08.968.733/0001-26",
    #     "30.317.454/0001-51",
    #     "17.162.002/0001-80",
    #     "18.623.722/0001-68",
    #     "36.498.670/0001-27",
    #     "21.918.896/0001-62",
    #     "21.934.992/0001-02",
    #     "21.940.681/0001-48",
    #     "21.946.290/0001-30",
    #     "21.956.674/0001-34",
    #     "21.983.061/0001-96",
    #     "22.003.296/0001-37",
    #     "22.003.346/0001-86",
    #     "22.003.742/0001-03",
    #     "22.003.777/0001-42",
    #     "22.003.855/0001-09",
    #     "22.003.930/0001-31",
    #     "22.013.560/0001-13",
    #     "22.013.584/0001-72",
    #     "22.013.612/0001-51",
    #     "22.013.935/0001-45",
    #     "22.013.978/0001-20",
    #     "22.014.279/0001-03",
    #     "22.016.560/0001-77",
    #     "22.016.608/0001-47",
    #     "22.031.950/0001-16",
    #     "22.041.150/0001-86",
    #     "22.032.175/0001-13",
    #     "22.041.241/0001-11",
    #     "22.080.561/0001-80",
    #     "22.099.965/0001-16",
    #     "22.100.039/0001-13",
    #     "22.106.240/0001-08",
    #     "22.106.310/0001-28",
    #     "22.106.390/0001-11",
    #     "22.118.281/0001-14",
    #     "22.118.303/0001-46",
    #     "22.118.329/0001-94",
    #     "22.118.342/0001-43",
    #     "22.128.289/0001-61",
    #     "22.128.298/0001-52",
    #     "22.150.102/0001-26",
    #     "22.150.409/0001-27",
    #     "22.150.467/0001-50",
    #     "22.150.568/0001-21"
    #   ]
    # }
    pass