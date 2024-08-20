from commbank_api_client import create_client, Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import asyncio
import os
from dotenv import load_dotenv
from typing import Optional
from getpass import getpass
from datetime import datetime, timedelta

from utils import (
    filter_transactions,
    cli,
    DateIterator,
    load_json_file,
    json_write_back,
)

load_dotenv("./.env")

try:
    auth = os.environ["x-api-key"]
except:
    auth = None


def get_date_n_days_back(n: int) -> str:
    now = datetime.today()

    delta = timedelta(days=n)
    ret = now - delta
    result = ret.strftime("%d/%m/%Y")
    print(f"Current end date to read from transactions: {result}")
    return result


async def get_n_pages_transactions(
    usr: str, pwd: str, num_pages: Optional[int] = 1, debug: Optional[bool] = False
):
    results = asyncio.gather(
        *[get_ith_transaction(usr, pwd, int(x) + 1, debug) for x in range(num_pages)]
    )
    return await results


async def get_ith_transaction(
    usr: str, pwd: str, i: Optional[int] = 1, debug: Optional[bool] = False
):
    """
    Get the sum of rounding all transactions to the nearest dollar amount.
    TODO: Write function to work within a date range
    Args:
        - usr (str) : Commbank netbank ID
        - pwd (str) : User netbank password
        - i (int) : Page number to pull transactions (default = 1)
        - debug (bool) : More verbose printing for debugging (default = False)
    """

    async with Client(usr, pwd) as client:
        transactions = []
        # get account ID
        account_id = (await client.get_accounts())[0].id
        if debug:
            print(f"Login attempt successful for account ID: {account_id}")
        # filter unnecessary metadata
        trans_1 = await client.get_transactions(account_id, i)
        transactions = [filter_transactions(x) for x in trans_1]
        await client.close()

    if transactions is None:
        print("Cannot retrieve transactions")
        raise ValueError("Unable to pull transactions for your account")
    df = pd.DataFrame.from_records(transactions)
    if debug:
        print(df.head())

    df = df.loc[df["type"] == "OUT"]

    # TODO: Sum: (int(abs(row['amount'])) + 1) - abs(float(row['amount']))
    rounded_sum = 0.0
    for idx, row in df.iterrows():
        round_up = (-1 * int(row["amount"])) + 1
        val = -1 * float(row["amount"])
        diff = round_up - val
        rounded_sum += diff
    if debug:
        print(f"Page {i} has a sum of: ${round(rounded_sum, 2)}")

    return round(rounded_sum, 2), df


def transform(df: pd.DataFrame, new_col_name: Optional[str] = "dollar_diff"):
    def _transform(row):
        rounded_sum = 0.0
        round_up = (-1 * int(row["amount"])) + 1
        val = -1 * float(row["amount"])
        diff = round_up - val
        rounded_sum += diff
        return round(rounded_sum, 2)

    col = [_transform(row) for idx, row in df.iterrows()]
    df[new_col_name] = col
    return df


def run_calc(name, days):
    print("Please log into the commbank client\n----------------")

    try:
        usr = os.environ[f"COMMBANK_USR_{name.upper()}"]
        pwd = os.environ[f"COMMBANK_PWD_{name.upper()}"]
    except KeyError:
        usr = str(input("Please enter your Netbank ID: "))

    end_date = get_date_n_days_back(int(days))

    results = asyncio.run(
        get_n_pages_transactions(
            usr,
            pwd,
            num_pages=10,
            debug=False,
        )
    )

    # get individual tuple lists
    rounded_savings = [x[0] for x in results]
    dfs: list = [x[1] for x in results]

    # concat dfs
    data: pd.DataFrame = pd.concat(dfs, axis=0)

    # Run the iterator
    iterator = DateIterator(df=data, stop=end_date)

    # Call and transform to get the rounded purchases
    df = iterator(transform=transform)

    total_amount = np.sum(df["dollar_diff"])

    # open data.json
    data = load_json_file("./data.json")
    val = round(np.sum(df["dollar_diff"]), 2)
    data[datetime.now().strftime("%d-%m-%Y")] = val
    return val


if __name__ == "__main__":
    args = cli()
    print("Please log into the commbank client\n----------------")

    try:
        usr = os.environ["COMMBANK_USR"]
    except KeyError:
        usr = str(input("Please enter your Netbank ID: "))

    end_date = get_date_n_days_back(int(args.days))

    if args.debug:
        print(f"Stopping requests on: {end_date}")

    results = asyncio.run(
        get_n_pages_transactions(
            usr,
            str(getpass("Enter your netbank password: ")),
            num_pages=args.page,
            debug=args.debug,
        )
    )

    # get individual tuple lists
    rounded_savings = [x[0] for x in results]
    dfs: list = [x[1] for x in results]

    # concat dfs
    data: pd.DataFrame = pd.concat(dfs, axis=0)

    # Run the iterator
    iterator = DateIterator(df=data, stop=end_date)

    # Call and transform to get the rounded purchases
    df = iterator(transform=transform)

    if args.save:
        filename = f"rounded-purchases-last-{args.days}-days.csv"
        df.to_csv(f"{args.persist}/{filename}")

    total_amount = np.sum(df["dollar_diff"])

    # open data.json
    data = load_json_file("./data.json")
    data[datetime.now().strftime("%d-%m-%Y")] = round(np.sum(df["dollar_diff"]), 2)
    json_write_back("./data.json", data)
