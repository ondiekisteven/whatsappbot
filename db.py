import pymysql
from loadConf import get_database_host, get_database_user, get_database_pass


def getDb():
    db = pymysql.connect(get_database_host(), get_database_user(), get_database_pass(), "heroku_2c9ec56dd042196")
    return db

# def getDb():
#     db = pymysql.connect("localhost", "root", "", "infermedica")
#     return db


def getUserById(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id=%s' % tg_id)
    return cursor.fetchone()


def saveUser(tg_id, first_name, last_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO users(tg_id, first_name, last_name) VALUES ("%s", "%s", "%s")' %
                   (tg_id, first_name, last_name))
    db.commit()


def saveAge(tg_id, age):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET age = %s WHERE tg_id=%s' % (age, tg_id))
    db.commit()
    cursor.close()
    db.close()


def getAge(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT age FROM users WHERE tg_id=%s' % tg_id)
    return cursor.fetchone()[0]


def saveGender(tg_id, gender):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET sex = "%s" WHERE tg_id=%s' % (gender, tg_id))
    db.commit()
    cursor.close()
    db.close()


def getGender(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT sex FROM users WHERE tg_id=%s' % tg_id)
    return cursor.fetchone()[0]


def saveFirstName(tg_id, first_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET first_name = "%s" WHERE tg_id=%s' % (first_name, tg_id))
    db.commit()
    cursor.close()
    db.close()


def saveLastName(tg_id, last_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET last_name = "%s" WHERE tg_id=%s' % (last_name, tg_id))
    db.commit()
    cursor.close()
    db.close()


def saveControlBoard(tg_id, count):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('INSERT INTO control_board (tg_id, count) VALUES(%s, %s)' % (tg_id, count))
    db.commit()


def getCurrentCount(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT * from control_board where tg_id = %s order  by `count` desc limit 1" % tg_id)
    return cursor.fetchone()[2]


def getQuestion(question_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT text FROM registration_questions WHERE question_id=%s' % question_id)
    return cursor.fetchone()[0]


def saveOnGoingUser(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('INSERT INTO on_going_diagnosis (tg_id) VALUES (%s)' % tg_id)
    db.commit()


def getOnGoingUser(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM on_going_diagnosis WHERE tg_id = %s' % tg_id)
    return cursor.fetchone()


def saveSymptom(tg_id, s_id, c_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO user_symptoms (tg_id, symptom_id, choice_id) VALUES({tg_id}, "{s_id}", "{c_id}")')
    db.commit()


def saveCurrentQuestion(tg_id, q_id, q_text):
    try:
        db = getDb()
        cursor = db.cursor()
        cursor.execute('INSERT INTO current_question (tg_id, question_id, question_text) VALUES (%s, "%s", "%s")' %
                       (tg_id, q_id, q_text))
        db.commit()
    except pymysql.err.IntegrityError:
        print({'Error': 'User record exists, skipping...'})


def updateCurrentQuestion(tg_id, q_id, q_text):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('UPDATE current_question SET question_id = "%s", question_text = "%s" WHERE tg_id = %s'
                   % (q_id, q_text, tg_id))
    db.commit()


def getCurrentQuestion(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM current_question WHERE tg_id = {tg_id}')
    return cursor.fetchone()


def deleteCurrentQuestion(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM current_question WHERE  tg_id = {tg_id}')
    db.commit()


def saveInitialSymptom(tg_id, symptom_id, choice_id, initial):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO user_symptoms (tg_id, symptom_id, choice_id, initial) VALUES({tg_id}, '
                   f'"{symptom_id}", "{choice_id}", {initial})')
    saveCurrentQuestion(tg_id, "", "")
    db.commit()


def getSymptoms(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM user_symptoms WHERE tg_id = {tg_id}')
    return cursor.fetchall()


def saveFinishedRegistration(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO finished_registrations(tg_id) VALUE ({tg_id})')
    db.commit()


def getFinishedRegistration(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM finished_registrations WHERE tg_id = {tg_id}')
    return cursor.fetchone()


def saveCurrentSymptom(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO current_symptoms(tg_id) VALUE ({tg_id})')
    db.commit()


def updateCurrentSymptom(tg_id, symptoms):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE current_symptoms SET symptoms = "{symptoms}" WHERE tg_id = {tg_id}')
    db.commit()


def getCurrentSymptoms(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM current_symptoms WHERE tg_id = {tg_id}')
    return cursor.fetchone()


def deleteUser(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM users WHERE tg_id = {tg_id}')
    db.commit()


def deleteUserSymptoms(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM user_symptoms WHERE tg_id = {tg_id}')
    db.commit()


def deleteUserCurrentSymptom(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM current_symptoms WHERE tg_id = {tg_id}')
    db.commit()


def deleteUserOngoingDiagnosis(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM on_going_diagnosis WHERE tg_id = {tg_id}')
    db.commit()


def addAllowedBotChat(chat_id, chat_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO allowed_bot_chats (chat_id, chat_name) VALUES ("{chat_id}", "{chat_name}")')
    db.commit()


def getAllowedBotChat():
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM allowed_bot_chats')
    return cursor.fetchall()


def checkAllowedChatBot(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM allowed_bot_chats WHERE chat_id = "{chat_id}"')
    return cursor.fetchone()


def deleteFromAllowedChat(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM allowed_bot_chats WHERE chat_id="{chat_id}"')
    db.commit()


def addLastCommand(chat_id, command):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO last_command (chat_id, command) VALUES ('{chat_id}', '{command}') ")
    db.commit()


def updateLastCommand(chat_id, new_command):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE last_command SET command = "{new_command}" WHERE chat_id = "{chat_id}"')
    db.commit()


def getLastCommand(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT command FROM last_command WHERE chat_id = "{chat_id}"')
    com = cursor.fetchone()
    return com[0] or 'join'


def add_downloading_user(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO downloading_users (chat_id) VALUE ("{chat_id}")')
    db.commit()


def is_downloading(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f"SELECT chat_id FROM downloading_users WHERE chat_id = '{chat_id}'")
    data = cursor.fetchone()
    if data:
        return True
    else:
        return False


def delete_downloading(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM downloading_users WHERE chat_id = '{chat_id}'")
    db.commit()
