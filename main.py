import fastapi
import pydantic

import database

db = database.fake_db
app = fastapi.FastAPI()


class ValueIn(pydantic.BaseModel):
    id: str
    value: str


class AllValues(pydantic.BaseModel):
    values: list[ValueIn]


@app.get("/{value_id}", response_model=str)
def get_value(value_id: str) -> str:
    if (value := db.get_value(value_id)) is None:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Value not found",
        )
    return value


@app.post("/", response_model=ValueIn)
def add_value(value_in: ValueIn):
    if db.get_value(value_in.id) is not None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Value already exists",
        )
    db.add_value(id_=value_in.id, value=value_in.value)
    return value_in


@app.delete("/{value_id}", response_model=str)
def delete_value(value_id: str):
    if db.get_value(value_id) is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Value not found {value_id}",
        )
    db.remove_value(value_id)
    return value_id


@app.get("/", response_model=AllValues)
def get_all_values():
    values = db.get_all_values()
    return AllValues(values=values)


@app.get("/long_running_task/", response_model=str)
def long_running_task(num_secs: int):
    db.some_long_running_task(num_secs)
    return "Done"
