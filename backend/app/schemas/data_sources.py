from pydantic import BaseModel
from typing import List, Optional


class DataSourceItem(BaseModel):
    id: int
    source_name: str
    source_url: str = ""
    category: str = ""
    years_covered: str = ""
    states_covered: str = ""
    districts_covered: int = 0
    sectors_covered: int = 0
    trades_covered: int = 0
    record_count: int = 0
    is_synthetic: bool = True
    last_updated: str = ""
    notes: str = ""


class DataSourcesResponse(BaseModel):
    data_honesty_statement: str
    sources: List[DataSourceItem]
    total_records_in_db: int
    synthetic_sources_count: int
    real_sources_count: int
    pilot_geography: str
