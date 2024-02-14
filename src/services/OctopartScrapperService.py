import time

import requests
from bs4 import BeautifulSoup

from enum import Enum
import json as JSON
from pathlib import Path
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Statut(Enum):
    INCONNU = 0
    PRODUCTION = 1
    NRND = 2
    OBSOLETE = 3

class ResponseStatut(Enum):
    RequestNotStarted = -1
    RefFounded = 0
    RefNotFound = 1
    PriceNotFound = 2


class ScrapperResult:
    def __init__(self):
        self.ref = ""
        self.responseStatut = ResponseStatut.RequestNotStarted
        self.sellers = []
        self.pricesAverage = {}
        self.totalStock = -1
        self.stockVariation = 0
        self.leadTime = 0
        self.status = Statut.INCONNU
        self.isOnlyBroker = False

    @classmethod
    def refNotFound(cls,ref):
        result = cls()
        result.ref = ref
        result.responseStatut = ResponseStatut.RefNotFound
        return result

    @classmethod
    def PriceNotFound(cls,ref):
        result = cls()
        result.ref = ref
        result.responseStatut = ResponseStatut.PriceNotFound
        return result

    @classmethod
    def refFounded(cls,ref, sellers, pricesAverage, totalStock, stockVariation, leadTime, status, isOnlyBroker):
        result = cls()
        result.ref = ref
        result.sellers = sellers
        result.pricesAverage = pricesAverage
        result.totalStock = totalStock
        result.stockVariation = stockVariation
        result.leadTime = leadTime
        result.status = status
        result.isOnlyBroker = isOnlyBroker
        result.responseStatut = ResponseStatut.RefFounded
        return result



class OctopartScrapperService:
    host = "https://octopart.com"
    proxies = {
        'http': 'http://HexaChip:RbQjY6Lc9HtQSis@unblock.oxylabs.io:60000',
        'https': 'http://HexaChip:RbQjY6Lc9HtQSis@unblock.oxylabs.io:60000',
    }
    leadTimeApi = f"{host}/api/v4/internal"
    exchangeRateApi = "https://open.er-api.com/v6/latest/USD"
    search_url = f"{host}/search?q="
    css_selectors = {
        "firstLinkSearch": ".prices-view :first-child .mpn a",
        "variationStock": ".label",
        "status": ".wrap .status",
        "pricesLink": ".currency-see-all a",
        "json": "#__NEXT_DATA__",
        "amountsList": ".pdp-all-breaks-table thead:first-child th.pdp-sort",
        "sellerArray": ".pdp-all-breaks-table",
        "arrayHeader": "thead:first-child h3",
        "authorizedSeller": "thead:first-child + tbody .offerRow",
        "sellerName": ".col-seller",
        "sellerStock": ".col-avail",
        "sellerPrice": "td[data-currency]",
    }

    files = {
        "exchangeRateFile": "./cache/exchangeRateCache.json"
    }

    def __init__(self):
        self.ref = ""

    def find_key_in_dict(self,data, target_key):
        if target_key in data:
            return data[target_key]
        for key, value in data.items():
            if isinstance(value, dict):
                result = self.find_key_in_dict(value, target_key)
                if result is not None:
                    return result
        return None

    def getLeadTime(self):
        responseSearch = requests.request('POST', OctopartScrapperService.leadTimeApi, verify=False, proxies=OctopartScrapperService.proxies, json={
            "operationName": "SpecsViewSearch",
            "variables": {
                "limit": 20,
                "currency": "USD",
                "in_stock_only": True,
                "q": self.ref,
                "start": 0
            },
            "query": "query SpecsViewSearch($currency: String!, $filters: Map, $in_stock_only: Boolean, $limit: Int!, $q: String, $sort: String, $sort_dir: SortDirection, $start: Int) {\n  search(currency: $currency, filters: $filters, in_stock_only: $in_stock_only, limit: $limit, q: $q, sort: $sort, sort_dir: $sort_dir, start: $start) {\n    all_filters {\n      group\n      id\n      name\n      shortname\n      __typename\n    }\n    applied_category {\n      ancestors {\n        id\n        name\n        path\n        __typename\n      }\n      id\n      name\n      path\n      __typename\n    }\n    applied_filters {\n      display_values\n      name\n      shortname\n      values\n      __typename\n    }\n    results {\n      part {\n        _cache_id\n        best_datasheet {\n          url\n          __typename\n        }\n        best_image {\n          url\n          __typename\n        }\n        cad {\n          add_to_library_url\n          footprint_image_url\n          has_3d_model\n          has_altium\n          has_eagle\n          has_kicad\n          has_orcad\n          symbol_image_url\n          __typename\n        }\n        counts\n        estimated_factory_lead_days\n        id\n        manufacturer {\n          id\n          is_verified\n          name\n          __typename\n        }\n        median_price_1000 {\n          _cache_id\n          converted_currency\n          converted_price\n          __typename\n        }\n        mpn\n        sellers {\n          _cache_id\n          company {\n            id\n            __typename\n          }\n          is_authorized\n          offers {\n            _cache_id\n            click_url\n            id\n            inventory_level\n            moq\n            packaging\n            prices {\n              _cache_id\n              conversion_rate\n              converted_currency\n              converted_price\n              currency\n              price\n              quantity\n              __typename\n            }\n            sku\n            updated\n            __typename\n          }\n          __typename\n        }\n        slug\n        specs {\n          attribute {\n            group\n            id\n            name\n            shortname\n            __typename\n          }\n          display_value\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    specs_view_attribute_groups {\n      attributes {\n        group\n        id\n        name\n        shortname\n        __typename\n      }\n      name\n      __typename\n    }\n    suggested_categories {\n      category {\n        id\n        name\n        path\n        __typename\n      }\n      count\n      __typename\n    }\n    suggested_filters {\n      id\n      group\n      name\n      shortname\n      __typename\n    }\n    hits\n    topline_advert_v2 {\n      id\n      part_id\n      seller_id\n      offer_id\n      click_url\n      is_co_op\n      price_breaks\n      text\n      __typename\n    }\n    __typename\n  }\n}\n"
        })
        return self.find_key_in_dict(responseSearch.json(), "results")[0]["part"]["estimated_factory_lead_days"]

    def getExchangesRateForUSD(self):
        exchangeRateFilePath = Path(OctopartScrapperService.files["exchangeRateFile"])
        exchangesRateData = None
        if (not exchangeRateFilePath.exists()):
            exchangesRateResponse = requests.request("GET", OctopartScrapperService.exchangeRateApi).json()
            exchangesRateResponse["requestDate"] = int(time.time())
            with open(exchangeRateFilePath, "w") as f:
                print("write")
                f.write(JSON.dumps(exchangesRateResponse))
            exchangesRateData = exchangesRateResponse
        else:
            with open(exchangeRateFilePath, "r+") as f:
                exchangesRateData = JSON.loads(f.read())
                if (exchangesRateData["requestDate"] < int(time.time()) + 24 * 3600):
                    exchangesRateResponse = requests.request("GET", OctopartScrapperService.exchangeRateApi).json()
                    exchangesRateResponse["requestDate"] = int(time.time())
                    f.seek(0)
                    f.write(JSON.dumps(exchangesRateResponse))
                    f.truncate()
                    exchangesRateData = exchangesRateResponse
        return exchangesRateData["rates"]

    def getPricesAndStock(self, pricesUrl: str):
        exchangesRates = self.getExchangesRateForUSD()
        pricesResponse = requests.request('GET', pricesUrl, verify=False, proxies=OctopartScrapperService.proxies)
        soup = BeautifulSoup(pricesResponse.text, "html.parser")
        amounts = []
        for amount in soup.select(OctopartScrapperService.css_selectors["amountsList"])[1:]:
            amounts.append(int(amount.text.replace(",", "")))

        amountsNumber = len(amounts)
        arrayOfSeller = soup.select(OctopartScrapperService.css_selectors["sellerArray"])
        isOnlyBroker = False
        try:
            isOnlyBroker = not arrayOfSeller[0].select(OctopartScrapperService.css_selectors["arrayHeader"])[0].text == "Authorized Distributors"
        except:
            isOnlyBroker = False
        authorizedSeller = arrayOfSeller[0].select(OctopartScrapperService.css_selectors["authorizedSeller"])

        totalStock = 0
        sellers = []
        for seller in authorizedSeller:
            currentSeller = {}
            name = seller.select(OctopartScrapperService.css_selectors["sellerName"])[0].text
            try:
                stock = int(seller.select(OctopartScrapperService.css_selectors["sellerStock"])[0].text.replace(",", ""))
            except ValueError:
                continue
            currentSeller["name"] = name
            currentSeller["stock"] = stock

            prices = seller.select(OctopartScrapperService.css_selectors["sellerPrice"])
            pricesNumber = len(prices)
            diff = amountsNumber - pricesNumber
            totalStock += stock
            currentSeller["prices"] = {}
            for i in range(diff, amountsNumber):
                currency = prices[i - diff].get("data-currency")
                price = float(prices[i - diff].text)
                if (currency != "USD"):
                    exchangeRate = exchangesRates[currency]
                    price = price / exchangeRate
                currentSeller["prices"][amounts[i]] = price
            sellers.append(currentSeller)
        return (sellers, totalStock, isOnlyBroker)

    def getDataByRef(self, ref: str, showInConsole = False) -> ScrapperResult:
        self.ref = ref
        refFounded = False
        responseSearch = requests.request('GET', OctopartScrapperService.search_url+self.ref, verify=False, proxies=OctopartScrapperService.proxies)
        soup = BeautifulSoup(responseSearch.text, 'html.parser')
        firstLink = soup.select(OctopartScrapperService.css_selectors["firstLinkSearch"])
        if (len(firstLink) < 1):
            print(f"{self.ref} est inconnue !")
            return ScrapperResult.refNotFound(self.ref)
        refFounded = True
        href = firstLink[0].get('href')
        responseData = requests.request('GET', f"{OctopartScrapperService.host}{href}", verify=False, proxies=OctopartScrapperService.proxies)
        soup = BeautifulSoup(responseData.text, 'html.parser')
        stockVariation = None
        try:
            stockVariation = float(soup.select(OctopartScrapperService.css_selectors["variationStock"])[0].text[:-1])
        except IndexError:
            stockVariation = 0
        except ValueError:
            stockVariation = 0

        statusData = soup.select(OctopartScrapperService.css_selectors["status"])
        try:
            pricesUrl = f"{OctopartScrapperService.host}{soup.select(OctopartScrapperService.css_selectors['pricesLink'])[0].get('href')}"
        except:
            return ScrapperResult.refNotFound(self.ref)
        status = Statut.INCONNU
        if (len(statusData) > 0):
            status = statusData[0].text
            if(status.lower() == "production"):
                status = Statut.PRODUCTION
            elif(status.lower() == "nrnd"):
                status = Statut.NRND
            elif(status.lower() == "obsolete"):
                status = Statut.OBSOLETE
            elif(status.lower() == "new"):
                status = Statut.PRODUCTION
            elif(status.lower() == "eol"):
                status = Statut.OBSOLETE
        json = soup.select(OctopartScrapperService.css_selectors["json"])[0].text
        traitedJson = JSON.loads(json)
        totalStockScrapped = None
        try:
            totalStockScrapped = self.find_key_in_dict(traitedJson, "parts_history")[0]["historical_inventory"][-1][
                "total_authorized"]
        except:
            totalStockScrapped = None
        leadTime = None
        try:
            leadTime = self.getLeadTime()
        except TypeError:
            leadTime = None

        sellers, totalStock, isOnlyBroker = self.getPricesAndStock(pricesUrl)
        if (totalStockScrapped != None and stockVariation != None):
            if (
                    totalStockScrapped != totalStock):  # Si le stock calculé est différent du stock scappé, on recaclule la variation
                stockVariation = ((totalStock * (100 + stockVariation)) / totalStockScrapped) - 100
        prices = {}
        pricesAverage = {}

        for seller in sellers:
            if (seller["stock"] > 0):
                for amount in seller["prices"]:
                    if amount not in prices:
                        prices[amount] = [seller["prices"][amount]]
                    else:
                        prices[amount].append(seller["prices"][amount])
        for key in prices:
            pricesAverage[key] = sum(prices[key]) / len(prices[key])

        if (showInConsole):
            print(f"Pour la référence: {ref}:")
            print(f"Prix moyens pour: ")
            for key in pricesAverage:
                print(f"- {key} = {pricesAverage[key]}$")
            print(f"Stock mondial de: {totalStock}")
            print(f"Variation de stock de: {stockVariation}")
            print("Cycle de vie: ", end="")
            if (status == Statut.INCONNU):
                print("INCONNU")
            else:
                print(status)
            print("LeadTime: ", end="")
            if (leadTime == None):
                print("INCONNU")
            else:
                print(f"{leadTime} jours")

            print("\n")
        return ScrapperResult.refFounded(self.ref, sellers,pricesAverage,totalStock,stockVariation,leadTime,status,isOnlyBroker)
