from abc import ABC, abstractmethod

from core.bot import Bot


class BaseProject(ABC):
    def __init__(self, bot: Bot):
        self.bot = bot

    @abstractmethod
    def _table_data_ready_to_start(self):
        pass

    @abstractmethod
    def _run_tasks(self):
        pass

    def run(self):
        self._table_data_ready_to_start()
        self._run_tasks()
