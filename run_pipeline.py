from dotenv import load_dotenv
import os
from analyze_id import extract_id_data
from verify_and_route import verify_data

load_dotenv()

def main():
    sas_url = os.getenv("AZURE_SAS_URL")
    print("📨 Sending ID to Azure Document Intelligence...")

    extracted_data = extract_id_data(sas_url)

    if not extracted_data:
        print("❌ Could not extract data.")
        return

    print("✅ Extracted Data:")
    for k, v in extracted_data.items():
        print(f"{k}: {v}")

    verified, message = verify_data(extracted_data)
    if verified:
        print("✅ Data Verified: Proceeding with profile creation...")
        # simulate_profile_creation(extracted_data)
    else:
        print("⚠️ Verification failed. Routing to underwriter.")
        # simulate_underwriter_routing(extracted_data)

if __name__ == "__main__":
    main()
