import sqlite3
import os

class Database():

    def __init__(self, name):
        self.name = name + '.db'

    def view_table(self, server_id, type):
        """
        Get data stored in a specific table in the speicified database
        """

        # Establish a connection to the database
        connection = sqlite3.connect(f'{os.getcwd()}\\{self.name}')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(f"CREATE TABLE IF NOT EXISTS server_{server_id} (type, user_id, val, UNIQUE(type,user_id))")

        # Get the chosen table
        return_dict = {}
        table = cursor.execute(f"SELECT * FROM server_{server_id} WHERE type = (?)", (type,)).fetchall()
        i = 0
        for row in table:
            ins = table[i]
            row_dict = {key: ins[key] for key in ins.keys()}
            return_dict[row_dict['user_id']] = row_dict
            i+=1
        return return_dict

    def save_in_table(
        self,
        type=None,
        server_id=None,
        user_id=None,
        val=None,
        ):
        """
        Save/Update the right row in the server's table
        """
        # Establish a connection to the database
        connection = sqlite3.connect(f'{os.getcwd()}\\{self.name}')
        cursor = connection.cursor()

        cursor.execute(f"CREATE TABLE IF NOT EXISTS server_{server_id} (type, user_id, val, UNIQUE(type,user_id))")

        if type != 'shop':
            cursor.execute(f"INSERT OR REPLACE INTO server_{server_id} VALUES (?, ?, ?)", (type, str(user_id), str(val)))
        else:
            cursor.execute(f"INSERT INTO server_{server_id} VALUES (?, ?, ?)", (type, str(user_id), str(val)))

        connection.commit()
        connection.close()

    def delete_from_table(
        self,
        type=None,
        server_id=None,
        user_id=None
        ):
        
        # Establish a connection to the database
        connection = sqlite3.connect(f'{os.getcwd()}\\{self.name}')
        cursor = connection.cursor()

        cursor.execute(f"CREATE TABLE IF NOT EXISTS server_{server_id} (type, user_id, val, UNIQUE(type,user_id))")

        if type == 'annoy':
            cursor.execute(f"DELETE FROM server_{server_id} WHERE user_id = ?", (user_id,))

        connection.commit()
        connection.close()