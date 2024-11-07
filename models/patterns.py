class Singleton:
    """
    Паттерн Singleton, который позволяет создать только один экземпляр класса.
    """
    # словарь для хранения экземпляров класса
    _instances = {}

    def __new__(cls, *args, **kwargs):
        """
        Функция запускаемая при инициализации объекта класса
        :param args: аргументы
        :param kwargs: именованные аргументы
        """
        # если экземпляр класса еще не создан, то создаем его
        if cls not in cls._instances:
            # создаем экземпляр класса и записываем его в словарь
            cls._instances[cls] = super(Singleton, cls).__new__(cls)
        # возвращаем экземпляр класса
        return cls._instances[cls]
