import sys
import os
from fastapi import FastAPI, HTTPException, status

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.database import TicketDB

app = FastAPI(title="Ticket System - REST Worker")
db = TicketDB()

@app.post("/buy/unnumbered")
async def buy_unnumbered(client_id: str, request_id: str):
    result = db.buy_unnumbered(client_id, request_id)
    
    if result["status"] == "SUCCESS":
        return {"status": "success", "ticket": result["ticket"]}
    
    elif result["status"] == "ALREADY_PROCESSED":
        return {"status": "success", "message": "Already processed", "owner": result["owner"]}
    
    else:
        return {"status": "rejected", "reason": result["status"]}

@app.post("/buy/numbered")
async def buy_numbered(client_id: str, seat_id: int, request_id: str):
    result = db.buy_numbered(client_id, seat_id, request_id)
    
    if result["status"] == "SUCCESS":
        return {"status": "success", "seat_id": seat_id}
    
    elif result["status"] == "ALREADY_PROCESSED":
        return {"status": "success", "message": "Already processed", "owner": result["owner"]}
    
    else:
        return {"status": "rejected", "reason": result["status"]}