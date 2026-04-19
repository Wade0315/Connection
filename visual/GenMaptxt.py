import pandas as pd

def GentxtMap() :
    df = pd.read_csv('map.csv', index_col='index')
    with open('map.txt', 'w') as txt_file:   
        weight = 10.0
        txt_file.write(f'{len(df)}\n')

        row_string = ''
        for index, row in df.iterrows():
            for col_name in df.columns[1:]:
                if pd.notna(row[col_name]) and row[col_name] > index:
                    row_string += f'({int(row[col_name])}, {weight}, {col_name[0]})'
            if row_string:
                #print(f'{index}: {row_string}')
                txt_file.write(f'{index}: {row_string}\n')
            row_string = ''
    print('finish file conversion.')


GentxtMap()