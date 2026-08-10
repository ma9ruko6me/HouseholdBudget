from pydantic import BaseModel, ConfigDict, Field


class MajorCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class ExpenseCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    major_category_id: int
    name: str
    sort_order: int


class ExpenseCategoryCreate(BaseModel):
    major_category_id: int
    name: str = Field(min_length=1, max_length=50)


class IncomeCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class IncomeCategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
