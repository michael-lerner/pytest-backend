import asyncio
import time

__all__ = ["DB"]


class DB:
    _fake_db = {}

    def remove_value(self, id_: str):
        self._fake_db.pop(id_)

    def add_value(self, id_: str, value: str):
        self._fake_db[id_] = value

    def get_value(self, id_: str):
        return self._fake_db.get(id_)

    def get_all_values(self):
        return [{"value": value, "id": id_} for id_, value in self._fake_db.items()]

    def some_long_running_task(self, sleep_time: int):
        time.sleep(sleep_time)
        return True


fake_db = DB()
