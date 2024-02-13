from typing import Optional

import digikey
import requests
import json
import os
from digikey.v3.productinformation import ManufacturerProductDetailsRequest
import logging


class SearchMpnResult:
    def __init__(self, mpn, is_obsolete, market_price, stock):
        self.mpn = mpn
        self.is_obsolete = is_obsolete
        self.market_price = market_price
        self.stock = stock


class SearchEngineService:
    def __init__(self):
        os.environ['DIGIKEY_CLIENT_ID'] = 'uFbyuoadeIp6BG1MDP5xVxZaYLgweyBL'
        os.environ['DIGIKEY_CLIENT_SECRET'] = 'CmNER7ConcrSIfLE'
        os.environ['DIGIKEY_CLIENT_SANDBOX'] = 'False'
        os.environ['DIGIKEY_STORAGE_PATH'] = "../cache"
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        digikey_logger = logging.getLogger('digikey')
        digikey_logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        digikey_logger.addHandler(handler)


    def search_by_mpn(self, mpn, filename) -> SearchMpnResult:
        octopart_result = self.search_by_mpn_octopart(mpn)
        digikey_result = self.search_by_mpn_digikey(mpn)

        print(
            f"For mpn: {mpn}, octopart: {octopart_result}, digikey: {octopart_result}")

        estimate_price = None
        if octopart_result.market_price is None and digikey_result.market_price is not None:
            estimate_price = digikey_result.market_price
        if digikey_result.market_price is None and octopart_result.market_price is not None:
            estimate_price = octopart_result.market_price
        if octopart_result.market_price is not None and digikey_result.market_price is not None:
            estimate_price = min(octopart_result.market_price, digikey_result.market_price)

        is_obsolete = octopart_result.is_obsolete and digikey_result.is_obsolete
        stock = (digikey_result.stock + octopart_result.stock) // 2

        return SearchMpnResult(mpn=mpn, market_price=estimate_price, is_obsolete=is_obsolete, stock=stock)


    def search_by_mpn_digikey(self, mpn) -> Optional[SearchMpnResult]:
        print("searching by mpn for digikey : ", mpn)

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

        unit_price = results[0].get("unit_price", 0)
        is_obsolete = results[0].get("obsolete", False)
        quantity_available = results[0].get("quantity_available", 0)

        if unit_price <= 0 and quantity_available <= 0:
            print(f"No results for partId {mpn}")
            return None

        return SearchMpnResult(mpn=mpn, market_price=unit_price, is_obsolete=is_obsolete, stock=quantity_available)


    def search_by_mpn_octopart(self, mpn) -> Optional[SearchMpnResult]:
        print("searching by mpn for octopart : ", mpn)
        BEARER_TOKEN_OCTOPART = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjA5NzI5QTkyRDU0RDlERjIyRDQzMENBMjNDNkI4QjJFIiwidHlwIjoiYXQrand0In0.eyJuYmYiOjE3MDc2NjczODgsImV4cCI6MTcwNzc1Mzc4OCwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5uZXhhci5jb20iLCJjbGllbnRfaWQiOiIwMGI1MjJiYS1iNTA1LTQxYzEtOGJhOC02ZDljYzgyNDQ1NWEiLCJzdWIiOiJGODY3NzFGQS00Qjg0LTRDNDEtOUNFMi1GQUQwQjM5QTEyOUEiLCJhdXRoX3RpbWUiOjE3MDc2NjczNTgsImlkcCI6ImxvY2FsIiwicHJpdmF0ZV9jbGFpbXNfaWQiOiIyZmQ5NmMzZS05NDhlLTQ1YTUtYmRlNC00NDE3NjczZjc2MjYiLCJwcml2YXRlX2NsYWltc19zZWNyZXQiOiJYNTVJbVBSVGk3c1kwN1o3SThub24wbHBUbWttbnVmYjF0MEMrQ2lqWWxnPSIsImp0aSI6IjgwNjREQzcxRTJDQzhGRDhFQUIzQTRBNERGOTgwMjUxIiwic2lkIjoiMTUwMDlBODg1M0ZEN0FENDQwNDFFODRGMDMzQTY3QjUiLCJpYXQiOjE3MDc2NjczODgsInNjb3BlIjpbIm9wZW5pZCIsInVzZXIuYWNjZXNzIiwicHJvZmlsZSIsImVtYWlsIiwidXNlci5kZXRhaWxzIiwic3VwcGx5LmRvbWFpbiIsImRlc2lnbi5kb21haW4iXSwiYW1yIjpbInB3ZCJdfQ.k42iQUnww3B6n444KSY2hWzjS40seLDdHDoQ7e8njWHBaRHAMb7CkhiHxbkLhCD3VIGZBYPGjrqmGnpvkNgvV1VAcrPNRRZharQRtQxLQNie1VzAJBDOBAeFtYZquL09PaVjJ6Unh471Aguri4N_5YnNYnrwbWn9iCN_suIlo3HxYiYOZPKMqZzKrJ6xXIoVbXMyCjomlEbWe-yfNuoKHjdXpkm-V5olg1-5P9CXxhpw1PTvomyuRm4MUBIu9you75aJRnwBxrMsE1XLlo0LCozwPITMiXa_agKRHWl8FZ-L8czf3xaBUecvw4qCY6q19qWXd1PFpuz2ZP50cfg4YA"
        API_URL_OCTOPART = "https://api.nexar.com/graphql"
        HEADERS_OCTOPART = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BEARER_TOKEN_OCTOPART}"
        }

        is_obsolete = False
        market_price = None

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
                    stock = results.get("totalAvail", 0)
                    median_price = results[0].get("part", {}).get("medianPrice1000", None)
                    if median_price is not None:
                        converted_median_price = median_price.get("convertedPrice", None)
                        print(f"converted_median_price: {converted_median_price}")
                        print(f"median_price: {median_price}")
                        if converted_median_price is not None and converted_median_price > 0:
                            market_price = converted_median_price

                        if median_price is not None and median_price > 0:
                            market_price = median_price

                    sellers = results[0].get("part", {}).get("sellers", [])
                    sellers_authorized = [seller for seller in sellers if seller.get("isAuthorized", False)]
                    number_of_prices = 0
                    total_converted_price = 0

                    if len(sellers_authorized) <= 0:
                        print("no authorized sellers")
                        is_obsolete = True
                    else:
                        # We only use authorized sellers
                        sellers = sellers_authorized

                    for seller in sellers:
                        seller_offers = seller.get("offers", [])
                        if len(seller_offers) > 0:
                            seller_prices = seller_offers[0].get("prices", [])
                            total_converted_price += sum(item['convertedPrice'] for item in seller_prices)
                            number_of_prices += len(seller_prices)

                    if number_of_prices > 0:
                        market_price = total_converted_price / number_of_prices

                    return SearchMpnResult(mpn=mpn, market_price=market_price, stock=stock, is_obsolete=is_obsolete)
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
