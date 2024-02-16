import datetime

from src.services.OctopartScrapperService import ScrapperResult, ResponseStatut
from src.utils.formule import State
import pandas as pd
import regex as re


class InvalidData(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        self.message = message


class DataTransformer(object):

    @classmethod
    def transform(cls, lead_time_in_day, fabrication_statut: State, stock_mondiale, stock_variaton, date_code,
                  stock_vendeur, prix_moyen_marche, scrapperResult: ScrapperResult):
        print(scrapperResult.responseStatut.name)
        if (scrapperResult.responseStatut.value != ResponseStatut.RefFounded.value):
            raise InvalidData("Les données scrappées ne sont pas utilisable")
        cls.__verifyLeadTime(lead_time_in_day)
        cls.__verifyDateCode(date_code)

        return cls.__transformResultInDataFrame(lead_time_in_day, fabrication_statut, stock_mondiale, stock_variaton,
                                         date_code, stock_vendeur, prix_moyen_marche, scrapperResult)

    @classmethod
    def __convert_dateCode_to_weeks(cls, dateCode_str):
        def __calculate_weeks_elapsed(dateCode):
            current_year = datetime.datetime.now().year
            current_week = datetime.datetime.now().isocalendar()[1]

            if dateCode == '-1':
                return None
            elif '+' in dateCode:
                year = 2000 + int(dateCode.replace('+', ''))
                weeks_elapsed = (current_year - year) * 52
            else:
                year = int('20' + dateCode[:2])
                week = int(dateCode[2:])
                weeks_elapsed = (current_year - year) * 52 + (current_week - week)

            return weeks_elapsed

        # Séparer la chaîne en plusieurs dateCodes et calculer les semaines écoulées pour chacun
        dateCodes = str(dateCode_str).split()
        for i,dc in enumerate(dateCodes):
            if len(dc) == 2:
                dateCodes[i] = dc+"+"
        weeks_list = [__calculate_weeks_elapsed(dc) for dc in dateCodes]

        # Filtrer None et calculer la moyenne
        weeks_list = [week for week in weeks_list if week is not None]
        if len(weeks_list) > 0:
            return sum(weeks_list) / len(weeks_list)
        else:
            return None

    @classmethod
    def __verifyLeadTime(cls, lead_time_in_day):
        if (lead_time_in_day == None or lead_time_in_day < 0):
            raise InvalidData("Le lead_time n'est pas valide")
        # pattern = pattern = r'^\d{2}(?:\d{2}|\+)$'
        # if(re.match(pattern, lead_time_in_day) == None):
        #    raise InvalidData("Le lead_time n'est pas valide")

    @classmethod
    def __verifyDateCode(cls, date_code: str):
        dates_codes = date_code.replace("+","+ ").split(" ")
        pattern = pattern = r'^\d{2}(?:\d{2}|\+)$'
        for dc in dates_codes:
            if(len(dc) == 2):
                dc = dc+"+"
            if (re.match(pattern, dc) == None):
                raise InvalidData("Le lead_time n'est pas valide")
    @classmethod
    def __transformResultInDataFrame(cls, lead_time_in_day, fabrication_statut, stock_mondiale, stock_variaton,
                                     date_code, stock_vendeur,prix_moyen_marche, scrapperResult: ScrapperResult):

        map_cycle_vie = {
            'INCONNUE': -1,
            'NEW': 0,
            'PRODUCTION': 0,
            'NRND': 1,
            'EOL': 2,
            'OBSOLETE': 2
        }

        vendors = '4 Star Electronics;A.E. Petsche;AAA CHIPS;Abacus Technologies;ACDS;Ace Hardware;Acme Tools;Adafruit Industries;ADAJUSA;Adimpex;Advanced Wire & Cable;AFIOS Engineering;AGS Devices;AiPCBA;Air Electro;Airline Hydraulics;ALEXANDER BÜRKLE;All System Electronics;Allchips;ALLICDATA ELECTRONICS;Alpine Electronics;Amar Radio Corporation;Ameya360;Amphenol Cables on Demand;Amphenol LTW;Antdic Electronics;Approved Optics;Arcadian;ARCEL Power Electronics;Ariat Technology Limited;Armbar Industries;Arrow Electronics;Arrow.cn;ASIA Components;Asourcing Electronics Ltd.;Astrosystems;Atakel Electronics;Authorized Procurement Solutions;Autotech Controls;Avnet;Aztech;Back To Earth Surplus;Balluff Inc.;BatteryGuy;Bearing King;Benchmark Connector Corporation;Benley Electronics;Berger & Schroeter;Best Source;BidChips;BiPOM Electronics;Bisco;Bison Technologies;Bitfoic;Boersig;Bohrer;Boss Manufacturing Company;Bravo Electro Components;Brevan Electronics;Briocean Technology Co.,Ltd;Brydge;BTC Electronics;Burklin Elektronik;C Plus Electronics;Cables Direct;ce consumer electronic GmbH;Chanhon Technology Ltd.;Chief Enterprises;Chip 1 Exchange;Chip One Stop;Chip One Stop Global;Chipdigger;Chipmh;Chips Find;Chipsmall Limited;Chromeon;Classic Components;Coast Pneumatics;Coilcraft Direct;Comet Electronics;Commtes;COMPARTA;Compona;Component Distributors Inc.;Component Dynamics;Component Search;Component Sense;Component Stockers USA;ComSIT Distribution GmbH;Conrad;CoreStaff;CUI Devices Direct;CustomConnectorKits;CXDA Electronics;Cynergy;Cytech Systems;Dachs;Dan Réseaux;Darrah Electric Company;DB Lectro;DB Roberts;DComponents;Decca Corp;Demsay Elektronik;Digi-ic_SMART PIONEER;DigiKey;DigiKey Marketplace;Direct Components;Distrelec;DRex Electronics;Eagle MRO;Easev;Eastek;EBV Elektronik;Ecomal;Edge Electronics;EIS COMPONENTS;Elcom Components;Electram;Electro Sonic;Electronic Stock;Electronic Supply;ElectroShield;element14 APAC;Ellison Electronics Ltd.;Elta;Encitech;Epart123;EPS Global;EQUINSA;Ermec;ErreBi Group;Esaler Electronic;Euro-Tech;EUROPOWER;EVE;EVERSTAR DATA ENTERPRISES;Fairview Microwave;Famous Connections;FantastIC Sourcing;Farnell;FDH Electronics;FEI INC;FENCO;Fiber Instruments Sales;Flame Enterprises;Flip Electronics (Authorized);Flip Electronics (Recertified);Florida Circuit;Flyking;FORGEFIX;Freelance Electronics;Future Electronics;Galco;Geefook;Golledge;GreenChips;GreenTree Electronics;Haeger;Halfin;Hawk Electronics;Heilind Electronics;Heilind Europe;Heisener Electronics;HeiYo Trading Co.,Ltd.;HENGJI TIAN WEI TECHNOLOGY LIMITED;Henskes;Heqing Electronics;Hisco;HK Feilidi Electronic Co Limited;Home Depot;Homevision;Honeng Elec.;HSMELECT TECHNOLOGY CO., LIMITED;Hughes Peters;Hyper Source Electronics;IBS Electronics;IC Components Ltd.;iComTech;ICPartonline;ICSOLE;ICSOSO Electronics Company Limited;IEC Supply;IGBT.US;IndustrialeMart;Interstate Connecting Components;iodParts Technologies Inc.;ISC Semi;J2 Sourcing;J3;Jak Electronics;Jameco;Jinrongda Electronics Co. Ltd.;Kaian Technology Co., Limited;Kempston Controls;Kepictronics;Klychip;KnorrTec;Kruse;L-com;Lansheng IC;LCSC;LightChip;Lingto Electronic Ltd.;Livingston & Haven;Lixinc;LJR Electronics;LKR;Lotson Electronic;LTE Elektronik;LTL Group;Lucentia Tech;Machine Compare;Manco;March Electronics;March Technology;Marine Air Supply;Maritex;Markertek;Master Electronics;MASTERS;materialboerse.de;MBH Industries;Mercury Tool;MICRO BIT;Microchip;Microchip USA;Micros;Microwave Components, LLC;Midan Electronics;Misumi USA;Mlccbase Electronics Technology Co Ltd;Mobius Materials;Modulus Dynamics;Monolithic Power Systems;Monroe Aerospace;Morrihan;MOSTELEC TECHNOLOGY(HK) LIMITED;Mouser;MRO Stop;MRO Supply;MRO-PT;Multiconn;NAC Semi;NCD.IO;NEP Electronics;NetSight One;NetSource Technology;New Yorker Electronics;Newark;NewYang;Nexxon Inc. (USA);North Star Micro;NY-Components;Oemstron Technology Co. Ltd.;OKdo;Omega Fusibili S.p.a.;Omnical;OMO Electronic Components;Onlinecomponents.com;Origin Data Global Limited;P+C Schwick;Pan Pacific Electronics;Pasternack;PCB Cart;PCB Electronics;PCX;PDI Works;Peerless Electronics;PEI-Genesis;PLC Direct;PlusOptic;PNEDA Technology Co., Ltd.;PolyPhaser;Powell Electronics;Power and Signal Group;Proax Technologies Ltd;ProConnecting;PROTON-ELECTROTEX;PSC Electronics;PUI;Quail Electronics;QUARKTWIN TECHNOLOGY LTD;Quattro Technology Co.,Ltd;Quest;Quotebeam;Rapid Electronics;RC Electronics;REC Connectors;Renesas;Renesas Electronics America;Resion;RFMW;Richard Electronics;Richardson RFPD;Robosynatics;RobotShop;Rochester Electronics;Ronglianxing Technology;Rotakorn;RS;RS (Formerly Allied Electronics);RS APAC;RS Components - Supplier Marketing;RS Components Australia;RS Components Russia;Run Hong Electronics;Rutronik;RX Electronics Limited;RYX Electronic (HK) Limited;Sager Electronics;Sager Power Systems;Samtec;SB Components;Schukat;Schwaiger;SemiconductorPLUS;Semicontronic;Sensible Micro;Sferaco;Shenzhen Glow Technology Co., Ltd;Shortec Electronics;SI Electronics;Sierra IC;Simcona Electronics;SiTime Direct;Sky-chips Co., Ltd.;Skyworks Direct;Smith & Associates;SOFRAGRAF;SOL-EXPERT;Sourceability;Sourcengine;South Electronics;Space Coast Electronics;Spacer Distribution;SRD Solutions;Standard Electric Supply Co.;State Motor and Control Solutions;Steven Engineering;Sudarrshan Tech Services;Summit Electronics;Suntronic;Suntsu Electronics;Symmetry Electronics;TE Store;Technoline;Techship AB;TecNoticias Electronic Components;Testco;TestEquity;Texas Instruments;TH NEON-EC;Thermo Electric Devices;TLC Electronics;TME;TNR TECHNICAL;Toby Electronics;TodayComponents;Tomark Electronics Ltd UK;Touchstone Systems;TransparentC;Transtector;TRC Electronics;TSI Solutions;TTI;TTI Asia;TTI Europe;Ulti-Mate Connector;Utmel Electronic;VCT Technology;Venkel;Verical;Viczone;Vigor;Vital Electronics UK;VNN Services;Vokel;Voyager Components;Walker Industrial;Waytek;Wes Garde;Williams Automation;Win Source;Winshare;WIZnet Germany;WKK;Wolf Automation;Worldway Electronics;WorldwideIC;WPG Americas;WPG EMEA B.V;Wylex;XingHuan International;XINSHOP ELECTRONICS CO.,LTD.;XINVRY;XScomponents;You We Technology;Zahnriemen;Zheng Da Industrial;ZHIWEI ROBOTICS;Zoro;Zoro UK;ZTZ Technology Limited;'.split(
            ";")[:-1]

        newColumns = []

        for i in range(0, len(vendors)):
            newColumns.append("VENDEUR_NAME_" + vendors[i])
            newColumns.append("VENDEUR_PRICE_" + vendors[i])
            newColumns.append("VENDEUR_STOCK_" + vendors[i])

        best_amount = -1
        best_ecart = -1
        correctAmountPrice = [{"amount": -1, "price": -1} for x in range(0, len(scrapperResult.sellers))]
        correctSellerIndex = []

        for i, seller in enumerate(scrapperResult.sellers):
            for amount in seller["prices"]:
                if amount <= stock_vendeur:
                    correctAmountPrice[i]["amount"] = amount
                    correctAmountPrice[i]["price"] = seller["prices"][amount]
                    if best_amount == -1:
                        best_ecart = stock_vendeur - amount
                        best_amount = amount
                    elif best_ecart > (stock_vendeur - amount):
                        best_ecart = stock_vendeur - amount
                        best_amount = amount

        sommeAverage = 0
        numberOfSellerOk = 0

        for i, elt in enumerate(correctAmountPrice):
            if elt["amount"] == best_amount:
                sommeAverage += elt["price"]
                numberOfSellerOk += 1
                correctSellerIndex.append(i)

        average = sommeAverage / numberOfSellerOk

        object = {
            "REFERENCE": scrapperResult.ref,
            "LEAD_TIME": lead_time_in_day,
            "STATUT_FABRICANT": fabrication_statut,
            "STOCK_MONDIALE": stock_mondiale,
            "EVOLUTION_STOCK_3_MOIS": stock_variaton,
            "QUANTITE_PRIX": best_amount,
            "DATE_CODE": cls.__convert_dateCode_to_weeks(date_code.replace("+","+ ")),
            "PRIX_MARCHE": prix_moyen_marche,
            "STOCK_VENDEUR": stock_vendeur,
        }

        if(scrapperResult.isOnlyBroker):
            object["IS_ONLY_BROKER"] = 1
        else:
            object["IS_ONLY_BROKER"] = 0

        for column in newColumns:
            object[column] = 0

        for index in correctSellerIndex:
            vendor = scrapperResult.sellers[index]
            object["VENDEUR_NAME_" + vendor["name"]] = 1
            object["VENDEUR_PRICE_" + vendor["name"]] = correctAmountPrice[index]["price"]
            object["VENDEUR_STOCK_" + vendor["name"]] = correctAmountPrice[index]["amount"]

        df = pd.DataFrame([object])

        def labelEncodeStatut(value: State):
            if value == State.FABRICATION:
                return map_cycle_vie["PRODUCTION"]
            if value == State.NRND:
                return map_cycle_vie["NRND"]
            if value == State.OBSOLETE:
                return map_cycle_vie["OBSOLETE"]

        df["STATUT_FABRICANT"].fillna("INCONNUE", inplace=True)
        df["LEAD_TIME"].fillna(-1, inplace=True)
        df["EVOLUTION_STOCK_3_MOIS"].fillna(0, inplace=True)
        df["DATE_CODE"].fillna(-1, inplace=True)

        df["STATUT_FABRICANT"] = df["STATUT_FABRICANT"].map(labelEncodeStatut)

        df = df.drop("REFERENCE", axis=1)


        return df
