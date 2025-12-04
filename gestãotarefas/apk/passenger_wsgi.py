import sys
import os

# Adiciona o diretório da aplicação ao Python Path para que os módulos sejam encontrados.
sys.path.insert(0, os.path.dirname(__file__))

# Importa a instância 'app' do seu arquivo principal (gestaotarefa.py).
# O alias 'as application' é uma convenção que muitos servidores WSGI, como o Phusion Passenger, procuram.
from gestaotarefa import app as application
