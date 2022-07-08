import sqlite3
from dashes_class import *


class BotDB:

    def __init__(self, db_file):
        """Инициаця соединения с БД"""
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT id "
                                     "FROM players "
                                     "WHERE user_id = ?",
                                     (user_id,))
        return bool(len(result.fetchall()))

    def add_user(self, user_id):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO players (user_id) "
                            "VALUES (?)",
                            (user_id,))
        return self.conn.commit()

    def check_active_session(self, user_id):
        result = self.cursor.execute("SELECT active_session "
                                     "FROM players "
                                     "WHERE user_id = ?",
                                     (user_id,))
        if result is None:
            return 0
        return bool(result.fetchall()[0][0])

    def flag_active_session(self, user_id):
        """Смена флага активной сессии"""
        flag = list(self.cursor.execute("SELECT active_session "
                                        "FROM players "
                                        "WHERE user_id = ?",
                                        (user_id,)))

        if flag[0][0]:
            self.cursor.execute("UPDATE players "
                                "SET active_session = 0 "
                                "WHERE user_id = ?",
                                (user_id,))
        else:
            self.cursor.execute("UPDATE players "
                                "SET active_session = 1 "
                                "WHERE user_id = ?",
                                (user_id,))
        self.conn.commit()

    def get_turn(self, user_id):
        result = self.cursor.execute("SELECT your_turn "
                                     "FROM players "
                                     "WHERE user_id = ?",
                                     (user_id,))
        if result is None:
            return 0
        return bool(result.fetchall()[0][0])

    def reset_turn(self, user_id):
        self.cursor.execute("UPDATE players "
                            "SET your_turn = 0 "
                            "WHERE user_id = ?;",
                            (user_id,))


    def update_turn(self, user_id):
        turn = list(self.cursor.execute("SELECT your_turn "
                                        "FROM players "
                                        "WHERE user_id = ?",
                                        (user_id,)))

        if turn[0][0]:
            self.cursor.execute("UPDATE players "
                                "SET your_turn = 0 "
                                "WHERE user_id = ?;",
                                (user_id,))
            self.cursor.execute("UPDATE players "
                                "SET your_turn = 1 "
                                "WHERE user_id = (SELECT opponent FROM players WHERE user_id = ?);",
                                (user_id,))
        else:
            self.cursor.execute("UPDATE players "
                                "SET your_turn = 1 "
                                "WHERE user_id = ?;",
                                (user_id,))
            self.cursor.execute("UPDATE players "
                                "SET your_turn = 0 "
                                "WHERE user_id = (SELECT opponent FROM players WHERE user_id = ?);",
                                (user_id,))
        self.conn.commit()



    # def add_session(self, user_id, opponent, user_dice, opponent_dice):
    #     """Добавляем запись в игровую сессию"""
    #     self.cursor.execute("INSERT INTO 'active_session' ('user_id', 'opponent', 'user_dice', 'opponent_dice') "
    #                         "VALUES (?, ?, ?, ?)",
    #                         (user_id, opponent, user_dice, opponent_dice))
    #     self.conn.commit()

    def get_user_opponent(self, user_id):
        """Получить id соперника из БД"""
        result = self.cursor.execute("SELECT opponent "
                                     "FROM players "
                                     "WHERE user_id = ?;",
                                     (user_id,))
        result, = result.fetchall()[0]
        return result

    def update_opponent(self, user_id, opponent_id):
        self.cursor.execute("UPDATE players "
                            "SET opponent = ?"
                            "WHERE user_id = ?",
                            (opponent_id, user_id))
        self.conn.commit()

    def get_user_dice(self, user_id):
        """Получить кубили игрока"""
        result = self.cursor.execute("SELECT user_dice "
                                     "FROM players "
                                     "WHERE user_id = ?;",
                                     [user_id])
        result, = result.fetchall()[0]
        return result
        # return result.fetchall()[0]

    def update_dice(self, user_id, new_user_dice):
        self.cursor.execute("UPDATE players "
                            "SET user_dice = ?"
                            "WHERE user_id = ?",
                            (str(new_user_dice), user_id))
        self.conn.commit()

    # def del_session(self, user_id):
    #     self.cursor.execute("DELETE FROM active_session "
    #                         "WHERE user_id = ?",
    #                         (user_id,))
    #     self.conn.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.conn.close()


if __name__ == '__main__':
    BotDB = BotDB('players_db.db')
    # BotDB.add_user(108)
    # BotDB.flag_active_session(123213)
    # sql = "SELECT `active_session` FROM `players` WHERE `user_id` = 123213"
    # flag = list(BotDB.cursor.execute(sql))
    user_id = '777'
    print(user_id.isalnum())
    # BotDB.update_turn(user_id)
    # print(BotDB.check_turn(user_id))
    # print(BotDB.get_user_dice(user_id))
    # user_dice = HandDice(hand_dice=BotDB.get_user_dice(user_id))
    # opponent_dice = HandDice(hand_dice=BotDB.get_user_dice(BotDB.get_user_opponent(user_id)))
    #
    # BotDB.update_dice(user_id, user_dice.get_hand_dice())
    # BotDB.update_dice(BotDB.get_user_opponent(user_id), opponent_dice.get_hand_dice())

    # def get_records(self, user_id, within="all"):
    #     """Получаем историю о доходах/расходах"""
    #
    #     if within == "day":
    #         result = self.cursor.execute(
    #             "SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of day')"
    #             "AND datetime('now', 'localtime') ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #     elif within == "week":
    #         result = self.cursor.execute(
    #             "SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', '-6 days')"
    #             "AND datetime('now', 'localtime') ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #     elif within == "month":
    #         result = self.cursor.execute(
    #             "SELECT * FROM `records` WHERE `users_id` = ? AND `date` BETWEEN datetime('now', 'start of month')"
    #             "AND datetime('now', 'localtime') ORDER BY `date`",
    #             (self.get_user_id(user_id),))
    #     else:
    #         result = self.cursor.execute("SELECT * FROM `records` WHERE `users_id` = ? ORDER BY `date`",
    #                                      (self.get_user_id(user_id),))
    #
    #     return result.fetchall()

