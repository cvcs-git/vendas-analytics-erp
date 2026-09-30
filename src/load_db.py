import sqlite3
import sys

from clean import limpar_vendas


def carregar_no_banco(df, caminho_db):
    conexao = sqlite3.connect(caminho_db)
    df.to_sql("vendas", conexao, if_exists="replace", index=False)
    conexao.close()


if __name__ == "__main__":
    caminho_csv = sys.argv[1] if len(sys.argv) > 1 else "data/raw/vendas_analitico.csv"
    caminho_db = sys.argv[2] if len(sys.argv) > 2 else "vendas.db"
    df = limpar_vendas(caminho_csv)
    carregar_no_banco(df, caminho_db)
    print(f"{len(df)} linhas carregadas em {caminho_db}")