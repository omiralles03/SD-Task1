# Common logic for parsing benchmark lines

def parse_benchmark_line(line):

    parts = line.strip().split()
    if not parts or parts[0] != "BUY":
        return None

    if len(parts) == 4:  # BUY <client_id> <seat_id> <request_id>
        return {
            "action": "buy_numbered",
            "client_id": parts[1],
            "seat_id": parts[2],
            "request_id": parts[3]
        }
    elif len(parts) == 3:  # BUY <client_id> <request_id>

        return {
            "action": "buy_unnumbered",
            "client_id": parts[1],
            "request_id": parts[2]
        }
    return None


# Formatter for debugging
def format_result_msg(result):
    status = result['status']
    msg = f" [<-] Result: {result['status']}"

    details = {
        "SUCCESS": lambda r: f" (Ticket #: {r.get('ticket')})",
        "CONFIRMED": lambda r: f" (Ticket #: {r.get('ticket')} already yours ({r.get('owner')})",
        "ALREADY_PROCESSED": lambda r: f" (Owned by: {r.get('owner')})",
        "OCCUPIED": lambda r: f" (Seat {r.get('seat_id')} owned by {r.get('owner')})",
        "INVALID_SEAT": lambda r: f" (Seat {r.get('seat_id')} out of range. Limit: 1 - {r.get('limit')})",
        "SOLD_OUT": lambda r: f" (Limit {r.get('limit')} reached (current: {r.get('current')})"
    }
    
    if status in details:
        msg += details[status](result)
    
    return msg
