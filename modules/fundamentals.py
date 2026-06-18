import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime
import pytz
import warnings
import xml.etree.ElementTree as ET
import html as html_lib
import re

BRAPI_TOKEN = st.secrets.get("BRAPI_TOKEN", "iExnKM1xcbQcYL3cNPhPQ3")  # Token gratuito da BRAPI


BDR_TO_US_MAP = {
    'A1AP34': 'AAP',
    'A1DC34': 'ADC',
    'A1DI34': 'ADI',
    'A1EP34': 'AEP',
    'A1ES34': 'AES',
    'A1FL34': 'AFL',
    'A1IV34': 'AIV',
    'A1KA34': 'AKAM',
    'A1LB34': 'ALB',
    'A1LK34': 'ALK',
    'A1LL34': 'BFH',
    'A1MD34': 'AMD',
    'A1MP34': 'AMP',
    'A1MT34': 'AMAT',
    'A1NE34': 'ANET',
    'A1PH34': 'APH',
    'A1PL34': 'APLD',
    'A1PO34': 'APO',
    'A1PP34': 'APP',
    'A1RE34': 'ARE',
    'A1RG34': 'ARGX',
    'A1SU34': 'AIZ',
    'A1TH34': 'ATHM',
    'A1VB34': 'AVB',
    'A1WK34': 'AWK',
    'A1ZN34': 'AZN',
    'A2MB34': 'AMBA',
    'A2RR34': 'ARWR',
    'A2RW34': 'ARW',
    'A2SO34': 'ASO',
    'A2XO34': 'AXON',
    'A2ZT34': 'AZTA',
    'AADA39': 'AADA',
    'AALL34': 'AAL',
    'AAPL34': 'AAPL',
    'ABBV34': 'ABBV',
    'ABGD39': 'ABGD',
    'ABTT34': 'ABT',
    'ABUD34': 'BUD',
    'ACNB34': 'ACN',
    'ACWX39': 'ACWX',
    'ADBE34': 'ADBE',
    'AIRB34': 'ABNB',
    'AMGN34': 'AMGN',
    'AMZO34': 'AMZN',
    'APTV34': 'APTV',
    'ARGT39': 'ARGT',
    'ARMT34': 'MT',
    'ARNC34': 'HWM',
    'ASML34': 'ASML',
    'ATTB34': 'T',
    'AURA33': 'ORA',
    'AVGO34': 'AVGO',
    'AWII34': 'AWI',
    'AXPB34': 'AXP',
    'B1AM34': 'BN',
    'B1AX34': 'BAX',
    'B1BW34': 'BBWI',
    'B1CS34': 'BCS',
    'B1FC34': 'BF-B',
    'B1IL34': 'BILI',
    'B1LL34': 'BALL',
    'B1MR34': 'BMRN',
    'B1NT34': 'BNTX',
    'B1PP34': 'BP',
    'B1RF34': 'BR',
    'B1SA34': 'BSAC',
    'B1TI34': 'BTI',
    'B2AH34': 'BAH',
    'B2HI34': 'BILL',
    'B2LN34': 'BL',
    'B2MB34': 'BMBL',
    'B2RK34': 'BRKR',
    'B2UR34': 'BURL',
    'B2YN34': 'BYND',
    'BAAX39': 'BAAX',
    'BABA34': 'BABA',
    'BACW39': 'BACW',
    'BAER39': 'BAER',
    'BAGG39': 'BAGG',
    'BAIQ39': 'AIQ',
    'BAOR39': 'BAOR',
    'BARY39': 'BARY',
    'BASK39': 'BASK',
    'BBER39': 'BBER',
    'BBJP39': 'BBJP',
    'BBUG39': 'BBUG',
    'BCAT39': 'BCAT',
    'BCHI39': 'BCHI',
    'BCIR39': 'BCIR',
    'BCLO39': 'BCLO',
    'BCNY39': 'BCNY',
    'BCOM39': 'BCOM',
    'BCPX39': 'BCPX',
    'BCSA34': 'SAN',
    'BCTE39': 'BCTE',
    'BCWV39': 'BCWV',
    'BDVD39': 'BDVD',
    'BDVE39': 'BDVE',
    'BDVY39': 'BDVY',
    'BECH39': 'BECH',
    'BEEM39': 'BEEM',
    'BEFA39': 'BEFA',
    'BEFG39': 'BEFG',
    'BEFV39': 'BEFV',
    'BEGD39': 'BEGD',
    'BEGE39': 'BEGE',
    'BEGU39': 'BEGU',
    'BEIS39': 'BEIS',
    'BEMV39': 'BEMV',
    'BEPP39': 'BEPP',
    'BEPU39': 'BEPU',
    'BERK34': 'BRK-B',
    'BEWA39': 'BEWA',
    'BEWC39': 'BEWC',
    'BEWD39': 'BEWD',
    'BEWG39': 'BEWG',
    'BEWH39': 'BEWH',
    'BEWJ39': 'BEWJ',
    'BEWL39': 'BEWL',
    'BEWP39': 'BEWP',
    'BEWS39': 'BEWS',
    'BEWW39': 'BEWW',
    'BEWY39': 'BEWY',
    'BEWZ39': 'BEWZ',
    'BEZA39': 'BEZA',
    'BEZU39': 'BEZU',
    'BFAV39': 'BFAV',
    'BFLO39': 'BFLO',
    'BFXI39': 'BFXI',
    'BGLC39': 'BGLC',
    'BGOV39': 'BGOV',
    'BGOZ39': 'BGOZ',
    'BGRT39': 'BGRT',
    'BGWH39': 'BGWH',
    'BHEF39': 'BHEF',
    'BHER39': 'BHER',
    'BHVN34': 'BHVN',
    'BHYC39': 'BHYC',
    'BHYG39': 'BHYG',
    'BIAI39': 'BIAI',
    'BIAU39': 'BIAU',
    'BIBB39': 'BIBB',
    'BICL39': 'BICL',
    'BIDU34': 'BIDU',
    'BIEF39': 'BIEF',
    'BIEI39': 'BIEI',
    'BIEM39': 'BIEM',
    'BIEO39': 'BIEO',
    'BIEU39': 'BIEU',
    'BIEV39': 'BIEV',
    'BIGF39': 'BIGF',
    'BIGS39': 'BIGS',
    'BIHE39': 'BIHE',
    'BIHF39': 'BIHF',
    'BIHI39': 'BIHI',
    'BIIB34': 'BIIB',
    'BIJH39': 'BIJH',
    'BIJR39': 'BIJR',
    'BIJS39': 'BIJS',
    'BIJT39': 'BIJT',
    'BILF39': 'BILF',
    'BIPC39': 'BIPC',
    'BITB39': 'BITB',
    'BITO39': 'BITO',
    'BIUS39': 'BIUS',
    'BIVB39': 'BIVB',
    'BIVE39': 'BIVE',
    'BIVW39': 'BIVW',
    'BIWF39': 'BIWF',
    'BIWM39': 'BIWM',
    'BIXG39': 'BIXG',
    'BIXJ39': 'BIXJ',
    'BIXN39': 'BIXN',
    'BIXU39': 'BIXU',
    'BIYE39': 'BIYE',
    'BIYF39': 'BIYF',
    'BIYJ39': 'BIYJ',
    'BIYT39': 'BIYT',
    'BIYW39': 'BIYW',
    'BIYZ39': 'BIYZ',
    'BJQU39': 'JQUA',
    'BKCH39': 'BKCH',
    'BKNG34': 'BKNG',
    'BKWB39': 'BKWB',
    'BKXI39': 'BKXI',
    'BLAK34': 'BLAK',
    'BLBT39': 'BLBT',
    'BLPX39': 'BLPX',
    'BLQD39': 'BLQD',
    'BMTU39': 'BMTU',
    'BMYB34': 'BMYB',
    'BNDA39': 'BNDA',
    'BOAC34': 'BAC',
    'BOEF39': 'BOEF',
    'BOEI34': 'BA',
    'BONY34': 'BK',
    'BOTZ39': 'BOTZ',
    'BOXP34': 'BOXP',
    'BPIC39': 'BPIC',
    'BPVE39': 'BPVE',
    'BQQW39': 'BQQW',
    'BQUA39': 'BQUA',
    'BQYL39': 'BQYL',
    'BSCZ39': 'BSCZ',
    'BSDV39': 'BSDV',
    'BSHV39': 'BSHV',
    'BSHY39': 'BSHY',
    'BSIL39': 'BSIL',
    'BSIZ39': 'BSIZ',
    'BSLV39': 'BSLV',
    'BSOC39': 'BSOC',
    'BSOX39': 'BSOX',
    'BSRE39': 'BSRE',
    'BTFL39': 'BTFL',
    'BTIP39': 'BTIP',
    'BTLT39': 'BTLT',
    'BURA39': 'BURA',
    'BURT39': 'BURT',
    'BUSM39': 'BUSM',
    'BUSR39': 'BUSR',
    'BUTL39': 'BUTL',
    'C1AB34': 'CABO',
    'C1AG34': 'CAG',
    'C1AH34': 'CAH',
    'C1BL34': 'CB',
    'C1BR34': 'CBRE',
    'C1CJ34': 'CCJ',
    'C1CL34': 'CCL',
    'C1CO34': 'COR',
    'C1DN34': 'CDNS',
    'C1FG34': 'CFG',
    'C1GP34': 'CSGP',
    'C1HR34': 'CHRW',
    'C1IC34': 'CI',
    'C1MG34': 'CMG',
    'C1MI34': 'CMI',
    'C1MS34': 'CMS',
    'C1NC34': 'CNC',
    'C1OO34': 'COO',
    'C1PB34': 'CPB',
    'C1RH34': 'CRH',
    'C2AC34': 'CACI',
    'C2CA34': 'KOF',
    'C2GN34': 'CGNX',
    'C2HD34': 'CHDN',
    'C2OI34': 'COIN',
    'C2OL34': 'CIBR',
    'C2OU34': 'COUR',
    'C2RN34': 'CRNC',
    'C2RS34': 'CRSP',
    'C2RW34': 'CRWD',
    'C2ZR34': 'CZR',
    'CAON34': 'CAON',
    'CATP34': 'CAT',
    'CHCM34': 'CHTR',
    'CHDC34': 'CHDC',
    'CHME34': 'CME',
    'CHVX34': 'CVX',
    'CLOV34': 'CLOV',
    'CLXC34': 'CLXC',
    'CNIC34': 'CNIC',
    'COCA34': 'KO',
    'COLG34': 'CL',
    'COPH34': 'COPH',
    'COTY34': 'COTY',
    'COWC34': 'COWC',
    'CPRL34': 'CPRL',
    'CRIN34': 'CRIN',
    'CSCO34': 'CSCO',
    'CSXC34': 'CSXC',
    'CTGP34': 'C',
    'CTSH34': 'CTSH',
    'CVSH34': 'CVSH',
    'D1DG34': 'DDOG',
    'D1EX34': 'DXCM',
    'D1LR34': 'DLR',
    'D1OC34': 'DOCU',
    'D1OW34': 'DOW',
    'D1VN34': 'DVN',
    'D2AR34': 'DAR',
    'D2AS34': 'DASH',
    'D2NL34': 'DNLI',
    'D2OC34': 'DOCS',
    'D2OX34': 'DOX',
    'D2PZ34': 'DPZ',
    'DBAG34': 'DBAG',
    'DDNB34': 'DDNB',
    'DEEC34': 'DE',
    'DEFT31': 'DEFT',
    'DEOP34': 'DEOP',
    'DGCO34': 'DGCO',
    'DHER34': 'DHR',
    'DISB34': 'DIS',
    'DOLL39': 'DOLL',
    'DTCR39': 'DTCR',
    'DUOL34': 'DUOL',
    'DVAI34': 'DVAI',
    'E1CO34': 'EC',
    'E1DU34': 'EDU',
    'E1LV34': 'ELV',
    'E1MN34': 'EMN',
    'E1MR34': 'EMR',
    'E1OG34': 'EOG',
    'E1QN34': 'EQNR',
    'E1RI34': 'ERIC',
    'E1TN34': 'ETN',
    'E1WL34': 'EW',
    'E2AG34': 'EXP',
    'E2EF34': 'EEFT',
    'E2NP34': 'ENPH',
    'E2ST34': 'ESTC',
    'E2TS34': 'ETSY',
    'EAIN34': 'EAIN',
    'EBAY34': 'EBAY',
    'EIDO39': 'EIDO',
    'ELCI34': 'ELCI',
    'EPHE39': 'EPHE',
    'EQIX34': 'EQIX',
    'ETHA39': 'ETHA',
    'EVEB31': 'EVEB',
    'EVTC31': 'EVTC',
    'EWJV39': 'EWJV',
    'EXGR34': 'EXGR',
    'EXPB31': 'EXPB',
    'EXXO34': 'XOM',
    'F1AN34': 'FANG',
    'F1IS34': 'FI',
    'F1MC34': 'FMC',
    'F1NI34': 'FIS',
    'F1SL34': 'FSLY',
    'F1TN34': 'FTNT',
    'F2IC34': 'FICO',
    'F2IV34': 'FIVN',
    'F2NV34': 'FNV',
    'F2RS34': 'FRSH',
    'FASL34': 'FASL',
    'FBOK34': 'META',
    'FCXO34': 'FCXO',
    'FDMO34': 'F',
    'FDXB34': 'FDXB',
    'FSLR34': 'FSLR',
    'G1AM34': 'GLPI',
    'G1AR34': 'IT',
    'G1DS34': 'GDS',
    'G1FI34': 'GFI',
    'G1LO34': 'GLOB',
    'G1LW34': 'GLW',
    'G1MI34': 'GIS',
    'G1PI34': 'GPN',
    'G1RM34': 'GRMN',
    'G1SK34': 'GSK',
    'G1TR39': 'G1TR',
    'G1WW34': 'GWW',
    'G2DD34': 'GDDY',
    'G2DI33': 'G2D',
    'G2EV34': 'GEV',
    'GDBR34': 'GDBR',
    'GDXB39': 'GDXB',
    'GEOO34': 'GEOO',
    'GILD34': 'GILD',
    'GMCO34': 'GM',
    'GOGL34': 'GOOGL',
    'GOGL35': 'GOOG',
    'GPRK34': 'GPRK',
    'GPRO34': 'GPRO',
    'GPSI34': 'GPSI',
    'GROP31': 'GROP',
    'GSGI34': 'GS',
    'H1AS34': 'HAS',
    'H1CA34': 'HCA',
    'H1DB34': 'HDB',
    'H1II34': 'HII',
    'H1OG34': 'HOG',
    'H1PE34': 'HPE',
    'H1RL34': 'HRL',
    'H1SB34': 'HSBC',
    'H1UM34': 'HUM',
    'H2TA34': 'HR',
    'H2UB34': 'HUBS',
    'HALI34': 'HALI',
    'HOME34': 'HD',
    'HOND34': 'HOND',
    'HPQB34': 'HPQB',
    'HYEM39': 'HYEM',
    'I1AC34': 'IAC',
    'I1DX34': 'IDXX',
    'I1EX34': 'IEX',
    'I1FO34': 'INFY',
    'I1LM34': 'ILMN',
    'I1NC34': 'INCY',
    'I1PC34': 'IP',
    'I1PG34': 'IPGP',
    'I1QV34': 'IQV',
    'I1QY34': 'IQ',
    'I1RM34': 'IRM',
    'I1RP34': 'TT',
    'I1SR34': 'ISRG',
    'I2NG34': 'INGR',
    'I2NV34': 'INVH',
    'IBIT39': 'IBIT',
    'IBKR34': 'IBKR',
    'ICLR34': 'ICLR',
    'INBR32': 'INTR',
    'INTU34': 'INTU',
    'ITLC34': 'INTC',
    'J1EG34': 'J',
    'J2BL34': 'JBL',
    'JBSS32': 'JBSS',
    'JDCO34': 'JD',
    'JNJB34': 'JNJ',
    'JPMC34': 'JPM',
    'K1BF34': 'KB',
    'K1LA34': 'KLAC',
    'K1MX34': 'KMX',
    'K1SG34': 'KEYS',
    'K1SS34': 'KSS',
    'K1TC34': 'KT',
    'K2CG34': 'KC',
    'KHCB34': 'KHCB',
    'KMBB34': 'KMBB',
    'KMIC34': 'KMIC',
    'L1EG34': 'LEG',
    'L1EN34': 'LEN',
    'L1HX34': 'LHX',
    'L1MN34': 'LUMN',
    'L1NC34': 'LNC',
    'L1RC34': 'LRCX',
    'L1WH34': 'LW',
    'L1YG34': 'LYG',
    'L1YV34': 'LYV',
    'L2PL34': 'LPLA',
    'L2SC34': 'LSCC',
    'LBRD34': 'LBRD',
    'LILY34': 'LILY',
    'LOWC34': 'LOWC',
    'M1AA34': 'MAA',
    'M1CH34': 'MCHP',
    'M1CK34': 'MCK',
    'M1DB34': 'MDB',
    'M1HK34': 'MHK',
    'M1MC34': 'MMC',
    'M1NS34': 'MNST',
    'M1RN34': 'MRNA',
    'M1SC34': 'MSCI',
    'M1SI34': 'MSI',
    'M1TA34': 'META',
    'M1TC34': 'MTCH',
    'M1TT34': 'MAR',
    'M1UF34': 'MUFG',
    'M2KS34': 'MKSI',
    'M2PM34': 'MP',
    'M2PR34': 'MPWR',
    'M2RV34': 'MRVL',
    'M2ST34': 'MSTR',
    'MACY34': 'MACY',
    'MCDC34': 'MCDC',
    'MCOR34': 'MCOR',
    'MDLZ34': 'MDLZ',
    'MDTC34': 'MDT',
    'MELI34': 'MELI',
    'MKLC34': 'MKLC',
    'MMMC34': 'MMM',
    'MOOO34': 'MOOO',
    'MOSC34': 'MOSC',
    'MRCK34': 'MRK',
    'MSBR34': 'MS',
    'MSCD34': 'MA',
    'MSFT34': 'MSFT',
    'MUTC34': 'MU',
    'N1BI34': 'NBIX',
    'N1CL34': 'NCLH',
    'N1DA34': 'NDAQ',
    'N1EM34': 'NEM',
    'N1GG34': 'NGG',
    'N1IS34': 'NI',
    'N1OW34': 'NOW',
    'N1RG34': 'NRG',
    'N1TA34': 'NTAP',
    'N1UE34': 'NUE',
    'N1VO34': 'NVO',
    'N1VR34': 'NVR',
    'N1VS34': 'NVS',
    'N1WG34': 'NWG',
    'N1XP34': 'NXPI',
    'N2ET34': 'NET',
    'N2LY34': 'NLY',
    'N2TN34': 'NTNX',
    'N2VC34': 'NVCR',
    'NETE34': 'NETE',
    'NEXT34': 'NEE',
    'NFLX34': 'NFLX',
    'NIKE34': 'NIKE',
    'NMRH34': 'NMRH',
    'NOCG34': 'NOCG',
    'NOKI34': 'NOKI',
    'NVDC34': 'NVDA',
    'O1DF34': 'ODFL',
    'O1KT34': 'OKTA',
    'O2HI34': 'OHI',
    'O2NS34': 'ON',
    'ORCL34': 'ORCL',
    'ORLY34': 'ORLY',
    'OXYP34': 'OXYP',
    'P1AC34': 'PCAR',
    'P1AY34': 'PAYX',
    'P1DD34': 'PDD',
    'P1EA34': 'DOC',
    'P1GR34': 'PGR',
    'P1KX34': 'PKX',
    'P1LD34': 'PLD',
    'P1NW34': 'PNW',
    'P1PL34': 'PPL',
    'P1RG34': 'PRGO',
    'P1SX34': 'PSX',
    'P2AN34': 'PANW',
    'P2AT34': 'PATH',
    'P2AX34': 'PAX',
    'P2EG34': 'PEGA',
    'P2EN34': 'PENN',
    'P2IN34': 'PINS',
    'P2LT34': 'PLTR',
    'P2ST34': 'PSTG',
    'P2TC34': 'PTC',
    'PAGS34': 'PAGS',
    'PEPB34': 'PEP',
    'PFIZ34': 'PFE',
    'PGCO34': 'PG',
    'PHGN34': 'PHGN',
    'PHMO34': 'PHMO',
    'PNCS34': 'PNCS',
    'PRXB31': 'PRXB',
    'PSKY34': 'PSKY',
    'PYPL34': 'PYPL',
    'Q2SC34': 'QS',
    'QCOM34': 'QCOM',
    'QUBT34': 'QUBT',
    'R1DY34': 'RDY',
    'R1EG34': 'REG',
    'R1EL34': 'RELX',
    'R1HI34': 'RHI',
    'R1IN34': 'O',
    'R1KU34': 'ROKU',
    'R1MD34': 'RMD',
    'R1OP34': 'ROP',
    'R1SG34': 'RSG',
    'R1YA34': 'RYAAY',
    'R2BL34': 'RBLX',
    'R2NG34': 'RNG',
    'R2PD34': 'RPD',
    'REGN34': 'REGN',
    'RGTI34': 'RGTI',
    'RIGG34': 'RIGG',
    'RIOT34': 'RIOT',
    'ROST34': 'ROST',
    'ROXO34': 'NU',
    'RSSL39': 'RSSL',
    'RYTT34': 'RYTT',
    'S1BA34': 'SBAC',
    'S1BS34': 'SBSW',
    'S1HW34': 'SHW',
    'S1KM34': 'SKM',
    'S1LG34': 'SLG',
    'S1NA34': 'SNA',
    'S1NP34': 'SNPS',
    'S1OU34': 'LUV',
    'S1PO34': 'SPOT',
    'S1RE34': 'SRE',
    'S1TX34': 'STX',
    'S1WK34': 'SWK',
    'S1YY34': 'SYY',
    'S2CH34': 'SQM',
    'S2EA34': 'SE',
    'S2ED34': 'SEDG',
    'S2FM34': 'SFM',
    'S2GM34': 'SGML',
    'S2HO34': 'SHOP',
    'S2NA34': 'SNAP',
    'S2NW34': 'SNOW',
    'S2TA34': 'STAG',
    'S2UI34': 'SUI',
    'S2YN34': 'SYNA',
    'SAPP34': 'SAPP',
    'SBUB34': 'SBUB',
    'SCHW34': 'SCHW',
    'SIVR39': 'SIVR',
    'SLBG34': 'SLBG',
    'SLXB39': 'SLXB',
    'SMIN39': 'SMIN',
    'SNEC34': 'SNEC',
    'SOLN39': 'SOLN',
    'SPGI34': 'SPGI',
    'SSFO34': 'CRM',
    'STMN34': 'STMN',
    'STOC34': 'STOC',
    'STZB34': 'STZB',
    'T1AL34': 'TAL',
    'T1AM34': 'TEAM',
    'T1EV34': 'TEVA',
    'T1LK34': 'TLK',
    'T1MU34': 'TMUS',
    'T1OW34': 'AMT',
    'T1RI34': 'TRIP',
    'T1SC34': 'TSCO',
    'T1SO34': 'SO',
    'T1TW34': 'TTWO',
    'T1WL34': 'TWLO',
    'T2DH34': 'TDOC',
    'T2ER34': 'TER',
    'T2RM34': 'TRMB',
    'T2TD34': 'TTD',
    'T2YL34': 'TYL',
    'TAKP34': 'TAKP',
    'TBIL39': 'TBIL',
    'TMCO34': 'TMCO',
    'TMOS34': 'TMO',
    'TOPB39': 'TOPB',
    'TPRY34': 'TPRY',
    'TRVC34': 'TRVC',
    'TSLA34': 'TSLA',
    'TSMC34': 'TSMC',
    'TSNF34': 'TSNF',
    'TXSA34': 'TXSA',
    'U1AI34': 'UA',
    'U1AL34': 'UAL',
    'U1BE34': 'UBER',
    'U1DR34': 'UDR',
    'U1HS34': 'UHS',
    'U1RI34': 'URI',
    'U2PS34': 'UPST',
    'U2PW34': 'UPWK',
    'U2ST34': 'U',
    'U2TH34': 'UTHR',
    'UBSG34': 'UBSG',
    'ULEV34': 'ULEV',
    'UNHH34': 'UNH',
    'UPAC34': 'UPAC',
    'USBC34': 'USBC',
    'V1MC34': 'VMC',
    'V1NO34': 'VNO',
    'V1OD34': 'VOD',
    'V1RS34': 'VRSK',
    'V1RT34': 'VRT',
    'V1SA34': 'V',
    'V1ST34': 'VST',
    'V1TA34': 'VTR',
    'V2EE34': 'VEEV',
    'V2TX34': 'VTEX',
    'VERZ34': 'VZ',
    'VISA34': 'V',
    'VLOE34': 'VLOE',
    'VRSN34': 'VRSN',
    'W1BD34': 'WBD',
    'W1BO34': 'WB',
    'W1DC34': 'WDC',
    'W1EL34': 'WELL',
    'W1HR34': 'WHR',
    'W1MB34': 'WMB',
    'W1MC34': 'WM',
    'W1MG34': 'WMG',
    'W1YC34': 'WY',
    'W2ST34': 'WST',
    'W2YF34': 'W',
    'WABC34': 'WABC',
    'WALM34': 'WMT',
    'WFCO34': 'WFC',
    'WUNI34': 'WU',
    'X1YZ34': 'SQ',
    'XPBR31': 'XPBR',
    'Y2PF34': 'YPF',
    'YUMR34': 'YUMR',
    'Z1BR34': 'ZBRA',
    'Z1OM34': 'ZM',
    'Z1TA34': 'ZETA',
    'Z1TS34': 'ZTS',
    'Z2LL34': 'Z',
    'Z2SC34': 'ZS',
    'A1CR34': 'AMCR',
    'A1DM34': 'ADM',
    'A1EE34': 'AEE',
    'A1EG34': 'AEG',
    'A1EN34': 'LNT',
    'A1GI34': 'A',
    'A1GN34': 'ALLE',
    'A1JG34': 'AJG',
    'A1LG34': 'ALGN',
    'A1LN34': 'ALNY',
    'A1ME34': 'AME',
    'A1NS34': 'ANSS',
    'A1ON34': 'AON',
    'A1OS34': 'AOS',
    'A1PA34': 'APA',
    'A1PD34': 'APD',
    'A1RC34': 'ARCO',
    'A1SN34': 'ASND',
    'A1TM34': 'ATO',
    'A1TT34': 'ALL',
    'A1UT34': 'ADSK',
    'A1VY34': 'AVY',
    'A1YX34': 'AYX',
    'A2FY34': 'AFYA',
    'A2LC34': 'ALC',
    'A2RE34': 'ARES',
    'ABNB34': 'ABNB',
    'ADPR34': 'ADP',
    'AETH39': 'ETHA',
    'ANGV39': 'ANGL',
    'ARM334': 'ARM',
    'AXRP39': 'AXRP',
    'AZOI34': 'AZO',
    'B1BT34': 'TFC',
    'B1DX34': 'BDX',
    'B1GN34': 'ONC',
    'B1KR34': 'BKR',
    'B1ME34': 'BONE',
    'BICI39': 'BICI',
    'CFLT34': 'CFLT',
    'COIN34': 'COIN',
    'CRWD34': 'CRWD',
    'CRYP39': 'CRYP',
    'DDOG34': 'DDOG',
    'DKNG34': 'DKNG',
    'ETHE39': 'ETHA',
    'FTNT34': 'FTNT',
    'HOOD34': 'HOOD',
    'MNDB34': 'MDB',
    'NET234': 'NET',
    'PANW34': 'PANW',
    'PATH34': 'PATH',
    'RDDT34': 'RDDT',
    'RKLB34': 'RKLB',
    'SMCI34': 'SMCI',
    'SNOW34': 'SNOW',
    'ZS1234': 'ZS',
}


def mapear_ticker_us(ticker_bdr):
    """
    Mapeia BDR para o ticker US da empresa mãe.
    Usa BDR_TO_US_MAP completo (678 empresas) derivado do NOMES_BDRS.
    Fallback: remove sufixo numérico (cobre novos BDRs ainda não mapeados).
    """
    if ticker_bdr in BDR_TO_US_MAP:
        return BDR_TO_US_MAP[ticker_bdr]
    # Fallback para BDRs recém-listados não cobertos pelo mapa
    stripped = ticker_bdr.rstrip('0123456789')
    # Se sobrar dígito no meio, retorna o BDR original (OpenBB pode resolver pelo nome)
    return stripped


def calcular_score_fundamentalista(info):
    """
    Calcula score 0-100 baseado em métricas fundamentalistas
    Retorna: (score, detalhes_dict)
    """
    score = 50  # Base neutra
    detalhes = {
        'pe_ratio': {'valor': None, 'pontos': 0, 'criterio': ''},
        'dividend_yield': {'valor': None, 'pontos': 0, 'criterio': ''},
        'revenue_growth': {'valor': None, 'pontos': 0, 'criterio': ''},
        'recomendacao': {'valor': None, 'pontos': 0, 'criterio': ''},
        'market_cap': {'valor': None, 'pontos': 0, 'criterio': ''},
    }

    try:
        # P/E Ratio (15 pontos)
        pe = info.get('trailingPE') or info.get('forwardPE')
        if pe:
            detalhes['pe_ratio']['valor'] = pe
            if 10 <= pe <= 25:
                detalhes['pe_ratio']['pontos'] = 15
                detalhes['pe_ratio']['criterio'] = 'Ótimo (10-25)'
                score += 15
            elif 5 <= pe < 10 or 25 < pe <= 35:
                detalhes['pe_ratio']['pontos'] = 10
                detalhes['pe_ratio']['criterio'] = 'Bom (5-10 ou 25-35)'
                score += 10
            elif pe < 5:
                detalhes['pe_ratio']['pontos'] = 5
                detalhes['pe_ratio']['criterio'] = 'Baixo (<5)'
                score += 5
            elif pe > 50:
                detalhes['pe_ratio']['pontos'] = -10
                detalhes['pe_ratio']['criterio'] = 'Muito alto (>50)'
                score -= 10
            else:
                detalhes['pe_ratio']['criterio'] = 'Regular (35-50)'

        # Dividend Yield (10 pontos)
        div_yield = info.get('dividendYield')
        if div_yield:
            detalhes['dividend_yield']['valor'] = div_yield
            if div_yield > 0.04:
                detalhes['dividend_yield']['pontos'] = 10
                detalhes['dividend_yield']['criterio'] = 'Excelente (>4%)'
                score += 10
            elif div_yield > 0.02:
                detalhes['dividend_yield']['pontos'] = 5
                detalhes['dividend_yield']['criterio'] = 'Bom (>2%)'
                score += 5
            else:
                detalhes['dividend_yield']['criterio'] = 'Baixo (<2%)'

        # Crescimento de Receita (15 pontos)
        rev_growth = info.get('revenueGrowth')
        if rev_growth:
            detalhes['revenue_growth']['valor'] = rev_growth
            if rev_growth > 0.20:
                detalhes['revenue_growth']['pontos'] = 15
                detalhes['revenue_growth']['criterio'] = 'Excelente (>20%)'
                score += 15
            elif rev_growth > 0.10:
                detalhes['revenue_growth']['pontos'] = 10
                detalhes['revenue_growth']['criterio'] = 'Muito bom (>10%)'
                score += 10
            elif rev_growth > 0.05:
                detalhes['revenue_growth']['pontos'] = 5
                detalhes['revenue_growth']['criterio'] = 'Bom (>5%)'
                score += 5
            elif rev_growth < -0.10:
                detalhes['revenue_growth']['pontos'] = -10
                detalhes['revenue_growth']['criterio'] = 'Negativo (<-10%)'
                score -= 10
            else:
                detalhes['revenue_growth']['criterio'] = 'Estável'

        # Recomendação (10 pontos)
        rec = info.get('recommendationKey', '')
        detalhes['recomendacao']['valor'] = rec
        if rec == 'strong_buy':
            detalhes['recomendacao']['pontos'] = 10
            detalhes['recomendacao']['criterio'] = 'Compra Forte'
            score += 10
        elif rec == 'buy':
            detalhes['recomendacao']['pontos'] = 5
            detalhes['recomendacao']['criterio'] = 'Compra'
            score += 5
        elif rec == 'hold':
            detalhes['recomendacao']['criterio'] = 'Manter'
        elif rec == 'sell':
            detalhes['recomendacao']['pontos'] = -5
            detalhes['recomendacao']['criterio'] = 'Venda'
            score -= 5
        elif rec == 'strong_sell':
            detalhes['recomendacao']['pontos'] = -10
            detalhes['recomendacao']['criterio'] = 'Venda Forte'
            score -= 10

        # Market Cap (10 pontos)
        mcap = info.get('marketCap')
        if mcap:
            detalhes['market_cap']['valor'] = mcap
            if mcap > 1e12:
                detalhes['market_cap']['pontos'] = 10
                detalhes['market_cap']['criterio'] = 'Mega Cap (>$1T)'
                score += 10
            elif mcap > 100e9:
                detalhes['market_cap']['pontos'] = 5
                detalhes['market_cap']['criterio'] = 'Large Cap (>$100B)'
                score += 5
            elif mcap > 10e9:
                detalhes['market_cap']['criterio'] = 'Mid Cap (>$10B)'
            else:
                detalhes['market_cap']['criterio'] = 'Small Cap (<$10B)'

    except Exception:
        pass

    return max(0, min(100, score)), detalhes


def buscar_dados_brapi(ticker_bdr):
    """
    Busca dados da BDR diretamente na BRAPI (B3)
    Retorna dict com dados ou None
    """
    try:
        url = f"https://brapi.dev/api/quote/{ticker_bdr}?token={BRAPI_TOKEN}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if 'results' not in data or len(data['results']) == 0:
            return None

        result = data['results'][0]

        # Extrair dados disponíveis
        return {
            'preco': result.get('regularMarketPrice'),
            'variacao': result.get('regularMarketChangePercent'),
            'volume': result.get('regularMarketVolume'),
            'market_cap': result.get('marketCap'),
            'setor': result.get('sector', 'N/A'),
            'nome': result.get('longName', ticker_bdr),
            'cambio': result.get('currency', 'BRL'),
        }
    except Exception:
        return None


def calcular_score_brapi(dados_brapi):
    """
    Calcula score baseado em dados da BRAPI (mais limitados)
    """
    score = 50
    detalhes = {
        'fonte': {'valor': 'BRAPI (B3)', 'pontos': 0, 'criterio': 'Dados da BDR na B3'},
        'market_cap': {'valor': None, 'pontos': 0, 'criterio': ''},
        'volume': {'valor': None, 'pontos': 0, 'criterio': ''},
    }

    # Market Cap (20 pontos)
    mcap = dados_brapi.get('market_cap')
    if mcap:
        detalhes['market_cap']['valor'] = mcap
        mcap_b = mcap / 1e9
        if mcap_b > 100:
            detalhes['market_cap']['pontos'] = 20
            detalhes['market_cap']['criterio'] = 'Large Cap (>$100B)'
            score += 20
        elif mcap_b > 10:
            detalhes['market_cap']['pontos'] = 10
            detalhes['market_cap']['criterio'] = 'Mid Cap (>$10B)'
            score += 10
        else:
            detalhes['market_cap']['criterio'] = 'Small Cap (<$10B)'

    # Volume (10 pontos - liquidez na B3)
    volume = dados_brapi.get('volume')
    if volume:
        detalhes['volume']['valor'] = volume
        if volume > 1000000:
            detalhes['volume']['pontos'] = 10
            detalhes['volume']['criterio'] = 'Alta liquidez (>1M)'
            score += 10
        elif volume > 100000:
            detalhes['volume']['pontos'] = 5
            detalhes['volume']['criterio'] = 'Boa liquidez (>100K)'
            score += 5
        else:
            detalhes['volume']['criterio'] = 'Baixa liquidez (<100K)'

    return max(0, min(100, score)), detalhes


FMP_API_KEY = st.secrets.get("FMP_API_KEY", "tBsRam74Ac6bZRWS3C8HY83C6not17Uh")


def buscar_dados_openbb(ticker_us):
    """
    Busca dados fundamentalistas via OpenBB SDK (openbb-finance).
    Retorna um dict compatível com o formato do Yahoo Finance ou None.
    """
    try:
        from openbb import obb

        # Configura chave FMP em tempo de execução
        try:
            obb.user.credentials.fmp_api_key = FMP_API_KEY
        except Exception:
            pass

        info = {}

        # --- Perfil / visão geral ---
        try:
            profile = obb.equity.profile(symbol=ticker_us, provider="fmp")
            if profile and profile.results:
                r = profile.results[0]
                info['marketCap']   = getattr(r, 'mkt_cap', None)
                info['sector']      = getattr(r, 'sector', None)
                info['industry']    = getattr(r, 'industry', None)
                info['symbol']      = ticker_us
        except Exception:
            pass

        # --- Métricas fundamentais ---
        try:
            metrics = obb.equity.fundamental.metrics(symbol=ticker_us, provider="fmp")
            if metrics and metrics.results:
                m = metrics.results[0]
                info['trailingPE']    = getattr(m, 'pe_ratio', None)
                info['dividendYield'] = getattr(m, 'dividend_yield', None)
                info['revenueGrowth'] = getattr(m, 'revenue_growth', None)
        except Exception:
            pass

        # --- Recomendação de analistas ---
        try:
            rec = obb.equity.estimates.consensus(symbol=ticker_us, provider="fmp")
            if rec and rec.results:
                cons = rec.results[0]
                raw = str(getattr(cons, 'consensus', '') or '').lower().replace(' ', '_')
                # normaliza para o padrão Yahoo: strong_buy / buy / hold / sell / strong_sell
                mapping = {
                    'strong_buy': 'strong_buy', 'strongbuy': 'strong_buy',
                    'buy': 'buy', 'overweight': 'buy', 'outperform': 'buy',
                    'hold': 'hold', 'neutral': 'hold', 'market_perform': 'hold',
                    'sell': 'sell', 'underweight': 'sell', 'underperform': 'sell',
                    'strong_sell': 'strong_sell',
                }
                info['recommendationKey'] = mapping.get(raw, raw) if raw else None
        except Exception:
            pass

        # Só retorna se tiver ao menos market cap ou P/E
        if info.get('marketCap') or info.get('trailingPE'):
            return info

    except ImportError:
        pass
    except Exception:
        pass

    return None


NOMES_BDRS = {
    'A1AP34': 'Advance Auto Parts, Inc.',
    'A1DC34': 'Agree Realty Corp',
    'A1DI34': 'Analog Devices, Inc.',
    'A1EP34': 'American Electric Power Company, Inc.',
    'A1ES34': 'AES Corporation',
    'A1FL34': 'Aflac Incorporated',
    'A1IV34': 'Apartment Investment and Management Company',
    'A1KA34': 'Akamai Technologies, Inc.',
    'A1LB34': 'Albemarle Corporation',
    'A1LK34': 'Alaska Air Group, Inc.',
    'A1LL34': 'Bread Financial Holdings, Inc.',
    'A1MD34': 'Advanced Micro Devices, Inc.',
    'A1MP34': 'Ameriprise Financial, Inc.',
    'A1MT34': 'Applied Materials, Inc.',
    'A1NE34': 'Arista Networks Inc',
    'A1PH34': 'Amphenol Corporation',
    'A1PL34': 'Applied Digital Corporation',
    'A1PO34': 'Apollo Global Management Inc',
    'A1PP34': 'AppLovin Corp.',
    'A1RE34': 'Alexandria Real Estate Equities Inc',
    'A1RG34': 'argenx SE ADR',
    'A1SU34': 'Assurant, Inc.',
    'A1TH34': 'Autohome Inc. ADR',
    'A1VB34': 'AvalonBay Communities, Inc.',
    'A1WK34': 'American Water Works Co Inc',
    'A1ZN34': 'AstraZeneca PLC ADR',
    'A2MB34': 'Ambarella, Inc.',
    'A2RR34': 'Arrowhead Pharmaceuticals, Inc.',
    'A2RW34': 'Arrows Electronics Inc',
    'A2SO34': 'Academy Sports and Outdoors Inc',
    'A2XO34': 'Axon Enterprise Inc',
    'A2ZT34': 'Azenta Inc',
    'AADA39': '21Shares Ltd ETP',
    'AALL34': 'American Airlines Group Inc.',
    'AAPL34': 'Apple Inc.',
    'ABBV34': 'AbbVie, Inc.',
    'ABGD39': 'abrdn Gold ETF Trust',
    'ABTT34': 'Abbott Laboratories',
    'ABUD34': 'Anheuser-Busch InBev SA/NV ADR',
    'ACNB34': 'Accenture PLC',
    'ACWX39': 'iShares MSCI ACWI ex US ETF',
    'ADBE34': 'Adobe Inc.',
    'AIRB34': 'Airbnb, Inc.',
    'AMGN34': 'Amgen Inc.',
    'AMZO34': 'Amazon.com, Inc.',
    'APTV34': 'Aptiv PLC',
    'ARGT39': 'Global X MSCI Argentina ETF',
    'ARMT34': 'ArcelorMittal SA',
    'ARNC34': 'Howmet Aerospace Inc',
    'ASML34': 'ASML Holding NV ADR',
    'ATTB34': 'AT&T Inc',
    'AURA33': 'Aura Minerals Inc',
    'AVGO34': 'Broadcom Inc.',
    'AWII34': 'Armstrong World Industries, Inc.',
    'AXPB34': 'American Express Co',
    'B1AM34': 'Brookfield Corporation',
    'B1AX34': 'Baxter International Inc.',
    'B1BW34': 'Bath & Body Works, Inc.',
    'B1CS34': 'Barclays PLC ADR',
    'B1FC34': 'Brown-Forman Corporation',
    'B1IL34': 'Bilibili, Inc. ADR',
    'B1LL34': 'Ball Corporation',
    'B1MR34': 'Biomarin Pharmaceutical Inc.',
    'B1NT34': 'BioNTech SE ADR',
    'B1PP34': 'BP PLC',
    'B1RF34': 'Broadridge Financial Solutions, Inc.',
    'B1SA34': 'Banco Santander Chile ADR',
    'B1TI34': 'British American Tobacco PLC ADR',
    'B2AH34': 'Booz Allen Hamilton Holding Corp Class A',
    'B2HI34': 'BILL Holdings, Inc.',
    'B2LN34': 'BlackLine, Inc.',
    'B2MB34': 'Bumble, Inc.',
    'B2RK34': 'Bruker Corporation',
    'B2UR34': 'Burlington Stores, Inc.',
    'B2YN34': 'Beyond Meat, Inc.',
    'BAAX39': 'iShares MSCI All Country Asia ex Japan ETF',
    'BABA34': 'Alibaba Group Holding Limited ADR',
    'BACW39': 'iShares MSCI ACWI ETF',
    'BAER39': 'iShares U.S. Aerospace & Defense ETF',
    'BAGG39': 'iShares Core U.S. Aggregate Bond ETF',
    'BAIQ39': 'AIQ',
    'BAOR39': 'iShares Core Growth Allocation ETF',
    'BARY39': 'iShares Future AI & Tech ETF',
    'BASK39': '21Shares Ltd ETP',
    'BBER39': 'BBER',
    'BBJP39': 'BBJP',
    'BBUG39': 'Global X Cybersecurity ETF',
    'BCAT39': 'Global X S&P 500 Catholic Values Custom ETF',
    'BCHI39': 'iShares MSCI China ETF',
    'BCIR39': 'First Trust NASDAQ Cybersecurity ETF',
    'BCLO39': 'Global X Cloud Computing ETF',
    'BCNY39': 'iShares MSCI China A ETF',
    'BCOM39': 'iShares GSCI Commodity Dynamic Roll Strategy ETF',
    'BCPX39': 'Global X Copper Miners ETF',
    'BCSA34': 'Banco Santander SA ADR',
    'BCTE39': 'Global X CleanTech ETF',
    'BCWV39': 'iShares MSCI Global Min Vol Factor ETF',
    'BDVD39': 'Global X Superdividend U.S. ETF',
    'BDVE39': 'iShares Emerging Markets Dividend ETF',
    'BDVY39': 'iShares Select Dividend ETF',
    'BECH39': 'iShares MSCI Chile ETF',
    'BEEM39': 'iShares MSCI Emerging Markets ETF',
    'BEFA39': 'iShares MSCI EAFE ETF',
    'BEFG39': 'iShares MSCI EAFE Growth ETF',
    'BEFV39': 'iShares MSCI EAFE Value ETF',
    'BEGD39': 'iShares ESG Aware MSCI EAFE ETF',
    'BEGE39': 'iShares ESG Aware MSCI EM ETF',
    'BEGU39': 'iShares Trust iShares ESG Aware MSCI USA ETF',
    'BEIS39': 'iShares MSCI Israel ETF',
    'BEMV39': 'iShares MSCI Emerging Markets Min Vol Factor ETF',
    'BEPP39': 'iShares MSCI Pacific ex Japan ETF',
    'BEPU39': 'iShares MSCI Peru and Global Exposure ETF',
    'BERK34': 'Berkshire Hathaway Inc. B',
    'BEWA39': 'iShares MSCI Australia ETF',
    'BEWC39': 'iShares MSCI Canada ETF',
    'BEWD39': 'iShares MSCI Sweden ETF',
    'BEWG39': 'iShares MSCI Germany ETF',
    'BEWH39': 'iShares MSCI Hong Kong ETF',
    'BEWJ39': 'iShares MSCI Japan ETF',
    'BEWL39': 'iShares MSCI Switzerland ETF',
    'BEWP39': 'iShares MSCI Spain ETF',
    'BEWS39': 'iShares MSCI Singapore ETF',
    'BEWW39': 'iShares MSCI Mexico ETF',
    'BEWY39': 'iShares MSCI South Korea Capped ETF',
    'BEWZ39': 'iShares MSCI Brazil ETF',
    'BEZA39': 'iShares MSCI South Africa ETF',
    'BEZU39': 'iShares MSCI Eurozone ETF',
    'BFAV39': 'iShares MSCI EAFE Min Vol Factor ETF',
    'BFLO39': 'iShares Floating Rate Bond ETF',
    'BFXI39': 'iShares China Large-Cap ETF',
    'BGLC39': 'iShares Global 100 ETF',
    'BGOV39': 'iShares US Treasury Bond ETF',
    'BGOZ39': 'iShares 25+ Year Treasury STRIPS Bond ETF',
    'BGRT39': 'iShares Global REIT ETF',
    'BGWH39': 'iShares Core Dividend Growth ETF',
    'BHEF39': 'iShares Currency Hedged MSCI EAFE ETF',
    'BHER39': 'Global X Video Games & Esports ETF',
    'BHVN34': 'Biohaven Research Ltd',
    'BHYC39': 'iShares 0-5 Year High Yield Corporate Bond ETF',
    'BHYG39': 'iShares iBoxx USD High Yield Corporate Bond ETF',
    'BIAI39': 'iShares U.S. Broker-Dealers & Securities Exchanges ETF',
    'BIAU39': 'iShares Gold Trust',
    'BIBB39': 'iShares Biotechnology ETF',
    'BICL39': 'iShares Global Clean Energy ETF',
    'BIDU34': 'Baidu, Inc. ADR',
    'BIEF39': 'iShares Core MSCI EAFE ETF',
    'BIEI39': 'iShares 3-7 Year Treasury Bond ETF',
    'BIEM39': 'iShares Core MSCI Emerging Markets ETF',
    'BIEO39': 'iShares US Oil & Gas Exploration & Production ETF',
    'BIEU39': 'iShares Core MSCI Europe ETF',
    'BIEV39': 'iShares Europe ETF',
    'BIGF39': 'iShares Global Infrastructure ETF',
    'BIGS39': 'iShares 1-5 Year Investment Grade Corporate BondETF',
    'BIHE39': 'iShares US Pharmaceuticals ETF',
    'BIHF39': 'iShares US Healthcare Providers ETF',
    'BIHI39': 'iShares US Medical Devices ETF',
    'BIIB34': 'Biogen Inc.',
    'BIJH39': 'iShares Core S&P Mid-Cap ETF',
    'BIJR39': 'iShares Core S&P Small-Cap ETF',
    'BIJS39': 'iShares S&P Small-Cap 600 Value ETF',
    'BIJT39': 'iShares S&P Small-Cap 600 Growth ETF',
    'BILF39': 'iShares Latin America 40 ETF',
    'BIPC39': 'iShares Core MSCI Pacific ETF',
    'BITB39': 'iShares US Home Construction ETF',
    'BITO39': 'iShares Core S&P Total U.S. Stock Market ETF',
    'BIUS39': 'iShares Core Total USD Bond Market ETF',
    'BIVB39': 'iShares Core S&P 500 ETF',
    'BIVE39': 'iShares S&P 500 Value ETF',
    'BIVW39': 'iShares S&P 500 Growth ETF',
    'BIWF39': 'iShares Russell 1000 Growth ETF',
    'BIWM39': 'iShares Russell 2000 ETF',
    'BIXG39': 'iShares Global Financials ETF',
    'BIXJ39': 'iShares Global Healthcare ETF',
    'BIXN39': 'iShares Global Tech ETF',
    'BIXU39': 'iShares Core MSCI Total International Stock ETF',
    'BIYE39': 'iShares US Energy ETF',
    'BIYF39': 'iShares US Financials ETF',
    'BIYJ39': 'iShares US Industrials ETF',
    'BIYT39': 'iShares 7-10 Year Treasury Bond ETF',
    'BIYW39': 'iShares US Technology ETF',
    'BIYZ39': 'iShares US Telecommunications ETF',
    'BJQU39': 'JQUA',
    'BKCH39': 'Global X Blockchain ETF',
    'BKNG34': 'Booking Holdings Inc.',
    'BKWB39': 'KraneShares CSI China Internet ETF',
    'BKXI39': 'iShares Global Consumer Staples ETF',
    'BLAK34': 'BlackRock, Inc.',
    'BLBT39': 'Global X Lithium & Battery Tech ETF',
    'BLPX39': 'Global X MLP & Energy Infrastructure ETF',
    'BLQD39': 'iShares iBoxx USD Investment Grade Corporate Bond ETF',
    'BMTU39': 'iShares MSCI USA Momentum Factor ETF',
    'BMYB34': 'Bristol-Myers Squibb Company',
    'BNDA39': 'iShares MSCI India ETF',
    'BOAC34': 'BAC',
    'BOEF39': 'iShares S&P 100 ETF',
    'BOEI34': 'BA',
    'BONY34': 'Bank of New York Mellon Corp',
    'BOTZ39': 'BOTZ',
    'BOXP34': 'BXP Inc',
    'BPIC39': 'iShares MSCI Global Metals & Mining Producers ETF',
    'BPVE39': 'Global X US Infrastructure Development ETF',
    'BQQW39': 'First Trust NASDAQ-100 Equal Weighted Index Fund',
    'BQUA39': 'iShares MSCI USA Quality Factor ETF',
    'BQYL39': 'Global X NASDAQ 100 Covered Call ETF',
    'BSCZ39': 'iShares MSCI EAFE Small-Cap ETF',
    'BSDV39': 'Global X Superdividend ETF',
    'BSHV39': 'iShares Short Treasury Bond ETF',
    'BSHY39': 'iShares 1-3 Year Treasury Bond ETF',
    'BSIL39': 'Global X Silver Miners ETF',
    'BSIZ39': 'iShares MSCI USA Size Factor ETF',
    'BSLV39': 'iShares Silver Trust',
    'BSOC39': 'Global X Social Media ETF',
    'BSOX39': 'iShares Semiconductor ETF',
    'BSRE39': 'Global X SuperDividend REIT ETF',
    'BTFL39': 'iShares Treasury Floating Rate Bond ETF',
    'BTIP39': 'iShares TIPS Bond ETF',
    'BTLT39': 'iShares 20+ Year Treasury Bond ETF',
    'BURA39': 'Global X Uranium ETF',
    'BURT39': 'iShares MSCI World ETF',
    'BUSM39': 'iShares MSCI USA Minimum Volatility ETF',
    'BUSR39': 'iShares Core US REIT ETF',
    'BUTL39': 'iShares US Utilities ETF',
    'C1AB34': 'Cable One, Inc.',
    'C1AG34': 'Conagra Brands, Inc.',
    'C1AH34': 'Cardinal Health, Inc.',
    'C1BL34': 'Chubb Limited',
    'C1BR34': 'CBRE Group, Inc.',
    'C1CJ34': 'Cameco Corporation',
    'C1CL34': 'Carnival Corporation',
    'C1CO34': 'Cencora, Inc.',
    'C1DN34': 'Cadence Design Systems, Inc.',
    'C1FG34': 'Citizens Financial Group, Inc.',
    'C1GP34': 'CoStar Group, Inc.',
    'C1HR34': 'C.H.Robinson Worldwide Inc',
    'C1IC34': 'Cigna Group',
    'C1MG34': 'Chipotle Mexican Grill, Inc.',
    'C1MI34': 'Cummins Inc. (Ex. Cummins Engine Inc)',
    'C1MS34': 'CMS Energy Corporation',
    'C1NC34': 'Centene Corporation',
    'C1OO34': 'Cooper Companies, Inc.',
    'C1PB34': 'Campbell\'s Company',
    'C1RH34': 'CRH public limited company',
    'C2AC34': 'CACI International Inc',
    'C2CA34': 'Coca-Cola Femsa SAB de CV ADR',
    'C2GN34': 'Cognex Corp',
    'C2HD34': 'Churchill Downs Inc',
    'C2OI34': 'Coinbase Global, Inc.',
    'C2OL34': 'Grupo Cibest S.A. ADR',
    'C2OU34': 'Coursera Inc',
    'C2RN34': 'Cerence Inc.',
    'C2RS34': 'CRISPR Therapeutics AG',
    'C2RW34': 'CrowdStrike Holdings, Inc.',
    'C2ZR34': 'Caesars Entertainment, Inc.',
    'CAON34': 'Capital One Financial Corp',
    'CATP34': 'CAT',
    'CHCM34': 'CHTR',
    'CHDC34': 'Church & Dwight Co., Inc.',
    'CHME34': 'CME',
    'CHVX34': 'Chevron Corporation',
    'CLOV34': 'Clover Health Investments Corp.',
    'CLXC34': 'Clorox Co',
    'CNIC34': 'Canadian National Railway Co',
    'COCA34': 'KO',
    'COLG34': 'CL',
    'COPH34': 'ConocoPhillips',
    'COTY34': 'Coty Inc.',
    'COWC34': 'Costco Wholesale Corporation',
    'CPRL34': 'Canadian Pacific Kansas City Limited',
    'CRIN34': 'Carter\'s Incorporated',
    'CSCO34': 'Cisco Systems, Inc.',
    'CSXC34': 'CSX Corporation',
    'CTGP34': 'C',
    'CTSH34': 'Cognizant Technology Solutions Corporation',
    'CVSH34': 'CVS Health Corp',
    'D1DG34': 'Datadog, Inc.',
    'D1EX34': 'DexCom, Inc.',
    'D1LR34': 'Digital Realty Trust, Inc.',
    'D1OC34': 'DocuSign, Inc.',
    'D1OW34': 'Dow, Inc.',
    'D1VN34': 'Devon Energy Corporation',
    'D2AR34': 'Darling Ingredients Inc',
    'D2AS34': 'DoorDash, Inc.',
    'D2NL34': 'Denali Therapeutics Inc',
    'D2OC34': 'Doximity, Inc.',
    'D2OX34': 'Amdocs Ltd',
    'D2PZ34': 'Domino\'s Pizza, Inc.',
    'DBAG34': 'Deutsche Bank AG',
    'DDNB34': 'DuPont de Nemours, Inc.',
    'DEEC34': 'DE',
    'DEFT31': 'DeFi Technologies Inc',
    'DEOP34': 'Diageo PLC ADR',
    'DGCO34': 'Dollar General Corporation',
    'DHER34': 'DHR',
    'DISB34': 'Walt Disney Company',
    'DOLL39': 'iShares 0-3 Month Treasury Bond ETF',
    'DTCR39': 'Global X Data Center REITs & Digital Infrastructure ETF',
    'DUOL34': 'Duolingo, Inc.',
    'DVAI34': 'DaVita Inc.',
    'E1CO34': 'Ecopetrol SA ADR',
    'E1DU34': 'New Oriental Education & Technology Group, Inc.',
    'E1LV34': 'Elevance Health, Inc.',
    'E1MN34': 'Eastman Chemical Company',
    'E1MR34': 'Emerson Electric Co.',
    'E1OG34': 'EOG Resources, Inc.',
    'E1QN34': 'Equinor ASA ADR',
    'E1RI34': 'Telefonaktiebolaget LM Ericsson ADR B',
    'E1TN34': 'Eaton Corp. PlcShs',
    'E1WL34': 'Edwards Lifesciences Corp',
    'E2AG34': 'EAGLE MATERIALS INC',
    'E2EF34': 'Euronet Worldwide Inc',
    'E2NP34': 'Enphase Energy, Inc.',
    'E2ST34': 'Elastic NV',
    'E2TS34': 'Etsy, Inc.',
    'EAIN34': 'Electronic Arts Inc.',
    'EBAY34': 'eBay Inc.',
    'EIDO39': 'iShares MSCI Indonesia ETF',
    'ELCI34': 'Estee Lauder Companies Inc',
    'EPHE39': 'iShares MSCI Philippines ETF',
    'EQIX34': 'Equinix Inc',
    'ETHA39': 'iShares Ethereum Trust',
    'EVEB31': 'Eve Holding Inc',
    'EVTC31': 'EVERTEC, Inc.',
    'EWJV39': 'iShares MSCI Japan Value ETF',
    'EXGR34': 'Expedia Group, Inc.',
    'EXPB31': 'Experian PLC Sponsored',
    'EXXO34': 'XOM',
    'F1AN34': 'Diamondback Energy, Inc.',
    'F1IS34': 'Fiserv, Inc.',
    'F1MC34': 'FMC Corp',
    'F1NI34': 'Fidelity National Information Services, Inc.',
    'F1SL34': 'Fastly, Inc.',
    'F1TN34': 'Fortinet, Inc.',
    'F2IC34': 'Fair Isaac Corporation',
    'F2IV34': 'Five9 Inc',
    'F2NV34': 'Franco-Nevada Corporation',
    'F2RS34': 'Freshworks, Inc.',
    'FASL34': 'Fastenal Company',
    'FCXO34': 'Freeport-McMoRan, Inc.',
    'FDMO34': 'F',
    'FDXB34': 'FedEx Corporation',
    'FSLR34': 'First Solar, Inc.',
    'G1AM34': 'Gaming and Leisure Properties Inc',
    'G1AR34': 'Gartner, Inc.',
    'G1DS34': 'GDS Holdings Ltd. ADR A',
    'G1FI34': 'Gold Fields Limited',
    'G1LO34': 'Globant Sa',
    'G1LW34': 'Corning Inc',
    'G1MI34': 'General Mills, Inc.',
    'G1PI34': 'Global Payments Inc.',
    'G1RM34': 'Garmin Ltd.',
    'G1SK34': 'GSK PLC ADR',
    'G1TR39': 'abrdn Precious Metals Basket ETF Trust',
    'G1WW34': 'W.W. Grainger, Inc.',
    'G2DD34': 'GoDaddy, Inc.',
    'G2DI33': 'G2D Investments, Ltd.',
    'G2EV34': 'GE Vernova Inc',
    'GDBR34': 'General Dynamics Corp',
    'GDXB39': 'VanEck Gold Miners ETF',
    'GEOO34': 'GE Aerospace',
    'GILD34': 'Gilead Sciences, Inc',
    'GMCO34': 'GM',
    'GOGL34': 'Alphabet Inc',
    'GOGL35': 'Alphabet Inc',
    'GPRK34': 'GeoPark Ltd',
    'GPRO34': 'GoPro, Inc.',
    'GPSI34': 'Gap Inc.',
    'GROP31': 'Brazil Potash Corp',
    'GSGI34': 'GS',
    'H1AS34': 'Hasbro, Inc.',
    'H1CA34': 'HCA Healthcare Inc',
    'H1DB34': 'HDFC Bank Limited',
    'H1II34': 'Huntington Ingalls Industries Inc',
    'H1OG34': 'Harley-Davidson Inc',
    'H1PE34': 'Hewlett Packard Enterprise Co.',
    'H1RL34': 'Hormel Foods Corporation',
    'H1SB34': 'HSBC Holdings Plc',
    'H1UM34': 'Humana Inc',
    'H2TA34': 'Healthcare Realty Trust Incorporated',
    'H2UB34': 'HubSpot, Inc.',
    'HALI34': 'Halliburton Company Shs',
    'HOME34': 'HD',
    'HOND34': 'Honda Motor Co., Ltd. ADR',
    'HPQB34': 'HP Inc.',
    'HYEM39': 'VanEck Emerging Markets High Yield Bond ETF',
    'I1AC34': 'IAC Inc.',
    'I1DX34': 'IDEXX Laboratories, Inc.',
    'I1EX34': 'IDEX Corporation',
    'I1FO34': 'Infosys Limited',
    'I1LM34': 'Illumina, Inc.',
    'I1NC34': 'Incyte Corporation',
    'I1PC34': 'International Paper Company',
    'I1PG34': 'IPG Photonics Corp',
    'I1QV34': 'IQVIA Holdings Inc',
    'I1QY34': 'iQIYI, Inc.',
    'I1RM34': 'Iron Mountain REIT Inc',
    'I1RP34': 'Trane Technologies plc',
    'I1SR34': 'Intuitive Surgical, Inc.',
    'I2NG34': 'Ingredion Inc',
    'I2NV34': 'Invitation Homes, Inc.',
    'IBIT39': 'IShares Bitcoin Trust',
    'IBKR34': 'Interactive Brokers Group, Inc.',
    'ICLR34': 'Icon PLC',
    'INBR32': 'Inter & Co., Inc.',
    'INTU34': 'Intuit Corp',
    'ITLC34': 'Intel Corporation',
    'J1EG34': 'Jacobs Solutions Inc.',
    'J2BL34': 'Jabil Inc.',
    'JBSS32': 'JBS N.V.',
    'JDCO34': 'JD.com, Inc. ADR',
    'JNJB34': 'JNJ',
    'JPMC34': 'JPM',
    'K1BF34': 'KB Financial Group Inc',
    'K1LA34': 'KLA Corporation',
    'K1MX34': 'CarMax, Inc.',
    'K1SG34': 'Keysight Technologies, Inc.',
    'K1SS34': 'Kohl\'s Corporation',
    'K1TC34': 'KT Corporation',
    'K2CG34': 'Kingsoft Cloud Holdings Ltd. ADR',
    'KHCB34': 'Kraft Heinz Company',
    'KMBB34': 'Kimberly-Clark Corp',
    'KMIC34': 'Kinder Morgan Inc',
    'L1EG34': 'Leggett & Platt Inc',
    'L1EN34': 'Lennar Corporation',
    'L1HX34': 'L3Harris Technologies Inc',
    'L1MN34': 'Lumen Technologies, Inc.',
    'L1NC34': 'Lincoln National Corp',
    'L1RC34': 'Lam Research Corporation',
    'L1WH34': 'Lamb Weston Holdings, Inc.',
    'L1YG34': 'Lloyds Banking Group PLC',
    'L1YV34': 'Live Nation Entertainment, Inc.',
    'L2PL34': 'LPL Financial Holdings Inc',
    'L2SC34': 'Lattice Semiconductor Corp',
    'LBRD34': 'Liberty Broadband Corp.',
    'LILY34': 'Eli Lilly & Co',
    'LOWC34': 'Lowe\'s Companies Inc',
    'M1AA34': 'Mid-America Apartment Communities, Inc.',
    'M1CH34': 'Microchip Technology Incorporated',
    'M1CK34': 'McKesson Corporation',
    'M1DB34': 'MongoDB, Inc.',
    'M1HK34': 'Mohawk Industries, Inc.',
    'M1MC34': 'Marsh & McLennan Companies, Inc.',
    'M1NS34': 'Monster Beverage Corporation',
    'M1RN34': 'Moderna, Inc.',
    'M1SC34': 'MSCI Inc.',
    'M1SI34': 'Motorola Solutions, Inc.',
    'M1TA34': 'Meta Platforms Inc',
    'M1TC34': 'Match Group, Inc.',
    'M1TT34': 'Marriott International, Inc. (New)',
    'M1UF34': 'Mitsubishi UFJ Financial Group, Inc.',
    'M2KS34': 'MKS Inc',
    'M2PM34': 'MP Materials Corp',
    'M2PR34': 'Monolithic Power Systems, Inc.',
    'M2RV34': 'Marvell Technology, Inc.',
    'M2ST34': 'Strategy Inc',
    'MACY34': 'Macy\'s, Inc.',
    'MCDC34': 'McDonald\'s Corporation',
    'MCOR34': 'Moody\'s Corporation',
    'MDLZ34': 'Mondelez International, Inc.',
    'MDTC34': 'MDT',
    'MELI34': 'MercadoLibre, Inc.',
    'MKLC34': 'Markel Group Inc.',
    'MMMC34': 'MMM',
    'MOOO34': 'Altria Group, Inc.',
    'MOSC34': 'Mosaic Co',
    'MRCK34': 'MRK',
    'MSBR34': 'MS',
    'MSCD34': 'Mastercard Inc',
    'MSFT34': 'Microsoft Corp',
    'MUTC34': 'Micron Technology Inc',
    'N1BI34': 'Neurocrine Biosciences, Inc.',
    'N1CL34': 'Norwegian Cruise Line Holdings Ltd.',
    'N1DA34': 'Nasdaq, Inc.',
    'N1EM34': 'Newmont Corporation',
    'N1GG34': 'National Grid PLC',
    'N1IS34': 'Nisource Inc',
    'N1OW34': 'ServiceNow, Inc.',
    'N1RG34': 'NRG Energy, Inc.',
    'N1TA34': 'NetApp, Inc.',
    'N1UE34': 'Nucor Corporation',
    'N1VO34': 'Novo Nordisk A/S ADR B',
    'N1VR34': 'NVR, Inc.',
    'N1VS34': 'Novartis AG',
    'N1WG34': 'NatWest Group Plc',
    'N1XP34': 'NXP Semiconductors NV',
    'N2ET34': 'Cloudflare Inc',
    'N2LY34': 'Annaly Capital Management, Inc.',
    'N2TN34': 'Nutanix, Inc.',
    'N2VC34': 'NovoCure Ltd.',
    'NETE34': 'Netease Inc ADR',
    'NEXT34': 'NEE',
    'NFLX34': 'Netflix, Inc.',
    'NIKE34': 'NIKE, Inc.',
    'NMRH34': 'Nomura Holdings, Inc. ADR',
    'NOCG34': 'Northrop Grumman Corp.',
    'NOKI34': 'Nokia Oyj',
    'NVDC34': 'NVIDIA Corporation',
    'O1DF34': 'Old Dominion Freight Line, Inc.',
    'O1KT34': 'Okta, Inc.',
    'O2HI34': 'Omega Healthcare Investors Inc',
    'O2NS34': 'ON Semiconductor Corporation',
    'ORCL34': 'Oracle Corp',
    'ORLY34': 'O\'Reilly Automotive Inc',
    'OXYP34': 'Occidental Petroleum Corp',
    'P1AC34': 'PACCAR Inc',
    'P1AY34': 'Paychex, Inc.',
    'P1DD34': 'PDD Holdings Inc. ADR A',
    'P1EA34': 'Healthpeak Properties, Inc.',
    'P1GR34': 'Progressive Corporation',
    'P1KX34': 'POSCO Holdings Inc. ADR',
    'P1LD34': 'Prologis, Inc.',
    'P1NW34': 'Pinnacle West Capital Corp',
    'P1PL34': 'PPL Corporation',
    'P1RG34': 'Perrigo Company PLC',
    'P1SX34': 'Phillips 66',
    'P2AN34': 'Palo Alto Networks, Inc.',
    'P2AT34': 'UiPath, Inc.',
    'P2AX34': 'Patria Investments Ltd.',
    'P2EG34': 'Pegasystems Inc.',
    'P2EN34': 'PENN Entertainment, Inc.',
    'P2IN34': 'Pinterest, Inc.',
    'P2LT34': 'Palantir Technologies Inc.',
    'P2ST34': 'Pure Storage, Inc.',
    'P2TC34': 'PTC Inc.',
    'PAGS34': 'PagSeguro Digital Ltd.',
    'PEPB34': 'PEP',
    'PFIZ34': 'PFE',
    'PGCO34': 'PG',
    'PHGN34': 'Koninklijke Philips N.V. ADR',
    'PHMO34': 'Philip Morris International Inc.',
    'PNCS34': 'PNC Financial Services Group, Inc.',
    'PRXB31': 'Prosus N.V. ADR Sponsored',
    'PSKY34': 'Paramount Skydance Corporation',
    'PYPL34': 'PayPal Holdings, Inc.',
    'Q2SC34': 'QuantumScape Corporation',
    'QCOM34': 'QUALCOMM Incorporated',
    'QUBT34': 'Quantum Computing Inc',
    'R1DY34': 'Dr Reddy\'S Laboratories Ltd ADR',
    'R1EG34': 'Regency Centers Corporation',
    'R1EL34': 'RELX PLC',
    'R1HI34': 'Robert Half Inc.',
    'R1IN34': 'Realty Income Corporation',
    'R1KU34': 'Roku, Inc.',
    'R1MD34': 'ResMed Inc.',
    'R1OP34': 'Roper Technologies, Inc.',
    'R1SG34': 'Republic Services, Inc.',
    'R1YA34': 'Ryanair Holdings PLC',
    'R2BL34': 'Roblox Corp.',
    'R2NG34': 'RingCentral, Inc.',
    'R2PD34': 'Rapid7 Inc',
    'REGN34': 'Regeneron Pharmaceuticals, Inc.Shs',
    'RGTI34': 'Rigetti Computing, Inc.',
    'RIGG34': 'Transocean Ltd.',
    'RIOT34': 'Rio Tinto PLC ADR',
    'ROST34': 'Ross Stores, Inc.',
    'ROXO34': 'Nu Holdings Ltd.',
    'RSSL39': 'Global X RUSSELL 2000 ETF',
    'RYTT34': 'RTX Corporation',
    'S1BA34': 'SBA Communications Corp.',
    'S1BS34': 'Sibanye Stillwater Limited',
    'S1HW34': 'Sherwin-Williams Company',
    'S1KM34': 'SK Telecom Co., Ltd.',
    'S1LG34': 'SL Green Realty Corp.',
    'S1NA34': 'Snap-On Incorporated',
    'S1NP34': 'Synopsys, Inc.',
    'S1OU34': 'Southwest Airlines Co.',
    'S1PO34': 'Spotify Technology S.A.',
    'S1RE34': 'Sempra',
    'S1TX34': 'Seagate Technology Holdings PLC',
    'S1WK34': 'Stanley Black & Decker, Inc.',
    'S1YY34': 'Sysco Corporation',
    'S2CH34': 'Sociedad Quimica y Minera de Chile SA SOQUIMICH ADR',
    'S2EA34': 'Sea Limited ADR A',
    'S2ED34': 'SolarEdge Technologies, Inc.',
    'S2FM34': 'Sprouts Farmers Market, Inc.',
    'S2GM34': 'Sigma Lithium Corporation',
    'S2HO34': 'Shopify, Inc.',
    'S2NA34': 'Snap, Inc.',
    'S2NW34': 'Snowflake, Inc.',
    'S2TA34': 'STAG Industrial, Inc.',
    'S2UI34': 'Sun Communities, Inc.',
    'S2YN34': 'Synaptics Inc',
    'SAPP34': 'SAP SE ADR',
    'SBUB34': 'Starbucks Corporation',
    'SCHW34': 'Charles Schwab Corp',
    'SIVR39': 'abrdn Silver ETF Trust',
    'SLBG34': 'SLB Limited',
    'SLXB39': 'VanEck Steel ETF',
    'SMIN39': 'iShares MSCI India Small Cap Index Fund',
    'SNEC34': 'Sony Group Corporation ADR',
    'SOLN39': '21Shares Ltd ETP',
    'SPGI34': 'S&P Global Inc',
    'SSFO34': 'CRM',
    'STMN34': 'STMicroelectronics NV ADR',
    'STOC34': 'StoneCo Ltd.',
    'STZB34': 'Constellation Brands, Inc.',
    'T1AL34': 'TAL Education Group ADR A',
    'T1AM34': 'Atlassian Corp',
    'T1EV34': 'Teva Pharmaceutical Industries Ltd',
    'T1LK34': 'PT Telkom Indonesia (Persero) TbkADR B',
    'T1MU34': 'T-Mobile US, Inc.',
    'T1OW34': 'American Tower Corporation',
    'T1RI34': 'TripAdvisor, Inc.',
    'T1SC34': 'Tractor Supply Company',
    'T1SO34': 'Southern Company',
    'T1TW34': 'Take-Two Interactive Software, Inc.',
    'T1WL34': 'Twilio, Inc.',
    'T2DH34': 'Teladoc Health, Inc.',
    'T2ER34': 'Teradyne, Inc.',
    'T2RM34': 'Trimble Inc',
    'T2TD34': 'Trade Desk, Inc.',
    'T2YL34': 'Tyler Technologies Inc',
    'TAKP34': 'Takeda Pharmaceutical Co. Ltd.',
    'TBIL39': 'Global X 1-3 Month T-Bill ETF',
    'TMCO34': 'Toyota Motor Corp ADR',
    'TMOS34': 'TMO',
    'TOPB39': 'iShares Top 20 US Stocks ETF',
    'TPRY34': 'Tapestry Inc',
    'TRVC34': 'Travelers Companies Inc',
    'TSLA34': 'Tesla, Inc.',
    'TSMC34': 'Taiwan Semiconductor Manufacturing Co., Ltd. ADR',
    'TSNF34': 'Tyson Foods, Inc.',
    'TXSA34': 'Ternium S.A. ADR',
    'U1AI34': 'Under Armour, Inc.',
    'U1AL34': 'United Airlines Holdings, Inc.',
    'U1BE34': 'Uber Technologies, Inc.',
    'U1DR34': 'UDR, Inc.',
    'U1HS34': 'Universal Health Services, Inc.',
    'U1RI34': 'United Rentals, Inc.',
    'U2PS34': 'Upstart Holdings, Inc.',
    'U2PW34': 'Upwork, Inc.',
    'U2ST34': 'Unity Software, Inc.',
    'U2TH34': 'United Therapeutics Corporation',
    'UBSG34': 'UBS Group AG',
    'ULEV34': 'Unilever PLC ADR',
    'UNHH34': 'UNH',
    'UPAC34': 'Union Pacific Corp',
    'USBC34': 'U.S. Bancorp',
    'V1MC34': 'Vulcan Materials Company',
    'V1NO34': 'Vornado Realty Trust',
    'V1OD34': 'Vodafone Group Public Limited Company',
    'V1RS34': 'Verisk Analytics, Inc.',
    'V1RT34': 'Vertiv Holdings LLC',
    'V1ST34': 'Vistra Corp',
    'V1TA34': 'Ventas, Inc.',
    'V2EE34': 'Veeva Systems Inc',
    'V2TX34': 'VTEX',
    'VERZ34': 'VZ',
    'VISA34': 'V',
    'VLOE34': 'Valero Energy Corp',
    'VRSN34': 'VeriSign, Inc.',
    'W1BD34': 'Warner Bros. Discovery, Inc.',
    'W1BO34': 'Weibo Corp.',
    'W1DC34': 'Western Digital Corporation',
    'W1EL34': 'Welltower Inc.',
    'W1HR34': 'Whirlpool Corporation',
    'W1MB34': 'Williams Companies, Inc.',
    'W1MC34': 'Waste Management, Inc.',
    'W1MG34': 'Warner Music Group Corp.',
    'W1YC34': 'Weyerhaeuser Company',
    'W2ST34': 'West Pharmaceutical Services Inc',
    'W2YF34': 'Wayfair, Inc.',
    'WABC34': 'Western Alliance Bancorp',
    'WALM34': 'WMT',
    'WFCO34': 'WFC',
    'WUNI34': 'WU',
    'X1YZ34': 'Block, Inc.',
    'XPBR31': 'XP Inc.',
    'Y2PF34': 'YPF SA',
    'YUMR34': 'Yum! Brands, Inc.',
    'Z1BR34': 'Zebra Technologies Corporation',
    'Z1OM34': 'Zoom Communications, Inc.',
    'Z1TA34': 'Zeta Global Holdings Corp.',
    'Z1TS34': 'Zoetis, Inc.',
    'Z2LL34': 'Zillow Group, Inc.',
    'Z2SC34': 'Zscaler, Inc.',
    'A1CR34': 'Amcor PLC',
    'A1DM34': 'Archer-Daniels-Midland Company',
    'A1EE34': 'Ameren Corporation',
    'A1EG34': 'Aegon Ltd.',
    'A1EN34': 'Alliant Energy Corporation',
    'A1GI34': 'Agilent Technologies, Inc.',
    'A1GN34': 'Allegion plc',
    'A1JG34': 'Arthur J. Gallagher & Co.',
    'A1LG34': 'Align Technology, Inc.',
    'A1LN34': 'Alnylam Pharmaceuticals, Inc.',
    'A1ME34': 'AMETEK, Inc.',
    'A1NS34': 'ANSYS, Inc.',
    'A1ON34': 'Aon plc',
    'A1OS34': 'A. O. Smith Corporation',
    'A1PA34': 'APA Corporation',
    'A1PD34': 'Air Products and Chemicals, Inc.',
    'A1RC34': 'Arcos Dorados Holdings Inc.',
    'A1SN34': 'Ascendis Pharma A/S',
    'A1TM34': 'Atmos Energy Corporation',
    'A1TT34': 'The Allstate Corporation',
    'A1UT34': 'Autodesk, Inc.',
    'A1VY34': 'Avery Dennison Corporation',
    'A1YX34': 'Alteryx, Inc.',
    'A2FY34': 'Afya Limited',
    'A2LC34': 'Alcon Inc.',
    'A2RE34': 'Ares Management Corporation',
    'ABNB34': 'Airbnb, Inc.',
    'ADPR34': 'Automatic Data Processing, Inc.',
    'AETH39': '21Shares Ethereum Staking ETP',
    'ANGV39': 'VanEck Fallen Angel High Yield Bond ETF',
    'ARM334': 'Arm Holdings plc',
    'AXRP39': '21Shares XRP ETP',
    'AZOI34': 'AutoZone, Inc.',
    'B1BT34': 'Truist Financial Corporation',
    'B1DX34': 'Becton, Dickinson and Company',
    'B1GN34': 'BeiGene, Ltd.',
    'B1KR34': 'Baker Hughes Company',
    'B1ME34': 'BeOne Medicines Ltd.',
    'BICI39': 'iShares Bitcoin Trust ETF',
    'CFLT34': 'Confluent, Inc.',
    'COIN34': 'Coinbase Global, Inc.',
    'CRWD34': 'CrowdStrike Holdings, Inc.',
    'CRYP39': 'iShares Blockchain and Tech ETF',
    'DDOG34': 'Datadog, Inc.',
    'DKNG34': 'DraftKings Inc.',
    'ETHE39': 'iShares Ethereum Trust ETF',
    'FTNT34': 'Fortinet, Inc.',
    'HOOD34': 'Robinhood Markets, Inc.',
    'MNDB34': 'MongoDB, Inc.',
    'NET234': 'Cloudflare, Inc.',
    'PANW34': 'Palo Alto Networks, Inc.',
    'PATH34': 'UiPath Inc.',
    'RDDT34': 'Reddit, Inc.',
    'RKLB34': 'Rocket Lab USA, Inc.',
    'SMCI34': 'Super Micro Computer, Inc.',
    'SNOW34': 'Snowflake Inc.',
    'ZS1234': 'Zscaler, Inc.',
}


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_dados_fundamentalistas(ticker_bdr):
    """
    Busca dados fundamentalistas com fallback em cascata:
    1. Yahoo Finance com ticker US mapeado (empresa mãe)
    2. Yahoo Finance com variantes do ticker (sufixo .SA removido, etc.)
    3. OpenBB / FMP com chave configurada
    4. BRAPI como último recurso
    """
    ticker_us = mapear_ticker_us(ticker_bdr)

    def _score_from_yf_info(info, fonte_label, ticker_label):
        """Processa info do yFinance e devolve dict padronizado ou None."""
        if not info or len(info) < 5:
            return None
        # Aceita mesmo sem marketCap — basta ter algum dado útil
        if not any([
            info.get('marketCap'),
            info.get('trailingPE'),
            info.get('forwardPE'),
            info.get('revenueGrowth'),
        ]):
            return None

        score = 50
        det = {}

        # P/E
        pe = info.get('trailingPE') or info.get('forwardPE')
        if pe and isinstance(pe, (int, float)):
            det['pe_ratio'] = {'valor': round(pe, 2), 'pontos': 0, 'criterio': ''}
            if 10 <= pe <= 25:   score += 15; det['pe_ratio'].update(pontos=15, criterio='Ótimo (10-25)')
            elif 5 <= pe <= 35:  score += 10; det['pe_ratio'].update(pontos=10, criterio='Bom (5-10 ou 25-35)')
            elif pe < 5:         score +=  5; det['pe_ratio'].update(pontos=5,  criterio='Baixo (<5)')
            elif pe > 50:        score -= 10; det['pe_ratio'].update(pontos=-10, criterio='Muito alto (>50)')
            else:                              det['pe_ratio']['criterio'] = 'Regular (35-50)'
        else:
            det['pe_ratio'] = {'valor': None, 'pontos': 0, 'criterio': ''}

        # Dividend Yield
        dy = info.get('dividendYield')
        if dy and isinstance(dy, (int, float)):
            det['dividend_yield'] = {'valor': dy, 'pontos': 0, 'criterio': ''}
            if dy > 0.04:   score += 10; det['dividend_yield'].update(pontos=10, criterio='Excelente (>4%)')
            elif dy > 0.02: score +=  5; det['dividend_yield'].update(pontos=5,  criterio='Bom (>2%)')
            else:                        det['dividend_yield']['criterio'] = 'Baixo (<2%)'
        else:
            det['dividend_yield'] = {'valor': None, 'pontos': 0, 'criterio': ''}

        # Revenue Growth
        rg = info.get('revenueGrowth')
        if rg and isinstance(rg, (int, float)):
            det['revenue_growth'] = {'valor': rg, 'pontos': 0, 'criterio': ''}
            if rg > 0.20:    score += 15; det['revenue_growth'].update(pontos=15,  criterio='Excelente (>20%)')
            elif rg > 0.10:  score += 10; det['revenue_growth'].update(pontos=10,  criterio='Muito bom (>10%)')
            elif rg > 0.05:  score +=  5; det['revenue_growth'].update(pontos=5,   criterio='Bom (>5%)')
            elif rg < -0.10: score -= 10; det['revenue_growth'].update(pontos=-10, criterio='Negativo (<-10%)')
            else:                         det['revenue_growth']['criterio'] = 'Estável'
        else:
            det['revenue_growth'] = {'valor': None, 'pontos': 0, 'criterio': ''}

        # Recomendação
        rec = info.get('recommendationKey', '')
        pts_rec = {'strong_buy': 10, 'buy': 5, 'hold': 0, 'sell': -5, 'strong_sell': -10}
        crit_rec = {'strong_buy': 'Compra Forte', 'buy': 'Compra', 'hold': 'Manter',
                    'sell': 'Venda', 'strong_sell': 'Venda Forte'}
        score += pts_rec.get(rec, 0)
        det['recomendacao'] = {
            'valor': rec,
            'pontos': pts_rec.get(rec, 0),
            'criterio': crit_rec.get(rec, rec.replace('_', ' ').title() if rec else ''),
        }

        # Market Cap
        mc = info.get('marketCap')
        if mc and isinstance(mc, (int, float)):
            det['market_cap'] = {'valor': mc, 'pontos': 0, 'criterio': ''}
            if mc > 1e12:    score += 10; det['market_cap'].update(pontos=10, criterio='Mega Cap (>$1T)')
            elif mc > 100e9: score +=  5; det['market_cap'].update(pontos=5,  criterio='Large Cap (>$100B)')
            elif mc > 10e9:               det['market_cap']['criterio'] = 'Mid Cap (>$10B)'
            else:                         det['market_cap']['criterio'] = 'Small Cap (<$10B)'
        else:
            det['market_cap'] = {'valor': None, 'pontos': 0, 'criterio': ''}

        score = max(0, min(100, score))

        return {
            'fonte': fonte_label,
            'ticker_fonte': ticker_label,
            'score': score,
            'detalhes': det,
            'pe_ratio':       det['pe_ratio']['valor'],
            'dividend_yield': det['dividend_yield']['valor'],
            'market_cap':     det['market_cap']['valor'],
            'revenue_growth': det['revenue_growth']['valor'],
            'recomendacao':   det['recomendacao']['valor'],
            'setor':          info.get('sector', 'N/A'),
        }

    # ------------------------------------------------------------------
    # TENTATIVA 1: Yahoo Finance — busca pelo NOME da empresa mãe
    # ------------------------------------------------------------------
    # Esta é a abordagem mais confiável: usa o nome completo da empresa
    # para encontrar o ticker correto no Yahoo Finance, independente
    # de erros no BDR_TO_US_MAP.
    try:
        nome_empresa = NOMES_BDRS.get(ticker_bdr, '')
        # Remove sufixos comuns de BDRs (ADR, PLC, Inc., Corp., etc.)
        # para melhorar a precisão da busca
        nome_limpo = nome_empresa
        for sufixo in [' ADR', ' ADS', ' Ordinary Shares', ' Class A', ' Class B',
                       ' Class C', ' A Shares', ' B Shares']:
            nome_limpo = nome_limpo.replace(sufixo, '')
        nome_limpo = nome_limpo.strip()

        if nome_limpo:
            try:
                resultado_busca = yf.Search(nome_limpo, max_results=5)
                quotes = resultado_busca.quotes if hasattr(resultado_busca, 'quotes') else []
                # Filtra apenas ações US (exchange NYSE, NASDAQ, etc.)
                tickers_encontrados = []
                for q in quotes:
                    tipo = q.get('quoteType', '')
                    exchange = q.get('exchange', '')
                    symbol = q.get('symbol', '')
                    # Aceita ações e ADRs em bolsas americanas
                    if tipo in ('EQUITY',) and '.' not in symbol and exchange in (
                        'NMS', 'NYQ', 'NGM', 'NCM', 'ASE', 'PCX', 'BTS', 'NAS', 'NYSE', 'NASDAQ'
                    ):
                        tickers_encontrados.append(symbol)

                for t in tickers_encontrados[:3]:  # testa até 3 candidatos
                    try:
                        info = yf.Ticker(t).info
                        resultado = _score_from_yf_info(info, f'Yahoo Finance — {t} ({nome_limpo})', t)
                        if resultado:
                            return resultado
                    except Exception:
                        continue
            except Exception:
                pass
    except Exception:
        pass

    # ------------------------------------------------------------------
    # TENTATIVA 2: Yahoo Finance — ticker US do mapa (fallback direto)
    # ------------------------------------------------------------------
    try:
        tickers_tentar = [ticker_us]
        if '-' in ticker_us:
            tickers_tentar.append(ticker_us.replace('-', '.'))

        for t in tickers_tentar:
            try:
                info = yf.Ticker(t).info
                resultado = _score_from_yf_info(info, f'Yahoo Finance — {t}', t)
                if resultado:
                    return resultado
            except Exception:
                continue
    except Exception:
        pass

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # TENTATIVA 3: OpenBB / FMP — empresa mãe
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    try:
        info_obb = buscar_dados_openbb(ticker_us)
        resultado = _score_from_yf_info(info_obb, f'OpenBB / FMP — {ticker_us}', ticker_us)
        if resultado:
            return resultado
    except Exception:
        pass

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # TENTATIVA 4: BRAPI — BDR na B3 (último recurso)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    try:
        dados_brapi = buscar_dados_brapi(ticker_bdr)
        if dados_brapi:
            score, detalhes = calcular_score_brapi(dados_brapi)
            return {
                'fonte': 'BRAPI (BDR na B3)',
                'ticker_fonte': ticker_bdr,
                'score': score,
                'detalhes': detalhes,
                'pe_ratio': None,
                'dividend_yield': None,
                'market_cap': dados_brapi.get('market_cap'),
                'revenue_growth': None,
                'recomendacao': None,
                'setor': dados_brapi.get('setor', 'N/A'),
                'volume_b3': dados_brapi.get('volume'),
            }
    except Exception:
        pass

    return None
