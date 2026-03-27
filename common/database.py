import redis
from common.config import REDIS_HOST, REDIS_PORT


class TicketDB:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        self.limit_unnumbered = 20000
        self.limit_numbered = 20000

    def buy_unnumbered(self, client_id, request_id):

        # Redis format K:V
        if self.redis_client.exists(f"req:{request_id}"):
            owner = self.redis_client.get(f"req:{request_id}")
            return {"status": "ALREADY_PROCESSED", "owner": owner}

        current = self.redis_client.incr("count:unnumbered")

        if current <= self.limit_unnumbered:
            self.redis_client.set(f"req:{request_id}", client_id)
            return {"status": "SUCCESS", "ticket": current}
        else:
            return {"status": "SOLD_OUT"}

    def buy_numbered(self, client_id, seat_id, request_id):

        s_id = int(seat_id)
        if s_id < 1 or s_id > self.limit_numbered:
            return {"status": "INVALID_SEAT", "err": "seat_id out of range"}

        # Redis format K:V
        if self.redis_client.exists(f"req:{request_id}"):
            owner = self.redis_client.get(f"req:{request_id}")
            return {"status": "ALREADY_PROCESSED", "owner": owner}

        # Check if seat is already Taken (K,V ==> "seat:XX", "userXXX")
        if self.redis_client.setnx(f"seat:{seat_id}", client_id):
            self.redis_client.set(f"req:{request_id}", client_id)
            return {"status": "SUCCESS"}
        else:
            return {"status": "OCCUPIED"}

    def reset_db(self):
        self.redis_client.flushall()
