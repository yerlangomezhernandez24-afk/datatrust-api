from pydantic import BaseModel, Field


class IssueOut(BaseModel):
    row_number: int = Field(description="Fila de datos, incluyendo el encabezado en la posición 1")
    field_name: str
    code: str
    message: str


class RunOut(BaseModel):
    id: str
    filename: str = Field(description="Nombre técnico neutral derivado del ID; no conserva el nombre original")
    profile: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    issue_count: int
    created_at: str


class RunDetail(RunOut):
    issues: list[IssueOut]


class ProfileOut(BaseModel):
    id: str
    version: int
    description: str
