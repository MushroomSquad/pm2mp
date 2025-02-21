class dual_method:
    """
    Декоратор для определения метода с двумя реализациями — синхронной и асинхронной.
    Для регистрации альтернативной реализации используется метод .register().
    """

    def __init__(self, func):
        self.sync_func = func
        self.async_func = None
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__

    def register(
        self,
    ):
        """
        Метод для регистрации альтернативной реализации.
        Использование:

            @<method>.register(async_version=True)
            async def _(self, ...):
                ...
        """

        def decorator(func):
            self.async_func = func
            return self

        return decorator

    def __get__(self, instance, owner):
        """
        Метод дескриптора, который вызывается при обращении к методу через экземпляр.
        Здесь происходит выбор между синхронной и асинхронной версией.
        """
        if instance is None:
            return self

        if instance.async_mode:
            if self.async_func is None:
                raise ValueError(
                    f"Async version for {self.sync_func.__name__} is not registered."
                )
            return self.async_func.__get__(instance, owner)
        return self.sync_func.__get__(instance, owner)

    def __call__(self, *args, **kwargs):
        """
        Фоллбэк-реализация __call__, чтобы линтер видел, что объект callable.
        Обычно объект не вызывается напрямую, а через дескриптор (__get__).
        Здесь, если первый аргумент является экземпляром, мы делегируем вызов привязанному методу.
        """
        if args:
            instance = args[0]
            bound_method = self.__get__(instance, type(instance))
            return bound_method(*args[1:], **kwargs)
        raise TypeError("Метод должен вызываться через экземпляр класса.")
