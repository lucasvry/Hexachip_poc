import requests
import json
from datetime import datetime

# Initialize variables
parts_ids = [
    "RFWD312.5CCLT-32.768KHz",
]
not_found_part_ids = []
invalid_response_part_ids = []

API_URL = "https://api.nexar.com/graphql"
BEARER_TOKEN_OCTOPART = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjA5NzI5QTkyRDU0RDlERjIyRDQzMENBMjNDNkI4QjJFIiwidHlwIjoiYXQrand0In0.eyJuYmYiOjE3MDc4MjY0ODYsImV4cCI6MTcwNzkxMjg4NiwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5uZXhhci5jb20iLCJjbGllbnRfaWQiOiIwMGI1MjJiYS1iNTA1LTQxYzEtOGJhOC02ZDljYzgyNDQ1NWEiLCJzdWIiOiJGODY3NzFGQS00Qjg0LTRDNDEtOUNFMi1GQUQwQjM5QTEyOUEiLCJhdXRoX3RpbWUiOjE3MDc4MjYzNzAsImlkcCI6ImxvY2FsIiwicHJpdmF0ZV9jbGFpbXNfaWQiOiI3ZGQwMWMxNi1hNzQ4LTQ0MWEtOGFiYS1kY2FiZjE4MzZjZjIiLCJwcml2YXRlX2NsYWltc19zZWNyZXQiOiJRQUdiNXZKV3RrdUltcVlVYm9NRy9mNmFzSDROaDM2cG0rUmtmeFVKZDR3PSIsImp0aSI6IjcwRUQ2NkQ5N0ZCQzkyNTRGQkREOTJFMTJDNUJFMzM1Iiwic2lkIjoiODE5NDFCQkJFOTAxRTk5NjQzNzA1MjkxRTEwMTg3QjAiLCJpYXQiOjE3MDc4MjY0ODYsInNjb3BlIjpbIm9wZW5pZCIsInVzZXIuYWNjZXNzIiwicHJvZmlsZSIsImVtYWlsIiwidXNlci5kZXRhaWxzIiwic3VwcGx5LmRvbWFpbiIsImRlc2lnbi5kb21haW4iXSwiYW1yIjpbInB3ZCJdfQ.KTR0CgB96iMfE54TZEuSTkZtScniGsFUhGJho6KiO2m_t39yPqASCeW4QDmyTB9FyqTXzZM2DwRpz7O18H1YcpOWBxETZ7Am5bQQompWUJYo9E_rvWAdauHA5wc9pkB1tW1blGxZboy1HpGrpMbzvsFpupvQGE8ATjwsumv52VRcmD991riw44SuilbeM4Z5ECDa8Kcbiy8M5V0uFps3XfkrB1HPvl4O0MHyaqh5amrhS0E5E2UOgtqtsFV75GaYtQiyp91pFgOEfV0htPK1VlCijK2rmfLX3AUtlsfIuO4gsz20xJaNtVz_BIlWeBqKKr-wigSywgStFsjz3QlCOg"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN_OCTOPART}"}

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"./output/results_octopart_{timestamp}.json"
log_filename = f"./output/log_{timestamp}.txt"

# Write initial empty array to file
with open(filename, "w") as file:
    json.dump([], file)

for part_id in parts_ids:
    query = {
        "query": f"""query pricingByVolumeLevels {{
                        supSearchMpn(q: "{part_id}", limit: 1, distributorApi: true) {{
                            results {{
                                part {{
                                    mpn
                                    id
                                    sellers {{
                                        company {{ name }}
                                        isBroker
                                        isAuthorized
                                        offers {{
                                            prices {{
                                                quantity
                                                convertedPrice
                                            }}
                                            factoryLeadDays
                                            inventoryLevel
                                        }}
                                    }}
                                    medianPrice1000 {{ convertedPrice }}
                                    totalAvail
                                    estimatedFactoryLeadDays
                                }}
                            }}
                        }}
                    }}"""
    }

    try:
        response = requests.post(API_URL, headers=headers, json=query)
        response.raise_for_status()

        data = response.json()
        print(data)
        results = data.get("data", {}).get("supSearchMpn", {}).get("results", [])
        if results:
            has_results = len(results) > 0
            if has_results:
                with open(filename, "r+") as file:
                    existing_data = json.load(file)
                    new_data = data["data"]["supSearchMpn"]["results"]
                    existing_data.extend(new_data)
                    file.seek(0)
                    json.dump(existing_data, file)
                print(f"Successfully formatted and parsed data for partId {part_id}")
            else:
                not_found_part_ids.append(part_id)
                print(f"No results for partId {part_id}")
        else:
            invalid_response_part_ids.append(part_id)
            print(f"Invalid json for partId {part_id}")
    except requests.exceptions.HTTPError as e:
        print(f"Invalid JSON response for partId {part_id}: {e}")
        invalid_response_part_ids.append(part_id)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for partId {part_id}: {e}")
        invalid_response_part_ids.append(part_id)

# Log results
with open(log_filename, "w") as log_file:
    log_file.write("Could not find data for the following partIds:\n")
    log_file.write(", ".join(not_found_part_ids) + "\n")
    log_file.write(f"List length: {len(not_found_part_ids)}\n")

    log_file.write("Invalid JSON response for the following partIds:\n")
    log_file.write(", ".join(invalid_response_part_ids) + "\n")
    log_file.write(f"List length: {len(invalid_response_part_ids)}\n")
