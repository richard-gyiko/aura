from __future__ import annotations

from enum import Enum
from typing import Any, List

from pydantic import BaseModel, Field


class FilterOperator(str, Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"


class FilterCondition(BaseModel):
    field: str = Field(description="The field/column name to filter on")
    operator: FilterOperator = Field(description="The comparison operator to use")
    value: Any = Field(description="The value to compare against")


def build_where_clause(conditions: List[FilterCondition]) -> str:
    """Build a SQL WHERE clause from a list of filter conditions."""
    clauses = []
    for condition in conditions:
        if condition.operator in (FilterOperator.IN, FilterOperator.NOT_IN):
            if not isinstance(condition.value, (list, tuple)):
                raise ValueError(f"Value for {condition.operator} must be a list")
            value_str = f"({', '.join(repr(v) for v in condition.value)})"
        else:
            value_str = repr(condition.value)

        clauses.append(f"{condition.field} {condition.operator.value} {value_str}")

    return " AND ".join(clauses)
