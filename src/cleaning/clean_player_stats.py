import pandas as pd



def safe_eval(x):
    try:
        if '+' in str(x):
            return sum(int(i) for i in str(x).split('+'))
        elif '-' in str(x):
            return int(str(x).split('-')[0]) - sum(int(i) for i in str(x).split('-')[1:])
        else:
            return int(x)
    except:
        return x

def clean_player_stats(df):
    df = df.copy()

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    df.loc[:, 'Name'] = df['Name'].str.replace(r'[A-Z]+$', '', regex=True)
    df.loc[:, 'date'] = pd.to_datetime(df['date']).dt.date

    pat = r'(\w+)\((\d+)\)(\d{4}) ~ (\d{4})'
    df[['position', 'jersey_num', 'contract_start',
        'contract_end']] = df.loc[:, 'Team & Contract'].astype(str).str.extract(pat)

    df.loc[:, 'height_cm'] = df['Height'].astype(str).str.split('cm ').str[0].astype('Int64')
    df.loc[:, 'weight_kg'] = df['Weight'].astype(str).str.split('kg ').str[0].astype('Int64')

    df.loc[:, 'wage_eur'] = df['Wage'].astype(str).str.replace('€', '').str.replace(
        ',', '').str.replace('K', '000').str.replace('M',
                                                     '000000').astype('Int64')

    df.loc[:, 'value_eur'] = df['Value'].astype(str).str.replace('€', '').str.replace(
        ',', '').str.replace('.', '').str.replace('K', '000').str.replace(
            'M', '000000').astype('Int64')


    df.drop(columns=['Height', 'Weight', 'Team & Contract', 'Value', 'Wage'],
            inplace=True)
    
    ## safe eval everything but date
    for col in df.columns:
        if col != 'date':
            df[col] = df[col].apply(safe_eval)

    
    main_cols = [
        'ID', 'date', 'Name', 'Age', 'height_cm', 'weight_kg', 'team',
        'contract_start', 'contract_end', 'position', 'foot', 'jersey_num',
        'wage_eur', 'value_eur'
    ]

    rest_cols = [col for col in df.columns if col not in main_cols]
    df = df[main_cols + rest_cols]

    for c in df.columns:
        try:
            df[c] = pd.to_numeric(df[c])
        except (ValueError, TypeError):
            pass 

    df.columns = df.columns.str.lower().str.replace(' ', '_')

    return df