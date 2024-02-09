import requests
import json
from datetime import datetime

# Initialize variables
parts_ids = [
    "ME310G1WW03T040400", "SX1301IMLTRC", "WL1801MODGBMOCR", "EC25EUXGR-128-SGNS", "MCIMX6Y2CVM08AB",
    "AS4C128M16D3LC-12BCN", "EMMC04G-M627-X03U", "SX1302IMLTRT", "DTE4048S48", "SMI6B-12-4-P6-C1", "MC7304_1102554",
    "SX1250IMLTRT", "SX1257IWLTRT", "TPS27081ADDCR", "SMI5-5-V-I38-C11", "NEO-7N-0", "ICE40HX1K_VQ100",
    "LPB-7-27-5N", "RSF-908.500-13000-3030-TR-NS1", "MC7430_1102477", "PT-PSE104GO-30-EU", "LAN8720Ai-CP-TR-ABC",
    "LAN8720Ai-CP", "LAN8720Ai-CP-TR", "OA-868M06-NF", "RFPA0133TR7", "STM32F103RET6TR", "TPS23753APW",
    "RSF-925.000-6000-3030-TR", "MC7354_1102581", "TYS50402R2N-10", "SX1239IMLTRT", "161323 RAPC712BK",
    "NT2016SA 32MHz END4263A", "SVC220B445N276-0", "TWFCB-915M26-C21M45-N03", "SiT8009BI-32-33S-133.333",
    "B39871B3717U410", "T521X227M016ATE050", "BD9D300MUV", "B39921B3728U410", "WFH24A0915FE", "B39871B3430U410",
    "331171302035", "HDC1080DMBR", "TW61-12-5L2-036-Rev A", "AF2C-P-40-G", "LQW18AN8N7C80D",
    "597-7701-507F SML-020MVTT86", "7-188275-8", "SN74AVC4T245RSVR", "615008137421", "RFSW1012", "RP500N121A-TR-FE",
    "MIC2005-1.2YM6", "ZLDO1117G33TA", "SG-3031CM : X1B000391000116", "B39921B4301F210", "LQW18AN10NG00D",
    "B39871B3717U410", "B39911B5322U410", "W3012", "482040001", "EEEFT1H331AP", "SiP32408DNP-T1-GE4",
    "CM7V-T1A-32.768KHZ-12.5PF-20PPM-TA-QC", "CM7V-T1A-LowESR-32.768KHZ-12.5PF-20-TA-QC", "ASFLMB-133.333MHZ-LR",
    "B39871B3440U410", "93LC46BT-I/OT", "2072350100", "W25Q16JVSSIQ", "GSC3F-LPX-7989", "824013", "B39871B2674P810",
    "74VHC125MTCX", "R1180Q121B-TR-FE", "STP390180060S", "SX1276LM1CAS", "WFC30B0924FF", "0900BL15C050E",
    "RClamp2504N.TCT", "TB2932HQ", "RFWD312.5CCLT-32.768KHz", "0603HP-3N3XGLU", "BKP1005EM221-T", "LMV722MM/NOPB",
    "LQW15AN4N7C00D", "LQW18AN13NJ80D", "PD-9501GO-48VDC", "615032243321", "L17H2110130", "LQW15AN2N7B00D", "TA0775A",
    "O 4.0-JO75-B-3.3-2-T1-LF", "SS10P6-M3/86A", "GDH08STR04 / 1-1571983-1", "SDSDQ-4096", "SX1276JM1CAS",
    "RFW39BCL1-24MHz 40 Ohms max", "RP103Q331B", "TSC2005IYZL", "43045-1001", "43045-0401", "CD74HC4016M",
    "MLX43045-0601", "LM4040C25IDBZ", "MLG1005S1N5BT000", "FH12A-40S-0.5SH(55)", "0387", "LQW15AN13NG00D",
    "ADSP-BF561SKBCZ-6A", "SMBJ7.5CA", "MVS0608-02", "PCF0805-13-10KBT1", "ZXMN6A07Z", "RN5RL33AA-TR-F",
    "PCF0805-13-1K-B", "BCAP0025 P270 T01", "BI-1S (V0)", "R1224N502E-F", "Q 12,0-JXS32-12-10/10-LF", "ST715MR",
    "16-DCLIP-1", "TPA0211DGN", "WF871L0433CD", "TPSC686K016R0200", "AS213-92LF", "DMN3150LW", "43045-0213",
    "TFP410PAP", "MLG1005S6N2ST000", "SKY13453-385LF", "SSAJ120100", "RC0603FR-074K7L", "NC7SZ14P5X", "7447841",
    "LQG15HN8N2J02D", "BCP69T1G", "L-07C3N9SV6T", "SPH0641LM4H-1", "BSS84AK", "742 792 640", "CRCW0402392KFKED",
    "RC0603FR-071K8L", "QUARZ6331 TSX-3225 16.000000MHz 16.0 +10.0-10.0",
    "QUARZ6498 TSX-3225 32.000000MHz 16.0 +10.0-10.0", "RC0402FR-071M5L", "ESDA6V1-4BC6", "MBR230LSFT1G",
    "cga2b2c0g1h060dt0y0f", "3021008"
]
not_found_part_ids = []
invalid_response_part_ids = []

API_URL = "https://api.nexar.com/graphql"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjA5NzI5QTkyRDU0RDlERjIyRDQzMENBMjNDNkI4QjJFIiwidHlwIjoiYXQrand0In0.eyJuYmYiOjE3MDc0NjQ3NzUsImV4cCI6MTcwNzU1MTE3NSwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5uZXhhci5jb20iLCJjbGllbnRfaWQiOiJlYmE0OWY0NS0yMWVjLTRkNzQtYTMzNS0yYzkwMTU5MGZiY2UiLCJzdWIiOiJFQzg4QTUzQi01MkEyLTRGRTItQjJBNy0zQjJBM0Q4N0JCOTYiLCJhdXRoX3RpbWUiOjE3MDc0NjQ3NDYsImlkcCI6ImxvY2FsIiwicHJpdmF0ZV9jbGFpbXNfaWQiOiJjYmQ0ZGZiNC0zMDhkLTQ0YmUtODU4Mi0yNzVmZjEzMWMyNzEiLCJwcml2YXRlX2NsYWltc19zZWNyZXQiOiJySDgvYnYwM3c5UXQ2Tk9EQll1YXZSMGVkNXNrdTRWeXNHR2xyOFNWWXUwPSIsImp0aSI6IjE3M0ZDQUYyRkNFQ0E1QjgwMTdCNjY4NThGM0M2MTAxIiwic2lkIjoiMTFBNEIwQjUxOEQ3MDk1MjhERTNBQTgwRjg2MkI5NjAiLCJpYXQiOjE3MDc0NjQ3NzUsInNjb3BlIjpbIm9wZW5pZCIsInVzZXIuYWNjZXNzIiwicHJvZmlsZSIsImVtYWlsIiwidXNlci5kZXRhaWxzIiwic3VwcGx5LmRvbWFpbiIsImRlc2lnbi5kb21haW4iXSwiYW1yIjpbInB3ZCJdfQ.Pt2KFB_oUT0wqPcYWVGcv8K1ksoXPtOkF9HL-Dns_hqtuNYRxxp7N9d2FeJBSSjoxFc1I8BK-MOZr3FPc3U8kdK-mUGU5io-os1GJ-DF0P9MNDTChZHjT4uStTvMTyrvlk_1v-6VQXJe3bXXx3MGq1TboTja6Il2n5Ma2Qbb_94yhT8WIRIa_HLHLIS9nHlD_Qx8OAQMryc4nOJ_wxMVzfQtZzlvGJG9RZLrnVpchZt9tpCsMrUT8vEtNaNAREUj6dBP6mDxW9OEk2wPWH6ia5UB-yAwhuW2ozmM35j2x3WqDLWabURWN0hm82NXKxiDWekIWfXAe6m9NjQf3ki8XQ"
}

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"./output/results_{timestamp}.json"
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
