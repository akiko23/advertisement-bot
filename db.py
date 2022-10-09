import sqlite3

import psycopg2


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.Connection(db_file)
        self.cursor = self.connection.cursor()

    def request_to_database(self, request, *args):
        with self.connection:
            return self.cursor.execute(request, *args)

    def add_user(self, user_id):
        self.request_to_database("INSERT INTO users (`user_id`) VALUES (?)", (user_id,))

    def user_exists(self, user_id):
        res = self.request_to_database("SELECT `user_id` FROM users WHERE user_id=?", (user_id,)).fetchall()
        return bool(len(res))

    def set_advertisement_user(self, user_id, user_name):
        self.request_to_database("INSERT INTO advertisement (owner_id, user_name) VALUES (?, ?)", (user_id, user_name,))

    def set_something(self, unique_id, param_to_set, value_to_set):
        self.request_to_database(f'UPDATE advertisement SET {param_to_set}=? WHERE id=?',
                                 (value_to_set, unique_id,))

    def get_last_id(self, user_id) -> int | None:
        return self.request_to_database("SELECT id FROM advertisement WHERE owner_id=?", (user_id,)).fetchall()[-1][
            0]

    def get_user_advertisements_data(self, user_id):
        return self.request_to_database("SELECT * FROM advertisement WHERE owner_id=?", (user_id,)).fetchall()

    def get_user_advertisement_by_id(self, unique_id):
        return self.request_to_database("SELECT * FROM advertisement WHERE id=?", (unique_id,)).fetchone()

    def get_not_user_advertisements_data(self, user_id):
        return self.request_to_database("SELECT * FROM advertisement WHERE owner_id!=?", (user_id,)).fetchall()

    def delete_advertisement(self, user_id, unique_id):
        self.request_to_database("DELETE FROM advertisement WHERE id=? and owner_id=?", (unique_id, user_id,))

    def change_advertisement(self, unique_id, param_to_change, value):
        self.request_to_database(f"UPDATE advertisement SET {param_to_change}=? WHERE id=?", (value, unique_id,))

# db = Database('database.db')
# db.change_advertisement('')
