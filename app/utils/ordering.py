from rest_framework.filters import OrderingFilter


class CustomOrderingFilter(OrderingFilter):
    """
    Extended OrderingFilter that supports alias ordering via `ordering_field_map`.
    Accepts both real and alias fields.
    Example:
    ordering_field_map = {
        "name": "first_name",
        "email": "email",
    }
    Then you can order by name or email.
    This is useful when you want to order by a field that is not the actual field name.
    Example:
    ordering = ["-name", "email"]
    This will order by name in descending order and email in ascending order.
    But if you want to order by first_name in descending order and email in ascending order, you can do:
    ordering = ["-first_name", "email"]
    This will order by first_name in descending order and email in ascending order.
    This is useful when you want to order by a field that is not the actual field name.
    Example:
    ordering = ["-name", "email"]
    This will order by name in descending order and email in ascending order.
    But if you want to order by first_name in descending order and email in ascending order, you can do:
    ordering = ["-first_name", "email"]
    This will order by first_name in descending order and email in ascending order.
    """

    def remove_invalid_fields(self, queryset, fields, view, request):
        valid_fields = [
            item[0]
            for item in self.get_valid_fields(queryset, view, {"request": request})
        ]
        alias_map = getattr(view, "ordering_field_map", {}) or {}
        cleaned_fields = []

        for term in fields:
            is_desc = term.startswith("-")
            raw_field = term[1:] if is_desc else term
            # Check if it's an alias, otherwise use as-is
            actual_field = alias_map.get(raw_field, raw_field)
            # Only include if the resolved field is valid
            if actual_field in valid_fields:
                cleaned_fields.append(f"-{actual_field}" if is_desc else actual_field)
        return cleaned_fields
