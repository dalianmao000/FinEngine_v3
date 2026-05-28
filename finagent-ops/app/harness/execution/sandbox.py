import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    success: bool
    output: str = ""
    error: Optional[str] = None
    timed_out: bool = False
    duration_ms: int = 0

class Sandbox:
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout

    async def execute(self, code: str, timeout_seconds: Optional[int] = None) -> ExecutionResult:
        timeout = timeout_seconds or self.default_timeout
        start_time = asyncio.get_event_loop().time()

        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                return ExecutionResult(
                    success=proc.returncode == 0,
                    output=stdout.decode() if stdout else "",
                    error=stderr.decode() if stderr else None,
                    timed_out=False,
                    duration_ms=duration_ms,
                )
            except asyncio.TimeoutError:
                proc.kill()
                duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                return ExecutionResult(
                    success=False,
                    error="Execution timed out",
                    timed_out=True,
                    duration_ms=duration_ms,
                )
        except Exception as e:
            duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                error=str(e),
                timed_out=False,
                duration_ms=duration_ms,
            )