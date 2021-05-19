import pymysql
from pymysql import IntegrityError
from loadConf import get_database_host, get_database_user, get_database_pass, get_database_name
import logging
logging.basicConfig(level=logging.INFO)


def getDb():
    db = pymysql.connect(get_database_host(), get_database_user(), get_database_pass(), get_database_name())
    return db

# def getDb():
#     db = pymysql.connect("localhost", "root", "", "infermedica")
#     return db


def getUserById(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id=%s' % tg_id)
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


def saveUser(tg_id, first_name, last_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO users(tg_id, first_name, last_name) VALUES ("%s", "%s", "%s")' %
                   (tg_id, first_name, last_name))
    db.commit()
    cursor.close()
    db.close()


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
    data = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return data


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
    data = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return data


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
    cursor.close()
    db.close()


def getCurrentCount(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT * from control_board where tg_id = %s order  by `count` desc limit 1" % tg_id)
    data = cursor.fetchone()[2]
    cursor.close()
    db.close()
    return data


def getQuestion(question_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT text FROM registration_questions WHERE question_id=%s' % question_id)
    data = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return data


def saveOnGoingUser(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('INSERT INTO on_going_diagnosis (tg_id) VALUES (%s)' % tg_id)
    db.commit()
    cursor.close()
    db.close()


def getOnGoingUser(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM on_going_diagnosis WHERE tg_id = %s' % tg_id)
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


def saveSymptom(tg_id, s_id, c_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO user_symptoms (tg_id, symptom_id, choice_id) VALUES({tg_id}, "{s_id}", "{c_id}")')
    db.commit()
    cursor.close()
    db.close()


def saveCurrentQuestion(tg_id, q_id, q_text):
    db = getDb()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO current_question (tg_id, question_id, question_text) VALUES (%s, "%s", "%s")' %
                       (tg_id, q_id, q_text))
        db.commit()
    except pymysql.err.IntegrityError:
        updateCurrentQuestion(tg_id, q_id, q_text)
    finally:
        cursor.close()
        db.close()


def updateCurrentQuestion(tg_id, q_id, q_text):
    db = getDb()
    cursor = db.cursor()
    cursor.execute('UPDATE current_question SET question_id = "%s", question_text = "%s" WHERE tg_id = %s'
                   % (q_id, q_text, tg_id))
    db.commit()
    cursor.close()
    db.close()


def getCurrentQuestion(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM current_question WHERE tg_id = {tg_id}')
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


def deleteCurrentQuestion(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM current_question WHERE  tg_id = {tg_id}')
    db.commit()
    cursor.close()
    db.close()


def saveInitialSymptom(tg_id, symptom_id, choice_id, initial):
    db = getDb()
    cursor = db.cursor()
    print("saving symptom in database")
    cursor.execute(f'INSERT INTO user_symptoms (tg_id, symptom_id, choice_id, initial) VALUES({tg_id}, '
                   f'"{symptom_id}", "{choice_id}", {initial})')
    saveCurrentQuestion(tg_id, "", "")
    db.commit()
    cursor.close()
    db.close()


def getSymptoms(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM user_symptoms WHERE tg_id = {tg_id}')
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data


def saveFinishedRegistration(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO finished_registrations(tg_id) VALUE ({tg_id})')
    db.commit()
    cursor.close()
    db.close()


def getFinishedRegistration(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM finished_registrations WHERE tg_id = {tg_id}')
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


def saveCurrentSymptom(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO current_symptoms(tg_id) VALUE ({tg_id})')
    db.commit()
    cursor.close()
    db.close()


def updateCurrentSymptom(tg_id, symptoms):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE current_symptoms SET symptoms = "{symptoms}" WHERE tg_id = {tg_id}')
    db.commit()
    cursor.close()
    db.close()


def getCurrentSymptoms(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM current_symptoms WHERE tg_id = {tg_id}')
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


def deleteUser(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM users WHERE tg_id = {tg_id}')
    db.commit()
    cursor.close()
    db.close()


def deleteUserSymptoms(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM user_symptoms WHERE tg_id = {tg_id}')
    db.commit()
    cursor.close()
    db.close()


def deleteUserCurrentSymptom(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM current_symptoms WHERE tg_id = {tg_id}')
    db.commit()
    cursor.close()
    db.close()


def deleteUserOngoingDiagnosis(tg_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM on_going_diagnosis WHERE tg_id = {tg_id}')
    db.commit()
    cursor.close()
    db.close()


def addAllowedBotChat(chat_id, chat_name):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO allowed_bot_chats (chat_id, chat_name) VALUES ("{chat_id}", "{chat_name}")')
    db.commit()
    cursor.close()
    db.close()


def getAllowedBotChat():
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM allowed_bot_chats')
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data


def checkAllowedChatBot(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM allowed_bot_chats WHERE chat_id = "{chat_id}"')
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


def deleteFromAllowedChat(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM allowed_bot_chats WHERE chat_id="{chat_id}"')
    db.commit()
    cursor.close()
    db.close()


def addLastCommand(chat_id, command):
    db = getDb()
    cursor = db.cursor()
    try:
        cursor.execute(f"INSERT INTO last_command (chat_id, command) VALUES ('{chat_id}', '{command}') ")
    except IntegrityError:
        return
    db.commit()
    cursor.close()
    db.close()


def updateLastCommand(chat_id, new_command):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE last_command SET command = "{new_command}" WHERE chat_id = "{chat_id}"')
    db.commit()
    cursor.close()
    db.close()


def getLastCommand(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT command FROM last_command WHERE chat_id = "{chat_id}"')
    com = cursor.fetchone()
    data = com[0] or 'join'
    cursor.close()
    db.close()
    return data


def add_downloading_user(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO downloading_users (chat_id) VALUE ("{chat_id}")')
    db.commit()
    cursor.close()
    db.close()


def is_downloading(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f"SELECT chat_id FROM downloading_users WHERE chat_id = '{chat_id}'")
    data = cursor.fetchone()
    cursor.close()
    db.close()
    if data:
        return True
    else:
        return False


def delete_downloading(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM downloading_users WHERE chat_id = '{chat_id}'")
    db.commit()
    cursor.close()
    db.close()


# --------------------------- TRANSLATION HANDLER ------------------------
def add_translating(chat_id, text=None, to_lang=None):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'INSERT INTO translating_text(chat_id) VALUES ({chat_id})')
    db.commit()
    cursor.close()
    db.close()


def update_translating(chat_id, text=None):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'UPDATE translating_text SET text = "{text}" WHERE chat_id = {chat_id}')
    db.commit()
    cursor.close()
    db.close()


def get_translating_text(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM translating_text WHERE chat_id = {chat_id}')
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data


# ------------------------------------ HOW-TO SEARCH HANDLER -------------------------------

def add_how_to_search(chat_id, term, size):
    db = getDb()
    cursor = db.cursor()
    try:
        cursor.execute(f'INSERT INTO howto_search_term (chat_id, search_term, size) VALUES ("{chat_id}", "{term}", {size})')
    except IntegrityError:
        cursor.execute(f'UPDATE howto_search_term SET search_term = "{term}", size = {size} WHERE chat_id = "{chat_id}"')
    finally:
        db.commit()
        cursor.close()
        db.close()        


def save_link(chat_id, text):
    logging.info('[*]saving user link...')
    logging.info(f'chat_id: -> {chat_id}')
    db = getDb()
    cursor = db.cursor()
    try:
        sql = 'INSERT INTO link_text (user_id, text) VALUES (%s, %s)'
        cursor.execute(sql, (chat_id, text))
    except Exception as e:
        logging.error(f'Error :{e}')
        sql = 'UPDATE link_text SET text = %s WHERE user_id = %s'
        cursor.execute(sql, (text, chat_id))
    finally:
        logging.info('[OK] done')
        db.commit()
        cursor.close()
        db.close()


def get_link_text(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM link_text WHERE user_id = "{chat_id}"')
    data = cursor.fetchone()[1]
    cursor.close()
    db.close()
    return data


def get_how_to_search(chat_id):
    db = getDb()
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM howto_search_term WHERE chat_id = "{chat_id}"')
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return data
