def verify_data(data):
    if not data:
        return False, "No data extracted"

    if not data.get("FullName") or not data.get("DocumentNumber"):
        return False, "Missing critical fields"

    # Add more checks if needed
    return True, "Verification passed"
