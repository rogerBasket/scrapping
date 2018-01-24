import pandas as pd

PAQUETE_EXPRESS = 'PAQUETE EXPRESS'
CASTORES = 'CASTORES'
PITIC = 'PITIC'
TRESGUERRAS = 'TRESGUERRAS'

def data_address(path):
    df = pd.read_csv(path, header = 0, delimiter = ',')

    return df
