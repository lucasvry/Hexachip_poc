import ast
import json
import os
from datetime import datetime
from pathlib import Path

import digikey
from digikey.v3.batchproductdetails import BatchProductDetailsRequest
from digikey.v3.productinformation import ManufacturerProductDetailsRequest
import logging


os.environ['DIGIKEY_CLIENT_ID'] = 'uFbyuoadeIp6BG1MDP5xVxZaYLgweyBL'
os.environ['DIGIKEY_CLIENT_SECRET'] = 'CmNER7ConcrSIfLE'
os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
os.environ['DIGIKEY_STORAGE_PATH'] = "./cache"

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
    "STM32F765NIH6",
    "MK10DX128VLQ10",
    "AG9924M",
    "0818111",
    "BTS432E2E3062ABUMA1",
    "BG96MA-128-SGN",
    "DSPIC33EV256GM102-I/MM",
    "XPC250300S-02",
    "1734346-1",
    "EPG.1B.304.HLN",
    "BNX028-01",
    "BQ25306RTER",
    "ADuM4160BRWZ",
    "LT3750EMS#TRPBF",
    "MAX11254ATJ+",
    "25AA256-I/SN",
    "NUCLEO-F303K8",
    "LD1117S33TR",
    "MAX6070AAUT21+T",
    "1-1634200-7",
    "ISR3SAD200",
    "AMDLA4010S-2R2MT",
    "SIR876ADP-T1-GE3",
    "DA2034-ALD",
    "LPS103-M",
    "S1227-66BR",
    "ODROID-C2",
    "7448060814",
    "LP2985-50DBVR",
    "STM32F302C8T6TR",
    "OWA-60E-24",
    "3210237",
    "FTSH-105-05-F-DV-P-TR",
    "MCP7940NT-I/SN",
    "PIC16F88-E/SO",
    "PIC16F88-I/SO",
    "RS-15-12",
    "PMEG2005EH",
    "Radxa Pi Zero SBC",
    "ORG1510-MK05-TR2",
    "LQW15AN9N1H00D",
    "MAX17205G+00E",
    "NC4FDM3-H-BAG",
    "CR95HF-VMD5T",
    "SIM868",
    "LM5122MHX/NOPB",
    "STGIF7CH60TS-L",
    "STM32F303VCT6",
]
batch_request = ManufacturerProductDetailsRequest(manufacturer_product="0ZCK0050FF2E", record_count=1, record_start_position=0, sort={"SortOption": "SortByDigiKeyPartNumber", "Direction": "Ascending", "SortParameterId": 0}, requested_quantity=1, search_options=["ManufacturerPartSearch"])
part_results = digikey.manufacturer_product_details(body=batch_request)

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
