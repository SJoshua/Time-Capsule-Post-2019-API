import connexion
import requests
import mysql.connector
import hashlib
import flask
import json
import six

from swagger_server.models.body import Body  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.question_capsule import QuestionCapsule  # noqa: E501
from swagger_server.models.time_capsule import TimeCapsule  # noqa: E501
from swagger_server import util

from config import cfg

f = open("./questions.json", "r")
questions = json.loads(f.read())
f.close()

class database:
    def getCursor():
        con = mysql.connector.connect(
            host = cfg["host"],
            user = cfg["user"],
            passwd = cfg["passwd"],
            database = cfg["database"]
        )
        cur = con.cursor(prepared = True)
        cur.execute("SET NAMES 'utf8mb4'")
        cur.execute("SET CHARACTER SET 'utf8mb4'")
        return con, cur

    def getInfo(open_id):
        (con, cur) = database.getCursor()
        cur.execute("SELECT uid, name, tel FROM users WHERE open_id = ?", [open_id])
        r = cur.fetchone()
        cur.close()
        con.close()
        return r and [r[0], str(r[1], 'utf-8'), str(r[2], 'utf-8')]

    def getNameByID(uid):
        (con, cur) = database.getCursor()
        cur.execute("SELECT name FROM users WHERE uid = ?", [uid])
        r = cur.fetchone()
        cur.close()
        con.close()
        return r and r[0]

    def getTimeCapsules(uid):
        (con, cur) = database.getCursor()
        cur.execute("SELECT * FROM time_capsules WHERE sender_id = ? and period = 'half-year'", [uid])
        r = cur.fetchall() 
        cur.close()
        con.close()
        return r
    
    def getTimeCapsuleByCode(code):
        (con, cur) = database.getCursor()
        cur.execute("SELECT * FROM time_capsules WHERE code = ? and period = 'half-year'", [code])
        r = cur.fetchone()
        cur.close()
        con.close()
        return r

    def getQuestionCapsules(uid):
        (con, cur) = database.getCursor()
        cur.execute("SELECT * FROM question_capsules WHERE sender_id = ? and period = 'half-year'", [uid])
        r = cur.fetchall() 
        cur.close()
        con.close()
        return r
    
    def getQuestionCapsuleByID(uid, cid):
        (con, cur) = database.getCursor()
        cur.execute("SELECT * FROM question_capsules WHERE sender_id = ? and capsule_id = ? and period = 'half-year'", [uid, cid])
        r = cur.fetchone() 
        cur.close()
        con.close()
        return r
    
    def updateQuestionCapsule(id, ans):
        (con, cur) = database.getCursor()
        cur.execute("UPDATE question_capsules SET NEW_MESSAGE = ? WHERE capsule_id = ? and period = 'half-year'", [ans, id])
        cur.close()
        con.commit()
        con.close()

def getAudioPath(fid):
    return cfg["media"] % hashlib.md5(fid.decode("utf-8").encode(encoding = 'utf-8')).hexdigest()

def checkOpenID():
    # for debug
    if "open_id" not in flask.session:
        sess_id = flask.request.cookies.get("PHPSESSID")
        if sess_id is not None:
            r = requests.get("https://hemc.100steps.net/2017/wechat/Home/Index/getUserInfo", timeout = 5, cookies = dict(PHPSESSID = sess_id))
            try:
                t = json.loads(r.text)
                if "openid" in t:
                    flask.session["open_id"] = t["openid"]
            except:
                pass
    return "open_id" in flask.session

def info_get():  # noqa: E501
    """Get user's info

     # noqa: E501


    :rtype: InlineResponse200
    """
    if not checkOpenID():
        return "Please call WeChat API first.", 401
        
    info = database.getInfo(flask.session.get("open_id"))
    return {
        "participated": info is not None
    }

def question_capsules_get():  # noqa: E501
    """Get question capsules

     # noqa: E501


    :rtype: List[QuestionCapsule]
    """
    if not checkOpenID():
        return "Please call WeChat API first.", 401
    u_info = database.getInfo(flask.session.get("open_id"))
    if u_info is None:
        return "Not found", 404
    info = database.getQuestionCapsules(u_info[0])
    ret = []
    for e in info:
        qid = int(e[3])
        t = {
            "id": e[0],
            "quesion": questions[qid // 100 - 1][qid % 100],
            "answer": e[4].decode("utf-8"),
            "time": int(e[5].timestamp()),
        }
        if e[6]:
            t["new_answer"] = e[6].decode("utf-8")
        ret.append(t)
    return ret

def question_capsule_cid_post(body, cid):  # noqa: E501
    """Post new answer for question capsules

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param cid: capsule id
    :type cid: int

    :rtype: List[QuestionCapsule]
    """
    if not checkOpenID():
        return "Please call WeChat API first.", 401
    u_info = database.getInfo(flask.session.get("open_id"))
    if u_info is None:
        return "Not found", 404
    if connexion.request.is_json:
        body = Body.from_dict(connexion.request.get_json())  # noqa: E501
        info = database.getQuestionCapsuleByID(u_info[0], cid)
        if not info:
            return "Not Found", 404
        if info[6]:
            return "Already answered", 409
        print(body)
        if not body.answer:
            return "Bad Request", 400
        qid = int(info[3])
        database.updateQuestionCapsule(cid, body.answer)
        return {
            "id": info[0],
            "quesion": questions[qid // 100 - 1][qid % 100],
            "answer": info[4].decode("utf-8") == "voice" and "audio" or "text",
            "time": int(info[5].timestamp()),
            "new_answer": body.answer
        }

    return "Bad Request", 400

def time_capsules_get():  # noqa: E501
    """Get time capsules received by qrcode

     # noqa: E501


    :rtype: List[TimeCapsule]
    """
    if not checkOpenID():
        return "Please call WeChat API first.", 401
    u_info = database.getInfo(flask.session.get("open_id"))
    if u_info is None:
        return "Not found", 404
    info = database.getTimeCapsules(u_info[0])
    ret = []
    for e in info:
        ret.append({
            "from": database.getNameByID(e[1]).decode("utf-8"),
            "to": e[2].decode("utf-8"),
            "type": e[4].decode("utf-8") == "voice" and "audio" or "text",
            "content": e[7] and getAudioPath(e[7]) or e[6].decode("utf-8"),
            "time": int(e[9].timestamp())
        })
    return ret

def time_capsule_code_get(code):  # noqa: E501
    """Get time capsule by code

     # noqa: E501

    :param code: capsule code
    :type code: str

    :rtype: TimeCapsule
    """
    if not checkOpenID():
        return "Please call WeChat API first.", 401
    info = database.getTimeCapsuleByCode(code)
    if info is None:
        return "Not found", 404
    return {
        "from": database.getNameByID(info[1]).decode("utf-8"),
        "to": info[2].decode("utf-8"),
        "type": info[4].decode("utf-8") == "voice" and "audio" or "text",
        "content": info[7] and getAudioPath(info[7]) or info[6].decode("utf-8"),
        "time": int(info[9].timestamp())
    }

