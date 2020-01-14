import connection


@connection.connection_handler
def get_all_questions(cursor, order={'order_by': 'id', 'order_direction': 'asc'}):
    cursor.execute(f"""
    SELECT * FROM question
    ORDER BY {order['order_by']} {order['order_direction'].upper()};
    """)
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def insert_new_question(cursor, title, message, submission_time, view_number, vote_number, image):
    cursor.execute(f"""
    INSERT INTO question
    (title, message, submission_time, view_number, vote_number, image)
    VALUES ('{title}', '{message}', '{submission_time}', '{view_number}', '{vote_number}', '{image}')
    """)
    cursor.execute(f"""
    SELECT id FROM question
    WHERE submission_time='{submission_time}';""")
    id = cursor.fetchall()
    return str(id[0]['id'])


@connection.connection_handler
def get_question_by_id(cursor, id):
    cursor.execute(f"""
    SELECT * FROM question
    WHERE id={id};
    """)
    question = cursor.fetchall()
    return question[0]


@connection.connection_handler
def update_question(cursor, id, title, message, filename, time):
    cursor.execute(f"""
    UPDATE question
    SET title='{title}', message='{message}', image='{filename}', submission_time='{time}'
    WHERE id={id};
    """)


@connection.connection_handler
def delete_question(cursor, id):
    cursor.execute(f"""
    DELETE FROM question
    WHERE id={id};
    """)


@connection.connection_handler
def vote_question(cursor, id, vote):
    cursor.execute(f"""
    UPDATE question
    SET vote_number = vote_number + {vote}
    WHERE id={id};
    """)


@connection.connection_handler
def get_answer_by_question_id(cursor, question_id):
    cursor.execute(f"""
    SELECT * FROM answer
    WHERE question_id={question_id};
    """)
    answers = cursor.fetchall()
    print(answers)
    return answers


@connection.connection_handler
def insert_new_answer(cursor, message, submission_time, vote_number, image, question_id):
    cursor.execute(f"""
    INSERT INTO answer
    (message, submission_time, vote_number, image, question_id)
    VALUES ('{message}', '{submission_time}', '{vote_number}', '{image}', '{question_id}')
    """)


@connection.connection_handler
def get_answer_by_id(cursor, id):
    cursor.execute(f"""
    SELECT * FROM answer
    WHERE id={id};
    """)
    answer = cursor.fetchall()
    return answer


@connection.connection_handler
def delete_answer(cursor, id):
    cursor.execute(f"""
    SELECT question_id FROM answer
    WHERE id={id};""")
    question_id = cursor.fetchall()
    cursor.execute(f"""
    DELETE FROM answer
    WHERE id={id};
    """)
    return str(question_id[0]['question_id'])


@connection.connection_handler
def vote_answer(cursor, id, vote):
    cursor.execute(f"""
    UPDATE answer
    SET vote_number = vote_number + {vote}
    WHERE id={id};
    """)
    cursor.execute(f"""
    SELECT question_id FROM answer
    WHERE id={id};""")
    question_id = cursor.fetchall()
    return str(question_id[0]['question_id'])


@connection.connection_handler
def insert_image(cursor, id, table, image):
    cursor.execute(f"""
    UPDATE {table}
    SET image = '{image}'
    WHERE id={id};
    """)