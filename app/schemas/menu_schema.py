from pydantic import BaseModel, Field


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=2)
    category: str
    description: str = ""
    price: float = Field(gt=0)
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    is_available: bool | None = None
