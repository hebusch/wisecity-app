import os
from dotenv import load_dotenv
from wisecity import WiseCityClient

load_dotenv()

# Get credentials from environment
EMAIL = os.getenv("WISECITY_EMAIL")
PASSWORD = os.getenv("WISECITY_PASSWORD")

if not EMAIL or not PASSWORD:
    print("Please set WISECITY_EMAIL and WISECITY_PASSWORD environment variables")
    exit(1)


def main():
    # Initialize client
    client = WiseCityClient(email=EMAIL, password=PASSWORD)

    # Get all devices
    print("📡 Fetching devices...")
    devices = client.devices.list()

    print(f"\n✅ Found {len(devices)} device(s)\n")

    for device in devices:
        print("=" * 50)
        print(f"🚗 Vehicle: {device.vehicle.full_name}")
        print(f"   Plate: {device.vehicle.plate}")
        print(f"   Device ID: {device.id}")
        print()
        print(f"📍 Location:")
        print(f"   Coordinates: {device.location}")
        print(f"   Google Maps: {device.location.google_maps_url}")
        print()
        print(f"📊 Status:")
        print(f"   Status: {device.status_name}")
        print(f"   Speed: {device.speed} km/h")
        print(f"   Last Update: {device.last_update}")
        print(f"   Locked: {'Yes' if device.locked else 'No'}")
        print()
        if device.subscription:
            print(f"💳 Subscription:")
            print(f"   Plan: {device.subscription.plan_name}")
            print(f"   Status: {device.subscription.status_text}")
            print(f"   Valid: {'Yes' if device.subscription.is_valid else 'No'}")
            print(f"   Expires: {device.subscription.finish_date}")
        print()


if __name__ == "__main__":
    main()
