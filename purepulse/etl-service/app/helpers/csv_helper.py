import os
from datetime import datetime, date
from typing import Optional

import pandas as pd


class CsvHelper:

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path


    def create_file(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "x"):
                pass
        except FileExistsError:
            pass
        except OSError as e:
            raise OSError(f"Failed to create file or directory at {self.file_path}: {str(e)}")


    def is_empty(self) -> bool:
        try:
            return os.stat(self.file_path).st_size == 0
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at {self.file_path}")
        except OSError as e:
            raise OSError(f"Error checking file size at {self.file_path}: {str(e)}")


    def remove_existing_rows_from_df(
        self,
        df: pd.DataFrame,
        column: str
    ) -> pd.DataFrame:
        try:
            if self.is_empty():
                return df
            csv_df = pd.read_csv(self.file_path)
            if column not in df.columns or column not in csv_df.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame")
            return df[~df[column].isin(csv_df[column])]
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at {self.file_path}")
        except pd.errors.EmptyDataError:
            return df
        except Exception as e:
            raise Exception(f"Error processing DataFrame: {str(e)}")


    def get_last_datetime(
        self,
        column: str,
        datetime_format: str
    ) -> Optional[datetime]:
        try:
            df = pd.read_csv(self.file_path, usecols=[column])
            if df.empty or column not in df.columns:
                return None
            max_value = df[column].max()
            if pd.isna(max_value):
                return None
            return datetime.strptime(max_value, datetime_format)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at {self.file_path}")
        except pd.errors.EmptyDataError:
            return None
        except ValueError as e:
            raise ValueError(f"Error parsing datetime with format {datetime_format}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error reading datetime from column {column}: {str(e)}")


    def get_last_date(
        self,
        column: str,
        datetime_format: str
    ) -> Optional[date]:
        try:
            dt = self.get_last_datetime(column=column, datetime_format=datetime_format)
            return dt.date() if dt else None
        except Exception as e:
            raise Exception(f"Error getting date from column {column}: {str(e)}")


    def sort(self, column: str) -> None:
        try:
            csv_df = pd.read_csv(self.file_path)
            if column not in csv_df.columns:
                raise ValueError(f"Column '{column}' not found in CSV")
            csv_df.sort_values(by=[column], inplace=True)
            csv_df.to_csv(self.file_path, index=False)
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at {self.file_path}")
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except Exception as e:
            raise Exception(f"Error sorting CSV by column {column}: {str(e)}")
