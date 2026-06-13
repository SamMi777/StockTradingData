# Grab stock lunr
import yfinance as yf

# import sqlalchemy for postgres connection
from sqlalchemy import create_engine

# import dotenv for environment variables streaming
import dotenv

dotenv.load_dotenv()

# import env variables
import os

username = os.getenv("pg_username")
password = os.getenv("password")
database = os.getenv("database")
host = os.getenv("host")
port = os.getenv("port")

tickers = os.getenv("tickers").strip("[]").replace('"', "").split(", ")

# create connection string for postgres
connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# create engine
engine = create_engine(connection_string)

for i in range(len(tickers)):
    tickers[i] = tickers[i].strip()

    dataset = yf.download(tickers[i], interval="30m", period="60d", auto_adjust=True)

    # Remove ticker level from MultiIndex columns
    if hasattr(dataset.columns, "levels"):
        dataset.columns = dataset.columns.get_level_values(0)

    # Convert index into a real column
    dataset = dataset.reset_index()

    # Optional: rename for consistency
    dataset.columns = [c.lower() for c in dataset.columns]

    ticker = tickers[i].lower()

    # write data to postgres
    dataset.to_sql(ticker, engine, if_exists="replace", index=True, schema="stock")
