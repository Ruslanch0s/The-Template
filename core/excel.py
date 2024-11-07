from __future__ import annotations

from typing import Optional

from openpyxl import Workbook, load_workbook
import os

from openpyxl.worksheet.worksheet import Worksheet
from config import config
from models.account import Account


class Excel:
    """
    Класс для работы с excel файлами
    """

    def __init__(self, account: Optional[Account] = None) -> None:
        self.account = account
        self.file = config.PATH_EXCEL
        self.table = self.get_table()
        self.sheet: Worksheet = self.table.active
        if account:
            self.acc_row = self.find_acc_row(str(self.account.profile_number))

    def get_table(self) -> Workbook:
        if not os.path.exists(self.file):  # Если файл не существует, создаем его
            table = self.create_excel()
        else:
            table = load_workbook(self.file)
        return table

    def create_excel(self) -> Workbook:
        """
        Создает excel файл и заполняет его заголовками.
        :return: None
        """
        table = Workbook()  # Создаем новую таблицу
        table.active["A1"] = "Profile Number"  # Заполняем ячейки
        table.active["B1"] = "Address"  # Заполняем ячейки
        table.active["C1"] = "Password"  # Заполняем ячейки
        table.active["D1"] = "Seed"  # Заполняем ячейки
        table.active["E1"] = "Private Key"  # Заполняем ячейки
        table.active["F1"] = "Proxy"  # Заполняем ячейки
        table.save(self.file)  # Сохраняем таблицу
        return table

    def find_acc_row(self, profile_number: str) -> int:
        """
        Находит номер строки в таблице по номеру профиля. Если строки нет, добавляет ее.
        :param profile_number: номер профиля
        :return: номер строки
        """
        for row in self.sheet.iter_rows(min_row=2, max_col=1):
            if str(row[0].value) == profile_number:
                return row[0].row
        add_row = self.sheet.max_row + 1
        self.sheet.cell(row=add_row, column=1, value=profile_number)
        return add_row

    def add_row(self, values: list) -> None:
        """
        Добавляет значения из списка в строку в конец таблицы.
        :param values: список значений
        :return:
        """
        self.sheet.append(values)
        self.table.save(self.file)

    def set_cell(self, column_name: str, value: str, row: Optional[int] = None) -> None:
        """
        Устанавливает значение в ячейку по имени столбца в строке аккаунта.
        :param column_name: имя столбца
        :param value: значение
        :param row: номер строки, если не указан, то берется строка аккаунта
        :return: None
        """
        row = self.acc_row if not row else row

        col_num = self.find_column(column_name)
        if not col_num:
            col_num = self.add_column(column_name)
        self.sheet.cell(row=row, column=col_num, value=value)
        self.table.save(self.file)

    def add_column(self, column_name: str) -> int:
        """
        Добавляет столбец в конец таблицы.
        :param column_name: имя столбца
        :return: номер столбца
        """
        col_num = self.sheet.max_column + 1
        self.sheet.cell(row=1, column=col_num, value=column_name)
        self.table.save(self.file)
        return col_num

    def find_column(self, column_name: str) -> int:
        """
        Находит номер столбца по имени.
        :param column_name: имя столбца
        :return:
        """
        for row in self.sheet.iter_rows(max_row=1):
            for cell in row:
                if cell.value == column_name:
                    return cell.column
        return 0

    def get_cell(self, column_name: str, row: Optional[int] = None) -> str | int | None:
        """
        Возвращает значение ячейки по имени столбца из строки аккаунта.
        :param column_name: имя столбца
        :return: значение ячейки
        """
        row = self.acc_row if not row else row

        col_num = self.find_column(column_name)

        return self.sheet.cell(row=row, column=col_num).value

    def get_column(self, column_name: str) -> list[str]:
        """
        Возвращает список значений столбца по имени.
        :param column_name: имя столбца
        :return: список значений столбца
        """
        col_num = self.find_column(column_name)
        if not col_num:
            raise ValueError(f"Column with name '{column_name}' not found.")
        column_values = []
        for raw in self.sheet.iter_cols(min_col=col_num, max_col=col_num, min_row=2):
            for cell in raw:
                column_values.append(cell.value)

        return column_values

    def get_row(self, row: Optional[int] = None) -> list[str]:
        """
        Возвращает список значений из строки аккаунта.
        :param row: номер строки, если не указан, то берется строка аккаунта
        :return: список значений строки
        """
        row = self.acc_row if not row else row
        row_values = []
        for raw in self.sheet.iter_rows(min_row=row, max_row=row):
            for cell in raw:
                row_values.append(cell.value)

        return row_values

    def increase_counter(self, column_name: str, number: int = 1, row: Optional[int] = None) -> None:
        """
        Увеличивает значение счетчика на 1 или на указанное число. Если столбец не существует, создает его.
        Если ячейка пустая, устанавливает значение 1.
        :param column_name: имя столбца
        :param number: на сколько увеличить
        :return: None
        """
        row = self.acc_row if not row else row
        col_num = self.find_column(column_name)
        if not col_num:
            col_num = self.add_column(column_name)
        cell = self.sheet.cell(row=row, column=col_num)
        if cell.value:
            cell.value += number
        else:
            cell.value = number
        self.table.save(self.file)
