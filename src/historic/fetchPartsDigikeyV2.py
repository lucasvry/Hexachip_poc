import ast
import json
import os
from datetime import datetime
from pathlib import Path

import digikey
from digikey.v3.batchproductdetails import BatchProductDetailsRequest
from digikey.v3.productinformation import ManufacturerProductDetailsRequest
import logging
from dotenv import load_dotenv


load_dotenv()
# Only if BatchProductDetails endpoint is explicitly enabled
# Search for Batch of Parts/Product
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

digikey_logger = logging.getLogger('digikey')
digikey_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
digikey_logger.addHandler(handler)


mpn_ids = [
    "MCP2515-I/ST"
]

not_found_part_ids = []
invalid_response_part_ids = []

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"./output/results_digikey_{timestamp}.json"

with open(filename, "w") as file:
    json.dump([], file)

for part_id in mpn_ids:
    batch_request = ManufacturerProductDetailsRequest(manufacturer_product=part_id, record_count=1, record_start_position=0, sort={"SortOption": "SortByDigiKeyPartNumber", "Direction": "Ascending", "SortParameterId": 0}, requested_quantity=1, search_options=["ManufacturerPartSearch"])
    data_dict = digikey.manufacturer_product_details(body=batch_request).to_dict()
    print(data_dict)
    results = data_dict.get("product_details")
    formatted_answer = {
            "part": {
                "mpn": part_id,
                "sellers": [
                ]
            }
        }

    with open(filename, "r+") as file:
        existing_data = json.load(file)
        if results:
            has_results = len(results) > 0
            if has_results:
                for result in results:
                    seller = {
                        "unitPrice": result.get("unit_price", ""),
                        "offers": [
                            {"price": pricing.get("total_price", ""), "quantity": pricing.get("break_quantity", "")}
                            for pricing in result.get("standard_pricing", [])],
                        "stock": result.get("quantity_available", 0),
                        "isActive": result.get("product_status", ""),
                        "isObsolete": result.get("obsolete", ""),
                        "leadTime": result.get("manufacturer_lead_weeks", "") if result.get("manufacturer_lead_weeks",
                                                                                          "") != "No lead time information available" else ""
                    }
                    formatted_answer["part"]["sellers"].append(seller)
                print(f"Successfully formatted and parsed data for partId {part_id}")
            else:
                not_found_part_ids.append(part_id)
                print(f"No results for partId {part_id}")
            # print(formatted_answer)
            existing_data.append(formatted_answer)
            file.seek(0)
            # print("existing_data", existing_data)
            json.dump(existing_data, file)

print(not_found_part_ids)
