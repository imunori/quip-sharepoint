"""
OData query parser for SharePoint-compatible $select, $filter, $orderby, $top, $skip.
"""
import operator
import re
from typing import Any


def apply_select(items: list[dict], select: str | None) -> list[dict]:
    """Apply $select to filter response fields."""
    if not select:
        return items
    fields = [f.strip() for f in select.split(",")]
    return [{k: v for k, v in item.items() if k in fields or k == "__metadata"} for item in items]


def apply_filter(items: list[dict], filter_expr: str | None) -> list[dict]:
    """Apply $filter with basic eq, ne, gt, lt, ge, le, contains, startswith support."""
    if not filter_expr:
        return items

    # Parse simple expressions: Field op 'value' or Field op number
    # Support: eq, ne, gt, lt, ge, le
    simple_pattern = re.compile(
        r"(\w+)\s+(eq|ne|gt|lt|ge|le)\s+'?([^']*?)'?\s*$"
    )
    # Support: contains(Field,'value'), startswith(Field,'value'), substringof('value',Field)
    func_pattern = re.compile(
        r"(contains|startswith|substringof)\((?:'([^']*?)',\s*(\w+)|(\w+),\s*'([^']*?)')\)"
    )

    def matches(item: dict) -> bool:
        # Try simple comparison
        m = simple_pattern.match(filter_expr)
        if m:
            field, op, value = m.group(1), m.group(2), m.group(3)
            item_val = str(item.get(field, ""))
            ops = {
                "eq": operator.eq, "ne": operator.ne,
                "gt": operator.gt, "lt": operator.lt,
                "ge": operator.ge, "le": operator.le,
            }
            return ops.get(op, operator.eq)(item_val, value)

        # Try function call
        m = func_pattern.match(filter_expr)
        if m:
            func = m.group(1)
            if func == "substringof":
                # substringof('value', Field)
                value, field = m.group(2), m.group(3)
            elif m.group(4):
                # contains(Field, 'value') or startswith(Field, 'value')
                field, value = m.group(4), m.group(5)
            else:
                value, field = m.group(2), m.group(3)

            item_val = str(item.get(field, "")).lower()
            value_lower = (value or "").lower()

            if func in ("contains", "substringof"):
                return value_lower in item_val
            elif func == "startswith":
                return item_val.startswith(value_lower)

        return True

    return [item for item in items if matches(item)]


def apply_orderby(items: list[dict], orderby: str | None) -> list[dict]:
    """Apply $orderby. Format: 'Field asc' or 'Field desc'."""
    if not orderby:
        return items
    parts = orderby.strip().split()
    field = parts[0]
    desc = len(parts) > 1 and parts[1].lower() == "desc"
    return sorted(items, key=lambda x: str(x.get(field, "")), reverse=desc)


def apply_top_skip(items: list[dict], top: int | None, skip: int | None) -> list[dict]:
    """Apply $top and $skip for pagination."""
    start = skip or 0
    end = start + top if top else None
    return items[start:end]


def apply_odata(
    items: list[dict],
    select: str | None = None,
    filter_expr: str | None = None,
    orderby: str | None = None,
    top: int | None = None,
    skip: int | None = None,
) -> list[dict]:
    """Apply all OData query options in sequence."""
    items = apply_filter(items, filter_expr)
    items = apply_orderby(items, orderby)
    items = apply_top_skip(items, top, skip)
    items = apply_select(items, select)
    return items
