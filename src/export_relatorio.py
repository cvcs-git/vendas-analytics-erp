import os
import sys
import pandas as pd
import queries as q

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q.CAMINHO_DB = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else "relatorio/relatorio_vendas.xlsx"

    tabelas = {
        "resumo" : q.resumo_geral(),
        "mensal" : q.faturamento_mensal(),
        "clientes" : q.concentracao_clientes(),
        "produtos" : q.ranking_produtos(),
        "vendedores" : q.desempenho_vendedores(),
    }

    os.makedirs(os.path.dirname(saida), exist_ok = True)
    with pd.ExcelWriter(saida) as arquivo:
        for nome, tabela, in tabelas.items():
            tabela.to_excel(arquivo, sheet_name=nome, index=False)

    print (f"Relatório salvo em {saida}")