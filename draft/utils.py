import pandas as pd

def store_feather_data(data, filename):
    data.to_feather(filename) 
    return print("Arquivo salvo")
