# In app/schemas/sql_schema.py

from typing import Any, List, Optional, Literal
from pydantic import BaseModel

class FilterField(BaseModel):
    field: str
    op: Literal["=", ">", "<", '>=', '<=',"between", "in"]
    value: Any

# UPDATED TO MATCH TYPESCRIPT
class AggregateField(BaseModel):
    field: str
    fn: Literal["count", "avg", "sum", "min", "max"] # Changed 'type' to 'fn'

# UPDATED TO MATCH TYPESCRIPT
class OrderByField(BaseModel):
    field: str
    direction: Literal["asc", "desc"] # Changed 'order' to 'direction'

# UPDATED TO MATCH TYPESCRIPT
class QueryInput(BaseModel):
    operation: Literal["find", "aggregate", "count", "groupBy"]
    filters: Optional[List[FilterField]] = None
    aggregates: Optional[List[AggregateField]] = None # Changed 'aggregations' to 'aggregates'
    limit: Optional[int] = None
    orderBy: Optional[List[OrderByField]] = None # Changed 'sort' to 'orderBy'
    groupBy: Optional[List[str]] = None
    select: Optional[List[str]] = None