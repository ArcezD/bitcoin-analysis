import os

import datetime as dt
import requests
import json

from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from pandas.io.json import json_normalize

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

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(app)
ma = Marshmallow(app)

class NoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(255))

    def __init__(self, title, content):
        self.title = title
        self.content = content


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NoteModel

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


def dateparse (time_in_secs):    
    return dt.datetime.fromtimestamp(float(time_in_secs))


def load_df_data(csv_filepath):
  df=pd.read_csv(csv_filepath, parse_dates=[0], date_parser=dateparse)
  # rename province to state
  df.rename(columns={'Timestamp': 'datetime', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume_(BTC)': 'volume_btc', 'Volume_(Currency)': 'volume_currency', 'Weighted_Price': 'weighted_price'}, inplace=True)
  df.isnull().sum()
  df.dropna(inplace=True)
  return df


bitstamp_origin_df = load_df_data('data/bitstampUSD_1-min_data_2012-01-01_to_2020-04-22.csv')
coinbase_origin_df = load_df_data('data/coinbaseUSD_1-min_data_2014-12-01_to_2019-01-09.csv')


def get_bitcoin_values_from_bitstamp(date):
    origin = 'bitstamp'
    try:
        b1 = bitstamp_origin_df[pd.to_datetime(bitstamp_origin_df['datetime'].dt.date) == date]
        b1.sort_values(by='datetime')
        b2 = b1.iloc[[0, -1]]
        row = {
            'origin': origin,
            'max': b1['high'].max(),
            'low': b1['low'].min(),
            'open': b2.iloc[0, 1:2][0],
            'close': b2.iloc[1, 4:5][0]
        }
        return row
    except Exception as e:
        print(f'Error getting values for date {date} from {origin}')
        return {'origin': origin}


def get_bitcoin_values_from_coinbase(date):
    origin = 'coinbase'
    try:
        c1 = coinbase_origin_df[pd.to_datetime(coinbase_origin_df['datetime'].dt.date) == date]
        c1.sort_values(by='datetime')
        c2 = c1.iloc[[0, -1]] # get first and last row
        row = {
            'origin': origin,
            'max': c1['high'].max(), # get highest price of the day
            'low': c1['low'].min(), # get lower price of the day
            'open': c2.iloc[0, 1:2][0], # get first open value of the day
            'close': c2.iloc[1, 4:5][0] # get last close value of the day
        }
        return row
    except Exception as e:
        print(f'Error getting values for date {date} from {origin}')
        return {'origin': origin}

def get_bitcoin_close_price_from_coindesk(date):
    origin = 'coindesk'
    try:
        url = f'https://api.coindesk.com/v1/bpi/historical/close.json?start={date}&end={date}'
        response = (requests.get(url).text)
        response_json = json.loads(response)
        row = {
            'origin': origin,
            'close': response_json['bpi'][date] # get close value from api
        }
        return row
    except Exception as e:
        print(f'Error getting values for date {date} from {origin}')
        return {'origin': origin}

def get_consolidate_data_for_date(date):
    coinbase_data = get_bitcoin_values_from_coinbase(date)
    bitstamp = get_bitcoin_values_from_bitstamp(date)
    coindesk = get_bitcoin_close_price_from_coindesk(date)
    return pd.DataFrame([coinbase_data, bitstamp, coindesk])

@app.route('/btc')
def get_btc_for_date():
    date = request.args.get('date')
    results = get_consolidate_data_for_date(date).to_dict('records')
    #dumps(results.where(pd.notnull(results), None))
    #return jsonify({'results':results})
    return Response(json.dumps(results).replace(": NaN" , ': null'), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=1, port=8080, host='0.0.0.0')
