from asyncio.subprocess import Process
import json
from asyncio import Semaphore
import asyncio
from subprocess import PIPE, Popen
import pathlib
import os
import platform
from typing import Any, Coroutine, List

from .models import PM2AppConfig, PM2Response
from .decorator import dual_method


class PM2MP:
    def __init__(
        self,
        semaphore_value: int = 2,
        async_mode: bool = False,
    ) -> None:
        self.node: str = "node"
        self.wrapper_file: str = (
            str(pathlib.Path(__file__).with_name("pm2wrapper.js")).replace(os.sep, "/")
            if platform.system() == "Windows"
            else str(pathlib.Path(__file__).with_name("pm2wrapper.js"))
        )
        cpu_count: int | None = os.cpu_count()
        self.semaphore: Semaphore = Semaphore(
            cpu_count if cpu_count else semaphore_value
        )
        self.async_mode: bool = async_mode

    def _prepare_command(
        self,
        command: str,
        args: dict,
    ) -> List[str]:
        return [
            self.node,
            "-e",
            f" require('{self.wrapper_file}').{command}({args})"
            + ".then(console.log)"
            + ".catch(console.error)",
        ]

    def _run_process(
        self,
        program: List[str],
    ) -> str:
        process: Popen = Popen(
            program,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
        )
        stdout: str
        stderr: str
        stdout, stderr = process.communicate()
        return stdout if process.returncode == 0 else stderr

    async def _run_process_async(
        self,
        program: List[str],
    ) -> bytes:
        async with self.semaphore:
            process: Process = await asyncio.subprocess.create_subprocess_exec(
                *program,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout: bytes
            stderr: bytes
            stdout, stderr = await process.communicate()
            return stdout if process.returncode == 0 else stderr

    def _execude(
        self,
        command: str,
        args_list: List[PM2AppConfig],
    ) -> List[PM2Response]:
        programs: List[List[str]] = [
            self._prepare_command(command, args.model_dump_json(exclude_none=True))
            for args in args_list
        ]
        return [
            PM2Response(**json.loads(res.strip()))
            for res in [
                self._run_process(
                    program,
                )
                for program in programs
            ]
        ]

    async def _execude_async(
        self,
        command: str,
        args_list: List[PM2AppConfig],
    ) -> List[PM2Response]:
        programs: List[List[str]] = [
            self._prepare_command(command, args.model_dump_json(exclude_none=True))
            for args in args_list
        ]
        tasks: List[Coroutine[Any, Any, bytes]] = [
            self._run_process_async(
                program,
            )
            for program in programs
        ]
        return [
            PM2Response(**json.loads(res.strip()))
            for res in await asyncio.gather(
                *tasks,
            )
        ]

    @dual_method
    def list(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("list", args)

    @list.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("list", args)

    @dual_method
    def start(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("start", args)

    @start.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("start", args)

    @dual_method
    def stop(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("stop", args)

    @stop.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("stop", args)

    @dual_method
    def restart(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("restart", args)

    @restart.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("restart", args)

    @dual_method
    def reload(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("reload", args)

    @reload.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("reload", args)

    @dual_method
    def delete(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("delete", args)

    @delete.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("delete", args)

    @dual_method
    def kill(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("delete", args)

    @kill.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("delete", args)

    @dual_method
    def describe(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("describe", args)

    @describe.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("describe", args)

    @dual_method
    def update(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return self._execude("update", args)

    @update.register()
    async def _(
        self,
        args: List[PM2AppConfig],
    ) -> List[PM2Response]:
        return await self._execude_async("update", args)
