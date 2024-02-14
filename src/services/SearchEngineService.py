from itertools import chain
from typing import Optional

import digikey
import requests
import json
import os
from digikey.v3.productinformation import ManufacturerProductDetailsRequest
import logging
from dotenv import load_dotenv


class SearchMpnResult:
    def __init__(self, mpn, is_obsolete, market_price, stock):
        self.mpn = mpn
        self.is_obsolete = is_obsolete
        self.market_price = market_price
        self.stock = stock

    def __str__(self):
        return f"{{mpn: {self.mpn}, market_price: {self.market_price}, is_obsolete: {self.is_obsolete}, stock: {self.stock}}}"

    def to_json(self):
        return {
            "mpn": self.mpn,
            "market_price": self.market_price,
            "is_obsolete": self.is_obsolete,
            "stock": self.stock
        }


class SearchEngineService:
    def __init__(self):
        load_dotenv()

        logger = logging.getLogger(__name__)
        # logger.setLevel(logging.DEBUG)

        digikey_logger = logging.getLogger('digikey')
        # digikey_logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        # handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        digikey_logger.addHandler(handler)

    def get_closest_price_octopart(self, quantity, prices):
        closest_price = None
        min_diff = float('inf')
        closest_quantity = None
        for price in prices:
            diff = abs(price.get("quantity", 0) - quantity)
            if diff < min_diff:
                min_diff = diff
                selected_price_value = price.get("convertedPrice", 0)
                closest_price = selected_price_value
                closest_quantity = price.get("quantity", 0)
            elif diff == min_diff and price.get("convertedPrice", 0) < closest_price:
                closest_price = price.get("convertedPrice", 0)
                closest_quantity = price.get("quantity", 0)
        # print(f"[OCTOPART] For quantity: {quantity}, closest price: {closest_price}, closest quantity: {closest_quantity}")
        return closest_price

    def get_closest_price_digikey(self, quantity, prices):
        closest_price = None
        min_diff = float('inf')
        closest_quantity = None
        for price in prices:
            diff = abs(price.get("break_quantity") - quantity)
            selected_price_value = price.get("unit_price")
            if diff < min_diff:
                min_diff = diff
                closest_price = selected_price_value
                closest_quantity = price.get("break_quantity")
            elif diff == min_diff and price.get("unit_price") < closest_price:
                closest_price = selected_price_value
                closest_quantity = price.get("break_quantity")
        # print(f"[DIGIKEY] For quantity: {quantity}, closest price: {closest_price}, closest_quantity: {closest_quantity}")
        return closest_price

    def search_by_mpn(self, mpn, quantity) -> SearchMpnResult:
        octopart_result = self.search_by_mpn_octopart(mpn, quantity)
        digikey_result = self.search_by_mpn_digikey(mpn, quantity)

        print(f"For mpn: {mpn},\n - octopart: {octopart_result},\n - digikey: {digikey_result}")

        if octopart_result is None and digikey_result is None:
            print("For each digikey and octopart, no result found")

        is_octopart_result = octopart_result is not None and octopart_result.market_price is not None
        is_digikey_result = digikey_result is not None and digikey_result.market_price is not None

        estimate_price = None
        is_obsolete = None
        stock = None
        # Case where only octopart has a result
        if is_octopart_result and not is_digikey_result:
            estimate_price = octopart_result.market_price
            is_obsolete = octopart_result.is_obsolete
            stock = octopart_result.stock
        # Case where only digikey has a result
        if not is_octopart_result and is_digikey_result:
            estimate_price = digikey_result.market_price
            is_obsolete = digikey_result.is_obsolete
            stock = digikey_result.stock
        # Case where both octopart and digikey has a result
        if is_octopart_result and is_digikey_result:
            estimate_price = min(octopart_result.market_price, digikey_result.market_price)
            is_obsolete = octopart_result.is_obsolete and digikey_result.is_obsolete
            if digikey_result.stock <= 0:
                # If no stock from digikey, using octopart stock
                stock = octopart_result.stock
            elif octopart_result.stock <= 0:
                # If no stock from octopart but in some in digikey, using digikey stock
                stock = digikey_result.stock
            else:
                # If stock in both, using the average
                stock = (digikey_result.stock + octopart_result.stock) // 2

        return SearchMpnResult(mpn=mpn, market_price=estimate_price, is_obsolete=is_obsolete, stock=stock)

    def search_by_mpn_digikey(self, mpn, quantity) -> Optional[SearchMpnResult]:
        try:
            batch_request = ManufacturerProductDetailsRequest(manufacturer_product=mpn, record_count=1,
                                                              record_start_position=0,
                                                              requested_quantity=1,
                                                              sort={"SortOption": "SortByDigiKeyPartNumber",
                                                                    "Direction": "Ascending", "SortParameterId": 0},
                                                              search_options=["ManufacturerPartSearch"])
            data_dict = digikey.manufacturer_product_details(body=batch_request).to_dict()
            results = data_dict.get("product_details")
            if results is None or (results is not None and len(results) <= 0):
                # print(f"No results for partId {mpn}")
                return None

            market_price = self.get_closest_price_digikey(quantity, results[0].get("standard_pricing", []))
            is_obsolete = results[0].get("obsolete", False)
            quantity_available = results[0].get("quantity_available", 0)

            if market_price <= 0 and quantity_available <= 0:
                # print(f"No results for partId {mpn}")
                return None

            return SearchMpnResult(mpn=mpn, market_price=market_price, is_obsolete=is_obsolete,
                                   stock=quantity_available)
        except Exception as e:
            print(f"Error while fetching data from digikey for partId {mpn}: {e}")
            return None

    def search_by_mpn_octopart(self, mpn, quantity) -> Optional[SearchMpnResult]:
        # print("searching by mpn for octopart : ", mpn)
        octopart_bearer_token = os.getenv("OCTOPART_BEARER_TOKEN")
        octopart_api_url = os.getenv("OCTOPART_API_URL")
        octopart_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {octopart_bearer_token}"
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
            response = requests.post(octopart_api_url, headers=octopart_headers, json=query)
            response.raise_for_status()

            data = response.json()
            results = data.get("data", {}).get("supSearchMpn", {}).get("results", [])
            if results is not None:
                has_results = len(results) > 0
                if has_results:
                    stock = results[0].get("part", {}).get("totalAvail", 0)
                    median_price = results[0].get("part", {}).get("medianPrice1000", None)
                    if median_price is not None:
                        if median_price is not float:
                            median_price = median_price.get("convertedPrice", None)
                        # print(f"median_price: {median_price}")

                        if median_price is not None and median_price > 0:
                            market_price = median_price

                    sellers = results[0].get("part", {}).get("sellers", [])
                    sellers_authorized = [seller for seller in sellers if seller.get("isAuthorized", False)]

                    if len(sellers_authorized) <= 0:
                        # print("no authorized sellers")
                        is_obsolete = True
                    else:
                        # print("using authorized sellers")
                        sellers = sellers_authorized
                    all_prices = list(
                        chain.from_iterable([seller.get("offers", [])[0].get("prices", []) for seller in sellers]))

                    if len(all_prices) > 0:
                        market_price = self.get_closest_price_octopart(quantity, all_prices)
                    res = SearchMpnResult(mpn=mpn, market_price=market_price, stock=stock, is_obsolete=is_obsolete)
                    return res
                else:
                    # print(f"No results for partId {mpn}")
                    return None
            else:
                print(f"Invalid json for partId {mpn}")
                return None
        except requests.exceptions.HTTPError as e:
            print(f"Invalid JSON response for partId {mpn}: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for partId {mpn}: {e}")
