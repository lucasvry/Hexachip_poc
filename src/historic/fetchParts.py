import os

import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Initialize variables
parts_ids = [
    "RFWD312.5CCLT-32.768KHz",
]
not_found_part_ids = []
invalid_response_part_ids = []

api_url = os.getenv("OCTOPART_API_URL")
octopart_bearer_token = os.getenv("OCTOPART_BEARER_TOKEN")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {octopart_bearer_token }"}

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
        response = requests.post(api_url, headers=headers, json=query)
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
