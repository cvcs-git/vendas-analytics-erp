import sqlite3
import pandas as pd
import sys

CAMINHO_DB = "vendas.db"

def executar_query(sql):
    conexao = sqlite3.connect(CAMINHO_DB)
    df = pd.read_sql_query(sql, conexao)
    conexao.close()
    return df


def ranking_produtos():
    sql = """
    SELECT produto_base,
           SUM(Total) AS faturamento,
           CAST(SUM(Qnt) AS INTEGER) AS unidades,
           ROUND(SUM(Total) * 100.0 / (SELECT SUM(Total) FROM vendas), 1) AS pct_do_total
    FROM vendas
    GROUP BY produto_base
    ORDER BY faturamento DESC
    LIMIT 10
    """
    return executar_query(sql)

def faturamento_mensal():
    sql = """
    SELECT strftime('%Y-%m', "Emissão") AS mes,
           ROUND(SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END), 2) AS bruto,
           ROUND(SUM(CASE WHEN Total < 0 THEN Total ELSE 0 END), 2) AS cancelado,
           ROUND(SUM(Total), 2) AS liquido,
           COUNT(DISTINCT CASE WHEN Total > 0 THEN Nota END) AS notas_venda,
           COUNT(DISTINCT CASE WHEN Total < 0 THEN Nota END) AS notas_cancelamento,
           ROUND(-SUM(CASE WHEN Total < 0 THEN Total ELSE 0 END) * 100.0
                 / SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END), 1) AS pct_cancelado
    FROM vendas
    GROUP BY mes
    ORDER BY mes
    """
    return executar_query(sql)

def ranking_clientes():
    sql = """
    SELECT "Razão Social",
           SUM(Total) AS faturamento,
           COUNT(DISTINCT Nota) AS qtd_notas,
           ROUND(SUM(Total) * 100.0 / (SELECT SUM(Total) FROM vendas), 1) AS pct_do_total
    FROM vendas
    GROUP BY "Razão Social"
    ORDER BY faturamento DESC
    LIMIT 10
    """
    return executar_query(sql)

def faturamento_bruto_liquido():
    sql = """
    SELECT strftime('%Y-%m', "Emissão") AS mes,
           SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END) AS bruto,
           SUM(CASE WHEN Total < 0 THEN Total ELSE 0 END) AS cancelado,
           SUM(Total) AS liquido,
           COUNT(DISTINCT CASE WHEN Total > 0 THEN Nota END) AS notas_venda,
           COUNT(DISTINCT CASE WHEN Total < 0 THEN Nota END) AS notas_cancelamento,
           ROUND(SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END) / COUNT(DISTINCT CASE WHEN Total > 0 THEN Nota END), 2) AS ticket_medio_bruto
    FROM vendas
    GROUP BY mes
    ORDER BY mes
    """
    return executar_query(sql)

def desempenho_vendedores():
    sql = """
    SELECT Vendedor,
           SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END) AS bruto,
           SUM(CASE WHEN Total < 0 THEN Total ELSE 0 END) AS cancelado,
           SUM(Total) AS liquido,
           COUNT(DISTINCT CASE WHEN Total > 0 THEN Nota END) AS notas_venda,
           COUNT (DISTINCT "Razão Social") AS clientes,
           ROUND(SUM(Total) * 100.0 / (SELECT SUM(Total) FROM vendas), 1) AS pct_do_total
    FROM vendas
    GROUP BY Vendedor
    ORDER BY liquido DESC
    """
    return executar_query(sql)

def concentracao_clientes():
    sql = """
    WITH por_cliente AS (
        SELECT "Razão Social" AS cliente,
               ROUND(SUM(Total), 2) AS liquido
        FROM vendas
        GROUP BY "Razão Social"
    )
    SELECT ROW_NUMBER() OVER (ORDER BY liquido DESC) AS posicao,
           cliente,
           liquido,
           ROUND(liquido * 100.0 / SUM(liquido) OVER (), 1) AS pct,
           ROUND(SUM(liquido) OVER (ORDER BY liquido DESC ROWS UNBOUNDED PRECEDING) * 100.0
                 / SUM(liquido) OVER (), 1) AS pct_acumulado
    FROM por_cliente
    ORDER BY liquido DESC
    """
    return executar_query(sql)

def cancelamentos_reemissoes():
    sql = """
    WITH notas AS (
        SELECT Nota,
               "Razão Social" AS cliente,
               MIN("Emissão") AS emissao,
               ROUND(SUM(Total), 2) AS valor
        FROM vendas
        GROUP BY Nota, "Razão Social"
    ),
    cancelamentos AS (
        SELECT * FROM notas WHERE valor < 0
    ),
    pares AS (
        SELECT c.*,
               (SELECT n.Nota
                FROM notas n
                WHERE n.cliente = c.cliente
                  AND n.valor = -c.valor
                  AND n.emissao < c.emissao
                ORDER BY n.emissao DESC
                LIMIT 1) AS nota_original,
               (SELECT n.Nota
                FROM notas n
                WHERE n.cliente = c.cliente
                  AND n.valor = -c.valor
                  AND n.emissao > c.emissao
                ORDER BY n.emissao
                LIMIT 1) AS nota_reemissao
        FROM cancelamentos c
    )
    SELECT p.Nota AS nota_cancelamento,
           p.cliente,
           p.emissao AS data_cancelamento,
           p.valor AS valor_cancelado,
           p.nota_original,
           o.emissao AS data_original,
           p.nota_reemissao,
           r.emissao AS data_reemissao,
           ROUND(julianday(r.emissao) - julianday(p.emissao), 1) AS dias_ate_reemissao
    FROM pares p
    LEFT JOIN notas o ON o.Nota = p.nota_original
    LEFT JOIN notas r ON r.Nota = p.nota_reemissao
    ORDER BY p.emissao
    """
    return executar_query(sql)

def resumo_geral():
    sql = """
    SELECT MIN(date("Emissão")) AS inicio,
           MAX(date("Emissão")) AS fim,
           ROUND(SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END), 2) AS bruto,
           ROUND(SUM(CASE WHEN Total < 0 THEN Total ELSE 0 END), 2) AS cancelado,
           ROUND(SUM(Total), 2) AS liquido,
           COUNT(DISTINCT CASE WHEN Total > 0 THEN Nota END) AS notas_venda,
           COUNT(DISTINCT CASE WHEN Total > 0 THEN "Razão Social" END) AS clientes,
           ROUND(SUM(CASE WHEN Total > 0 THEN Total ELSE 0 END)
                 / COUNT(DISTINCT CASE WHEN Total > 0 THEN Nota END), 2) AS ticket_medio_bruto
    FROM vendas
    """
    return executar_query(sql)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        CAMINHO_DB = sys.argv[1]
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 250)
    print(desempenho_vendedores())