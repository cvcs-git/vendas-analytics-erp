import pandas as pd
from src.clean import valores_verif, parse_descricao, limpar_vendas

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

def test_limpar_vendas_converte_qnt_e_descarta_registro_invalido(tmp_path):
    csv = tmp_path / "vendas_teste.csv"
    csv.write_text(
        "Nota;Emissão;Descrição;Qnt;Valor;Total;Total NF\n"
        "NFe 1;05/01/2026 10:00:00;TAMPA TESTE 26MM ROSCA - EMB. C/ 1.000 :: AZUL;1400000;0,068;95.200,00;99.960,00\n"
        "NFe 2;06/01/2026 11:00:00;ALÇA TESTE 48MM - EMB. C/ 1.500 :: BRANCO;-150.000;0,100;-15.000,00;-15.000,00\n"
        "NFe 3;07/01/2026 12:00:00;PRODUTO ANTIGO SEM PADRAO;1000;0,050;50,00;50,00\n",
        encoding="UTF-8",
    )
    df = limpar_vendas(str(csv))
    assert len(df) == 2
    assert df["Qnt"].tolist() == [1400000.0, -150000.0]