from asyncio import Semaphore
import asyncio
from subprocess import PIPE, Popen
import pathlib
import os
import platform

from typing import Optional, List, Dict, Union
from pydantic import BaseModel


class PM2AppConfig(BaseModel):
    # Обязательный параметр – путь к скрипту, который необходимо запустить
    script: str

    # Опциональные параметры
    name: Optional[str] = None  # Имя процесса
    args: Optional[List[str]] = None  # Аргументы для скрипта
    cwd: Optional[str] = None  # Рабочая директория
    interpreter: Optional[str] = None  # Интерпретатор (например, python, node)
    interpreter_args: Optional[List[str]] = None  # Аргументы для интерпретатора

    # Настройки запуска
    exec_mode: Optional[str] = None  # Режим выполнения: "fork" или "cluster"
    instances: Optional[Union[int, str]] = (
        None  # Количество инстансов (число или "max" для максимального числа процессов)
    )
    autorestart: Optional[bool] = True  # Автоматический рестарт процесса при сбое
    watch: Optional[bool] = False  # Мониторинг изменений файлов для перезапуска
    ignore_watch: Optional[List[str]] = (
        None  # Список директорий/файлов, которые не следует отслеживать
    )

    # Ограничение по памяти и рестарт
    max_memory_restart: Optional[Union[int, str]] = (
        None  # Лимит памяти (например, 100*1024*1024 или "100M")
    )
    restart_delay: Optional[int] = None  # Задержка перед перезапуском в мс
    max_restarts: Optional[int] = None  # Максимальное количество рестартов

    # Переменные окружения
    env: Optional[Dict[str, Union[str, int, float, bool]]] = (
        None  # Окружение по умолчанию
    )
    env_production: Optional[Dict[str, Union[str, int, float, bool]]] = (
        None  # Окружение для production
    )

    # Логирование и файлы PID
    error_file: Optional[str] = None  # Путь к файлу с логами ошибок
    out_file: Optional[str] = None  # Путь к файлу с логами вывода
    pid_file: Optional[str] = None  # Файл для хранения PID процесса
    merge_logs: Optional[bool] = False  # Объединять логи из разных инстансов
    log_date_format: Optional[str] = None  # Формат даты для логов

    # Дополнительные параметры PM2
    cron_restart: Optional[str] = None  # CRON-выражение для рестарта приложения
    listen_timeout: Optional[int] = None  # Таймаут ожидания слушателя (в мс)
    kill_timeout: Optional[int] = (
        None  # Таймаут ожидания корректного завершения процесса (в мс)
    )


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


class PM2MP:
    def __init__(self, semaphore_value: int = 2, async_mode: bool = False) -> None:
        self.node = "node"
        self.wrapper_file = (
            str(pathlib.Path(__file__).with_name("pm2wrapper.js")).replace(os.sep, "/")
            if platform.system() == "Windows"
            else str(pathlib.Path(__file__).with_name("pm2wrapper.js"))
        )
        cpu_count = os.cpu_count()
        self.semaphore: Semaphore = Semaphore(
            cpu_count if cpu_count else semaphore_value
        )
        self.async_mode = async_mode

    def _prepare_command(
        self,
        command,
        args,
    ):
        return (
            self.node
            + " -e"
            + f" require('{self.node}').{command}({args}).then(console.log).catch(console.error)"
        )

    def _run_process(
        self,
        program,
    ):
        process = Popen(
            program,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        return stdout if process.returncode == 0 else stderr

    async def _run_process_async(
        self,
        program,
    ):
        async with self.semaphore:
            process = await asyncio.subprocess.create_subprocess_exec(
                program,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout, stderr = await process.communicate()
            return stdout if process.returncode == 0 else stderr

    def _execude(
        self,
        command,
        args_list,
    ):
        programs = [self._prepare_command(command, args) for args in args_list]
        return [self._run_process(program) for program in programs]

    async def _execude_async(
        self,
        command,
        args_list,
    ):
        programs = [self._prepare_command(command, args) for args in args_list]
        tasks = [
            self._run_process_async(
                program,
            )
            for program in programs
        ]
        await asyncio.gather(*tasks)

    @dual_method
    def list(
        self,
        args: List[PM2AppConfig] = [],
    ):
        return self._execude("list", args)

    @list.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("list", args)

    @dual_method
    def start(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("start", args)

    @start.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("start", args)

    @dual_method
    def stop(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("stop", args)

    @stop.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("stop", args)

    @dual_method
    def restart(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("restart", args)

    @restart.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("restart", args)

    @dual_method
    def reload(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("reload", args)

    @reload.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("reload", args)

    @dual_method
    def delete(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("delete", args)

    @delete.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("delete", args)

    @dual_method
    def kill(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("delete", args)

    @kill.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("delete", args)

    @dual_method
    def describe(
        self,
        args: List = [PM2AppConfig],
    ):
        return self._execude("describe", args)

    @describe.register()
    async def _(
        self,
        args: List = [PM2AppConfig],
    ):
        return await self._execude_async("describe", args)

