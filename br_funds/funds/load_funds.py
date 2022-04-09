import pandas as pd

def load_funds_data_from_file() -> pd.DataFrame:
    ''' 
        Loads the fund information dataset from CVM.
    
        RETURNS
        pd.DataFrame
    '''
    url = "http://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
    # url = 'cad_fi.csv'

    cols = [
        "CNPJ_FUNDO"
        , "DENOM_SOCIAL"
        , "TP_FUNDO"
        , "CLASSE"
        , "SIT"
        , "DT_INI_ATIV"
        , "TAXA_ADM"
        , "TAXA_PERFM"
        , "INVEST_QUALIF"
        , "INVEST_PROF"
        , "CNPJ_ADMIN"
        , "ADMIN"
        , "CPF_CNPJ_GESTOR"
        , "GESTOR"
        ]

    funds_info = pd.read_csv(url, delimiter=';', encoding='ISO-8859-1', dtype='str', usecols=cols)
    funds_info.fillna(value='', inplace=True)
    return funds_info

def filter_data(funds: pd.DataFrame, cnpjs: list) -> pd.DataFrame:
    '''
        Filters the data selecting only the columns in the cols list
        and the rows that matches the CNPJs passed in the function argument

        RETURNS
        pd.DataFrame
    '''
    cols = [
            "CNPJ_FUNDO"
            , "DENOM_SOCIAL"
            , "TP_FUNDO"
            , "CLASSE"
            , "SIT"
            , "DT_INI_ATIV"
            , "TAXA_ADM"
            , "TAXA_PERFM"
            , "INVEST_QUALIF"
            , "INVEST_PROF"
            , "CNPJ_ADMIN"
            , "ADMIN"
            , "CPF_CNPJ_GESTOR"
            , "GESTOR"
            ]

    funds_info = funds.loc[funds['CNPJ_FUNDO'].isin(cnpjs), cols]

    return funds_info

def fix_columns(funds: pd.DataFrame) -> pd.DataFrame:
    '''
        Updates the column names in the pd.DataFrame based on the new_cols list.
        
        RETURNS
        pd.DataFrame
    '''
    new_cols = [
                "CNPJ"
                , "NOME"
                , "FUNDO_TIPO"
                , "FUNDO_CLASSE"
                , "STATUS"
                , "DATA_INICIO"
                , "TAXA_ADM"
                , "TAXA_PERFORMANCE"
                , "INVESTIDOR_QUALIFICADO"
                , "INVESTIDOR_PROFISSIONAL"
                , "ADMIN_CNPJ"
                , "ADMIN"
                , "GESTOR_CNPJ"
                , "GESTOR"
                ]

    funds.columns = new_cols

    return funds

def convert_to_dict(funds:pd.DataFrame) -> dict:
    '''
        Converts the DataFrame to a dictionary
        The 'records' orientation is used so each row becomes a dictionary.

        RETURNS
        A list of dict
    '''

    funds_dict = funds.to_dict(orient='records')
    
    return funds_dict

def load_funds_data(cnpjs:list) -> dict:
    '''
        Looks for the basic info for the Funds passed in the parameter as a list,
        process the dataframe
        
        RETURNS 
        A list of dict
    '''
    if len(cnpjs) == 0 or cnpjs is None:
        return None

    print(cnpjs)
    
    all_info = load_funds_data_from_file()

    funds_info = filter_data(all_info, cnpjs)
    funds_info = fix_columns(funds_info)

    fund_dict = convert_to_dict(funds_info)

    return fund_dict

if __name__ == '__main__':
    funds = load_funds_data(['21.917.184/0001-29', '21.917.206/0001-50'])
    print(funds)