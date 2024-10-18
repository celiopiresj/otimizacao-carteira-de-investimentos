# import install_packages
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import linprog, minimize

# Define os tickers dos ativos financeiros a serem analisados
tickers = ["PETR3.SA", "^BVSP", "^GSPC", "VALE3.SA", "ITUB4.SA", "B3SA3.SA"]

# Define as datas para o intervalo de coleta de dados
data_final = datetime.today()
data_inicial = data_final - timedelta(days=3*365)

# Coleta os dados de preço ajustado dos ativos
dados_mercado = yf.download(tickers, start=data_inicial, end=data_final)
dados_mercado = dados_mercado["Adj Close"]
dados_mercado = dados_mercado.dropna()
dados_mercado.columns = ["B3", "ITAU",
                         "PETROBRAS", "VALE", "IBOVESPA", "S&P500"]

# Calcular retornos logarítmicos para cada ativo
retornos = np.log(dados_mercado / dados_mercado.shift(1)).dropna()

# Calcular a volatilidade (risco) dos retornos
volatilidade = retornos.std() * np.sqrt(252)

# Função para calcular o Value at Risk (VaR)


def calcular_var(dados, nivel=0.05):
    var = np.percentile(dados, nivel * 100)
    return var

# Função para calcular o Conditional Value at Risk (CVaR)


def calcular_cvar(dados, nivel=0.05):
    var = calcular_var(dados, nivel)
    cvar = dados[dados < var].mean()
    return cvar


# Calcula o VaR e CVaR para os retornos
var = calcular_var(retornos)
cvar = calcular_cvar(retornos)

# Exibe os resultados calculados
print("Retornos Medios:")
print(retornos.mean())
print("\nVolatilidade (Risco):")
print(volatilidade)
print("\nVaR:")
print(var)
print("\nCVaR:")
print(cvar)

# Função para otimizar a carteira


def otimizar_carteira(retornos, risco, risco_maximo):
    n = len(retornos)

    # Função objetivo: maximizar o retorno
    def objetivo(pesos):
        return -np.dot(pesos, retornos)

    # Restrição de risco
    def restricao(pesos):
        return risco_maximo - np.sqrt(np.dot(pesos.T, np.dot(np.diag(risco**2), pesos)))

    # Restrições e limites dos pesos dos ativos
    restricoes = {'type': 'ineq', 'fun': restricao}
    limites = [(0, 1) for _ in range(n)]
    pesos_iniciais = np.ones(n) / n  # Pesos iniciais iguais

    # Resolver problema de otimização
    resultado = minimize(objetivo, pesos_iniciais, method='SLSQP',
                         bounds=limites, constraints=restricoes)

    return resultado.x


# Executa a otimização da carteira com limite de risco de 0.2
pesos = otimizar_carteira(retornos.mean(), volatilidade, 0.2)
pesos_percent = [peso * 100 for peso in pesos]

# Visualiza a Fronteira Eficiente
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
plt.savefig('fronteira_eficiente.png')
plt.show()

# Visualiza a Alocação dos Pesos
plt.figure(figsize=(10, 6))
bars = plt.bar(dados_mercado.columns, pesos_percent)
plt.xlabel('Ativos')
plt.ylabel('Peso (%)')
plt.title('Distribuição da Carteira')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2 - 0.1, yval + 0.5, f'{yval:.2f}%')

plt.savefig('alocacao_dos_pesos.png')
plt.show()

# Visualiza a Evolução dos Retornos
retornos_acumulados = (1 + retornos).cumprod() - 1
plt.figure(figsize=(10, 6))
plt.plot(retornos_acumulados)
plt.xlabel('Tempo')
plt.ylabel('Retornos Acumulados')
plt.title('Evolução dos Retornos')
plt.legend(dados_mercado.columns)
plt.savefig('evolucao_retornos.png')
plt.show()
