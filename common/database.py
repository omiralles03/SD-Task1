import redis
from redis import asyncio as aioredis
from common.config import REDIS_HOST, REDIS_PORT


class TicketDB:
    def __init__(self):
        # Sync connection (RabbitMQ)
        self.sync_redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        # Async connection (FastAPI)
        self.async_redis = aioredis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
        )

        self.limit_unnumbered = 3
        self.limit_numbered = 20000

    def buy_unnumbered(self, client_id, request_id):

        # Redis format K:V
        if not self.sync_redis.setnx(f"req:{request_id}", client_id):
            owner = self.sync_redis.get(f"req:{request_id}")
            if owner == client_id:
                return {
                    "status": "ALREADY_PROCESSED", 
                    "owner": owner
                }

        count = self.sync_redis.get("count:unnumbered")
        if count is None: count = 0
        if int(count) >= self.limit_unnumbered:
            self.sync_redis.delete(f"req:{request_id}")
            return {
                "status": "SOLD_OUT", 
                "current": count,
                "limit": self.limit_unnumbered
            }

        current = self.sync_redis.incr("count:unnumbered")

        if current <= self.limit_unnumbered:
            return {
                "status": "SUCCESS", 
                "ticket": current
            }

        else:
            current = self.sync_redis.decr("count:unnumbered")
            self.sync_redis.delete(f"req:{request_id}")
            return {
                "status": "SOLD_OUT", 
                "current": current,
                "limit": self.limit_unnumbered
            }

    async def buy_unnumbered_async(self, client_id, request_id):

        # Redis format K:V
        if not await self.async_redis.setnx(f"req:{request_id}", client_id):
            owner = await self.async_redis.get(f"req:{request_id}")
            return {
                "status": "ALREADY_PROCESSED", 
                "owner": owner
            }

        count = await self.async_redis.get("count:unnumbered")
        if count is None: count = 0
        if int(count) >= self.limit_unnumbered:
            await self.async_redis.delete(f"req:{request_id}")
            return {
                "status": "SOLD_OUT", 
                "current": count,
                "limit": self.limit_unnumbered
            }

        current = await self.async_redis.incr("count:unnumbered")
        if current <= self.limit_unnumbered:
            return {
                "status": "SUCCESS", 
                "ticket": current
            }

        else:
            await self.async_redis.decr("count:unnumbered")
            await self.async_redis.delete(f"req:{request_id}")
            return {
                "status": "SOLD_OUT", 
                "current": current,
                "limit": self.limit_unnumbered
            }

    def buy_numbered(self, client_id, seat_id, request_id):

        s_id = int(seat_id)
        if s_id < 1 or s_id > self.limit_numbered:
            return {
                "status": "INVALID_SEAT",
                "seat_id": s_id,
                "limit": self.limit_numbered
            }

        # Redis format K:V
        if not self.sync_redis.setnx(f"req:{request_id}", client_id):
            owner = self.sync_redis.get(f"req:{request_id}")
            if owner == client_id:
                return {
                    "status": "CONFIRMED",
                    "ticket": seat_id,
                    "owner": owner
                }

            else:
                return {
                    "status": "ALREADY_PROCESSED",
                    "owner": owner
                }

        # Check if seat is already Taken (K,V ==> "seat:XX", "userXXX")
        if self.sync_redis.setnx(f"seat:{seat_id}", client_id):
            return {
                "status": "SUCCESS",
                "ticket": seat_id
            }

        else:
            # Free the request from the queue if seat is OCCUPIED
            actual_owner = self.sync_redis.get(f"seat:{seat_id}")
            self.sync_redis.delete(f"req:{request_id}")
            return {
                "status": "OCCUPIED",
                "owner": actual_owner,
                "seat_id": seat_id
            }

    async def buy_numbered_async(self, client_id, seat_id, request_id):

        s_id = int(seat_id)
        if s_id < 1 or s_id > self.limit_numbered:
            return {
                "status": "INVALID_SEAT",
                "seat_id": s_id,
                "limit": self.limit_numbered
            }

        # Redis format K:V
        if not await self.async_redis.setnx(f"req:{request_id}", client_id):
            owner = await self.async_redis.get(f"req:{request_id}")
            if owner == client_id:
                return {
                    "status": "CONFIRMED",
                    "ticket": seat_id,
                    "owner": owner
                }

            else:
                return {
                    "status": "ALREADY_PROCESSED",
                    "owner": owner
                }

        # Check if seat is already Taken (K,V ==> "seat:XX", "userXXX")
        if await self.async_redis.setnx(f"seat:{seat_id}", client_id):
            return {
                "status": "SUCCESS",
                "ticket": seat_id
            }

        else:
            # Free the request from the queue if seat is OCCUPIED
            actual_owner = await self.async_redis.get(f"seat:{seat_id}")
            await self.async_redis.delete(f"req:{request_id}")
            return {
                "status": "OCCUPIED",
                "owner": actual_owner,
                "seat_id": seat_id
            }
    def reset_db(self):
        self.sync_redis.flushall()
