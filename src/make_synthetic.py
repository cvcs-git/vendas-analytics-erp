import os
import random
from datetime import datetime, timedelta

import pandas as pd

random.seed(42)

CLIENTES = [
    {"razao": "COMERCIAL ALFA LTDA", "fantasia": "ALFA", "cidade": "RECIFE/PE", "vendedor": "VENDEDOR A", "peso": 45},
    {"razao": "DISTRIBUIDORA BETA S/A", "fantasia": "BETA", "cidade": "OLINDA/PE", "vendedor": "VENDEDOR B", "peso": 17},
    {"razao": "INDUSTRIA GAMA LTDA", "fantasia": "GAMA", "cidade": "CARUARU/PE", "vendedor": "VENDEDOR B", "peso": 12},
    {"razao": "EMBALAGENS DELTA ME", "fantasia": "DELTA", "cidade": "JABOATAO/PE", "vendedor": "VENDEDOR B", "peso": 8},
    {"razao": "ATACADO OMEGA LTDA", "fantasia": "OMEGA", "cidade": "PAULISTA/PE", "vendedor": "VENDEDOR C", "peso": 18},
]

PRODUTOS = [
    {"codigo": 97,  "descricao": "TAMPA PCO 26MM - NORMAL :: PRETO", "valor": 0.068, "imposto": 0.05},
    {"codigo": 443, "descricao": "TAMPA PCO 38MM COM LACRE - NORMAL :: BRANCO", "valor": 0.110, "imposto": 0.05},
    {"codigo": 439, "descricao": "FRASCO 500ML - PET :: TRANSPARENTE", "valor": 0.850, "imposto": 0.0},
    {"codigo": 212, "descricao": "DOSADORA R2 28/43 - PADRAO :: AZUL", "valor": 0.250, "imposto": 0.05},
]

FORMATO_DATA = "%d/%m/%Y %H:%M:%S"
DATA_FIM = datetime(2026, 8, 31, 23, 59, 59)
DATA_ANOMALIA = datetime(2026, 7, 10)


def formatar_br(numero, casas=2):
    texto = f"{numero:,.{casas}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto


def criar_nota(numero_nota, numero_venda, emissao):
    pesos = [c["peso"] for c in CLIENTES]
    cliente = random.choices(CLIENTES, weights=pesos)[0]
    vendedor = cliente["vendedor"]
    prazo = random.choice(["21,28,35", "28,35,42", "38,45,52"])
    qtd_itens = random.randint(1, 3)
    produtos_da_nota = random.sample(PRODUTOS, qtd_itens)

    linhas = []
    for produto in produtos_da_nota:
        qnt = random.randint(5, 400) * 100
        total = round(qnt * produto["valor"], 2)
        total_nf = round(total * (1 + produto["imposto"]), 2)
        linha = {
            "Nota": f"NFe {numero_nota}",
            "Venda": str(numero_venda),
            "Emissão": emissao,
            "#": str(produto["codigo"]),
            "Descrição": produto["descricao"],
            "Razão Social": cliente["razao"],
            "Nome Fantasia": cliente["fantasia"],
            "Cidade/UF": cliente["cidade"],
            "Vendedor": vendedor,
            "Prazo": prazo,
            "Pag": "Boleto",
            "UN": "UNID",
            "Qnt": str(qnt),
            "Valor": formatar_br(produto["valor"], 3),
            "Total kg": "",
            "Total": formatar_br(total),
            "Total NF": formatar_br(total_nf),
        }
        linhas.append(linha)
    return linhas


def criar_cancelamento(linhas_originais, numero_nota, numero_venda, emissao):
    linhas = []
    for original in linhas_originais:
        linha = original.copy()
        linha["Nota"] = f"NFe {numero_nota}"
        linha["Venda"] = str(numero_venda)
        linha["Emissão"] = emissao
        linha["Qnt"] = formatar_br(-int(original["Qnt"]), 0)
        linha["Total"] = "-" + original["Total"]
        linha["Total NF"] = "-" + original["Total NF"]
        linhas.append(linha)
    return linhas


def criar_reemissao(linhas_originais, numero_nota, numero_venda, emissao):
    linhas = []
    for original in linhas_originais:
        linha = original.copy()
        linha["Nota"] = f"NFe {numero_nota}"
        linha["Venda"] = str(numero_venda)
        linha["Emissão"] = emissao
        linhas.append(linha)
    return linhas


def aplicar_anomalia_escala(linha):
    qnt = int(linha["Qnt"])
    valor = float(linha["Valor"].replace(",", "."))
    linha["Qnt"] = formatar_br(qnt / 1_000_000, 5)
    linha["Valor"] = formatar_br(valor * 1_000_000, 2)


def aplicar_descricao_antiga(linha):
    linha["#"] = "901"
    linha["Descrição"] = "TAMPA ANTIGA 28MM SEM PADRAO"


def avancar(momento):
    if momento.month == 4:
        horas = random.randint(2, 32)
    else:
        horas = random.randint(1, 20)
    return momento + timedelta(
        hours=horas,
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )


def gerar_vendas():
    todas_as_linhas = []
    numero_nota = 1848
    numero_venda = 859
    momento = datetime(2026, 1, 5, 8, 0, 0)
    anomalia_aplicada = False
    notas_geradas = 0

    while momento < DATA_FIM:
        linhas_nota = criar_nota(numero_nota, numero_venda, momento.strftime(FORMATO_DATA))
        if not anomalia_aplicada and momento >= DATA_ANOMALIA:
            aplicar_anomalia_escala(linhas_nota[0])
            anomalia_aplicada = True
        notas_geradas += 1
        if notas_geradas % 40 == 0:
            aplicar_descricao_antiga(linhas_nota[-1])
        todas_as_linhas.extend(linhas_nota)
        numero_nota += 1
        numero_venda += 1
        momento = avancar(momento)

        if random.random() < 0.10:
            linhas_cancel = criar_cancelamento(
                linhas_nota, numero_nota, numero_venda, momento.strftime(FORMATO_DATA)
            )
            todas_as_linhas.extend(linhas_cancel)
            numero_nota += 1
            numero_venda += 1
            momento = avancar(momento)

            if random.random() < 0.5:
                linhas_reemissao = criar_reemissao(
                    linhas_nota, numero_nota, numero_venda, momento.strftime(FORMATO_DATA)
                )
                todas_as_linhas.extend(linhas_reemissao)
                numero_nota += 1
                numero_venda += 1
                momento = avancar(momento)

    return pd.DataFrame(todas_as_linhas)


if __name__ == "__main__":
    df = gerar_vendas()
    os.makedirs("data/synthetic", exist_ok=True)
    df.to_csv("data/synthetic/vendas_sintetico.csv", sep=";", encoding="UTF-8", index=False)
    print(f"{len(df)} linhas geradas")