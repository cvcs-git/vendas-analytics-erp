import pandas as pd
import sqlite3
from clean import limpar_vendas

def carregar_no_banco(df):
    conexao = sqlite3.connect ("vendas.db")
    df.to_sql("vendas", conexao, if_exists="replace", index=False)
    conexao.close()

if __name__ == "__main__":
    df = limpar_vendas("data/raw/vendas_analitico.csv")
    carregar_no_banco (df)
    print("Dados carregados no banco de vendas.db com sucesso!")