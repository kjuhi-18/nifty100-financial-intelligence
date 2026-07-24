from pathlib import Path

import pandas as pd


class ExcelLoader:

    def __init__(self, data_path="data/raw"):
        self.data_path = Path(data_path)

    def load_excel(self, file_name, header=1):

        file_path = self.data_path / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"{file_name} not found")

        return pd.read_excel(file_path, header=header)

    def load_all(self, files):

        data = {}

        for file in files:
            data[file] = self.load_excel(file)

        return data
