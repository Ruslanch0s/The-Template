from __future__ import annotations

from typing import Optional
from datetime import datetime

from loguru import logger
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
        self.table = self._get_table()
        self.sheet: Worksheet = self.table.active
        if account:
            self.acc_row = self._find_acc_row(str(self.account.profile_number))

    def _get_table(self) -> Workbook:
        """
        Получает таблицу из файла, если файла нет, создает его.
        :return: объект таблицы
        """
        if not os.path.exists(self.file):  # Если файл не существует, создаем его
            table = self._create_excel()
        else:
            table = load_workbook(self.file)
        return table

    def _create_excel(self) -> Workbook:
        """
        Создает excel файл и заполняет его стандартными заголовками.
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

    def _find_acc_row(self, profile_number: str) -> int:
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
        Добавляет значения из списка в строку в конец таблицы. Каждое значение в отдельную ячейку.
        :param values: список значений
        :return: None
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
            logger.warning(f"Столбец '{column_name}' не найден, создаем новый.")
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
        :return: номер столбца
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
        :param row: номер строки, если не указан, то берется строка аккаунта
        :return: значение ячейки, может быть строкой, числом или None
        """
        row = self.acc_row if not row else row

        col_num = self.find_column(column_name)

        return self.sheet.cell(row=row, column=col_num).value

    def get_column(self, column_name: str) -> list[str | int | None]:
        """
        Возвращает список значений столбца по имени.
        :param column_name: имя столбца
        :return: список значений столбца
        """
        col_num = self.find_column(column_name)
        if not col_num:
            raise ValueError(f"Столбец '{column_name}' не найден")
        column_values = []
        for raw in self.sheet.iter_cols(min_col=col_num, max_col=col_num, min_row=2):
            for cell in raw:
                column_values.append(cell.value)

        return column_values

    def get_row(self, row: Optional[int] = None) -> list[str | int | None]:
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
            logger.warning(f"Столбец '{column_name}' не найден, создаем новый.")
            col_num = self.add_column(column_name)
        cell = self.sheet.cell(row=row, column=col_num)
        if cell.value:
            cell.value += number
        else:
            cell.value = number
        self.table.save(self.file)

    def set_date(self, column_name: str, row: Optional[int] = None) -> None:
        """
        Записывает текущее время и дату в excel таблицу.
        Формат даты настраивается в файле config/settings.py
        :param column_name: имя столбца
        :param row: номер строки, если не указан, то берется строка аккаунта
        :return: None
        """
        row = self.acc_row if not row else row

        col_num = self.find_column(column_name)
        if not col_num:
            logger.warning(f"Столбец '{column_name}' не найден, создаем новый.")
            col_num = self.add_column(column_name)

        self.sheet.cell(row=row, column=col_num, value=datetime.now().strftime(config.date_format))
        self.table.save(self.file)

    def get_date(self, column_name: str, row: Optional[int] = None) -> datetime:
        """
        Возвращает дату из ячейки в таблице Excel, если в ячейке пусто, возвращает старую дату.
        Не указывайте столбец, где есть что-либо кроме даты, иначе получите ошибку.
        Формат даты настраивается в файле config/settings.py
        :param column_name: имя столбца
        :return: значение ячейки
        """
        row = self.acc_row if not row else row

        col_num = self.find_column(column_name)
        if not col_num:
            logger.warning(f"Столбец '{column_name}' не найден, создаем новый.")
            col_num = self.add_column(column_name)

        date_str = self.sheet.cell(row=row, column=col_num).value
        if date_str:
            date_object = datetime.strptime(date_str, config.date_format)
            return date_object
        logger.error(
            f"Не нашли дату в столбце '{column_name}' у аккаунта {self.account.profile_number}, возвращаем старую дату")
        return datetime.now().replace(year=2000)
