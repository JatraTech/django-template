from decimal import Decimal
from typing import Any
from django.db.models import DecimalField


class MoneyField(DecimalField):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        kwargs["decimal_places"] = kwargs.pop("decimal_places", 2)
        kwargs["max_digits"] = kwargs.pop("max_digits", 10)
        kwargs["default"] = kwargs.pop("default", Decimal(0))
        super().__init__(*args, **kwargs)
