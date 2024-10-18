import install_packages
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import linprog

tickers = ["PETR3.SA", "^BVSP", "^GSPC", "VALE3.SA", "ITUB4.SA", "B3SA3.SA"]

data_final = datetime.today()
data_inicial = data_final - timedelta(days=3*365)

dados_mercado = yf.download(tickers, start=data_inicial, end=data_final)
dados_mercado = dados_mercado["Adj Close"]
dados_mercado = dados_mercado.dropna()
dados_mercado.columns = ["B3", "ITAÚ",
                         "PETROBRAS", "VALE", "IBOVESPA", "S&P500"]

# Calcular retornos logarítmicos
retornos = np.log(dados_mercado / dados_mercado.shift(1)).dropna()

# Calcular volatilidade (risco)
volatilidade = retornos.std() * np.sqrt(252)

# Calcular VaR e CVaR


def calcular_var(dados, nivel=0.05):
    var = np.percentile(dados, nivel * 100)
    return var


def calcular_cvar(dados, nivel=0.05):
    var = calcular_var(dados, nivel)
    cvar = dados[dados < var].mean()
    return cvar


var = calcular_var(retornos)
cvar = calcular_cvar(retornos)

print("Retornos Médios:")
print(retornos.mean())
print("\nVolatilidade (Risco):")
print(volatilidade)
print("\nVaR:")
print(var)
print("\nCVaR:")
print(cvar)


def otimizar_carteira(retornos, riscos, capacidade):
    c = [-r for r in retornos]
    A = [riscos]
    b = [capacidade]
    resultado = linprog(c, A_ub=A, b_ub=b, bounds=(0, 1))
    return resultado.x


pesos = otimizar_carteira(retornos.mean(), volatilidade, capacidade=0.2)
pesos_percent = [peso * 100 for peso in pesos]

# Fronteira eficiente
plt.figure(figsize=(10, 6))
plt.scatter(volatilidade * 100, retornos.mean() * 100,
            c=(retornos.mean() / volatilidade), marker='o')
for i, txt in enumerate(dados_mercado.columns):
    plt.annotate(
        txt, (volatilidade.iloc[i] * 100, retornos.mean().iloc[i] * 100))
plt.xlabel('Risco (Volatilidade) (%)')
plt.ylabel('Retorno Esperado (%)')
plt.title('Fronteira Eficiente')
plt.colorbar(label='Retorno / Risco')
plt.show()

# Alocação dos Pesos
plt.figure(figsize=(10, 6))
bars = plt.bar(dados_mercado.columns, pesos_percent)
plt.xlabel('Ativos')
plt.ylabel('Peso (%)')
plt.title('Distribuição da Carteira')
# Adicionar os valores das porcentagens acima das colunas
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2 - 0.1, yval + 0.5, f'{yval:.2f}%')

plt.show()

# Evolução dos Retornos
retornos_acumulados = (1 + retornos).cumprod() - 1
plt.figure(figsize=(10, 6))
plt.plot(retornos_acumulados)
plt.xlabel('Tempo')
plt.ylabel('Retornos Acumulados')
plt.title('Evolução dos Retornos')
plt.legend(dados_mercado.columns)
plt.show()
