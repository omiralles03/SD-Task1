from common.database import TicketDB


def run_tests():
    db = TicketDB()
    db.reset_db()

    print("--- TicketDB Tests ---")

    try:
        # Test 1: Successful Numbered Purchase
        res1 = db.buy_numbered("user_A", "101", "req_001")
        assert res1["status"] == "SUCCESS", f"Expected SUCCESS, got {
            res1['status']}"
        print("[PASS] Test 1: Initial purchase successful.")

        # Test 1.1: seat_ID out of range
        res1 = db.buy_numbered("user_Aa", "50123", "req_067")
        assert res1["status"] == "INVALID_SEAT", f"Expected INVALID_SEAT, got {
            res1['status']}"
        print("[PASS] Test 1.1: Range validation successful.")

        # Test 2: Prevent double selling of the same seat
        res2 = db.buy_numbered("user_B", "101", "req_002")
        assert res2["status"] == "OCCUPIED", f"Expected OCCUPIED, got {
            res2['status']}"
        print("[PASS] Test 2: Seat correctly blocked for other users.")

        # Test 3: Idempotency (Repeat same request)
        res3 = db.buy_numbered("user_A", "101", "req_001")
        assert res3["status"] == "ALREADY_PROCESSED", f"Expected ALREADY_PROCESSED, got {
            res3['status']}"
        print("[PASS] Test 3: Idempotency check works (Request already handled).")

        # Test 4: Unnumbered limit (Testing with limit = 2)
        db.limit_unnumbered = 2

        # First two should pass
        assert db.buy_unnumbered("u1", "r1")["status"] == "SUCCESS"
        assert db.buy_unnumbered("u2", "r2")["status"] == "SUCCESS"
        print("[PASS] Test 4.1: Unnumbered tickets within limit.")

        # Third should fail
        res_limit = db.buy_unnumbered("u3", "r3")
        assert res_limit["status"] == "SOLD_OUT", f"Expected SOLD_OUT, got {
            res_limit['status']}"
        print("[PASS] Test 4.2: Unnumbered limit enforced.")

        # Test 5: Idempotency for Unnumbered
        res_repeat_un = db.buy_unnumbered("u1", "r1")
        assert res_repeat_un["status"] == "ALREADY_PROCESSED"
        print("[PASS] Test 5: Unnumbered idempotency check works.")

        print("\nALL TESTS PASSED SUCCESSFULLY! ✅")

    except AssertionError as e:
        print(f"\n[FAIL] Test Assertion Failed: {e} ❌")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e} ⚠️")


if __name__ == "__main__":
    run_tests()
