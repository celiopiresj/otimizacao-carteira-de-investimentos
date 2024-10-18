import subprocess
import sys

# Lista de pacotes a serem instalados
pacotes = ['yfinance', 'pandas', 'matplotlib', 'seaborn', 'numpy', 'scipy']

# Função para instalar pacotes


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Instalar cada pacote da lista
for pacote in pacotes:
    install(pacote)
