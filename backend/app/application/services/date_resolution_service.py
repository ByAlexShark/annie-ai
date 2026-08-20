from datetime import date, timedelta
import unicodedata


class DateResolutionService:
    WEEKDAYS = {
        "lunes": 0,
        "martes": 1,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sabado": 5,
        "domingo": 6,
    }

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize(
            "NFD",
            value.lower().strip(),
        )

        return "".join(
            char
            for char in normalized
            if unicodedata.category(char) != "Mn"
        )

    def resolve(
        self,
        requested_date: str | None,
        today: date | None = None,
    ) -> date | None:
        if requested_date is None:
            return None

        current_date = today or date.today()

        value = self._normalize(requested_date)

        if value == "hoy":
            return current_date

        if value == "manana":
            return current_date + timedelta(days=1)

        for weekday_name, weekday_number in self.WEEKDAYS.items():
            if weekday_name in value:
                days_ahead = (
                    weekday_number - current_date.weekday()
                ) % 7

                if days_ahead == 0:
                    days_ahead = 7

                return current_date + timedelta(
                    days=days_ahead
                )

        try:
            return date.fromisoformat(value)
        except ValueError:
            return None