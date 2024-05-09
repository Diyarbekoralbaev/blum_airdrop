from fastapi import FastAPI
from database import Database
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/users")
def read_users():
    db = Database()
    users = db.get_all_users()
    db.close()
    response = [
        {
            "tg_id": user[1],
            "tg_name": user[2],
            "tg_username": user[3],
            "balance": user[4],
            "user_hash": user[5],
            "last_time_mine": user[6],
            "next_time_mine": user[7]
        }
        for user in users
    ]
    return response

@app.get("/users/count")
def read_users_count():
    db = Database()
    count = db.users_count()
    db.close()
    return {
        "count": count
    }

@app.get("/users/{user_hash}")
def read_user(user_hash: str):
    db = Database()
    user = db.get_user_with_hash(user_hash)
    db.close()
    user = {
        "tg_id": user[1],
        "tg_name": user[2],
        "tg_username": user[3],
        "balance": user[4],
        "last_time_mine": user[6],
        "next_time_mine": user[7]
    }
    return user

@app.get("/users/{user_hash}/balance")
def read_user_balance(user_hash: str):
    db = Database()
    user = db.get_user_with_hash(user_hash)
    db.close()
    return {
        "balance": user[4]
    }

@app.get("/users/{user_hash}/get_mining_reward")
def read_user_mining_reward(user_hash: str):
    db = Database()
    reward = db.get_mining_reward(user_hash)
    db.close()
    return {
        "reward": reward
    }

@app.get("/users/{user_hash}/referrals")
def read_user_referrals(user_hash: str):
    db = Database()
    user = db.get_user_with_hash(user_hash)
    referal_info = db.tg_get_user(user[1])
    db.close()
    response = [
        {
            "referral_id": referral[1],
            "referral_name": referral[2],            
        }
        for referral in referal_info
    ]
    return response
