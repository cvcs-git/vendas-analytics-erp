import pandas as pd
from src.clean import valores_verif, parse_descricao

def test_valores_verif_converte_numero_br():
    entrada = pd.Series(["95.200,00", "4.345,00"])
    resultado = valores_verif(entrada)
    assert resultado[0] == 95200.00
    assert resultado[1] == 4345.00

def test_parse_descricao_produto_comum():
    resultado = parse_descricao ("TAMPA FLIPTOP 26MM ROSCA - EMB. C/ 5.000 :: AZUL BIC")
    produto_base, medida, cor = resultado
    assert produto_base == "TAMPA FLIPTOP 26MM ROSCA"
    assert medida == 26
    assert cor == "AZUL BIC"

def test_parse_descricao_dosadora_r2():
    resultado = parse_descricao("DOSADORA R2 ROSCA DUPLA 28/43 - EMB. C/ 1.500 :: VERMELHO")
    produto_base, medida, cor = resultado
    assert produto_base == "DOSADORA R2 ROSCA DUPLA 28/43"
    assert medida == "28/43"
    assert cor == "VERMELHO"

def test_valores_verif_quantidade_com_ponto_de_milhar():
    entrada = pd.Series(["-150.000", "1400000"])
    resultado = valores_verif(entrada)
    assert resultado[0] == - 150000.0
    assert resultado[1] == 1400000.0