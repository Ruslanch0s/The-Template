from loguru import logger

from projects.base_project import BaseProject


class AuthMetamaskProject(BaseProject):
    def _table_data_ready_to_start(self) -> bool:
        if not self.bot.account.password:
            logger.error(
                f'#{self.bot.account.profile_number} Отсутсвует пароль для метамаска, авторизация не возможна.')
            return False

    def _run_tasks(self):
        self.bot.metamask.auth_metamask()
        address = self.bot.metamask.get_address()
        self.bot.excel.set_cell('Address', address)
        self.bot.metamask.set_language()


class CreateNewMetamaskProject(BaseProject):
    def _table_data_ready_to_start(self) -> bool:
        if self.bot.account.seed:
            logger.error(
                f'#{self.bot.account.profile_number} Сид фраза уже есть в таблице, создание кошелька не возможно.')
            return False

    def _run_tasks(self):
        address, seed, password = self.bot.metamask.create_wallet()
        self.bot.excel.set_cell('Address', address)
        self.bot.excel.set_cell('Seed', seed)
        self.bot.excel.set_cell('Password', password)


class ImportMetamaskProject(BaseProject):
    def _table_data_ready_to_start(self) -> bool:
        if not self.bot.account.seed:
            logger.error(
                f'#{self.bot.account.profile_number} Сид фраза отсутсвует в таблице, импорт кошелька не возможен.')
            return False

    def _run_tasks(self):
        address, seed, password = self.bot.metamask.import_wallet()
        self.bot.excel.set_cell('Address', address)
        self.bot.excel.set_cell('Seed', seed)
        self.bot.excel.set_cell('Password', password)
        self.bot.metamask.set_language()
