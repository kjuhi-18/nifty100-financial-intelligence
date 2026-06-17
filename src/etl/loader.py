from pathlib import Path


class ExcelLoader:

    def __init__(self, data_path="data/raw"):
        self.data_path = Path(data_path)

    def load_excel(self, file_name):
        pass