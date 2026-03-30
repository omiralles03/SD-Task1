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
