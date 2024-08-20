from typing import Optional, List, Tuple, Any
from commbank_api_client.types import Transaction
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
import argparse
import os
import json


def cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-page",
        "--page",
        dest="page",
        metavar="PAGE",
        default=1,
        type=int,
        help="Page number to pull transactions from (default=1)",
    )

    parser.add_argument(
        "-debug",
        "--debug",
        dest="debug",
        metavar="DEBUG",
        default=False,
        type=bool,
        help="Web app debug flag for testing python functions (default=False)",
    )

    parser.add_argument(
        "-days",
        "--days",
        dest="days",
        metavar="days",
        default=30,
        type=int,
        help="Number of days to check back (default=30)",
    )

    parser.add_argument(
        "-save",
        "--save",
        dest="save",
        metavar="save",
        default=True,
        type=bool,
        help="Toggle saving (default=True)",
    )

    parser.add_argument(
        "-persist",
        "--persist",
        dest="persist",
        metavar="persist",
        default="./persist",
        type=str,
        help="Directory to save output files (default=./persist)",
    )

    args = parser.parse_args()
    return args


def filter_transactions(
    transaction: Transaction,
    allowed_keys: Optional[List[str]] = ["id", "amount", "pending", "created"],
):
    """
    Remove all unneccessary metadata from retrieved transaction
    """
    #
    result = {}
    for key in allowed_keys:
        if key == "amount":
            if float(transaction.__getattribute__(key)) < 0:
                result["type"] = "OUT"
            else:
                result["type"] = "IN"
        result[key] = transaction.__getattribute__(key)
    return result


def identity(x):
    return x


@dataclass
class DateInt:
    day: int
    month: int
    year: int

    def __eq__(self, x):
        try:
            if x.day == self.day and x.month == self.month and x.year == self.year:
                return True
            else:
                return False
        except:
            return False

    def __lt__(self, x):
        try:
            if x.day < self.day and x.month <= self.month and x.year <= self.year:
                return True
            else:
                if x.month < self.month:
                    return True
                return False
        except:
            return False

    def __gt__(self, x):
        try:
            if x.day > self.day and x.month >= self.month and x.year >= self.year:
                return True
            else:
                return False
        except:
            return False

    def __repr__(self):
        return f"{self.day}/{self.month}/{self.year}"


class DateIterator:
    """
    Description:
    ---
    Generator class yielding a mask array for rows that satisfy the date constraint
    """

    def __init__(
        self, df: pd.DataFrame, stop: str, date_col_name: Optional[str] = "created"
    ):

        # init attributes
        self.df = df
        self.stop_date = stop
        self.col = date_col_name
        self.row_idx = -1
        self.switch = False

        # init integer comparisons
        int_vals = self.stop_date.split("/")
        self._stop = DateInt(int(int_vals[0]), int(int_vals[1]), int(int_vals[2]))
        print(f"Finished initializing DateIterator. Finishing on: {self._stop}")

    def _is_date_after(self, row):
        date_ = row["created"].strftime("%d/%m/%Y")
        date = date_.split("/")

        check = DateInt(int(date[0]), int(date[1]), int(date[2]))

        if check < self._stop:
            return True
        else:
            return False

    def __iter__(self):
        self.row_idx = self.row_idx + 1
        if self.row_idx > self.df.shape[0]:
            raise StopIteration("DF searched")
        row = self.df.iloc[self.row_idx]
        yield self._is_date_after(row)

    def __call__(self, transform: Optional[callable] = identity) -> pd.DataFrame:
        """
        Runs the entire generation sequence with an optional transform function to post process the dataframe
        """
        mask = []
        loop = True
        while loop:
            try:
                mask.append(next(self.__iter__()))
            except IndexError:
                loop = False
        df = self.df.iloc[mask]
        if not transform == identity:
            df = transform(df)
            assert isinstance(df, pd.DataFrame)
        assert df.shape[0] <= self.df.shape[0]
        return df


def load_json_file(file_loc: str):
    if not os.path.exists(file_loc):
        raise ValueError("Incorrect json file path.")
    else:
        try:
            with open(file_loc, "r") as file:
                return json.load(file)
        except:
            return {}


def json_write_back(file_loc: str, obj: Any):
    if not os.path.exists(file_loc):
        raise ValueError("Incorrect json file path.")
    else:
        with open(file_loc, "w") as file:
            file.write(json.dumps(obj))
