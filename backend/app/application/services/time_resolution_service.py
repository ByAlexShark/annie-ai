import re
from datetime import time


class TimeResolutionService:
    def resolve(
        self,
        value: str,
    ) -> time | None:
        normalized = value.lower().strip()

        match = re.search(
            r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
            normalized,
        )

        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))

            return time(
                hour=hour,
                minute=minute,
            )

        match = re.fullmatch(
            r"\s*([01]?\d|2[0-3])\s*",
            normalized,
        )

        if match:
            return time(
                hour=int(match.group(1)),
                minute=0,
            )

        return None