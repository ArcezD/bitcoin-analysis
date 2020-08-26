# /run.py
import os

from src.app import create_app

env_name = os.getenv('FLASK_ENV')

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = 'Expected environmecatnt variable {} not set.'.format(name)
        raise Exception(message)

# the values of those depend on your setup
POSTGRES_URL = get_env_variable('POSTGRES_URL')
POSTGRES_USER = get_env_variable('POSTGRES_USER')
POSTGRES_PW = get_env_variable('POSTGRES_PW')
POSTGRES_DB = get_env_variable('POSTGRES_DB')

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app = create_app(env_name, DB_URL)

if __name__ == '__main__':
  port = os.getenv('PORT')
  # run app
  app.run(host='0.0.0.0', port=port)