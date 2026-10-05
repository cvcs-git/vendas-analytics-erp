# Análise de vendas a partir de exportações do ERP

Projeto de análise de vendas: os dados exportados do ERP (CSV) são limpos com Python, guardados em SQLite, consultados com SQL e apresentados em um dashboard no Power BI.

> Este projeto usa **dados sintéticos**, gerados por `src/make_synthetic.py`, que reproduz a estrutura do arquivo exportado do ERP. Nenhum dado real de empresa, clientes ou colaboradores foi utilizado. Alguns padrões (queda de um mês, concentração em um cliente, cancelamentos) foram incluídos de propósito para demonstrar as análises, entretanto, foi diferente do observado pela empresa.

![Dashboard](docs/images/relat_fic_1.png)

## Problema
O ERP exporta um CSV com uma linha por item de nota fiscal, com valores em texto, datas no formato brasileiro e cancelamentos como notas separadas. Faltava uma visão simples de faturamento, clientes, produtos e vendedores.

## Decisões de análise
- **Faturamento**: usa a coluna `Total` (sem impostos).
- **Faturamento líquido**: notas de venda menos notas de cancelamento, que entram como linhas negativas.
- **Ticket médio**: faturamento bruto ÷ número de notas de venda.
- **Filtro**: linhas com descrição fora do padrão são descartadas na limpeza, visando posterior investigação.
- Os dados brutos nunca são alterados. O tratamento gera um banco separado.

## Estrutura
```
data/synthetic/   CSV sintético
src/              limpeza, carga, consultas, exportação
tests/            testes com pytest
docs/images/      imagens do dashboard
```

## Como executar
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/make_synthetic.py
python src/load_db.py data/synthetic/vendas_sintetico.csv vendas_sintetico.db
python src/queries.py vendas_sintetico.db
python src/export_relatorio.py vendas_sintetico.db relatorio/relatorio_sintetico.xlsx
pytest
```
O Excel gerado é a fonte do dashboard no Power BI.

## Stack
Python (pandas, openpyxl), SQLite, SQL, Power BI, pytest, Git.

## Próximos passos
Análise de cancelamentos e reemissões, automação da atualização e conteinerização.