from datetime import datetime
import bcrypt
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
from dotenv import load_dotenv

import json
import time
import uuid
import sqlite3
import os
import json
import psycopg2

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

initial_yyyymmdd =  '19900101'

class QuestionData(BaseModel):
    syntax_id: str
    syntax: str
    japanese_sentence: str

class AnswerData(BaseModel):
    result: int
    correct_answer: str
    explanation: str

class sessionData(BaseModel):
    session_id: str
    user_id: int
    current_start_id: int

class startData(BaseModel):
    session_id: str
    start_id: int
    start_date: str
    number_questions: int
    level_category: str
    level: str

@app.get("/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@app.get("/regist_user", response_class=HTMLResponse)
def regist_user(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="regist_user.html",
        context={}
    )

@app.post("/regist_user")
def regist_user(request: Request,
             username: str = Form(...),
             password: str = Form(...)):
    
    connn = db_connect()

    try:
        with connn:
            cursor = connn.cursor()
        
            cursor.execute(
                "select * from M_User where user_name = %s",
                (username,)
            )
            user_data = cursor.fetchone()

            if user_data:
                return JSONResponse(
                    { "success": False,
                     "message": "ユーザー名は既に使用されています"
                    })
            
            hashed_password = get_password_hash(password)

            cursor.execute(
                "Insert into M_User "
                "(user_name, hashed_password, update_date,create_date) "
                "values "
                "(%s, %s, %s, %s)",
                (username, 
                 hashed_password, 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
    finally:
        connn.close()

    response = JSONResponse(
        { "success": True,
         "next": "/",
         "usernamedisplay": username,
            "condition_message": "登録が完了しました。ログインしてください。"
        })

    return response

@app.get("/regist_syntax", response_class=HTMLResponse)
def regist_syntax(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="regist_syntax.html",
        context={}
    )

@app.post("/regist_syntax")
def regist_syntax(request: Request,
             syntaxId: Optional[str] = Form(default=""),
             automaticNumbering: bool = Form(...),
             syntax: str = Form(...),
             meaning: str = Form(...)):

    conn = db_connect()

    sessionId = request.cookies.get("session_id")
    userId = get_session_data(sessionId).user_id

    useSyntaxId = ''
    if not automaticNumbering:
        try:
            with conn:
                cursor = conn.cursor()
            
                cursor.execute(
                    "select * from M_Syntax "
                    "where user_id = %s and Syntax_id = %s",
                    (userId,
                     syntaxId)
                )
                syntax_data = cursor.fetchone()

                if syntax_data:
                    return JSONResponse(
                        { "success": False,
                        "message": "シンタックスIDは既に使用されています"
                        })
        finally:
            conn.close()
        
        useSyntaxId = syntaxId
    else:
        try:
            with conn:
                cursor = conn.cursor()

                cursor.execute(
                    "select MAX(Syntax_id) from M_Syntax "
                    "where user_id = %s",
                    (userId,)
                )
                syntax_data = cursor.fetchone()
        finally:
            conn.close()
    
    conn = db_connect()

    if not syntax_data[0]:
        useSyntaxId = 1
    else:
        useSyntaxId = syntax_data[0] + 1

    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "Insert into M_Syntax "
                "(user_id, syntax_id, syntax, meaning, studied_date, study_number, true_number, false_number, true_rate, review_interval, next_review_date, update_date, create_date) "
                "values "
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (userId, 
                useSyntaxId, 
                syntax,
                meaning,
                initial_yyyymmdd, 0, 0, 0, 0, 0, initial_yyyymmdd,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
    finally:
        conn.close()

    response = JSONResponse(
        { "success": True,
         "next": "/start",
         "syntaxIdDisplay": useSyntaxId,
         "syntaxDisplay": syntax,
         "meaningDisplay": meaning,
         "condition_message": "登録が完了しました。"
        })

    return response

@app.post("/login")
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...)):
    
    conn = db_connect()

    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select * from M_User where user_name = %s",
                (username,)
            )
            user_data = cursor.fetchone()
    finally:
        conn.close()

    if not user_data:
        return JSONResponse(
            { "success": False,
             "message": "ユーザー名またはパスワードが間違っています"
            })
    
    if not verify_password(password, user_data[2]):
        return JSONResponse(
            { "success": False,
             "message": "ユーザー名またはパスワードが間違っています"
            })
    
    sessionId = str(uuid.uuid4())

    conn = db_connect()

    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "Insert into T_Session "
                "(session_id, user_id, current_start_id, update_date, create_date) "
                "values "
                "(%s, %s, %s, %s, %s)",
                (sessionId, 
                 user_data[0],
                 0,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
    finally:
        conn.close()

    response = JSONResponse(
        { "success": True,
         "next": "/start",
         "username": username
        })
    
    response.set_cookie(
        key="session_id",
        value=sessionId,
        httponly=True
    )
    
    return response

@app.get("/start", response_class=HTMLResponse)
def start_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="start.html",
        context={}
    )

@app.post("/start")
def start(request: Request,
          numberquestions: int = Form(...),
          levelCategory: str = Form(...),
          level: str = Form(...)):
    
    if numberquestions <= 0:
        return JSONResponse({
            "success": False,
            "message": "有効な数字を入力してください"
        })
    
    if numberquestions > 20:
        return JSONResponse({
            "success": False,
            "message": "一回に学習できる問題数は20問までです"
        })

    sessionId = request.cookies.get("session_id")
    
    sessionData = get_session_data(sessionId)

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select MAX(start_id) "
                "from T_Start "
                "where session_id = %s",
                (sessionId,)
            )
            max_start_id = cursor.fetchone()
    finally:
        conn.close()

    if max_start_id[0] is None:
        start_id = 1
    else:
        start_id = max_start_id[0] + 1

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select 1 from M_Syntax "
                "where user_id = %s ",
                (sessionData.user_id,)
            )
            syntax_data = cursor.fetchall()

            cursor.execute(
                "select syntax_id, syntax, meaning "
                "from M_Syntax "
                "where user_id = %s and next_review_date < %s "
                "order by next_review_date, true_rate limit %s",
                (sessionData.user_id,
                 datetime.now().strftime("%Y%m%d"),
                 numberquestions)
            )
            target_syntax_data = cursor.fetchall()
    finally:
        conn.close()

    if not syntax_data:
        return JSONResponse({
            "success": False,
            "message": "シンタックスが登録されていません。登録してください。"
    })

    if not target_syntax_data:
        return JSONResponse({
            "success": False,
            "message": "練習対象のシンタックスがありません。"
    })

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
    
            cursor.execute("Insert into T_Start "
                           "(session_id, start_id, start_date, number_questions, level_category, level, update_date, create_date) "
                           "values "
                           "(%s, %s, %s, %s, %s, %s, %s, %s)",
                           (sessionId,
                            start_id,
                            datetime.now().strftime("%Y%m%d"),
                            numberquestions,
                            levelCategory,
                            level,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            cursor.execute("update T_Session set current_start_id = %s, update_date = %s where session_id = %s",
                           (start_id,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            sessionId))
    finally:
        conn.close()

    # 3. gemini APIを呼び出して質問を生成し、履歴データに書き出し
    rowNumber = 0

    if levelCategory == "1":
        levelCategoryname = "CEFR"

        if level == "1":
            levelname = "A1"
        elif level == "2":
            levelname = "A2"
        elif level == "3":
            levelname = "B1"
        elif level == "4":
            levelname = "B2"
        elif level == "5":
            levelname = "C1"
        else:
            levelname = "C2"

    elif levelCategory == "2":
        levelCategoryname = "IELTS"
        
        if level == "1":
            levelname = "5.0"
        elif level == "2":
            levelname = "6.0"
        elif level == "3":
            levelname = "7.0"
        elif level == "4":
            levelname = "8.0"
        else:
            levelname = "9.0"
    else:
        levelCategoryname = "TOEIC"

        if level == "1":
            levelname = "500"
        elif level == "2":
            levelname = "600"
        elif level == "3":
            levelname = "700"
        elif level == "4":
            levelname = "800"
        else:
            levelname = "900"

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            for syntax in target_syntax_data:

                response_api = call_gemini_api(
                    prompt="Please generate a question in Japanese based on the following English syntax: " + syntax[1] + ", meaning: " + syntax[2] + " and also follow level category: " + levelCategoryname + " and level: " + levelname + " in terms of vocabulary and grammar. The response should be in JSON format with the following structure: {\"syntax_id\": \"<syntax_id>\", \"syntax\": \"<syntax>\", \"japanese_sentence\": \"<japanese_sentence>\"}.",
                    response_schema=QuestionData,  # Pydanticモデルを直接指定
                )
                
                data = QuestionData.model_validate_json(response_api.text)

                rowNumber += 1

                cursor.execute(
                    "Insert into T_History "
                    "(session_id, start_id, row_num, syntax_id, japanese_sentence, update_date, create_date) "
                    "values "
                    "(%s, %s, %s, %s, %s, %s, %s)",
                    (sessionId,
                     start_id,
                     rowNumber,
                     syntax[0],
                     data.japanese_sentence,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
    finally:
        conn.close()

    response = JSONResponse(
        { "success": True,
         "next": "/question" 
        })

    return response

@app.get("/question")
def question_page(request: Request):

    sessionId = request.cookies.get("session_id")
    current_start_id = get_session_data(sessionId).current_start_id
    startData = get_start_data(sessionId, current_start_id)

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "select japanese_sentence, row_num "
                "from T_History "
                "where session_id = %s and answer is null "
                "order by row_num limit 1",
                (sessionId,)
            )
            question_data = cursor.fetchone()
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "question.html",
        {
            "sessionId": sessionId,
            "startId": current_start_id,
            "rowNumber": question_data[1],
            "numberquestions": startData.number_questions,
            "levelCategory": startData.level_category,
            "level": startData.level,
            "japaneseSentence": question_data[0]
        }
    )

@app.post("/answer")
def answer(request: Request,
           sessionId: str = Form(...),
           startId: str = Form(...),
           rowNumber: int = Form(...),
           answer: str = Form(...)):

    sessionData = get_session_data(sessionId)

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select M1.syntax, T1.japanese_sentence, T2.number_questions "
                "from T_History T1 "
                "inner join M_Syntax M1 "
                "on M1.user_id = %s and M1.syntax_id = T1.syntax_id "
                "inner join T_Start T2 "
                "on T2.session_id = T1.session_id and T2.start_id = T1.start_id "
                "where T1.session_id = %s and T1.start_id = %s and T1.row_num = %s",
                (sessionData.user_id,
                 sessionId,
                 startId,
                 rowNumber)
            )
            syntax_data = cursor.fetchone()
    finally:
        conn.close()

    response_api = call_gemini_api(
        prompt="Please evaluate the following English sentence if it is use following syntax correctly and if it is correct compared to following japanese sentence. english sentence:" + answer + ", syntax:" + syntax_data[0] + ",japanese sentence:" + syntax_data[1] + ". The response should be in JSON format with the following structure: {\"result\": \"<result>\", \"correct_answer\": \"<correct_answer>\", \"Explanation\": \"<Explanation>\"}. <result> can be either 1(means 'correct') or 0(means 'incorrect'). If the answer is incorrect, provide the correct answer in <correct_answer> and a brief within 100 characters explanation in <Explanation>.",
        response_schema=AnswerData,  # Pydanticモデルを直接指定
    )
    
    data = AnswerData.model_validate_json(response_api.text)

    print(data)

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "update T_History "
                "set answer = %s, result = %s, correct_answer = %s, explanation = %s, update_date = %s "
                "where session_id = %s and start_id = %s and row_num = %s",
                (answer,
                 data.result,
                 data.correct_answer,
                 data.explanation,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 sessionId,
                 startId,
                 rowNumber) 
            )

            cursor.execute(
                "update M_Syntax "
                "set studied_date = %s, "
                "study_number = study_number + 1, "
                "true_number = CASE WHEN T_History.result = 1 THEN true_number + 1 ELSE true_number END, "
                "false_number = CASE WHEN T_History.result = 0 THEN false_number + 1 ELSE false_number END, "
                "review_interval = CASE "
                "                      WHEN review_interval = 0 THEN 1 "
                "                      WHEN review_interval = 16 THEN review_interval "
                "                      ELSE "
                "                          CASE "
                "                              WHEN T_History.result = 1 THEN review_interval * 2 "
                "                              ELSE review_interval "
                "                          END "
                "                  END, "
                "update_date = %s "
                "from T_History "
                "where T_History.session_id = %s and T_History.start_id = %s and T_History.row_num = %s "
                "and M_Syntax.user_id = %s and T_History.syntax_id = M_Syntax.syntax_id",
                (datetime.now().strftime("%Y%m%d"),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 sessionId,
                 startId,
                 rowNumber,
                 sessionData.user_id)
            )

            cursor.execute(
                "update M_Syntax "
                "set true_rate = ROUND((CAST(true_number AS NUMERIC) / CAST(study_number AS NUMERIC)) * 100, 1), "
                "next_review_date = to_char( "
                "                       CASE "
                "                           WHEN next_review_date = %s THEN %s::date "
                "                           ELSE to_date(next_review_date, 'YYYYMMDD') "
                "                       END + (review_interval || ' days')::interval, "
                "                       'YYYYMMDD' "
                "                   ), "
                "update_date = %s "
                "from T_History "
                "where T_History.session_id = %s and T_History.start_id = %s and T_History.row_num = %s "
                "and M_Syntax.user_id = %s and T_History.syntax_id = M_Syntax.syntax_id",
                (initial_yyyymmdd,
                 datetime.now().strftime("%Y-%m-%d"),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 sessionId,
                 startId,
                 rowNumber,
                 sessionData.user_id)
            )

    finally:
        conn.close()

    finished = False
    if syntax_data[2] == rowNumber:
        finished = True

    return JSONResponse({
        "success": True,
        "result": "correct" if data.result == 1 else "incorrect",
        "correct_answer": data.correct_answer,
        "explanation": data.explanation,
        "finished": finished
    })

@app.get("/result")
def result_page(request: Request):

    sessionId = request.cookies.get("session_id")
    sessionData = get_session_data(sessionId)

    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select "
                "sum(case when result = 1 then 1 else 0 end) as correct_count, "
                "sum(case when result = 0 then 1 else 0 end) as incorrect_count "
                "from T_History "
                "where session_id = %s and start_id = %s",
                (sessionId,
                 sessionData.current_start_id)
            )
            result_data = cursor.fetchone()
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "sessionId": sessionId,
            "true_count": result_data[0],
            "false_count": result_data[1],
            "true_rate": round((result_data[0] / (result_data[0] + result_data[1])) * 100, 1) if (result_data[0] + result_data[1]) > 0 else 0,
            "false_syntax_id_list": get_false_syntax_id_list(sessionId, sessionData),
            "wrong_answers": get_wrong_answers(sessionId, sessionData),
        }
    )

def db_connect():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def call_gemini_api(prompt: str, response_schema: BaseModel):

    api_key = os.getenv("GEMINI_API_KEY")

    with genai.Client(api_key=api_key) as client:
        response_api = call_gemini_with_retry(
            client,
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
    
    return response_api

def call_gemini_with_retry(client, **kwargs):

    MAX_RETRIES = 3
    last_error = None

    for attempt in range(MAX_RETRIES):

        try:
            return client.models.generate_content(**kwargs)
            
        except Exception as e:
            last_error = e

            if "503" not in str(e):
                raise

            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                time.sleep(wait)

    raise last_error

def get_false_syntax_id_list(sessionId: str, sessionData: sessionData):
    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select M_Syntax.syntax_id, M_Syntax.syntax, T_History.japanese_sentence, T_History.answer "
                "from T_History "
                "inner join M_Syntax "
                "on M_Syntax.user_id = %s and T_History.syntax_id = M_Syntax.syntax_id "
                "where T_History.session_id = %s and T_History.start_id = %s and T_History.result = 0",
                (sessionData.user_id,
                 sessionId,
                 sessionData.current_start_id)
            )
            false_syntax_data = cursor.fetchall()
    finally:
        conn.close()
    
    false_syntax_id_list = []
    for row in false_syntax_data:
        false_syntax_id_list.append(row[0])

    return false_syntax_id_list

def get_wrong_answers(sessionId: str, sessionData: sessionData):
    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select M_Syntax.syntax_id, M_Syntax.syntax, T_History.row_num, T_History.japanese_sentence, T_History.answer, T_History.correct_answer, T_History.explanation "
                "from T_History "
                "inner join M_Syntax "
                "on M_Syntax.user_id = %s and T_History.syntax_id = M_Syntax.syntax_id "
                "where T_History.session_id = %s and T_History.start_id = %s and T_History.result = 0",
                (sessionData.user_id,
                 sessionId,
                 sessionData.current_start_id)
            )
            wrong_answers_data = cursor.fetchall()
    finally:
        conn.close()
    
    wrong_answers = []
    for row in wrong_answers_data:
        wrong_answers.append({
            "syntax_id": row[0],
            "syntax": row[1],
            "row_num": row[2],
            "japanese_sentence": row[3],
            "answer": row[4],
            "correct_answer": row[5],
            "explanation": row[6],
        })

    return wrong_answers

def get_session_data(sessionId: str):
    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select * "
                "from T_Session "
                "where session_id = %s",
                (sessionId,)
            )
            session_data = cursor.fetchone()
    finally:
        conn.close()

    return sessionData(
        session_id = session_data[0],
        user_id = session_data[1],
        current_start_id = session_data[2]
    )

def get_start_data(sessionId: str, startId: str):
    conn = db_connect()
    try:
        with conn:
            cursor = conn.cursor()
        
            cursor.execute(
                "select * "
                "from T_Start "
                "where session_id = %s and start_id = %s",
                (sessionId, startId)
            )
            start_data = cursor.fetchone()
    finally:
        conn.close()

    return startData(
        session_id = start_data[0],
        start_id = start_data[1],
        start_date = start_data[2],
        number_questions = start_data[3],
        level_category = start_data[4],
        level = start_data[5]
    )