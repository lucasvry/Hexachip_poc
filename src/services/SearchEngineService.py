from typing import Optional

import requests
import json
import os
import digikey
from digikey.v3.productinformation import ManufacturerProductDetailsRequest


class SearchEngineService:
    def __init__(self):
        os.environ['DIGIKEY_CLIENT_ID'] = 'uFbyuoadeIp6BG1MDP5xVxZaYLgweyBL'
        os.environ['DIGIKEY_CLIENT_SECRET'] = 'CmNER7ConcrSIfLE'
        os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
        os.environ['DIGIKEY_STORAGE_PATH'] = "../cache"

    def search_price_by_mpn(self, mpn, filename):
        octopart_price = self.search_price_by_mpn_octopart(mpn)
        digikey_price = self.search_price_by_mpn_digikey(mpn)

        with open(filename, "r+") as file:
            existing_data = json.load(file)
            existing_data.append({
                "mpn": mpn,
                "octopart_price": octopart_price,
                "digikey_price": digikey_price
            })
            file.seek(0)
            json.dump(existing_data, file)

        print(f"For mpn: {mpn}, octopart price: {octopart_price}, digikey price: {digikey_price}")

        if octopart_price is None and digikey_price is not None:
            return octopart_price
        if digikey_price is None and octopart_price is not None:
            return octopart_price
        if digikey_price is None and octopart_price is None:
            return None

        return min(digikey_price, octopart_price)

    def search_price_by_mpn_digikey(self, mpn) -> Optional[float]:
        os.environ['DIGIKEY_CLIENT_ID'] = 'uFbyuoadeIp6BG1MDP5xVxZaYLgweyBL'
        os.environ['DIGIKEY_CLIENT_SECRET'] = 'CmNER7ConcrSIfLE'
        os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
        os.environ['DIGIKEY_STORAGE_PATH'] = "./cache"

        batch_request = ManufacturerProductDetailsRequest(manufacturer_product=mpn, record_count=1,
                                                          record_start_position=0,
                                                          sort={"SortOption": "SortByDigiKeyPartNumber",
                                                                "Direction": "Ascending", "SortParameterId": 0},
                                                          requested_quantity=1,
                                                          search_options=["ManufacturerPartSearch"])
        data_dict = digikey.manufacturer_product_details(body=batch_request).to_dict()
        results = data_dict.get("product_details")

        if results is None or len(results) <= 0:
            print(f"No results for partId {mpn}")
            return None

        quantity_available = results[0].get("quantity_available", 0)
        unit_price = results[0].get("unit_price", 0)
        if unit_price <= 0 and quantity_available <= 0:
            print(f"No results for partId {mpn}")
            return None
        return unit_price

    def search_price_by_mpn_octopart(self, mpn) -> Optional[float]:
        BEARER_TOKEN_OCTOPART = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjA5NzI5QTkyRDU0RDlERjIyRDQzMENBMjNDNkI4QjJFIiwidHlwIjoiYXQrand0In0.eyJuYmYiOjE3MDc2NjczODgsImV4cCI6MTcwNzc1Mzc4OCwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5uZXhhci5jb20iLCJjbGllbnRfaWQiOiIwMGI1MjJiYS1iNTA1LTQxYzEtOGJhOC02ZDljYzgyNDQ1NWEiLCJzdWIiOiJGODY3NzFGQS00Qjg0LTRDNDEtOUNFMi1GQUQwQjM5QTEyOUEiLCJhdXRoX3RpbWUiOjE3MDc2NjczNTgsImlkcCI6ImxvY2FsIiwicHJpdmF0ZV9jbGFpbXNfaWQiOiIyZmQ5NmMzZS05NDhlLTQ1YTUtYmRlNC00NDE3NjczZjc2MjYiLCJwcml2YXRlX2NsYWltc19zZWNyZXQiOiJYNTVJbVBSVGk3c1kwN1o3SThub24wbHBUbWttbnVmYjF0MEMrQ2lqWWxnPSIsImp0aSI6IjgwNjREQzcxRTJDQzhGRDhFQUIzQTRBNERGOTgwMjUxIiwic2lkIjoiMTUwMDlBODg1M0ZEN0FENDQwNDFFODRGMDMzQTY3QjUiLCJpYXQiOjE3MDc2NjczODgsInNjb3BlIjpbIm9wZW5pZCIsInVzZXIuYWNjZXNzIiwicHJvZmlsZSIsImVtYWlsIiwidXNlci5kZXRhaWxzIiwic3VwcGx5LmRvbWFpbiIsImRlc2lnbi5kb21haW4iXSwiYW1yIjpbInB3ZCJdfQ.k42iQUnww3B6n444KSY2hWzjS40seLDdHDoQ7e8njWHBaRHAMb7CkhiHxbkLhCD3VIGZBYPGjrqmGnpvkNgvV1VAcrPNRRZharQRtQxLQNie1VzAJBDOBAeFtYZquL09PaVjJ6Unh471Aguri4N_5YnNYnrwbWn9iCN_suIlo3HxYiYOZPKMqZzKrJ6xXIoVbXMyCjomlEbWe-yfNuoKHjdXpkm-V5olg1-5P9CXxhpw1PTvomyuRm4MUBIu9you75aJRnwBxrMsE1XLlo0LCozwPITMiXa_agKRHWl8FZ-L8czf3xaBUecvw4qCY6q19qWXd1PFpuz2ZP50cfg4YA"
        API_URL_OCTOPART = "https://api.nexar.com/graphql"
        HEADERS_OCTOPART = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BEARER_TOKEN_OCTOPART}"
        }

        query = {
            "query": f"""query pricingByVolumeLevels {{
                            supSearchMpn(q: "{mpn}", limit: 1, distributorApi: true) {{
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
            response = requests.post(API_URL_OCTOPART, headers=HEADERS_OCTOPART, json=query)
            response.raise_for_status()

            data = response.json()
            results = data.get("data", {}).get("supSearchMpn", {}).get("results", [])

            if results:
                has_results = len(results) > 0
                if has_results:
                    median_price = results[0].get("part", {}).get("medianPrice1000", None)
                    if median_price is not None:
                        converted_median_price = median_price.get("convertedPrice", None)
                        print(f"converted_median_price: {converted_median_price}")
                        print(f"median_price: {median_price}")
                        if converted_median_price is not None and converted_median_price > 0:
                            return converted_median_price

                        if median_price is not None and median_price > 0:
                            return median_price

                    sellers = results[0].get("part", {}).get("sellers", [])
                    sellers_authorized = [seller for seller in sellers if seller.get("isAuthorized", False)]

                    if len(sellers_authorized) <= 0:
                        print("no authorized sellers")

                    number_of_prices = 0
                    total_converted_price = 0
                    for seller in sellers:
                        seller_offers = seller.get("offers", [])
                        if len(seller_offers) > 0:
                            seller_prices = seller_offers[0].get("prices", [])
                            total_converted_price += sum(item['convertedPrice'] for item in seller_prices)
                            number_of_prices += len(seller_prices)

                    if number_of_prices > 0:
                        return total_converted_price / number_of_prices
                    return None
                else:
                    print(f"No results for partId {mpn}")
                    return None
            else:
                print(f"Invalid json for partId {mpn}")
                return None
        except requests.exceptions.HTTPError as e:
            print(f"Invalid JSON response for partId {mpn}: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for partId {mpn}: {e}")
