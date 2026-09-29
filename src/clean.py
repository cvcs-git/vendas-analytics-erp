import pandas as pd
import re

def valores_verif(coluna):
    coluna = coluna.astype(str)
    coluna = coluna.str.replace(".", "", regex=False)
    coluna = coluna.str.replace(",",".", regex=False)
    coluna = coluna.astype(float)
    return coluna

def parse_descricao(texto):
    partes = texto.split("::")
    cor = partes[1].strip()
    resto = partes[0]
    produto_base = resto.split(" - ")[0].strip()


    if "DOSADORA R2" in produto_base:
        medida_match = re.search(r"(\d+/\d+)",resto)
        if medida_match:
            medida_mm = medida_match.group(1)
        else:
            medida_mm = None
    else:
        medida_match = re.search(r"(\d+)\s*MM", resto, flags=re.IGNORECASE)   
        if medida_match:
            medida_mm = int(medida_match.group(1))
        else:
            medida_mm = None 
    return produto_base, medida_mm, cor


def limpar_vendas(caminho_csv):
    df = pd.read_csv(caminho_csv, sep=";", encoding="UTF-8", dtype={"Valor": str, "Total": str, "Total NF": str, "Qnt": str})

    df["Valor"] = valores_verif(df["Valor"])
    df["Total"] = valores_verif(df["Total"])
    df["Total NF"] = valores_verif(df["Total NF"])
    df["Qnt"] = valores_verif(df["Qnt"])
    df["Emissão"] = pd.to_datetime(df["Emissão"], format="%d/%m/%Y %H:%M:%S")

    tem_cor = df["Descrição"].str.contains("::")
    tem_hifen = df["Descrição"].str.contains(" - ", regex=False)
    registro_valido = tem_cor & tem_hifen
    df = df[registro_valido]

    resultado_parse = df["Descrição"].apply(parse_descricao).apply(pd.Series)
    resultado_parse.columns = ["produto_base", "medida", "cor"]
    df = pd.concat([df, resultado_parse], axis=1)

    df = df.drop(columns=["Total kg"], errors = "ignore")

    return df

if __name__ == "__main__":
    df = limpar_vendas("data/raw/vendas_analitico.csv")
    print (df.head())
    print(f"total de linhas após a limpeza: {len(df)}")
