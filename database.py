import time

__all__ = ["fake_db"]


class DB:
    _fake_db = {}
    _fake_count = 0

    def fake_initialize_db(self):
        """
        Initialize the fake database but errors the first 5 times
        This is somewhat like when docker-compose starting a DB
        """
        if self._fake_count != 5:
            self._fake_count += 1
            raise RuntimeError("Fake DB is not started")
        return True

    def remove_value(self, id_: str):
        self._fake_db.pop(id_)

    def add_value(self, id_: str, value: str):
        self._fake_db[id_] = value

    def get_value(self, id_: str):
        return self._fake_db.get(id_)

    def get_all_values(self):
        return [{"value": value, "id": id_} for id_, value in self._fake_db.items()]

    @staticmethod
    def some_long_running_task(sleep_time: int):
        time.sleep(sleep_time)
        return True


fake_db = DB()
