# The-Template

Python 3.10

```commandline
pip install --upgrade pip
pip install botright
playwright install
python -c 'import hcaptcha_challenger as solver; solver.install(clip=True)'
```

### Описание

**Заготовка шаблона для создания скрипта автоматизации.**
Подготовлено для студентов обучающихся у https://t.me/maxzarev
Достаточно заполнить config и запустить файл run.py, чтобы скрипт начал запускать профили в ADS.

#### Возможности
- Запускает профили в ADS Power
- Установка прокси в профили ADS
- Авторизация в Metamask
- Создание и импорт Metamask
- Работа с расширениями
- Работа с всплывающими окнами
- Управление браузером ADS
- Работа из Excel файла или текстового файла
- Отчетность в Excel
- Расписание
- Выводы с биржи OKX
- Работа с балансами в EVM сетях
- Перевод токенов в ERC20 сетях
- Уведомления в телеграм

  **В планах:**
- Обмен любых ERC20 токенов в EVM сетях
- Вывод с любой биржи
- модуль шифрования и гайд

**Для запуска необходимо:**
- настроить файл config/settings.py.
- переименовать файл .env.example в .env и заполнить его.
- заполнить файлы в директории config/data

## Настройка:
Все настройки скрипта, все изменяемые данные загружаемые в скрипт, должны загружаться через файлы в директории 
`config`.

#### Структура директории `config`:
- `config/data` - файлы с данными для скрипта.
  - `config/data/ABIs` - технические json файлы с описанием работы смарт-контрактов.
  - `accounts.xlsx` **- файл с данными для работы скрипта. (Предпочтительно использовать xlsx)**
  - `config/data/addresses` - адреса кошельков для работы (если не используется файл accounts.xlsx).
  - `config/data/passwords` - пароли для метамасков (если не используется файл accounts.xlsx).
  - `config/data/private_keys` - приватные ключи для работы (если не используется файл accounts.xlsx).
  - `config/data/profile_numbers` - номера профилей в ADS для работы (если не используется файл accounts.xlsx).
  - `config/data/proxies` - proxy для установкив в профили, если надо настроить профили ADS. (если не используется файл accounts.xlsx).
  - `config/data/seeds` - seed для импорта метамасков (если не используется файл accounts.xlsx).
- `config/settings.py` - настройки скрипта.
- `config/.env` - приватные данные для скрипта.
- `config/chains` - настройка сетей для работы скрипта.
- `config/contracts` - адреса контрактов для работы скрипта.
- `config/tokens` - адреса токенов для работы скрипта.
- `config/__init__` - технический файл.

### Загрузка данных в скрипт:
Для загрузки данных в скрипт необходимо заполнить файлы в директории `config/data`.
- У всех файлов, которые имеют расширение .example, необходимо переименовать их, убрав .example. (они попадут в игнор лист git)
- Данные в скрипт можно загрузить либо из файла `accounts.xlsx`, либо из текстовых файлов в директории `config/data`.
- Предпочтительным способом является загрузка данных из файла `accounts.xlsx`.
- По стандарту при использовании модуля Excel данные будут записываться в таблицу `config/data/accounts.xlsx`.
- Если необходима работа с другими таблицами, помещайте их в папку `config/data`, скрипт будет искать таблицу в данной директории.
- Если при использовании модуля Excel указать несуществующую таблицу, она создастся в папке `config/data`.
- Если у вас нет Microsoft Excel, то можно использовать бесплатные аналоги:
  - LibreOffice Calc для Windows, Linux и macOS - https://www.libreoffice.org/
  - OpenOffice Calc для Windows, Linux и macOS - https://www.openoffice.org/
  - Numbers для macOS - https://apps.apple.com/us/app/numbers/id409203825?mt=12
- Способ загрузки данных в скрипт указывается в файле `config/settings.py` в переменной `accounts_source`, установите значение `excel` или `txt`.
- Для работы скрипта минимально необходимо заполнить номера профилей.
- Если вы укажите 100 номеров профилей и 150 паролей от метамаска, скрипт возьмет первые 100 профилей и 
  первые 100 паролей. (длина рабочих данных определяется по количеству номеров профилей).
- Если вам не нужно авторизоваться в метамаске, пароли от метамаска можно не указывать.
- Если вам не нужно отправлять транзакции в блокчейн при помощи модуля Onchain, приватные ключи можно не указывать.
- Если вам нужно работать с балансом кошелька в профиле и выводом с биржи, заполните адреса кошельков.
- Если указать приватные ключи, но не указывать адреса кошельков, скрипт самостоятельно определит адреса кошельков 
  по приватным ключам.
- Если вам нужно установить прокси в профили ADS укажите прокси в таблице. Формат `ip:port:login:password`
- Если у вас уже настроены прокси и их не нужно устанавливать, можно не указывать прокси.
- Если вам не нужно устанавливать прокси, но вы хотите проверять их на работоспособность и верность определяемого
  ip адреса, укажите прокси. Формат `ip:port:login:password`

### .env - загрузка приватных данных
Приватные данные для работы скрипта указываются в файле `config/.env`:
- удалите расширение `.example` из названия файла `config/.env.example`, чтобы скрипт мог загрузить приватные данные.
- `OKX_API_KEY_MAIN` - ключ API для работы с биржей OKX.
- `OKX_SECRET_KEY_MAIN` - секретный ключ API для работы с биржей OKX.
- `OKX_PASSPHRASE_MAIN` - пароль для работы с биржей OKX.
- `BOT_TOKEN` - токен бота для отправки уведомлений в телеграм. (можно получить в телеграм у @BotFather)

### Настройки в `config/settings.py`
Настройка работы скрипта делается в файле `config/settings.py`:
- `speed` - скорость работы робота в браузере, пауза между действиями в миллисекундах (от и до),
  увеличивайте если робот работает слишком быстро и элементы не успевают загружаться.
- `accounts_source` - источник данных для работы скрипта (excel или txt).
- `is_browser_run` - `True` или `False`,  запускать браузер или нет (например работа с балансами не требует запуска браузера).
  Eсли `False`, то не будет работать модуль ads, metamask, будет выходить ошибка.
- `date_format` - формат даты для записи в excel файл, при использовании методов работы с датами. (модуль datetime)
- `is_random` - `True` или `False`, случайный порядок выбора и запуска профилей.
- `is_schedule` - `True` или `False`, включать ли расписание и фильтрацию аккаунтов, которое настраивается в файле run в функции schedule_and_filter.
- `pause_between_profile` - пауза между запуском профилей в секундах, от и до.
- `cycle` - количество циклов работы скрипта (проходов по всем профилям).
- `pause_between_cycle` - пауза между каждой итерации цикла в секундах, от и до.
- `okx_proxy` - прокси для работы с биржей OKX, для защиты API по ip адресу или если вы находитесь в стране, где заблокирована биржа. (например РФ). Формат `ip:port:login:password`
- `set_proxy` - `True` или `False`, устанавливать прокси в профили или нет. Можно использовать даже если `is_browser_run = False`.
- `check_proxy` - `True` или `False`, проверять прокси на работоспособность или нет.
  сравнивает ip адреса прокси с ip адресом, который определяет скрипт. Работает только с `is_browser_run = True`
- `is_mobile_proxy` - `True` или `False`, используются ли мобильные прокси.
- `link_change_ip` - ссылка для смены ip адреса при использовании мобильных прокси.
- `start_chain` - стартовая сеть для работы скрипта в блокчейне. (не относится к метамаску)
- `gas_price_limit` - лимит цены газа для метода `Onchain.gas_price_wait`, ожидающий газ ниже указанного лимита в gwei.
- `chat_id` - id вашего аккаунта в телеграм, чтобы бот мог отправлять вам уведомления. (можно получить в боте @getmyid_bot)
- `alert_types` - тип логов, по которым необходимо отправлять уведомления в телеграм, возможные варианты:
  - "CRITICAL" - при выводе лога logger.critical()
  - "SUCCESS" - при выводе лога logger.success()
  - "ERROR" - при выводе лога logger.error()
  - "WARNING" - при выводе лога logger.warning()
  - "INFO" - при выводе лога logger.info()
  - "DEBUG" - при выводе лога logger.debug()
- `metamask_url` - адрес расширения метамаск, можно получить в адресной строке при открытии расширения на весь экран.

### Chains - хранилище сетей для работы скрипта

В файле `chains.py` содержится класс `Chains` (документация ниже), который используется для хранения объектов модели `Chain`, т.е. объекты
  сетей, которые используются для работы модулей `Metamask` и `Onchain`. 
- Класс `Chains` импортирован в файл `run.py`, вызывая класс по названию `Chains`, через точку можно получить доступ ко всем объектам сетей.
- Информацию для заполнения объектов сетей можно получить с сайтов  https://chainlist.org/, https://chainid.network/chains.json и https://api.debank.com/chain/list
- Название переменных для хранения объектов сетей пишите в большом регистре, название точно должно отражать название и тип сети, например: `ETHEREUM`, `ARBITRUM_ONE`. 
- Название переменных для хранения объектов сетей должно быть уникальным, не должно повторяться.
- Название переменных для хранения объектов сетей должно совпадать с названием сети в параметре `name` у объекта сети, без учета регистра.
- Если есть 2 сети одна Mainnet другая Testnet, то название переменных для хранения объектов сетей должно быть одинаковым, но вторая сеть должна иметь в конце названия `_TESTNET`, так же добавьте слово `testnet` в `name` и `metamask_name`.
- Для добавления сетей в класс `Chains` используется модель `Chain`, класс `Chain` располагается в файле `models/chain.py`. Описание класса будет ниже.
- Метод класса `get_chain(cls, name: str) -> Chain`, который позволяет найти нужный объект сети по названию, ищется полное соответствие без учета регистра,
- Метод класса `get_chains_list(cls) -> list[Chain]`, который позволяет получить список всех объектов сетей из класса `Chains`. Удобно для перебора всех сетей.

#### Примеры использования:
- в `config/settings.py` в параметре `start_chain` можно указать стартовую сеть для работы скрипта: `start_chain = Chains.ETHEREUM`
- если необходимо выбрать сеть в метамаске, в метод `select_chain`, можно передать объект сети из класса `Chains`: `bot.metamask.select_chain(Chains.ETHEREUM)`
- если необходимо добавить сеть в метамаск, в метод `set_chain`, можно передать объект сети из класса `Chains`: `bot.metamask.set_chain(Chains.ETHEREUM)`
- при создании объектов `Token`, в конфигурации токенов в файле `config/tokens.py`, сеть токена указывается через объект сети из класса `Chains`: `chain = Chains.ETHEREUM`
- при создании объектов `Contract`, в конфигурации контрактов в файле `config/contracts.py`, сеть контракта указывается через объект сети из класса `Chains`: `chain = Chains.ETHEREUM`
- при поиске нужного токена в `Tokens`, в методе `get_token_by_symbol`, можно передать объект сети из класса `Tokens.get_by_symbol('USDT', Chains.ETHEREUM)`
- при создании объекта подключения к блокчейну через класс Onchain, в параметре `chain` можно передать объект сети из класса `onchain_ethereum = Onchain(account, Chains.ETHEREUM)`
- можно получить список всех объектов сетей из класса `Chains` через метод класса `get_chains_list`: `chains = Chains.get_chains_list()`, далее можно перебрать все сети в цикле,
создавать объекты onchain, для работы с несколькими сетями:
```python
# получаем список сетей
chains = Chains.get_chains_list()
for chain in chains:
    # создаем объект onchain для работы с балансами
    onchain = Onchain(bot.account, chain)
    # получаем баланс нативного токена сети
    onchain.get_balance()
```

### Сhain - модель сети, хранилище данных сети
Модель Chain, используется для создания объектов сети, класс `Chain` располагается в файле `models/chain.py`.
Модель Chain, используется для заполнения объектов сетей в классе `Chains`, который хранит все объекты сетей для работы скрипта.
Модель Chain, используется в аннотациях методов и функций, где необходимо указать сеть для работы.
Объект Chain, используется везде где необходимо взаимодействие с сетью:
- в модуле `Metamask` для выбора сети, добавления сети.
- в модуле `Onchain` для создания объекта подключения к блокчейну.
- в модуле `Tokens` для создания объектов токенов.
- в модуле `Contracts` для создания объектов контрактов.

**При создании объекта Chain необходимо указать следующие следующие параметры:**
- `name` - название сети, желательно использовать название сети совпадающее с названием переменной в классе `Chains`.
- `rpc` - rpc адрес сети, можно получить с сайтов https://chainlist.org/, https://chainid.network/chains.json и 
- https://api.debank.com/chain/list,  данный адрес rpc ноды будет использоваться для добавления сети в метамаске, а так же для подключения к блокчейну
  в модуле Onchain (отправка транзакций и получения балансов)
- `chain_id` - id сети можно получить с сайтов https://chainlist.org/, https://chainid.network/chains.json и 
- https://api.debank.com/chain/list, данный id сети будет использоваться для добавления сети в метамаске, а так же для подключения к блокчейну
  в модуле Onchain (отправка транзакций и получения балансов)
- `metamask_name` - название сети в метамаске, будет использоваться при добавлении сети в метамаск, а так же
   для выбора. (по стандарту берется из параметра name).
- `tx_type` - тип транзакции блокчейна. `0 - legacy`, `2 - eip1559`, если указать неверно, могут перестать работать транзакции,
   можно получить с сайта https://api.debank.com/chain/list, по стандарту стоит 2 (eip1559).
- `native_token` - название нативного токена сети, по стандарту стоит `ETH`, нужно для работы с балансами.
А так же для ведения логов.
- `okx_name` - название сети в бирже OKX, корректный список названий сетей можно получить
вызвав метод `bot.okx.get_chains()` в скрипте, если указать некорректно перестанет работать вывод с биржи,
так же список названий есть в объявленном методе `OKX.withdraw()` в файле `modules/okx_py.py`.

Обязательными параметрами являются `name`, `rpc` и `chain_id`, но настоятельно рекомендуется заполнять все поля.

### Tokens - хранилище токенов для работы скрипта

В файле `tokens.py` содержится класс `Tokens`, который используется для хранения объектов модели `Token`, т.е. объекты
  токенов, которые используются для работы модуля `Onchain`, содержат все все необходимые данные описываюшие
токенов в различных блочейнах.
- Класс `Tokens` импортирован в файл `run.py`, вызывая класс по названию `Tokens`, через точку можно получить доступ ко всем объектам токенов.
- Адреса смарт-контрактов токенов в нужной сети можно получить с сайтов https://dropstab.com, http://coinmarketcap.com, https://coingecko.com
- Информацию для заполнения объектов токенов можно получить в эксплорерах блокчейнов (ищите по адресу контракта):
  - токены в сети Ethereum можно получить с сайта https://etherscan.io/tokens
  - токены в сети Binance Smart Chain можно получить с сайта https://bscscan.com/tokens
  - токены в сети Arbitrum One можно получить с сайта https://arbiscan.io/tokens
  - и т.д. Практически у всех популярных блокчейнов есть свои эксплореры от etherscan.io.
- Название переменных для хранения объектов токенов пишите в большом регистре, название должно состоять из
официального тикера токена и сети, например: `USDT_ETHEREUM`, `USDT_ARBITRUM_ONE`.
- Создавайте объекты токенов только для ERC20 токенов, создавать объекты нативных токенов (ETH, BNB, MATIC) различных блокчейнов не нужно.
- Названия переменных для хранения объектов токенов должно быть уникальным, не должно повторяться.
- Для добавления токенов в класс `Tokens` используется модель `Token`, класс `Token` располагается в файле `models/token.py`. Описание класса будет ниже.
- Метод класса `get_token_by_address(cls, address: str) -> Token`, который позволяет
найти нужный объект токена по адресу контракта, ищется полное соответствие, без учета регистра.
- Метод класса `get_token_by_symbol(cls, symbol: str, chain: Chain) -> Token`, 
который позволяет найти нужный объект токена по символу токена и сети, ищется полное соответствие, без учета регистра.
- Метод класса `get_tokens_by_chain(cls, chain: Chain) -> list[Token]`, который позволяет 
получить список всех объектов токенов из класса `Tokens` для определенной сети.
- Метод класса `get_tokens(cls) -> list[Token]`, который позволяет получить список всех объектов токенов из класса `Tokens`.
- Метод класс `add_token(cls, token: Token)`, который позволяет добавить объект токена в класс `Tokens` на время работы скрипта.

#### Примеры использования:
- можно передать объект токена в метод `send_token`, для отправки токена: `bot.onchain.send_token(Tokens.USDT_ETHEREUM, '0x...', 0.1)`
- можно передать объект токена в метод `get_balance`, для получения баланса токена: `bot.onchain.get_balance(Tokens.USDT_ETHEREUM)`
- можно найти объект токена по адресу контракта: `token = Tokens.get_token_by_address('0x...')`
- можно найти объект токена по символу токена и сети: `token = Tokens.get_token_by_symbol('USDT', Chains.ETHEREUM)`
- можно получить список всех объектов токенов из класса `Tokens`: `tokens = Tokens.get_tokens()` и далее перебрать все токены в цикле.
- можно получить список всех объектов токенов для определенной сети: `tokens = Tokens.get_tokens_by_chain(Chains.ETHEREUM)` и далее перебрать все токены в цикле.

```python
# получаем список токенов для сети Ethereum, проверяем баланс и отправляем токены
tokens = Tokens.get_tokens_by_chain(Chains.ETHEREUM)
for token in tokens:
    # проверяем баланс токена
    balance = bot.onchain.get_balance(token=token)
    print(f'Баланс токена {token.symbol} = {balance}')
    # отправляем токен
    bot.onchain.send_token(token, '0x...', balance)
```

```python
# проверяем балансы всех токенов во всех сетях
chains = Chains.get_chains_list()
for chain in chains:
    chain_instance = Onchain(bot.account, chain)
    native_balance = chain_instance.get_balance()
    print(f'Баланс токена {chain.native_token} = {native_balance}')
    tokens = Tokens.get_tokens_by_chain(chain)
    for token in tokens:
        # проверяем баланс токена
        balance = chain_instance.get_balance(token=token)
        print(f'Баланс токена {token.symbol} = {balance}')
    
```


