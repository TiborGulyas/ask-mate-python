import connection


@connection.connection_handler
def get_all_questions(cursor, order={'order_by': 'id', 'order_direction': 'asc'}):
    cursor.execute("""
    SELECT * FROM question
    ORDER BY """ + f"""{order['order_by']} {order['order_direction']}""")
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_first_five_questions(cursor):
    cursor.execute("""
    SELECT * FROM question
    ORDER BY submission_time desc 
    LIMIT 5;
    """)
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def insert_new_question(cursor, title, message, submission_time, view_number, vote_number, image, user_id):
    cursor.execute("""
    INSERT INTO question
    (title, message, submission_time, view_number, vote_number, image, user_id)
    VALUES (%(title)s, %(message)s, %(submission_time)s, %(view_number)s, %(vote_number)s, %(image)s, %(user_id)s)
    """,
                   {'title': title, 'message': message, 'submission_time': submission_time, 'view_number': view_number,
                    'vote_number': vote_number, 'image': image, 'user_id': user_id})
    cursor.execute("""
    SELECT id FROM question
    WHERE submission_time=%(submission_time)s;""",
                   {'submission_time': submission_time})
    id = cursor.fetchall()
    return str(id[0]['id'])


@connection.connection_handler
def get_question_by_id(cursor, id):
    cursor.execute("""
    SELECT * FROM question
    WHERE id=%(id)s;
    """,
                   {'id': id})
    question = cursor.fetchall()
    return question[0]


@connection.connection_handler
def update_question(cursor, id, title, message, filename, time):
    cursor.execute("""
    UPDATE question
    SET title = %(title)s, message = %(message)s, image = %(filename)s, submission_time = %(time)s
    WHERE id=%(id)s;
    """,
                   {'id': id, "title": title, "message": message, "filename": filename, 'time': time})


@connection.connection_handler
def delete_question(cursor, id):
    cursor.execute("""
    DELETE FROM question
    WHERE id=%(id)s;
    """,
                   {'id': id})


@connection.connection_handler
def vote_question(cursor, id, vote):
    cursor.execute("""
    UPDATE question
    SET vote_number = vote_number + %(vote)s
    WHERE id=%(id)s;
    """,
                   {'vote': int(vote), 'id': id})


@connection.connection_handler
def view_question(cursor, id):
    cursor.execute("""
    UPDATE question
    SET view_number = view_number + 1
    WHERE id=%(id)s;
    """,
                   {'id': id})


@connection.connection_handler
def get_answer_by_question_id(cursor, question_id):
    cursor.execute("""
    SELECT * FROM answer
    WHERE question_id= %(question_id)s
    ORDER BY submission_time DESC;
    """,
                   {'question_id': question_id})
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def insert_new_answer(cursor, message, submission_time, vote_number, question_id, image, user_id):
    cursor.execute("""
    INSERT INTO answer
    (message, submission_time, vote_number, question_id, image, user_id)
    VALUES (%(message)s, %(submission_time)s, %(vote_number)s, %(question_id)s, %(image)s, %(user_id)s)
    """,
                   {'message': message, 'submission_time': submission_time, 'vote_number': vote_number,
                    'question_id': question_id, 'image': image, 'user_id': user_id})
    cursor.execute("""
    SELECT id FROM answer
    WHERE submission_time = %(submission_time)s;""",
                   {'submission_time': submission_time})
    id = cursor.fetchall()
    return str(id[0]['id'])


@connection.connection_handler
def get_answer_by_id(cursor, id):
    cursor.execute("""
    SELECT * FROM answer
    WHERE id=%(id)s;
    """,
                   {'id': id})
    answer = cursor.fetchall()
    return answer


@connection.connection_handler
def update_answer(cursor, id, message, filename, time):
    cursor.execute("""
    UPDATE answer
    SET message = %(message)s, image = %(filename)s, submission_time = %(time)s
    WHERE id=%(id)s;
    """,
                   {'id': id, 'message': message, 'filename': filename, 'time': time})


@connection.connection_handler
def delete_answer(cursor, id):
    cursor.execute("""
    DELETE FROM answer
    WHERE id=%(id)s;
    """,
                   {'id': id})


@connection.connection_handler
def vote_answer(cursor, id, vote):
    cursor.execute("""
    UPDATE answer
    SET vote_number = vote_number + %(vote)s
    WHERE id=%(id)s;
    """,
                   {'vote': int(vote), 'id': id})
    cursor.execute("""
    SELECT question_id FROM answer
    WHERE id=%(id)s;""",
                   {'id': id})
    question_id = cursor.fetchall()
    return str(question_id[0]['question_id'])


@connection.connection_handler
def insert_image_question(cursor, id, image):
    cursor.execute('''
    UPDATE question 
    SET image = %(image)s
    WHERE id = %(id)s;
    ''',
                   {'id': id, 'image': image})


@connection.connection_handler
def get_tags_by_id(cursor, id):
    cursor.execute("""
    SELECT name, id FROM tag
    INNER JOIN question_tag ON id = tag_id
    WHERE question_id = %(id)s;
    """,
                   {'id': id})
    tags = cursor.fetchall()
    return tags


@connection.connection_handler
def save_tag(cursor, name):
    cursor.execute("""
        SELECT name FROM tag
        WHERE name = %(name)s;
        """,
                   {'name': name})
    answer = cursor.fetchall()
    return answer


@connection.connection_handler
def get_tag_id(cursor, question_id):
    cursor.execute("""
    SELECT tag_id FROM question_tag
    WHERE question_id=%(question_id)s;
    """,
                   {'question_id': question_id})
    tag_id = cursor.fetchall()
    return tag_id


@connection.connection_handler
def get_all_tags(cursor):
    cursor.execute("""
    SELECT name FROM tag
    """)
    tags = cursor.fetchall()
    return tags


@connection.connection_handler
def save_new_tag(cursor, new_tag):
    cursor.execute("""
    INSERT INTO tag (name)
    VALUES (%(new_tag)s);
    """,
                   {'new_tag': new_tag})


@connection.connection_handler
def save_tag_for_question(cursor, tag, question_id):
    cursor.execute("""
        INSERT INTO question_tag (question_id,tag_id)
        VALUES (%(question_id)s, (SELECT id FROM tag WHERE name = %(tag_id)s));
        
    """,
                   {'tag_id': tag, 'question_id': question_id})


@connection.connection_handler
def delete_tag(cursor, question_id, tag_id):
    cursor.execute("""
    DELETE FROM question_tag 
    WHERE tag_id=%(tag_id)s AND question_id=%(question_id)s;
    """,
                   {'tag_id': tag_id, 'question_id': question_id})


@connection.connection_handler
def insert_new_comment(cursor, id_type, id, message, submission_time, edited_count, user_id):
    cursor.execute('''
    INSERT INTO comment
    ( ''' + f'{id_type}' + ''', message, submission_time, edited_count,user_id)
    VALUES (%(id)s, %(message)s, %(submission_time)s, %(edited_count)s, %(user_id)s);
    ''',
                   {'id_type': id_type, 'id': id, 'message': message, 'submission_time': submission_time,
                    'edited_count': edited_count, 'user_id': user_id})


@connection.connection_handler
def get_comment_by_id(cursor, id):
    cursor.execute("""
    SELECT * FROM comment
    WHERE id= %(id)s;
    """,
                   {'id': id})
    comment = cursor.fetchall()
    return comment


@connection.connection_handler
def get_all_comments(cursor):
    cursor.execute("""
    SELECT * FROM comment
    ORDER BY submission_time DESC;
    """)
    comment = cursor.fetchall()
    return comment


@connection.connection_handler
def get_question_by_search(cursor, detail):
    cursor.execute("""
    SELECT * FROM question
    WHERE title LIKE %(detail)s or message LIKE %(detail)s;
    """,
                   {'detail': '%%' + detail + '%%'})
    found_questions = cursor.fetchall()
    return found_questions


@connection.connection_handler
def get_question_ids_by_search_from_answers(cursor, detail):
    cursor.execute("""
    SELECT * FROM answer
    WHERE message LIKE %(detail)s;
    """,
                   {'detail': '%%' + detail + '%%'})
    found_question_ids = cursor.fetchall()
    return found_question_ids


@connection.connection_handler
def update_comment(cursor, comment_to_update):
    cursor.execute("""
    UPDATE comment
    SET message = %(message)s, submission_time = %(submission_time)s
    WHERE id = %(comment_to_update)s;
    """,
                   {'message': comment_to_update['message'], 'submission_time': comment_to_update['submission_time'],
                    'comment_to_update': int(comment_to_update['id'])})


@connection.connection_handler
def get_comment_by_question_id(cursor, id):
    cursor.execute("""
    SELECT * FROM comment
    WHERE question_id= %(id)s
    ORDER BY submission_time DESC;
    """,
                   {'id': id})
    comment = cursor.fetchall()
    return comment


@connection.connection_handler
def delete_comment(cursor, comment_id):
    cursor.execute("""
    DELETE FROM comment 
    WHERE id=%(comment_id)s;
    """,
                   {'comment_id': comment_id})


@connection.connection_handler
def delete_comment_by_question_id(cursor, question_id):
    cursor.execute("""
    DELETE FROM comment 
    WHERE question_id=%(question_id)s;
    """,
                   {'question_id': question_id})


@connection.connection_handler
def delete_comment_by_answer_id(cursor, answer_id):
    cursor.execute("""
    DELETE FROM comment 
    WHERE answer_id=%(answer_id)s;
    """,
                   {'answer_id': answer_id})


@connection.connection_handler
def register_user(cursor, user_name, user_password, submission_time):
    cursor.execute("""
    INSERT INTO users
    (user_name, user_password, submission_time)
    VALUES (%(user_name)s, %(user_password)s, %(submission_time)s);
    """,
                   {'user_name': user_name, 'user_password': user_password,
                    'submission_time': submission_time})


@connection.connection_handler
def accept_answer(cursor, id):
    cursor.execute("""
    UPDATE answer
    SET accepted = 'yes'
    WHERE id=%(id)s;
    """,
                   {'id': id})


@connection.connection_handler
def get_user_password(cursor, user_name):
    cursor.execute("""
    SELECT user_password FROM users
    WHERE user_name=%(user_name)s;
    """, {'user_name': user_name})
    user_password = cursor.fetchall()
    if len(user_password) > 0:
        return user_password[0]['user_password']
    else:
        pass


@connection.connection_handler
def get_user_id_by_user_name(cursor, user_name):
    if user_name != 'not logged in':
        cursor.execute("""
        SELECT id FROM users
        WHERE user_name=%(user_name)s
        """, {'user_name': user_name})
        user_id = cursor.fetchall()
        return user_id[0]['id']
    else:
        pass


@connection.connection_handler
def get_questions_of_user(cursor, user_id):
    cursor.execute("""
        SELECT * FROM question
        WHERE id=%(user_id)s;
        """, {'user_id': user_id})
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers_of_user(cursor, user_id):
    cursor.execute("""
        SELECT * FROM answer
        WHERE id=%(user_id)s;
        """, {'user_id': user_id})
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def get_comments_of_user(cursor, user_id):
    cursor.execute("""
        SELECT * FROM comment
        WHERE id=%(user_id)s;
        """, {'user_id': user_id})
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def get_vote_history(cursor, input_type, user_id):
    cursor.execute("""
        SELECT type_id FROM vote_tracker
        WHERE user_id = %(user_id)s and type = %(type)s
        """, {'user_id': user_id, 'type': input_type})
    vote_history = []
    findings = cursor.fetchall()
    for dictionary in findings:
        vote_history.append(dictionary['type_id'])
    return vote_history


@connection.connection_handler
def update_vote_history(cursor, input_type, type_id, user_id):
    cursor.execute("""
        INSERT INTO vote_tracker
        (type, type_id, user_id)
        VALUES (%(type)s, %(type_id)s, %(user_id)s);
        """, {'type': input_type, 'type_id': type_id, 'user_id': user_id})


@connection.connection_handler
def get_user_id_by_question_id(cursor, question_id):
    cursor.execute("""
    SELECT user_id FROM question
    WHERE id=%(question_id)s
    """, {'question_id': question_id})
    user_id = cursor.fetchall()
    return int(user_id[0]['user_id'])


@connection.connection_handler
def get_all_tags(cursor):
    cursor.execute("""
    SELECT name, COUNT(tag_id) FROM tag
    JOIN question_tag ON tag.id = question_tag.tag_id
    GROUP BY name;
    """)
    tags = cursor.fetchall()
    return tags

@connection.connection_handler
def get_user_by_comment_id(cursor, comment_id):
    cursor.execute("""
        WHERE id=%(comment_id)s
        SELECT user_id FROM comment
        """, {'comment_id': comment_id})
    return user_id['user_id']
    user_id = cursor.fetchall()[0]

        SELECT question_id FROM comment
@connection.connection_handler
def get_question_id_by_comment_id(cursor, comment_id):
    cursor.execute("""
        WHERE id=%(comment_id)s
        """, {'comment_id': comment_id})
    question_id = cursor.fetchall()[0]
    return question_id['question_id']
@connection.connection_handler

def get_answer_id_by_comment_id(cursor, comment_id):
    return answer_id['answer_id']
    answer_id = cursor.fetchall()[0]
        """, {'comment_id': comment_id})
        WHERE id=%(comment_id)s
    cursor.execute("""
        SELECT answer_id FROM comment

@connection.connection_handler
def set_reputation(cursor, user_id):
    cursor.execute("""
    UPDATE users
    SET reputation = (
    (SELECT SUM(vote_number) FROM question JOIN users ON user_id = %(user_id)s WHERE user_id = users.id) +
    (SELECT SUM(vote_number) FROM answer JOIN users ON user_id = %(user_id)s WHERE user_id = users.id) +
    ((SELECT SUM(CASE WHEN accepted='yes' AND user_id = %(user_id)s THEN 15 ELSE 0 END) FROM answer JOIN users ON user_id = users.id )))
    WHERE id = %(user_id)s;
    """, {'user_id': user_id})


@connection.connection_handler
def get_user_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
    SELECT user_id FROM answer
    WHERE id = %(answer_id)s;""",
                   {'answer_id': answer_id})
    user_id = cursor.fetchall()
    return user_id[0]['user_id']


@connection.connection_handler
def get_reputation_of_user(cursor, user_id):
    cursor.execute("""
    SELECT reputation FROM users
    WHERE id = %(user_id)s;""",
                   {'user_id': user_id})
    reputation = cursor.fetchall()
    return reputation[0]['reputation']