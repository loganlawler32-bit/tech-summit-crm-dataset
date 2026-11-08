#!/usr/bin/env python3
"""
Synthetic Salesforce CRM dataset generator
==========================================

Fictional company : Altura Cloud Systems (B2B SaaS platform + services + edge hardware)
Time span         : FY2021 - FY2025 (Jan 1 2021 -> Dec 31 2025), snapshot taken 2025-12-31
Story             : The company migrated from a legacy CRM into Salesforce on 2021-01-04,
                    then grew ~30%/yr. All people, companies, emails and phone numbers are fake.

Outputs (written next to this script's parent folder):
    data/*.csv                 one CSV per Salesforce object, Salesforce-style API field names
    salesforce_crm.sqlite      the same data loaded into SQLite (indexed) for easy querying
    data_summary.md            row counts + yearly KPIs computed from the generated data

Pure Python standard library; deterministic (fixed seed). Usage:
    python3 generate_salesforce_data.py [--seed N] [--scale 1.0] [--no-sqlite]
"""
import argparse
import csv
import datetime as dt
import math
import os
import random
import sqlite3
import time
import unicodedata
from collections import Counter, defaultdict
from itertools import accumulate

# --------------------------------------------------------------------------------------
# CLI / globals
# --------------------------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=20212025)
ap.add_argument("--scale", type=float, default=1.0, help="multiply record volumes")
ap.add_argument("--no-sqlite", action="store_true")
ARGS = ap.parse_args()

R = random.Random(ARGS.seed)
SCALE = ARGS.scale

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

START = dt.date(2021, 1, 1)
END = dt.date(2025, 12, 31)
SNAP = END
MIGRATION = dt.date(2021, 1, 4)
COMPANY = "Altura Cloud Systems"
COMPANY_DOMAIN = "alturacloud.com"

N_LEGACY_CUSTOMERS = int(900 * SCALE)
N_LEGACY_PROSPECTS = int(1100 * SCALE)
N_LEAD_ACCOUNTS = int(6000 * SCALE)
N_OUTBOUND_ACCOUNTS = int(4000 * SCALE)
N_OPEN_LEADS = int(69000 * SCALE)

# --------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
SFX = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
_idc = Counter()


def sfid(prefix):
    """Salesforce-style 18 character Id with a valid case-safe checksum suffix."""
    _idc[prefix] += 1
    n = 3_000_000_000 + _idc[prefix] * 7919 + R.randint(0, 7000)
    s = ""
    while n:
        n, r = divmod(n, 62)
        s = B62[r] + s
    base = prefix + "Hx0" + s.rjust(9, "0")
    suf = ""
    for i in range(3):
        chunk = base[i * 5:(i + 1) * 5]
        bits = sum(1 << j for j, c in enumerate(chunk) if "A" <= c <= "Z")
        suf += SFX[bits]
    return base + suf


def D(n):
    return dt.timedelta(days=n)


def bday(d):
    """Roll weekends forward to Monday."""
    wd = d.weekday()
    return d + D(7 - wd) if wd >= 5 else d


def bday_back(d):
    wd = d.weekday()
    return d - D(wd - 4) if wd >= 5 else d


def dtime(d, lo=13, hi=23):
    """Date -> Salesforce UTC datetime string (business hours in the Americas/EU)."""
    return f"{d.isoformat()}T{R.randint(lo, hi):02d}:{R.randint(0, 59):02d}:{R.randint(0, 59):02d}.000Z"


def after(ts, lo=1, hi=30):
    """Salesforce datetime string shifted forward a few minutes."""
    t = dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.000Z") + dt.timedelta(minutes=R.randint(lo, hi), seconds=R.randint(0, 59))
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def ds(d):
    return d.isoformat() if d else None


def tf(x):
    return "true" if x else "false"


def between(a, b):
    if b <= a:
        return a
    return a + D(R.randint(0, (b - a).days))


def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    m += 1
    last = (dt.date(y + m // 12, m % 12 + 1, 1) - D(1)).day
    return dt.date(y, m, min(d.day, last))


def quarter_end(d):
    q = (d.month - 1) // 3
    return add_months(dt.date(d.year, q * 3 + 1, 1), 3) - D(1)


def fq(d):
    return (d.month - 1) // 3 + 1


def clip(x, lo, hi):
    return max(lo, min(hi, x))


def wpick(pairs):
    items, weights = zip(*pairs.items()) if isinstance(pairs, dict) else zip(*pairs)
    return R.choices(items, weights=weights)[0]


def poisson(lam):
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(R.gauss(lam, math.sqrt(lam))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= R.random()
        if p < L:
            return k
        k += 1


def lognorm_int(median, sigma, lo, hi):
    return int(clip(round(median * math.exp(R.gauss(0, sigma))), lo, hi))


def ascii_fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def slug(s):
    return "".join(ch for ch in ascii_fold(s).lower() if ch.isalnum())


SEASON = {1: .85, 2: .92, 3: 1.08, 4: .95, 5: 1.0, 6: 1.06, 7: .86, 8: .88, 9: 1.15, 10: 1.1, 11: 1.02, 12: .78}
MONTHS = [(y, m) for y in range(START.year, END.year + 1) for m in range(1, 13)]


def make_cum(growth):
    return list(accumulate(growth ** ((y - START.year) + (m - 1) / 12) * SEASON[m] for y, m in MONTHS))


def growth_date(cum):
    y, m = R.choices(MONTHS, cum_weights=cum)[0]
    last = (add_months(dt.date(y, m, 1), 1) - D(1)).day
    return min(bday(dt.date(y, m, R.randint(1, last))), SNAP)


class Out:
    """Streaming CSV writer (keys beginning with '_' are private and never written)."""

    def __init__(self, name, fields):
        self.name, self.fields, self.n = name, fields, 0
        self.f = open(os.path.join(DATA_DIR, name + ".csv"), "w", newline="", encoding="utf-8")
        self.w = csv.DictWriter(self.f, fieldnames=fields, extrasaction="ignore")
        self.w.writeheader()

    def add(self, row):
        self.w.writerow(row)
        self.n += 1

    def close(self):
        self.f.close()


def write_all(name, fields, rows):
    o = Out(name, fields)
    for r in rows:
        o.add(r)
    o.close()
    return o.n


# --------------------------------------------------------------------------------------
# Reference data: names, geography, industries
# --------------------------------------------------------------------------------------
NAMES = {
    "anglo": ("James Mary Michael Jennifer David Linda Robert Patricia John Elizabeth William Susan Richard Jessica "
              "Thomas Sarah Christopher Karen Daniel Lisa Matthew Nancy Anthony Emily Mark Ashley Andrew Michelle "
              "Joshua Amanda Kevin Melissa Brian Rebecca Ryan Laura Jason Rachel Justin Megan Brandon Lauren Eric "
              "Hannah Tyler Olivia Scott Emma Gregory Chloe Benjamin Grace Samuel Natalie Patrick Kayla Nathan "
              "Abigail Taylor Jordan Morgan Casey Alex Jamie Avery Riley Quinn Cameron Dylan Ethan Madison Caleb "
              "Sophie Owen Claire Lucas Allison Connor Erin Heather Adam Kristen Sean Victoria Derek Brooke",
              "Smith Johnson Williams Brown Jones Miller Davis Wilson Anderson Taylor Thomas Moore Jackson Martin "
              "Thompson White Harris Clark Lewis Robinson Walker Young Allen King Wright Scott Hill Green Adams Baker "
              "Nelson Carter Mitchell Roberts Turner Phillips Campbell Parker Evans Edwards Collins Stewart Morris "
              "Murphy Cook Rogers Reed Bailey Bell Cooper Richardson Cox Howard Ward Peterson Gray Watson Brooks "
              "Kelly Sanders Price Bennett Wood Barnes Ross Henderson Coleman Jenkins Perry Powell Long Patterson "
              "Hughes Butler Simmons Foster Bryant Russell Griffin Hayes Myers Ford Hamilton Graham Sullivan Wallace "
              "Woods Cole West Owens Reynolds Fisher Ellis Harrison Gibson McDonald Marshall Murray O'Brien Kennedy "
              "Wells Fletcher Doyle Burke Lawson Holt Spencer Brennan"),
    "hispanic": ("Carlos María José Ana Luis Sofía Javier Lucía Miguel Valentina Diego Camila Alejandro Isabella "
                 "Fernando Gabriela Ricardo Daniela Andrés Mariana Pablo Paula Sergio Carmen Jorge Elena Raúl "
                 "Laura Manuel Adriana Mateo Ximena Emilio Renata",
                 "García Rodríguez Martínez Hernández López González Pérez Sánchez Ramírez Torres Flores Rivera "
                 "Gómez Díaz Morales Reyes Cruz Ortiz Gutiérrez Chávez Ramos Vargas Castillo Jiménez Moreno Romero "
                 "Herrera Medina Aguilar Vega Navarro Delgado Castro Ruiz"),
    "portuguese": ("João Ana Pedro Mariana Lucas Beatriz Gabriel Larissa Rafael Fernanda Thiago Camila Bruno "
                   "Juliana Mateus Letícia Gustavo Carolina Felipe Amanda Rodrigo Patrícia",
                   "Silva Santos Oliveira Souza Lima Pereira Ferreira Costa Rodrigues Almeida Nascimento Carvalho "
                   "Araújo Ribeiro Barbosa Rocha Gomes Martins Cardoso Teixeira Moura Correia"),
    "german": ("Lukas Anna Maximilian Lena Felix Laura Jonas Julia Leon Sophie Paul Lea Tobias Katharina Florian "
               "Johanna Sebastian Miriam Stefan Sabine Matthias Petra Andreas Claudia Jan Nina Markus Kerstin",
               "Müller Schmidt Schneider Fischer Weber Meyer Wagner Becker Schulz Hoffmann Schäfer Koch Bauer Richter "
               "Klein Wolf Schröder Neumann Schwarz Zimmermann Braun Krüger Hofmann Hartmann Lange Werner Vogel"),
    "french": ("Louis Camille Hugo Léa Thomas Chloé Antoine Manon Julien Inès Nicolas Sarah Pierre Juliette Mathieu "
               "Claire Alexandre Émilie Maxime Pauline Olivier Céline Théo Margaux",
               "Martin Bernard Dubois Thomas Robert Richard Petit Durand Leroy Moreau Simon Laurent Lefebvre Michel "
               "Fournier Girard Bonnet Dupont Lambert Fontaine Rousseau Vincent Faure Mercier Blanc Guérin Chevalier"),
    "dutch": ("Daan Emma Sem Julia Lucas Sophie Levi Tess Thijs Fleur Bram Anouk Ruben Lotte Jesse Eva Niels Sanne",
              "de_Jong Jansen de_Vries van_den_Berg van_Dijk Bakker Visser Smit Meijer de_Boer Mulder de_Groot Bos "
              "Vos Peters Hendriks van_Leeuwen Dekker"),
    "nordic": ("Erik Astrid Lars Ingrid Johan Freja Anders Elin Oskar Maja Nils Sara Henrik Linnea Magnus Karin",
               "Andersson Johansson Karlsson Nilsson Eriksson Larsson Olsson Persson Svensson Gustafsson Lindberg "
               "Lindqvist Berg Holm Lund Dahl"),
    "japanese": ("Haruto Yui Sota Hina Yuto Sakura Ren Aoi Kenji Yuki Takumi Mei Hiroshi Akiko Daiki Naoko Shota "
                 "Emi Kazuki Riko",
                 "Sato Suzuki Takahashi Tanaka Watanabe Ito Yamamoto Nakamura Kobayashi Kato Yoshida Yamada Sasaki "
                 "Yamaguchi Matsumoto Inoue Kimura Hayashi Shimizu Mori"),
    "indian": ("Aarav Priya Arjun Ananya Rohan Kavya Vikram Sneha Rahul Pooja Aditya Divya Karthik Neha Siddharth "
               "Meera Arun Lakshmi Rajesh Shreya Nikhil Isha Sanjay Anjali",
               "Sharma Patel Singh Kumar Gupta Reddy Iyer Nair Rao Mehta Shah Joshi Desai Menon Agarwal Verma "
               "Chopra Malhotra Bhat Pillai Krishnan Banerjee Das Kapoor"),
    "chinese": ("Wei Mei Jun Hao Xin Ming Yan Jian Hui Tao Ying Kai Lin Jia Ethan Grace Jason Michelle Vivian Kelvin",
                "Wang Li Zhang Liu Chen Yang Huang Zhao Wu Zhou Xu Sun Ma Zhu Hu Lin Tan Lim Ng Wong Lee Goh Chua Ong"),
    "arabic": ("Mohammed Fatima Ahmed Aisha Omar Layla Ali Noor Khalid Mariam Yousef Sara Hassan Huda Tariq Rania",
               "Al_Mansouri Al_Hashimi Haddad Khalil Nasser Saleh Rahman Farouk Aziz Hamdan Al_Suwaidi Mansour"),
}
NAMES = {k: ([x.replace("_", " ") for x in f.split()], [x.replace("_", " ") for x in l.split()])
         for k, (f, l) in NAMES.items()}

# country: region weights inside NA split by city; name mix; legal suffixes; tld; phone cc
COUNTRIES = {
    "United States": dict(w=46, mix={"anglo": 62, "hispanic": 13, "indian": 8, "chinese": 7, "german": 3, "french": 2, "arabic": 2, "japanese": 3},
                          sfx=["Inc.", "LLC", "Corp.", "Co."], tld=".com", cc="+1"),
    "Canada": dict(w=9, mix={"anglo": 65, "french": 15, "chinese": 10, "indian": 10}, sfx=["Inc.", "Ltd.", "Corp."], tld=".ca", cc="+1"),
    "United Kingdom": dict(w=8, mix={"anglo": 80, "indian": 12, "arabic": 4, "french": 4}, sfx=["Ltd", "PLC", "LLP"], tld=".co.uk", cc="+44"),
    "Germany": dict(w=5, mix={"german": 92, "dutch": 4, "anglo": 4}, sfx=["GmbH", "AG"], tld=".de", cc="+49"),
    "France": dict(w=3, mix={"french": 95, "arabic": 5}, sfx=["S.A.S.", "S.A."], tld=".fr", cc="+33"),
    "Netherlands": dict(w=2.2, mix={"dutch": 90, "anglo": 10}, sfx=["B.V.", "N.V."], tld=".nl", cc="+31"),
    "Ireland": dict(w=1.5, mix={"anglo": 100}, sfx=["Ltd", "DAC"], tld=".ie", cc="+353"),
    "Spain": dict(w=1.5, mix={"hispanic": 100}, sfx=["S.L.", "S.A."], tld=".es", cc="+34"),
    "Sweden": dict(w=1.2, mix={"nordic": 100}, sfx=["AB"], tld=".se", cc="+46"),
    "Switzerland": dict(w=1, mix={"german": 60, "french": 40}, sfx=["AG", "SA", "GmbH"], tld=".ch", cc="+41"),
    "United Arab Emirates": dict(w=1, mix={"arabic": 60, "indian": 30, "anglo": 10}, sfx=["LLC", "FZE"], tld=".ae", cc="+971"),
    "South Africa": dict(w=0.8, mix={"anglo": 80, "dutch": 20}, sfx=["(Pty) Ltd"], tld=".co.za", cc="+27"),
    "Australia": dict(w=5, mix={"anglo": 80, "chinese": 10, "indian": 10}, sfx=["Pty Ltd", "Ltd"], tld=".com.au", cc="+61"),
    "New Zealand": dict(w=1, mix={"anglo": 90, "chinese": 5, "indian": 5}, sfx=["Ltd", "Limited"], tld=".co.nz", cc="+64"),
    "Japan": dict(w=2, mix={"japanese": 100}, sfx=["K.K.", "Co., Ltd."], tld=".co.jp", cc="+81"),
    "Singapore": dict(w=2, mix={"chinese": 70, "indian": 20, "anglo": 10}, sfx=["Pte. Ltd."], tld=".com.sg", cc="+65"),
    "India": dict(w=2, mix={"indian": 100}, sfx=["Pvt. Ltd.", "Ltd."], tld=".in", cc="+91"),
    "Brazil": dict(w=3.5, mix={"portuguese": 100}, sfx=["Ltda.", "S.A."], tld=".com.br", cc="+55"),
    "Mexico": dict(w=2.5, mix={"hispanic": 100}, sfx=["S.A. de C.V."], tld=".com.mx", cc="+52"),
    "Chile": dict(w=0.8, mix={"hispanic": 100}, sfx=["SpA", "S.A."], tld=".cl", cc="+56"),
    "Colombia": dict(w=0.7, mix={"hispanic": 100}, sfx=["S.A.S."], tld=".com.co", cc="+57"),
    "Argentina": dict(w=0.5, mix={"hispanic": 100}, sfx=["S.A.", "S.R.L."], tld=".com.ar", cc="+54"),
}
# city, state/province, postal prefix, region, phone area
CITIES = {
    "United States": [
        ("New York", "NY", "100", "NA East", "212"), ("Boston", "MA", "021", "NA East", "617"), ("Atlanta", "GA", "303", "NA East", "404"),
        ("Miami", "FL", "331", "NA East", "305"), ("Chicago", "IL", "606", "NA East", "312"), ("Philadelphia", "PA", "191", "NA East", "215"),
        ("Charlotte", "NC", "282", "NA East", "704"), ("Washington", "DC", "200", "NA East", "202"), ("Pittsburgh", "PA", "152", "NA East", "412"),
        ("Columbus", "OH", "432", "NA East", "614"), ("Detroit", "MI", "482", "NA East", "313"), ("Nashville", "TN", "372", "NA East", "615"),
        ("Raleigh", "NC", "276", "NA East", "919"), ("Tampa", "FL", "336", "NA East", "813"), ("Minneapolis", "MN", "554", "NA East", "612"),
        ("Indianapolis", "IN", "462", "NA East", "317"), ("Baltimore", "MD", "212", "NA East", "410"), ("Hartford", "CT", "061", "NA East", "860"),
        ("San Francisco", "CA", "941", "NA West", "415"), ("Los Angeles", "CA", "900", "NA West", "213"), ("Seattle", "WA", "981", "NA West", "206"),
        ("Denver", "CO", "802", "NA West", "303"), ("Austin", "TX", "787", "NA West", "512"), ("Dallas", "TX", "752", "NA West", "214"),
        ("Houston", "TX", "770", "NA West", "713"), ("Phoenix", "AZ", "850", "NA West", "602"), ("San Diego", "CA", "921", "NA West", "619"),
        ("Portland", "OR", "972", "NA West", "503"), ("Salt Lake City", "UT", "841", "NA West", "801"), ("San Jose", "CA", "951", "NA West", "408"),
        ("Las Vegas", "NV", "891", "NA West", "702"), ("Irvine", "CA", "926", "NA West", "949"), ("Boise", "ID", "837", "NA West", "208"),
    ],
    "Canada": [("Toronto", "ON", "M5V", "NA East", "416"), ("Montreal", "QC", "H3B", "NA East", "514"), ("Ottawa", "ON", "K1P", "NA East", "613"),
               ("Vancouver", "BC", "V6B", "NA West", "604"), ("Calgary", "AB", "T2P", "NA West", "403")],
    "United Kingdom": [("London", "England", "EC2", "EMEA", "20"), ("Manchester", "England", "M1", "EMEA", "161"), ("Birmingham", "England", "B1", "EMEA", "121"),
                       ("Edinburgh", "Scotland", "EH1", "EMEA", "131"), ("Bristol", "England", "BS1", "EMEA", "117"), ("Leeds", "England", "LS1", "EMEA", "113")],
    "Germany": [("Berlin", "BE", "10", "EMEA", "30"), ("Munich", "BY", "80", "EMEA", "89"), ("Hamburg", "HH", "20", "EMEA", "40"),
                ("Frankfurt", "HE", "60", "EMEA", "69"), ("Cologne", "NW", "50", "EMEA", "221"), ("Stuttgart", "BW", "70", "EMEA", "711")],
    "France": [("Paris", "Île-de-France", "75", "EMEA", "1"), ("Lyon", "Auvergne-Rhône-Alpes", "69", "EMEA", "4"), ("Toulouse", "Occitanie", "31", "EMEA", "5"),
               ("Marseille", "Provence-Alpes-Côte d'Azur", "13", "EMEA", "4")],
    "Netherlands": [("Amsterdam", "NH", "10", "EMEA", "20"), ("Rotterdam", "ZH", "30", "EMEA", "10"), ("Utrecht", "UT", "35", "EMEA", "30"), ("Eindhoven", "NB", "56", "EMEA", "40")],
    "Ireland": [("Dublin", "Leinster", "D02", "EMEA", "1"), ("Cork", "Munster", "T12", "EMEA", "21")],
    "Spain": [("Madrid", "Madrid", "280", "EMEA", "91"), ("Barcelona", "Catalonia", "080", "EMEA", "93"), ("Valencia", "Valencia", "460", "EMEA", "96")],
    "Sweden": [("Stockholm", "Stockholm", "111", "EMEA", "8"), ("Gothenburg", "Västra Götaland", "411", "EMEA", "31")],
    "Switzerland": [("Zurich", "ZH", "80", "EMEA", "44"), ("Geneva", "GE", "12", "EMEA", "22")],
    "United Arab Emirates": [("Dubai", "Dubai", "", "EMEA", "4"), ("Abu Dhabi", "Abu Dhabi", "", "EMEA", "2")],
    "South Africa": [("Johannesburg", "Gauteng", "20", "EMEA", "11"), ("Cape Town", "Western Cape", "80", "EMEA", "21")],
    "Australia": [("Sydney", "NSW", "20", "APAC", "2"), ("Melbourne", "VIC", "30", "APAC", "3"), ("Brisbane", "QLD", "40", "APAC", "7"), ("Perth", "WA", "60", "APAC", "8")],
    "New Zealand": [("Auckland", "Auckland", "10", "APAC", "9"), ("Wellington", "Wellington", "60", "APAC", "4")],
    "Japan": [("Tokyo", "Tokyo", "100", "APAC", "3"), ("Osaka", "Osaka", "530", "APAC", "6"), ("Yokohama", "Kanagawa", "220", "APAC", "45")],
    "Singapore": [("Singapore", "", "0", "APAC", "6")],
    "India": [("Bengaluru", "Karnataka", "560", "APAC", "80"), ("Mumbai", "Maharashtra", "400", "APAC", "22"), ("Hyderabad", "Telangana", "500", "APAC", "40"),
              ("Pune", "Maharashtra", "411", "APAC", "20"), ("Chennai", "Tamil Nadu", "600", "APAC", "44")],
    "Brazil": [("São Paulo", "SP", "01", "LATAM", "11"), ("Rio de Janeiro", "RJ", "20", "LATAM", "21"), ("Belo Horizonte", "MG", "30", "LATAM", "31")],
    "Mexico": [("Mexico City", "CDMX", "06", "LATAM", "55"), ("Monterrey", "NL", "64", "LATAM", "81"), ("Guadalajara", "JAL", "44", "LATAM", "33")],
    "Chile": [("Santiago", "RM", "75", "LATAM", "2")],
    "Colombia": [("Bogotá", "Bogotá D.C.", "110", "LATAM", "1"), ("Medellín", "Antioquia", "050", "LATAM", "4")],
    "Argentina": [("Buenos Aires", "CABA", "C10", "LATAM", "11")],
}
REGION_COUNTRIES = defaultdict(list)
for _c, _cities in CITIES.items():
    for _city in _cities:
        if _c not in REGION_COUNTRIES[_city[3]]:
            REGION_COUNTRIES[_city[3]].append(_c)
REGION_W = {"NA East": 30, "NA West": 25, "EMEA": 25, "APAC": 12, "LATAM": 8}
REGION_TZ = {"NA East": "America/New_York", "NA West": "America/Los_Angeles", "EMEA": "Europe/London",
             "APAC": "Australia/Sydney", "LATAM": "America/Sao_Paulo", "Global": "America/Chicago"}
STREETS = ("Main Market Oak Pine Maple Cedar Elm Washington Park Lake Hill River Church High Mill Station Bridge "
           "Commerce Harbor Union Liberty Franklin Jefferson Madison Lincoln Spring Sunset Ridge Valley Industrial "
           "Technology Innovation Enterprise Corporate Gateway Summit Meridian Kingsway Victoria Queen King").split()
STREET_TYPES = ["St", "Ave", "Blvd", "Rd", "Way", "Dr", "Pkwy", "Ln", "Plaza", "Ct"]


def pick_city(region):
    country = wpick({c: COUNTRIES[c]["w"] for c in REGION_COUNTRIES[region]})
    city = R.choice([c for c in CITIES[country] if c[3] == region])
    return country, city


def postal(country, prefix):
    L = "ABCDEFGHJKLMNPRSTUVWXYZ"
    if country == "United States":
        return prefix + f"{R.randint(0, 99):02d}"
    if country == "Canada":
        return f"{prefix} {R.randint(1, 9)}{R.choice(L)}{R.randint(1, 9)}"
    if country == "United Kingdom":
        return f"{prefix} {R.randint(1, 9)}{R.choice(L)}{R.choice(L)}"
    if country == "Ireland":
        return f"{prefix} {R.choice(L)}{R.randint(10, 99)}{R.choice(L)}"
    if country == "Netherlands":
        return f"{prefix}{R.randint(10, 99)} {R.choice(L)}{R.choice(L)}"
    if country == "Argentina":
        return f"{prefix}{R.randint(10, 99)}{R.choice(L)}{R.choice(L)}{R.choice(L)}"
    if country == "United Arab Emirates":
        return ""
    if country == "Brazil":
        return f"{prefix}{R.randint(100, 999)}-{R.randint(100, 999)}"
    if country == "Japan":
        return f"{prefix}-{R.randint(1000, 9999)}"
    if country == "Singapore":
        return f"{R.randint(10, 82)}{R.randint(1000, 9999)}"
    width = {"Germany": 5, "France": 5, "Spain": 5, "Mexico": 5, "Australia": 4, "New Zealand": 4, "Switzerland": 4,
             "South Africa": 4, "India": 6, "Sweden": 5, "Chile": 7, "Colombia": 6}.get(country, 5)
    rest = width - len(prefix)
    return prefix + "".join(str(R.randint(0, 9)) for _ in range(max(rest, 0)))


def phone(country, area):
    cc = COUNTRIES[country]["cc"]
    if cc == "+1":
        return f"({area}) 555-{R.randint(100, 9999):04d}"  # 555 = fictional exchange
    return f"{cc} {area} {R.randint(100, 999)} {R.randint(1000, 9999)}"


def person_name(country):
    pool = wpick(COUNTRIES[country]["mix"])
    f, l = NAMES[pool]
    return R.choice(f), R.choice(l)


INDUSTRIES = {
    "Technology": (14, ["Technologies", "Software", "Systems", "Digital", "Data", "Networks", "Labs", "Computing", "Analytics", "Cyber"], 260_000),
    "Financial Services": (10, ["Capital", "Financial", "Bank", "Partners", "Investments", "Wealth", "Credit Union", "Asset Management", "Payments", "Trust"], 420_000),
    "Healthcare": (9, ["Health", "Medical Group", "Healthcare", "Clinics", "Health System", "Care", "Medical Center"], 160_000),
    "Manufacturing": (10, ["Manufacturing", "Industries", "Fabrication", "Components", "Machinery", "Industrial", "Precision", "Tooling", "Metals"], 230_000),
    "Retail": (7, ["Retail", "Outfitters", "Stores", "Market", "Goods", "Brands", "Supply", "Mercantile"], 180_000),
    "Education": (4, ["University", "College", "Academy", "Learning Group", "School District", "Institute"], 90_000),
    "Government": (3, ["County", "Water Authority", "Port Authority", "Transit Authority", "Public Works"], 110_000),
    "Media & Entertainment": (4, ["Media", "Studios", "Entertainment", "Productions", "Broadcasting", "Publishing"], 250_000),
    "Telecommunications": (4, ["Telecom", "Communications", "Wireless", "Fiber", "Networks", "Connect"], 380_000),
    "Energy & Utilities": (4, ["Energy", "Power", "Utilities", "Solar", "Renewables", "Gas & Electric"], 520_000),
    "Transportation & Logistics": (6, ["Logistics", "Freight", "Transport", "Shipping", "Express", "Distribution", "Carriers"], 210_000),
    "Professional Services": (8, ["Consulting", "Advisors", "Group", "Associates", "Partners", "Solutions"], 170_000),
    "Hospitality": (3, ["Hotels", "Resorts", "Hospitality", "Restaurant Group", "Inns", "Travel"], 90_000),
    "Construction": (4, ["Construction", "Builders", "Contractors", "Engineering", "Development", "Homes"], 240_000),
    "Insurance": (4, ["Insurance", "Mutual", "Assurance", "Underwriters", "Indemnity"], 450_000),
    "Life Sciences": (3, ["Biosciences", "Pharmaceuticals", "Therapeutics", "Genomics", "Bio", "Diagnostics"], 380_000),
    "Nonprofit": (2, ["Foundation", "Alliance", "Trust", "Society", "Charities"], 80_000),
    "Consumer Goods": (5, ["Foods", "Beverages", "Home", "Apparel", "Products", "Brands"], 300_000),
}
ADJ = ("Blue Silver Golden Red North South East West Summit Pinnacle Clear Bright Iron Granite Cedar Maple Oak Pine "
       "River Lake Harbor Prairie Meadow Crest Coastal Atlas Vertex Nova Stellar Evergreen Redwood Falcon Eagle Lion "
       "Fox Bear Wolf Orion Polaris Apex Keystone Liberty Pioneer Frontier Horizon Crescent Sterling Cobalt Emerald "
       "Sapphire Amber Onyx Quartz Copper Titan Union Heritage Legacy Unity Vista Beacon Lighthouse Anchor Compass "
       "Meridian Zenith Aurora Solstice Tidewater Highland Lakeshore Riverbend Stonebridge Willow Aspen Birch Juniper "
       "Sequoia Cypress Blackstone Whitewater Greenfield Brightwater Northwind Silverline Ironwood Clearview Bluewater "
       "Fairview Westbrook Eastgate Southport Northgate Kingfisher Bluebird Hawthorne Ashford Brookfield Oakridge").split()
NOUN = ("Ridge Peak Valley Bay Point Field Stone Bridge Creek Grove Park Gate Harbor Path Forge Works Line Wave Spring "
        "Rock Hill Port Crossing Landing Haven Mill Shore Trail Hollow Mesa Canyon Summit Glen Falls Point Isle").split()
SYL1 = "Vel Nov Tri Zen Aer Cor Lum Quan Syn Ver Xan Kel Ori Pyr Sol Tor Val Neo Omn Cyr Dyn Ev Ix Lyr Mav Nex Ray Sky Tek Vox".split()
SYL2 = "ora ix ity ex ara is yn ent ium ova ia on ar us eo ana ica ent era ix".split()
_used_names, _used_domains = set(), set()


def company_name(industry, country, unique=True):
    words = INDUSTRIES[industry][1]
    for _ in range(50):
        p = R.random()
        if industry == "Education":
            n = R.choice([f"{R.choice(ADJ)} {R.choice(NOUN)} {R.choice(words)}", f"{R.choice(ADJ)} {R.choice(words)}"])
        elif industry == "Government":
            n = f"{R.choice(ADJ)} {R.choice(NOUN)} {R.choice(words)}"
        elif p < 0.38:
            n = f"{R.choice(ADJ)} {R.choice(NOUN)} {R.choice(words)}"
        elif p < 0.60:
            n = f"{R.choice(ADJ)} {R.choice(words)}"
        elif p < 0.80:
            ln = person_name(country)[1]
            n = f"{ln} {R.choice(words)}" if R.random() < .7 else f"{ln} & {person_name(country)[1]} {R.choice(words)}"
        else:
            n = R.choice(SYL1) + R.choice(SYL2)
            if R.random() < .6:
                n += " " + R.choice(words)
        if industry not in ("Education", "Government", "Nonprofit") and R.random() < .45:
            n += " " + R.choice(COUNTRIES[country]["sfx"])
        if not unique or n not in _used_names:
            _used_names.add(n)
            return n
    n = f"{n} {R.randint(2, 99)}"
    _used_names.add(n)
    return n


LEGAL = {s for c in COUNTRIES.values() for s in c["sfx"]}


def domain_for(name, country, industry):
    base = name
    for s in sorted(LEGAL, key=len, reverse=True):
        if base.endswith(" " + s):
            base = base[: -len(s) - 1]
    parts = [slug(w) for w in base.replace("&", " ").split()]
    d = "".join(parts)[:22] or "company"
    tld = COUNTRIES[country]["tld"]
    if industry in ("Government", "Nonprofit", "Education") and tld == ".com":
        tld = ".org"
    dom, i = d + tld, 2
    while dom in _used_domains:
        dom, i = f"{d}{i}{tld}", i + 1
    _used_domains.add(dom)
    return dom


TITLES = [
    # title, department, level
    ("Chief Executive Officer", "Executive", "C-Level"), ("Chief Technology Officer", "IT", "C-Level"),
    ("Chief Information Officer", "IT", "C-Level"), ("Chief Financial Officer", "Finance", "C-Level"),
    ("Chief Operating Officer", "Operations", "C-Level"), ("Chief Data Officer", "Data & Analytics", "C-Level"),
    ("Chief Information Security Officer", "Security", "C-Level"),
    ("VP of IT", "IT", "VP"), ("VP of Engineering", "Engineering", "VP"), ("VP of Operations", "Operations", "VP"),
    ("VP of Finance", "Finance", "VP"), ("VP of Digital Transformation", "IT", "VP"), ("VP of Sales Operations", "Sales", "VP"),
    ("VP of Data & Analytics", "Data & Analytics", "VP"),
    ("Director of IT", "IT", "Director"), ("Director of Infrastructure", "IT", "Director"), ("Director of Engineering", "Engineering", "Director"),
    ("Director of Business Intelligence", "Data & Analytics", "Director"), ("Director of Procurement", "Procurement", "Director"),
    ("Director of Security", "Security", "Director"), ("Director of Operations", "Operations", "Director"),
    ("Director of Marketing Operations", "Marketing", "Director"),
    ("IT Manager", "IT", "Manager"), ("Engineering Manager", "Engineering", "Manager"), ("Analytics Manager", "Data & Analytics", "Manager"),
    ("Procurement Manager", "Procurement", "Manager"), ("Operations Manager", "Operations", "Manager"), ("Security Manager", "Security", "Manager"),
    ("Finance Manager", "Finance", "Manager"), ("Marketing Operations Manager", "Marketing", "Manager"),
    ("Systems Administrator", "IT", "Individual Contributor"), ("Solutions Architect", "Engineering", "Individual Contributor"),
    ("Data Engineer", "Data & Analytics", "Individual Contributor"), ("Business Analyst", "Operations", "Individual Contributor"),
    ("Software Engineer", "Engineering", "Individual Contributor"), ("Security Analyst", "Security", "Individual Contributor"),
    ("Procurement Specialist", "Procurement", "Individual Contributor"), ("Data Analyst", "Data & Analytics", "Individual Contributor"),
    ("Platform Administrator", "IT", "Individual Contributor"), ("Financial Analyst", "Finance", "Individual Contributor"),
]
LEVEL_W = {"SMB": {"C-Level": 30, "VP": 15, "Director": 20, "Manager": 20, "Individual Contributor": 15},
           "Mid-Market": {"C-Level": 10, "VP": 15, "Director": 28, "Manager": 27, "Individual Contributor": 20},
           "Enterprise": {"C-Level": 5, "VP": 12, "Director": 28, "Manager": 30, "Individual Contributor": 25}}
TITLES_BY_LEVEL = defaultdict(list)
for _t in TITLES:
    TITLES_BY_LEVEL[_t[2]].append(_t)


def pick_title(seg):
    return R.choice(TITLES_BY_LEVEL[wpick(LEVEL_W[seg])])


# --------------------------------------------------------------------------------------
# Users (sales org with growth + attrition)
# --------------------------------------------------------------------------------------
USERS, POOL = [], defaultdict(list)
REGIONS = ["NA East", "NA West", "EMEA", "APAC", "LATAM"]
REGION_HOME = {"NA East": ["United States"], "NA West": ["United States"], "EMEA": ["United Kingdom", "Germany", "France", "Netherlands", "Ireland"],
               "APAC": ["Australia", "Singapore", "India", "Japan"], "LATAM": ["Brazil", "Mexico"], "Global": ["United States"]}
_user_emails = set()


def new_user(role, title, dept, region, seg, hire, term, manager, profile):
    country = R.choice(REGION_HOME[region])
    f, l = person_name(country)
    base = f"{slug(f)}.{slug(l)}"
    email, i = f"{base}@{COMPANY_DOMAIN}", 2
    while email in _user_emails:
        email, i = f"{base}{i}@{COMPANY_DOMAIN}", i + 1
    _user_emails.add(email)
    created = max(hire, MIGRATION)
    u = dict(Id=sfid("005"), FirstName=f, LastName=l, Name=f"{f} {l}", Alias=(slug(f)[:1] + slug(l)[:7])[:8],
             Email=email, Username=email.replace("@", "@crm."), Title=title, Department=dept, Division=region,
             UserRole=f"{role} - {region}" + (f" {seg}" if seg else ""), Profile=profile,
             ManagerId=manager["Id"] if manager else None, IsActive=tf(term is None),
             CreatedDate=dtime(created), Hire_Date__c=ds(hire), Termination_Date__c=ds(term),
             Region__c=region, Segment__c=seg, TimeZoneSidKey=REGION_TZ[region],
             _role=role, _region=region, _seg=seg, _hire=hire, _term=term)
    USERS.append(u)
    for key in ((role, region, seg), (role, region), (role,)):
        POOL[key].append(u)
    return u


def staff(role, title, dept, region, seg, n_start, n_end, manager, profile, tenure_yrs=2.8):
    for i in range(n_end):
        if i < n_start:
            hire = START - D(R.randint(60, 2200))
        else:
            frac = (i - n_start + R.random()) / max(1, n_end - n_start)
            hire = bday(START + D(int(frac * (END - START).days * 0.95)))
        while hire <= SNAP:
            tenure = int(R.expovariate(1 / (tenure_yrs * 365))) + 150
            term = hire + D(tenure)
            if term > SNAP:
                term = None
            if i < n_start and term and term < START:  # pre-CRM leavers never existed in Salesforce
                hire = term + D(R.randint(20, 75))
                continue
            new_user(role, title, dept, region, seg, hire, term, manager, profile)
            if term is None:
                break
            hire = bday(term + D(R.randint(20, 75)))


def active(u, d):
    return u["_hire"] <= d and (u["_term"] is None or d < u["_term"])


def pick(role, region=None, seg=None, d=SNAP):
    for key in ((role, region, seg), (role, region), (role,)):
        cands = POOL.get(key)
        if cands:
            act = [u for u in cands if active(u, d)]
            if act:
                return R.choice(act)
    cands = POOL[(role,)]
    return min(cands, key=lambda u: abs((u["_hire"] - d).days))


def build_users():
    old = lambda: START - D(R.randint(400, 3000))
    integ = new_user("System", "Integration User", "IT", "Global", None, dt.date(2020, 12, 1), None, None, "System Administrator")
    integ.update(FirstName="Integration", LastName="User", Name="Integration User", Email="integration@" + COMPANY_DOMAIN,
                 Username="integration@crm." + COMPANY_DOMAIN, Alias="integ")
    ceo = new_user("Executive", "Chief Executive Officer", "Executive", "Global", None, old(), None, None, "Executive")
    cro = new_user("Executive", "Chief Revenue Officer", "Sales", "Global", None, old(), None, ceo, "Executive")
    vp_na = new_user("VP Sales", "VP Sales, North America", "Sales", "NA East", None, old(), None, cro, "Sales Manager")
    vp_intl = new_user("VP Sales", "VP Sales, International", "Sales", "EMEA", None, dt.date(2021, 3, 1), None, cro, "Sales Manager")
    vp_cs = new_user("Executive", "VP Customer Success", "Customer Success", "Global", None, old(), None, cro, "Executive")
    vp_mkt = new_user("Executive", "VP Marketing", "Marketing", "Global", None, old(), None, ceo, "Marketing User")
    dir_sup = new_user("Support Manager", "Director of Customer Support", "Support", "Global", None, old(), None, vp_cs, "Support Manager")
    ops = new_user("Sales Ops", "Director of Revenue Operations", "Sales Operations", "Global", None, old(), None, cro, "System Administrator")
    staff("Sales Ops", "Sales Operations Analyst", "Sales Operations", "Global", None, 2, 5, ops, "Sales Operations")
    staff("Marketing", "Marketing Manager", "Marketing", "Global", None, 4, 9, vp_mkt, "Marketing User")
    caps = {  # AE seats (start, end) by region and segment
        "NA East": {"SMB": (4, 7), "Mid-Market": (4, 9), "Enterprise": (3, 7)},
        "NA West": {"SMB": (3, 6), "Mid-Market": (3, 8), "Enterprise": (2, 6)},
        "EMEA": {"SMB": (2, 5), "Mid-Market": (2, 6), "Enterprise": (1, 5)},
        "APAC": {"SMB": (1, 3), "Mid-Market": (1, 3), "Enterprise": (1, 2)},
        "LATAM": {"SMB": (1, 2), "Mid-Market": (1, 2), "Enterprise": (1, 1)},
    }
    sdr = {"NA East": (3, 8), "NA West": (3, 7), "EMEA": (2, 6), "APAC": (1, 3), "LATAM": (1, 2)}
    csm = {"NA East": (2, 6), "NA West": (2, 6), "EMEA": (1, 4), "APAC": (1, 2), "LATAM": (1, 1)}
    for reg in REGIONS:
        vp = vp_na if reg.startswith("NA") else vp_intl
        rd = new_user("RD", f"Regional Sales Director, {reg}", "Sales", reg, None, old() if reg != "LATAM" else dt.date(2021, 6, 1), None, vp, "Sales Manager")
        for seg, (a, b) in caps[reg].items():
            staff("AE", f"{'Enterprise' if seg == 'Enterprise' else seg} Account Executive", "Sales", reg, seg, a, b, rd, "Sales User")
        staff("SDR", "Sales Development Representative", "Sales Development", reg, None, *sdr[reg], rd, "Sales User", tenure_yrs=1.6)
        staff("CSM", "Customer Success Manager", "Customer Success", reg, None, *csm[reg], vp_cs, "Customer Success")
    staff("Support", "Technical Support Engineer", "Support", "Global", None, 9, 26, dir_sup, "Support Agent", tenure_yrs=2.2)
    staff("SE", "Solutions Engineer", "Sales", "Global", None, 5, 14, cro, "Sales User")
    return integ


# --------------------------------------------------------------------------------------
# Products & price books
# --------------------------------------------------------------------------------------
P = lambda code, name, fam, price, unit, rec, seat, launch=None, retire=None, cap=.40: dict(
    code=code, name=name, fam=fam, base=price, unit=unit, rec=rec, seat=seat, launch=launch, retire=retire, cap=cap)
PRODUCTS = [
    P("ALT-PLAT-STD", "Altura Platform - Standard Edition", "Platform", 300, "Seat / Year", True, True),
    P("ALT-PLAT-PRO", "Altura Platform - Professional Edition", "Platform", 600, "Seat / Year", True, True),
    P("ALT-PLAT-ENT", "Altura Platform - Enterprise Edition", "Platform", 900, "Seat / Year", True, True),
    P("ALT-PLAT-LEG", "Altura Platform - Legacy Basic", "Platform", 220, "Seat / Year", True, True, retire=dt.date(2022, 6, 30)),
    P("ALT-ANL", "Advanced Analytics Add-on", "Add-On", 150, "Seat / Year", True, True),
    P("ALT-SEC", "Security & Compliance Pack", "Add-On", 120, "Seat / Year", True, True),
    P("ALT-AI", "AI Insights Add-on", "Add-On", 200, "Seat / Year", True, True, launch=dt.date(2023, 6, 6)),
    P("ALT-COPILOT", "Altura Copilot", "Add-On", 240, "Seat / Year", True, True, launch=dt.date(2024, 9, 17)),
    P("ALT-INT", "Integration Hub", "Add-On", 12000, "Org / Year", True, False),
    P("ALT-API", "API Access Tier (per 10M calls)", "Add-On", 6000, "Block / Year", True, False),
    P("ALT-STOR", "Additional Storage (1 TB)", "Add-On", 1200, "TB / Year", True, False),
    P("ALT-SBX", "Full Copy Sandbox", "Add-On", 9000, "Org / Year", True, False),
    P("SUP-PREM", "Premium Support", "Support", 15000, "Org / Year", True, False, cap=.25),
    P("SUP-PLAT", "Platinum Support (24x7, TAM)", "Support", 45000, "Org / Year", True, False, cap=.25),
    P("TRN-ELEARN", "Altura Academy eLearning", "Training", 60, "Seat / Year", True, True),
    P("PS-IMPL-QS", "QuickStart Implementation", "Professional Services", 7500, "Package", False, False, cap=.15),
    P("PS-IMPL-STD", "Standard Implementation", "Professional Services", 35000, "Package", False, False, cap=.15),
    P("PS-IMPL-ENT", "Enterprise Implementation", "Professional Services", 90000, "Package", False, False, cap=.15),
    P("PS-MIG", "Data Migration Service", "Professional Services", 20000, "Package", False, False, cap=.15),
    P("PS-CUST", "Custom Development (per day)", "Professional Services", 1800, "Day", False, False, cap=.15),
    P("PS-HEALTH", "Annual Health Check", "Professional Services", 8000, "Package", False, False, cap=.15),
    P("TRN-ADMIN", "Admin Certification Training", "Training", 1200, "Seat", False, False, cap=.20),
    P("TRN-USER", "End-User Training Workshop", "Training", 4000, "Session", False, False, cap=.20),
    P("HW-EDGE-100", "Altura Edge Gateway 100", "Hardware", 2500, "Unit", False, False, cap=.12),
    P("HW-EDGE-500", "Altura Edge Gateway 500", "Hardware", 9500, "Unit", False, False, cap=.12),
    P("HW-SENS", "Edge Sensor Kit (10-pack)", "Hardware", 1500, "Kit", False, False, cap=.12),
    P("HW-MAINT", "Hardware Maintenance", "Hardware", 400, "Unit / Year", True, False, cap=.10),
]
PROD = {p["code"]: p for p in PRODUCTS}
EDITIONS = ["ALT-PLAT-STD", "ALT-PLAT-PRO", "ALT-PLAT-ENT", "ALT-PLAT-LEG"]
PRICEBOOKS = [  # name, effective from, multiplier
    ("FY2021-FY2022 Price List", dt.date(2021, 1, 1), 1.00),
    ("FY2023-FY2024 Price List", dt.date(2023, 1, 1), 1.06),
    ("FY2025 Price List", dt.date(2025, 1, 1), 1.10),
]


def price_mult(d):
    m = 1.0
    for _, eff, mult in PRICEBOOKS:
        if d >= eff:
            m = mult
    return m


def pb_index(d):
    i = 0
    for k, (_, eff, _) in enumerate(PRICEBOOKS):
        if d >= eff:
            i = k
    return i


def list_price(code, d):
    return round(PROD[code]["base"] * price_mult(d), 2)


def available(code, d):
    p = PROD[code]
    return (p["launch"] is None or d >= p["launch"]) and (p["retire"] is None or d <= p["retire"])


def build_products(integ):
    prows, pbrows, pberows = [], [], []
    for p in PRODUCTS:
        p["Id"] = sfid("01t")
        created = p["launch"] - D(R.randint(20, 60)) if p["launch"] else MIGRATION
        prows.append(dict(Id=p["Id"], Name=p["name"], ProductCode=p["code"], Family=p["fam"],
                          Description=f"{p['name']} ({p['unit']})", IsActive=tf(p["retire"] is None),
                          QuantityUnitOfMeasure=p["unit"], Revenue_Type__c="Recurring" if p["rec"] else "One-Time",
                          Per_Seat__c=tf(p["seat"]), Launch_Date__c=ds(p["launch"] or dt.date(2019, 1, 1)),
                          Retired_Date__c=ds(p["retire"]), Max_Discount__c=p["cap"], CreatedDate=dtime(created), CreatedById=integ["Id"]))
    std = dict(Id=sfid("01s"), Name="Standard Price Book", IsStandard="true", IsActive="true",
               Description="Standard price book (current list prices)", Effective_From__c=None, CreatedDate=dtime(MIGRATION))
    pbrows.append(std)
    for p in PRODUCTS:
        p["std_pbe"] = sfid("01u")
        pberows.append(dict(Id=p["std_pbe"], Pricebook2Id=std["Id"], Product2Id=p["Id"], ProductCode=p["code"],
                            Name=p["name"], UnitPrice=round(p["base"] * PRICEBOOKS[-1][2], 2), IsActive=tf(p["retire"] is None),
                            UseStandardPrice="false", CreatedDate=dtime(MIGRATION)))
    for name, eff, mult in PRICEBOOKS:
        pb = dict(Id=sfid("01s"), Name=name, IsStandard="false", IsActive="true", Description=f"List prices effective {eff}",
                  Effective_From__c=ds(eff), CreatedDate=dtime(max(eff - D(30), MIGRATION)))
        pbrows.append(pb)
        for p in PRODUCTS:
            pid = sfid("01u")
            p.setdefault("pbe", []).append(pid)
            pberows.append(dict(Id=pid, Pricebook2Id=pb["Id"], Product2Id=p["Id"], ProductCode=p["code"], Name=p["name"],
                                UnitPrice=round(p["base"] * mult, 2), IsActive=tf(p["retire"] is None or p["retire"] >= eff),
                                UseStandardPrice="false", CreatedDate=pb["CreatedDate"]))
    PRICEBOOK_IDS[:] = [r["Id"] for r in pbrows[1:]]
    return prows, pbrows, pberows


PRICEBOOK_IDS = []

# --------------------------------------------------------------------------------------
# Campaigns
# --------------------------------------------------------------------------------------
CAMPAIGNS = []
CAMP_BY_TYPE = defaultdict(list)
SUMMITS = {2021: ("Virtual", dt.date(2021, 9, 14)), 2022: ("San Francisco", dt.date(2022, 9, 13)),
           2023: ("Austin", dt.date(2023, 9, 12)), 2024: ("Las Vegas", dt.date(2024, 9, 17)), 2025: ("Chicago", dt.date(2025, 9, 16))}
WORLD_TOUR = {2022: ["London", "Sydney"], 2023: ["London", "Sydney", "Toronto", "São Paulo"],
              2024: ["London", "Sydney", "Toronto", "São Paulo", "Tokyo", "Singapore"],
              2025: ["London", "Sydney", "Toronto", "São Paulo", "Tokyo", "Singapore", "Frankfurt"]}
TOUR_REGION = {"London": "EMEA", "Frankfurt": "EMEA", "Sydney": "APAC", "Tokyo": "APAC", "Singapore": "APAC",
               "Toronto": "NA East", "São Paulo": "LATAM"}
TRADE_SHOWS = ["CloudScape Expo", "DataOps World", "SecureStack Conference", "RetailNext Forum", "HealthTech Connect",
               "Industry 5.0 Summit", "FinServ Innovation Forum", "Public Sector Digital Day", "EdgeCompute Live", "Analytics Leaders Forum"]
SHOW_CITIES = ["Las Vegas", "Orlando", "New York", "San Francisco", "Chicago", "Boston", "London", "Amsterdam", "Berlin", "Austin", "Atlanta", "Toronto"]
WEBINARS = ["Modernizing Your Data Stack", "Zero-Trust Security in Practice", "From Dashboards to Decisions", "Automating Ops Workflows",
            "Scaling Analytics Across the Enterprise", "Customer Story Spotlight", "Integration Hub Deep Dive", "Admin Best Practices",
            "Total Cost of Ownership Workshop", "Edge Computing for Operations", "Governance & Compliance Made Simple",
            "Platform Roadmap Preview", "AI Insights: Getting Started", "Copilot in Action", "Building a Data Culture",
            "Migrating Off Legacy Tools", "Benchmarking Your Operations", "Executive Briefing: Digital Transformation",
            "Real-Time Monitoring with Edge Gateways", "Security Pack Walkthrough", "Driving Adoption with Altura Academy",
            "Forecasting with Advanced Analytics", "API-First Architecture", "Year in Review"]
NEWSLETTER = "Altura Monthly Newsletter"


def add_campaign(name, ctype, start, end, budget, owner, region="Global", parent=None, desc=None, expected_resp=None):
    status = "Completed" if end < SNAP else ("In Progress" if start <= SNAP else "Planned")
    actual = round(budget * R.uniform(0.85, 1.12), -2) if status == "Completed" else (round(budget * R.uniform(.3, .8), -2) if status == "In Progress" else 0)
    c = dict(Id=sfid("701"), Name=name, Type=ctype, Status=status, StartDate=ds(start), EndDate=ds(end),
             IsActive=tf(status != "Completed"), ParentId=parent["Id"] if parent else None, BudgetedCost=budget,
             ActualCost=actual, ExpectedResponse=expected_resp or R.choice([1, 2, 3, 5, 8, 10]),
             NumberSent=0, OwnerId=owner["Id"], Region__c=region, Description=desc,
             CreatedDate=dtime(max(MIGRATION, start - D(R.randint(30, 120)))),
             _start=start, _end=end, _type=ctype, _year=start.year)
    CAMPAIGNS.append(c)
    return c


def build_campaigns():
    mk = lambda d: pick("Marketing", d=d)
    for y in range(2021, 2026):
        g = 1.25 ** (y - 2021)
        city, d0 = SUMMITS[y]
        s = add_campaign(f"Altura Tech Summit {y} - {city}", "Conference", d0, d0 + D(2), round(900_000 * g, -3), mk(d0),
                         desc=f"Flagship annual customer & prospect conference ({city}).", expected_resp=25)
        s["_kind"] = "summit"
        CAMP_BY_TYPE["summit"].append(s)
        for city2 in WORLD_TOUR.get(y, []):
            dd = bday(d0 + D(R.randint(30, 75)))
            w = add_campaign(f"Tech Summit World Tour {y} - {city2}", "Conference", dd, dd, round(120_000 * g, -3), mk(dd),
                             region=TOUR_REGION[city2], parent=s, desc="Regional one-day Tech Summit event.", expected_resp=20)
            w["_kind"] = "summit_tour"
            CAMP_BY_TYPE["summit"].append(w)
        shows = R.sample(TRADE_SHOWS, 6)
        for i, show in enumerate(shows):
            dd = bday(dt.date(y, [2, 3, 5, 6, 10, 11][i], R.randint(3, 24)))
            c = add_campaign(f"{show} {y}", "Trade Show", dd, dd + D(2), round(R.uniform(60_000, 180_000) * g, -3), mk(dd),
                             desc=f"Booth sponsorship at {show} in {R.choice(SHOW_CITIES)}.", expected_resp=12)
            CAMP_BY_TYPE["Trade Show"].append(c)
        for m in range(1, 13):
            for k in range(2):
                dd = bday(dt.date(y, m, 8 if k == 0 else 22))
                topic = R.choice([t for t in WEBINARS if (("AI" not in t or dd >= dt.date(2023, 6, 1)) and ("Copilot" not in t or dd >= dt.date(2024, 9, 1)))])
                c = add_campaign(f"Webinar: {topic} ({dd.strftime('%b %Y')})", "Webinar", dd, dd, round(R.uniform(3_000, 12_000) * g, -2), mk(dd), expected_resp=15)
                CAMP_BY_TYPE["Webinar"].append(c)
            dd = dt.date(y, m, 3)
            c = add_campaign(f"{NEWSLETTER} - {dd.strftime('%b %Y')}", "Email", dd, dd + D(27), round(1500 * g, -2), mk(dd), expected_resp=3)
            CAMP_BY_TYPE["Email"].append(c)
        for q in range(1, 5):
            qs = dt.date(y, q * 3 - 2, 1)
            qe = quarter_end(qs)
            for kind, ctype, name, bud in (("Paid Search", "Advertisement", "Paid Search", 140_000),
                                           ("Content Syndication", "Advertisement", "Content Syndication", 60_000),
                                           ("Partner Referral", "Partners", "Partner Co-Marketing", 40_000),
                                           ("Outbound Prospecting", "Direct Mail", "ABM Outbound Program", 30_000)):
                c = add_campaign(f"{name} - Q{q} FY{y}", ctype, qs, qe, round(bud * g, -3), mk(qs), expected_resp=4)
                CAMP_BY_TYPE[kind].append(c)
        ys, ye = dt.date(y, 1, 1), dt.date(y, 12, 31)
        CAMP_BY_TYPE["Web"].append(add_campaign(f"Website Inbound FY{y}", "Website", ys, ye, round(200_000 * g, -3), mk(ys), expected_resp=6))
        CAMP_BY_TYPE["Customer Referral"].append(add_campaign(f"Customer Referral Program FY{y}", "Referral Program", ys, ye, round(50_000 * g, -3), mk(ys), expected_resp=30))
    for name, d0 in (("AI Insights Launch", dt.date(2023, 6, 6)), ("Altura Copilot Launch", dt.date(2024, 9, 17))):
        c = add_campaign(name, "Product Launch", d0, d0 + D(30), 250_000, mk(d0), desc="Global product launch campaign.", expected_resp=8)
        CAMP_BY_TYPE["launch"].append(c)


def campaign_on(kind, d):
    for c in CAMP_BY_TYPE.get(kind, []):
        if c["_start"] <= d <= c["_end"]:
            return c
    return None


# --------------------------------------------------------------------------------------
# Leads (sources, quality, cadence)
# --------------------------------------------------------------------------------------
LEAD_SOURCES = {  # share of all leads, conversion quality multiplier
    "Web": (22, 1.0), "Paid Search": (15, 0.7), "Content Syndication": (14, 0.45), "Webinar": (13, 0.9),
    "Trade Show": (10, 0.9), "Outbound Prospecting": (10, 1.0), "Tech Summit": (6, 1.8),
    "Partner Referral": (6, 2.0), "Customer Referral": (4, 2.6),
}
EVENT_SOURCES = {"Webinar": "Webinar", "Trade Show": "Trade Show", "Tech Summit": "summit"}
LEAD_CUM = make_cum(1.32)
ACCT_CUM = make_cum(1.30)


def lead_core(source):
    """Return (campaign, created_date) for a lead of the given source."""
    if source in EVENT_SOURCES:
        camps = [c for c in CAMP_BY_TYPE[EVENT_SOURCES[source]] if c["_end"] <= SNAP]
        w = [1.3 ** (c["_year"] - 2021) * (6 if c.get("_kind") == "summit" else 1) for c in camps]
        c = R.choices(camps, weights=w)[0]
        return c, min(bday(c["_end"] + D(R.randint(0, 9))), SNAP)
    d = growth_date(LEAD_CUM)
    c = campaign_on(source, d)
    if source == "Outbound Prospecting" and R.random() < .5:
        c = None
    return c, d


# --------------------------------------------------------------------------------------
# Main generation
# --------------------------------------------------------------------------------------
t0 = time.time()
print("Building users, products, campaigns ...")
INTEG = build_users()
PROD_ROWS, PB_ROWS, PBE_ROWS = build_products(INTEG)
build_campaigns()

ACCOUNTS, CONTACTS, LEADS, OPPS = [], [], [], []
LAST_ACT = {}
CONTACT_EMAILS = set()


def touch(rid, d):
    if d <= SNAP and (rid not in LAST_ACT or LAST_ACT[rid] < d):
        LAST_ACT[rid] = d


SEG_EMP = {"SMB": (60, .8, 10, 199), "Mid-Market": (650, .6, 200, 1999), "Enterprise": (8000, 1.0, 2000, 180000)}


def make_account(created, seg, origin, legacy=False):
    region = wpick(REGION_W)
    country, city = pick_city(region)
    industry = wpick({k: v[0] for k, v in INDUSTRIES.items()})
    emp = lognorm_int(*SEG_EMP[seg])
    name = company_name(industry, country)
    dom = domain_for(name, country, industry)
    rev = round(emp * INDUSTRIES[industry][2] * R.uniform(0.55, 1.6), -4)
    owner = pick("AE", region, seg, created)
    a = dict(Id=sfid("001"), Name=name, Type="Prospect", Industry=industry, AnnualRevenue=rev, NumberOfEmployees=emp,
             Segment__c=seg, Region__c=region,
             BillingStreet=f"{R.randint(1, 9800)} {R.choice(STREETS)} {R.choice(STREET_TYPES)}" + (f", Suite {R.randint(100, 2400)}" if R.random() < .35 else ""),
             BillingCity=city[0], BillingState=city[1], BillingPostalCode=postal(country, city[2]), BillingCountry=country,
             Phone=phone(country, city[4]) if R.random() > .04 else None, Website=f"www.{dom}",
             Ownership=wpick({"Private": 70, "Public": 18, "Subsidiary": 7, "Other": 5}) if industry not in ("Government", "Nonprofit", "Education") else "Other",
             AccountSource={"lead": None, "outbound": "Outbound Prospecting", "legacy": "Legacy CRM Migration"}[origin],
             CreatedDate=dtime(created, 10, 11) if legacy else dtime(created), CreatedById=(INTEG if legacy else owner)["Id"],
             Rating=None, Description=None, Customer_Since__c=None, Churn_Date__c=None, Current_ARR__c=0,
             Lifetime_Bookings__c=0, Health_Score__c=None, Contract_End_Date__c=None, Licensed_Seats__c=0,
             Primary_Edition__c=None, CSM__c=None,
             _created=created, _seg=seg, _region=region, _country=country, _city=city, _dom=dom, _owner=owner,
             _origin=origin, _legacy=legacy, _subs={}, _price={}, _health=clip(R.gauss(72, 16), 5, 100),
             _contacts=[], _periods=[], _arr_hist=[], _disc=None, _contract_end=None, _hw=False)
    ACCOUNTS.append(a)
    return a


def make_contact(a, created, first=None, last=None, title=None, source=None, from_lead=False):
    if first is None:
        first, last = person_name(a["_country"])
    t = title or pick_title(a["_seg"])
    base = f"{slug(first)}.{slug(last)}"
    email, i = f"{base}@{a['_dom']}", 2
    while email in CONTACT_EMAILS:
        email, i = f"{base}{i}@{a['_dom']}", i + 1
    CONTACT_EMAILS.add(email)
    city = a["_city"]
    c = dict(Id=sfid("003"), AccountId=a["Id"], FirstName=first, LastName=last, Title=t[0], Department=t[1], Level__c=t[2],
             Email=email, Phone=phone(a["_country"], city[4]) if R.random() > .12 else None,
             MobilePhone=phone(a["_country"], city[4]) if R.random() < .45 else None,
             MailingCity=city[0], MailingState=city[1], MailingCountry=a["_country"],
             LeadSource=source or (a["AccountSource"] if R.random() < .5 else None),
             OwnerId=a["_owner"]["Id"], CreatedDate=after(a["CreatedDate"]) if created == a["_created"] else dtime(created), HasOptedOutOfEmail=tf(R.random() < .07),
             DoNotCall=tf(R.random() < .03), Converted_From_Lead__c=tf(from_lead),
             _created=created, _acct=a)
    CONTACTS.append(c)
    a["_contacts"].append(c)
    return c


def add_contacts(a, n_extra):
    for _ in range(n_extra):
        d = a["_created"] if R.random() < .35 else between(a["_created"], SNAP)
        make_contact(a, bday(d) if bday(d) <= SNAP else d)


CONTACTS_PER_SEG = {"SMB": (2, 5), "Mid-Market": (4, 10), "Enterprise": (8, 20)}

# ---- Writers for large, streamed objects -------------------------------------------------
OLI_OUT = Out("OpportunityLineItem", ["Id", "OpportunityId", "Product2Id", "PricebookEntryId", "ProductCode", "Name", "Quantity",
                                      "ListPrice", "UnitPrice", "Discount", "TotalPrice", "ServiceDate", "Revenue_Type__c", "CreatedDate"])
HIST_OUT = Out("OpportunityHistory", ["Id", "OpportunityId", "StageName", "Amount", "Probability", "ExpectedRevenue", "CloseDate",
                                      "ForecastCategory", "CreatedDate", "CreatedById"])
OCR_OUT = Out("OpportunityContactRole", ["Id", "OpportunityId", "ContactId", "Role", "IsPrimary", "CreatedDate"])
TASK_OUT = Out("Task", ["Id", "Subject", "Status", "Priority", "TaskSubtype", "Type", "ActivityDate", "WhoId", "WhatId", "AccountId",
                        "OwnerId", "CallType", "CallDurationInSeconds", "CallDisposition", "IsClosed", "Description", "CreatedDate"])
EVENT_OUT = Out("Event", ["Id", "Subject", "Type", "StartDateTime", "EndDateTime", "DurationInMinutes", "ActivityDate", "Location",
                          "IsAllDayEvent", "WhoId", "WhatId", "AccountId", "OwnerId", "Description", "CreatedDate"])
CM_OUT = Out("CampaignMember", ["Id", "CampaignId", "LeadId", "ContactId", "Type", "Status", "HasResponded", "FirstRespondedDate", "CreatedDate"])
CM_STATS = defaultdict(Counter)


def add_member(camp, d, lead=None, contact=None, status="Responded"):
    responded = status not in ("Sent", "Registered", "No Show")
    CM_OUT.add(dict(Id=sfid("00v"), CampaignId=camp["Id"], LeadId=lead["Id"] if lead else None,
                    ContactId=contact["Id"] if contact else None, Type="Lead" if lead and not contact else "Contact",
                    Status=status, HasResponded=tf(responded), FirstRespondedDate=ds(d) if responded else None,
                    CreatedDate=dtime(d)))
    st = CM_STATS[camp["Id"]]
    st["leads" if lead else "contacts"] += 1
    st["responses"] += responded
    st["sent"] += 1
    if lead and lead.get("IsConverted") == "true":
        st["converted"] += 1


# ---- Activities ------------------------------------------------------------------------------
CALL_SUBJ = ["Discovery call", "Follow-up call", "Pricing discussion call", "Check-in call", "Call re: proposal",
             "Call - procurement next steps", "Call with champion", "Technical validation call", "Call - legal review status"]
EMAIL_SUBJ = ["Email: Sent product overview", "Email: Follow-up on demo", "Email: Sent proposal", "Email: Pricing questions",
              "Email: Security questionnaire", "Email: Contract redlines", "Email: Intro to solutions engineer",
              "Email: Shared customer case study", "Email: Meeting recap & next steps", "Email: Sent order form"]
TODO_SUBJ = ["Prepare proposal", "Update mutual action plan", "Send MSA for review", "Build ROI analysis",
             "Schedule executive sponsor meeting", "Complete security review", "Submit deal desk approval", "Update close plan"]
RENEW_SUBJ = ["Email: Renewal quote sent", "Renewal check-in call", "Prepare renewal quote", "Email: Usage report shared",
              "Call - renewal terms", "Confirm renewal PO", "Email: Co-term options"]
SDR_SUBJ = ["Cold call - intro", "Prospecting email #1", "Prospecting email #2", "Prospecting email #3", "Breakup email",
            "LinkedIn InMail", "Voicemail - intro", "Follow-up email - event", "Qualification call", "Content follow-up email"]
DISPOSITIONS = {"Connected": 30, "Left Voicemail": 35, "No Answer": 22, "Wrong Number": 3, "Meeting Booked": 5, "Not Interested": 5}
EVENT_NB = ["Discovery Meeting", "Product Demo", "Technical Deep Dive", "Solution Workshop", "Executive Briefing",
            "Security Review Session", "Proposal Review", "Negotiation Meeting"]
EVENT_RN = ["Renewal Planning Meeting", "Quarterly Business Review", "Executive Business Review"]
EVENT_UP = ["Expansion Discovery", "Add-on Demo", "Roadmap Briefing", "Usage Review"]
LOCATIONS = ["Zoom", "Microsoft Teams", "Google Meet", "Zoom", "Microsoft Teams", None]


def add_task(subject, d, owner_id, who=None, what=None, acct=None, kind=None, priority="Normal", desc=None):
    kind = kind or ("Email" if subject.startswith("Email") or "email" in subject.lower() or "InMail" in subject
                    else "Call" if ("call" in subject.lower() or "Voicemail" in subject) else "Task")
    done = d <= SNAP
    disp = dur = ctype = None
    if kind == "Call":
        ctype = "Outbound"
        disp = wpick(DISPOSITIONS)
        dur = R.randint(15, 60) if disp in ("Left Voicemail", "No Answer", "Wrong Number") else R.randint(180, 2700)
    TASK_OUT.add(dict(Id=sfid("00T"), Subject=subject, Status="Completed" if done else "Not Started", Priority=priority,
                      TaskSubtype=kind, Type=kind if kind != "Task" else "Other", ActivityDate=ds(d), WhoId=who, WhatId=what,
                      AccountId=acct, OwnerId=owner_id, CallType=ctype, CallDurationInSeconds=dur, CallDisposition=disp,
                      IsClosed=tf(done), Description=desc, CreatedDate=dtime(min(d, SNAP) if done else SNAP - D(R.randint(0, 10)))))
    if done:
        for rid in (who, what, acct):
            if rid:
                touch(rid, d)


def add_event(subject, d, owner_id, who=None, what=None, acct=None, etype="Meeting", loc=None, desc=None):
    dur = R.choice([30, 30, 45, 60, 60, 90])
    h = R.randint(13, 21)
    m = R.choice([0, 0, 30])
    st = dt.datetime(d.year, d.month, d.day, h, m)
    en = st + dt.timedelta(minutes=dur)
    EVENT_OUT.add(dict(Id=sfid("00U"), Subject=subject, Type=etype, StartDateTime=st.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                       EndDateTime=en.strftime("%Y-%m-%dT%H:%M:%S.000Z"), DurationInMinutes=dur, ActivityDate=ds(d),
                       Location=loc if loc is not None else R.choice(LOCATIONS), IsAllDayEvent="false", WhoId=who, WhatId=what,
                       AccountId=acct, OwnerId=owner_id, Description=desc, CreatedDate=dtime(max(MIGRATION, d - D(R.randint(1, 14))))))
    if d <= SNAP:
        for rid in (who, what, acct):
            if rid:
                touch(rid, d)


# ---- Opportunities -----------------------------------------------------------------------------
STAGES = [("Prospecting", 10, "Pipeline"), ("Qualification", 20, "Pipeline"), ("Needs Analysis", 30, "Pipeline"),
          ("Value Proposition", 50, "Pipeline"), ("Proposal/Price Quote", 70, "Best Case"), ("Negotiation/Review", 90, "Commit")]
PATHS = {"New Business": [0, 1, 2, 3, 4, 5], "Existing Business - Upsell": [1, 2, 4, 5], "Existing Business - Renewal": [1, 4, 5]}
LOSS_REASONS = {"New Business": {"Price": 22, "Lost to Competitor": 26, "No Decision / Status Quo": 24, "Timing": 10,
                                 "Feature Gap": 9, "Budget Cut": 6, "Champion Left": 3},
                "Existing Business - Upsell": {"Price": 25, "No Decision / Status Quo": 35, "Budget Cut": 25, "Timing": 15},
                "Existing Business - Renewal": {"Switched to Competitor": 30, "Budget Cut": 22, "Low Adoption": 20,
                                                "Product Fit": 12, "Company Acquired": 8, "Moved In-House": 8}}
COMPETITORS = {"Vantor Cloud": 30, "Helixa": 22, "Cobaltix": 16, "BrightGrid": 14, "Quorra Systems": 10, "In-house build": 8}
NEXT_STEPS = ["Schedule technical validation", "Send revised proposal", "Awaiting legal review", "Executive sponsor call",
              "Security questionnaire in progress", "Procurement reviewing order form", "Book demo with wider team",
              "Confirm budget owner", "Mutual close plan review", "Renewal quote with uplift sent"]
CYCLE = {"SMB": (35, .45), "Mid-Market": (75, .4), "Enterprise": (150, .35)}
NB_WIN = {"SMB": .30, "Mid-Market": .26, "Enterprise": .22}
RENEW_BASE = {"SMB": .86, "Mid-Market": .91, "Enterprise": .95}
UPSELL_RATE = {"SMB": .35, "Mid-Market": .8, "Enterprise": 1.6}
SEATS = {"SMB": (18, .7, 3, 200), "Mid-Market": (70, .6, 20, 800), "Enterprise": (280, .65, 80, 4000)}
DISC = {"SMB": (0, .10), "Mid-Market": (.05, .22), "Enterprise": (.12, .35)}


def line(code, qty, d, disc):
    p = PROD[code]
    lp = list_price(code, d)
    disc = round(min(disc, p["cap"]), 3)
    up = round(lp * (1 - disc), 2)
    return dict(code=code, qty=qty, list=lp, unit=up, disc=disc, total=round(up * qty, 2))


def newbiz_lines(a, d, disc):
    seg = a["_seg"]
    seats = lognorm_int(*SEATS[seg])
    L = []
    ed = {"SMB": {"ALT-PLAT-STD": 70, "ALT-PLAT-PRO": 30}, "Mid-Market": {"ALT-PLAT-STD": 20, "ALT-PLAT-PRO": 65, "ALT-PLAT-ENT": 15},
          "Enterprise": {"ALT-PLAT-PRO": 25, "ALT-PLAT-ENT": 75}}[seg]
    L.append(line(wpick(ed), seats, d, disc))
    pr = lambda smb, mm, ent: R.random() < {"SMB": smb, "Mid-Market": mm, "Enterprise": ent}[seg]
    if pr(.2, .4, .6): L.append(line("ALT-ANL", seats, d, disc))
    if pr(.1, .3, .65): L.append(line("ALT-SEC", seats, d, disc))
    if available("ALT-AI", d) and pr(.15, .3, .4): L.append(line("ALT-AI", seats, d, disc))
    if available("ALT-COPILOT", d) and pr(.12, .28, .38): L.append(line("ALT-COPILOT", seats, d, disc))
    if pr(.05, .35, .7): L.append(line("ALT-INT", 1, d, disc))
    if pr(.02, .2, .5): L.append(line("ALT-API", R.randint(1, 4 if seg != "Enterprise" else 12), d, disc))
    if pr(.15, .25, .4): L.append(line("ALT-STOR", R.randint(1, 3 if seg == "SMB" else 20), d, disc))
    if pr(0, .25, .6): L.append(line("ALT-SBX", 1, d, disc))
    if seg == "Enterprise" and R.random() < .55:
        L.append(line("SUP-PLAT", 1, d, disc))
    elif pr(.05, .3, .35):
        L.append(line("SUP-PREM", 1, d, disc))
    if pr(.1, .2, .3): L.append(line("TRN-ELEARN", seats, d, disc))
    impl = {"SMB": ("PS-IMPL-QS", .6), "Mid-Market": ("PS-IMPL-STD", .7), "Enterprise": ("PS-IMPL-ENT", .7)}[seg]
    if R.random() < impl[1]: L.append(line(impl[0], 1, d, disc))
    if pr(.05, .35, .5): L.append(line("PS-MIG", 1, d, disc))
    if pr(0, .1, .35): L.append(line("PS-CUST", R.randint(5, 60), d, disc))
    if pr(.3, .5, .8): L.append(line("TRN-ADMIN", R.randint(1, 2) if seg == "SMB" else R.randint(2, 20), d, disc))
    if pr(0, .3, .6): L.append(line("TRN-USER", R.randint(1, 12), d, disc))
    if pr(.08, .15, .2):
        a["_hw"] = True
        big = seg == "Enterprise"
        units = R.randint(2, 40) if big else R.randint(1, 6)
        L.append(line("HW-EDGE-500" if big or R.random() < .3 else "HW-EDGE-100", units, d, disc))
        L.append(line("HW-SENS", units * R.randint(1, 4), d, disc))
        L.append(line("HW-MAINT", units, d, disc))
    return L


def upsell_lines(a, d, disc):
    subs = a["_subs"]
    ed = next((c for c in EDITIONS if c in subs), None)
    seats = subs.get(ed, 10)
    r = R.random()
    L = []
    addons = [c for c in ("ALT-COPILOT", "ALT-AI", "ALT-ANL", "ALT-SEC", "TRN-ELEARN") if c not in subs and available(c, d)]
    if r < .4 and ed:
        L.append(line(ed if ed != "ALT-PLAT-LEG" or available(ed, d) else "ALT-PLAT-STD", max(1, int(seats * R.uniform(.08, .35))), d, disc))
    elif r < .75 and addons:
        w = [4 if c in ("ALT-COPILOT", "ALT-AI") else 1 for c in addons]
        L.append(line(R.choices(addons, weights=w)[0], max(1, int(seats * R.uniform(.3, 1.0))), d, disc))
    elif r < .9:
        L.append(line(R.choice(["PS-HEALTH", "TRN-USER", "PS-CUST", "TRN-ADMIN"]), R.randint(1, 3) if R.random() < .7 else R.randint(5, 40), d, disc))
        if "ALT-INT" not in subs and R.random() < .4:
            L.append(line("ALT-INT", 1, d, disc))
    else:
        a["_hw"] = True
        u = R.randint(1, 15)
        L += [line("HW-EDGE-100" if a["_seg"] != "Enterprise" else "HW-EDGE-500", u, d, disc), line("HW-MAINT", u, d, disc)]
    if not L:
        L.append(line("PS-HEALTH", 1, d, disc))
    return L


def renewal_lines(a, d, disc):
    L = []
    for code, qty in a["_subs"].items():
        if code == "ALT-PLAT-LEG" and not available(code, d):
            code = "ALT-PLAT-STD"
        if PROD[code]["seat"]:
            qty = max(1, int(round(qty * clip(R.gauss(1.04, .09), .7, 1.4))))
        L.append(line(code, qty, d, disc))
    return L


def apply_subs(a, lines, mode, d):
    """mode: set (new business / renewal) or add (upsell)."""
    if mode == "set":
        a["_subs"], a["_price"] = {}, {}
    for ln in lines:
        if not PROD[ln["code"]]["rec"]:
            continue
        c = ln["code"]
        old_q = a["_subs"].get(c, 0)
        old_p = a["_price"].get(c, 0)
        a["_subs"][c] = old_q + ln["qty"]
        a["_price"][c] = (old_q * old_p + ln["qty"] * ln["unit"]) / (old_q + ln["qty"])
    a["_arr_hist"].append((d, arr_of(a)))


def arr_of(a):
    return round(sum(q * a["_price"][c] for c, q in a["_subs"].items()), 2)


def disc_for(a, d, kind):
    lo, hi = DISC[a["_seg"]]
    x = R.uniform(lo, hi)
    if kind == "Existing Business - Renewal" and a["_disc"] is not None:
        x = max(0, a["_disc"] - R.uniform(0, .03))
    if d.month in (3, 6, 9, 12) and d.day > 15:
        x += .03
    return round(clip(x, 0, .45), 3)


def owner_for(a, d):
    o = a["_owner"]
    if not active(o, d):
        o = pick("AE", a["_region"], a["_seg"], d)
        a["_owner"] = o
    return o


def make_opp(a, kind, created, cycle, win_p, source=None, campaign=None, lead_owner=None, renew_date=None, attempt=1):
    seg = a["_seg"]
    owner = owner_for(a, created)
    close = bday(created + D(max(5, cycle)))
    if renew_date:
        close = bday_back(renew_date - D(R.randint(-5, 20)))
        if close <= created:
            close = created + D(5)
    won = R.random() < win_p
    path = PATHS[kind]
    reached = len(path) - 1
    if won and kind != "Existing Business - Renewal" and R.random() < .4:  # quarter-end crunch
        qe = bday_back(quarter_end(close) - D(R.randint(0, 8)))
        if created + D(7) <= qe <= close + D(60):
            close = qe
    if not won:
        if kind == "New Business":
            reached = R.choices(range(len(path)), weights=[14, 22, 20, 16, 16, 12])[0]
        elif kind == "Existing Business - Upsell":
            reached = R.choices(range(len(path)), weights=[30, 30, 25, 15])[0]
        else:
            reached = R.choices(range(len(path)), weights=[15, 35, 50])[0]
        if not renew_date:
            close = bday(created + D(max(3, int((close - created).days * (reached + 1) / len(path) * R.uniform(.8, 1.3)))))
    is_open = close > SNAP
    stale = (not is_open and SNAP - D(50) < close <= SNAP and R.random() < .18)
    if is_open or stale:
        total = max(1, (close - created).days)
        frac = (SNAP - created).days / total
        reached = min(len(path) - 1, int(frac * len(path))) if not stale else min(len(path) - 1, max(0, len(path) - 2))
    if created > SNAP:
        return None

    disc = disc_for(a, close, kind)
    a["_disc"] = disc if a["_disc"] is None or kind != "Existing Business - Upsell" else a["_disc"]
    lines = {"New Business": newbiz_lines, "Existing Business - Upsell": upsell_lines,
             "Existing Business - Renewal": renewal_lines}[kind](a, close if not is_open else created, disc)
    amount = round(sum(l["total"] for l in lines), 2)
    arr = round(sum(l["total"] for l in lines if PROD[l["code"]]["rec"]), 2)
    term = {"SMB": 12, "Mid-Market": R.choice([12, 12, 12, 12, 24]), "Enterprise": R.choice([12, 12, 24, 36, 36])}[seg]
    closed = not (is_open or stale)
    if closed:
        stage, prob, fc = ("Closed Won", 100, "Closed") if won else ("Closed Lost", 0, "Omitted")
    else:
        stage, prob, fc = STAGES[path[reached]]
        won = None
    oid = sfid("006")
    short = a["Name"]
    if kind == "New Business":
        ed = next((PROD[l["code"]]["name"].split(" - ")[1] for l in lines if l["code"] in EDITIONS), "Platform")
        seats = next((l["qty"] for l in lines if l["code"] in EDITIONS), 0)
        nm = f"{short} - {ed} ({seats:,} seats)"
    elif kind == "Existing Business - Upsell":
        nm = f"{short} - Expansion: {PROD[lines[0]['code']]['name']}"
    else:
        nm = f"{short} - Renewal FY{(renew_date or close).year}"
    fy_d = close
    pb = pb_index(created if not closed else close)
    o = dict(Id=oid, Name=nm, AccountId=a["Id"], OwnerId=owner["Id"], CreatedById=(lead_owner or owner)["Id"],
             Type=kind, StageName=stage, Amount=amount, Probability=prob, ExpectedRevenue=round(amount * prob / 100, 2),
             CloseDate=ds(close), CreatedDate=after(a["CreatedDate"], 5, 90) if created == a["_created"] else dtime(created), IsClosed=tf(closed), IsWon=tf(bool(won)),
             ForecastCategoryName=fc, LeadSource=source or ("Existing Customer" if kind != "New Business" else None),
             CampaignId=campaign["Id"] if campaign else None, Pricebook2Id=PRICEBOOK_IDS[pb],
             NextStep=R.choice(NEXT_STEPS) if not closed else None,
             Loss_Reason__c=wpick(LOSS_REASONS[kind]) if closed and not won else None,
             Primary_Competitor__c=(wpick(COMPETITORS) if (kind == "New Business" and R.random() < .55) or
                                    (closed and not won and kind != "Existing Business - Upsell" and R.random() < .6) else None),
             FiscalYear=fy_d.year, FiscalQuarter=fq(fy_d), Fiscal=f"{fy_d.year} {fq(fy_d)}",
             Contract_Term_Months__c=term if kind != "Existing Business - Upsell" else None,
             ARR__c=arr, One_Time_Amount__c=round(amount - arr, 2), TCV__c=round(arr * (term if kind != "Existing Business - Upsell" else 12) / 12 + amount - arr, 2),
             Discount_Percent__c=round(disc * 100, 1), Segment__c=seg, Region__c=a["_region"],
             Sales_Cycle_Days__c=(close - created).days if closed else None,
             Push_Count__c=min(6, poisson(.4 + (0.8 if not won else 0) + (0.6 if seg == "Enterprise" else 0))),
             Attempt_Number__c=attempt if kind == "New Business" else None,
             HasOpportunityLineItem="true",
             _a=a, _created=created, _close=close, _won=won, _closed=closed, _kind=kind, _owner=owner, _lines=lines, _term=term)
    if stale:
        o["Description"] = "Close date passed - needs update"
    OPPS.append(o)

    # line items
    for ln in lines:
        p = PROD[ln["code"]]
        OLI_OUT.add(dict(Id=sfid("00k"), OpportunityId=oid, Product2Id=p["Id"], PricebookEntryId=p["pbe"][pb],
                         ProductCode=p["code"], Name=f"{short} {p['name']}", Quantity=ln["qty"], ListPrice=ln["list"],
                         UnitPrice=ln["unit"], Discount=round(ln["disc"] * 100, 1), TotalPrice=ln["total"],
                         ServiceDate=ds(close), Revenue_Type__c="Recurring" if p["rec"] else "One-Time", CreatedDate=o["CreatedDate"]))
    # stage history
    steps = path[:reached + 1]
    span = max(1, ((close if closed else min(close, SNAP)) - created).days)
    n = len(steps) + (1 if closed else 0)
    est = amount * R.uniform(.7, 1.4)
    for i, si in enumerate(steps):
        sd = created + D(int(span * i / n)) if i else created
        if sd > SNAP:
            break
        name, p_, f_ = STAGES[si]
        amt = round(est if si < 4 else amount, -2 if si < 4 else 0) if kind == "New Business" else amount
        HIST_OUT.add(dict(Id=sfid("008"), OpportunityId=oid, StageName=name, Amount=amt, Probability=p_,
                          ExpectedRevenue=round(amt * p_ / 100, 2), CloseDate=ds(close), ForecastCategory=f_,
                          CreatedDate=o["CreatedDate"] if i == 0 else (after(o["CreatedDate"], 30, 300) if sd == created else dtime(sd)), CreatedById=owner["Id"]))
    if closed:
        HIST_OUT.add(dict(Id=sfid("008"), OpportunityId=oid, StageName=stage, Amount=amount, Probability=prob,
                          ExpectedRevenue=round(amount * prob / 100, 2), CloseDate=ds(close), ForecastCategory=fc,
                          CreatedDate=after(o["CreatedDate"], 301, 600) if close == created else dtime(close), CreatedById=owner["Id"]))
    # contact roles
    avail = [c for c in a["_contacts"] if c["_created"] <= created] or a["_contacts"][:1]
    k = min(len(avail), {"SMB": R.randint(1, 2), "Mid-Market": R.randint(1, 3), "Enterprise": R.randint(2, 5)}[seg])
    roles = R.sample(avail, k)
    role_names = ["Decision Maker", "Economic Buyer", "Technical Buyer", "Evaluator", "Influencer", "Executive Sponsor", "Business User"]
    for i, c in enumerate(roles):
        OCR_OUT.add(dict(Id=sfid("00K"), OpportunityId=oid, ContactId=c["Id"], Role=role_names[0] if i == 0 else R.choice(role_names[1:]),
                         IsPrimary=tf(i == 0), CreatedDate=o["CreatedDate"]))
    # activities
    end = close if closed else min(close, SNAP)
    if kind == "New Business":
        nt = {"SMB": (4, 10), "Mid-Market": (8, 18), "Enterprise": (12, 32)}[seg]
        ne = {"SMB": (1, 3), "Mid-Market": (2, 5), "Enterprise": (3, 8)}[seg]
        subj_pool = CALL_SUBJ + EMAIL_SUBJ + EMAIL_SUBJ + TODO_SUBJ
        ev_pool = EVENT_NB
    elif kind == "Existing Business - Upsell":
        nt, ne, subj_pool, ev_pool = (3, 8), (1, 2), CALL_SUBJ + EMAIL_SUBJ + TODO_SUBJ, EVENT_UP
    else:
        nt, ne, subj_pool, ev_pool = (2, 7), (0, 2), RENEW_SUBJ + EMAIL_SUBJ[:3], EVENT_RN
    scale = (reached + 1) / len(path)
    for _ in range(max(1, int(R.randint(*nt) * scale))):
        d = bday(between(created, end))
        who = R.choice(roles)["Id"] if roles else None
        add_task(R.choice(subj_pool), d, owner["Id"], who, oid, a["Id"])
    for i in range(max(0, int(R.randint(*ne) * scale))):
        d = bday(between(created, end))
        subj = ev_pool[min(i, len(ev_pool) - 1)] if kind == "New Business" else R.choice(ev_pool)
        add_event(subj, d, owner["Id"], R.choice(roles)["Id"] if roles else None, oid, a["Id"],
                  loc=None if R.random() > .2 else f"Customer Office - {a['_city'][0]}")
    if not closed:
        for _ in range(R.randint(1, 2)):
            add_task(R.choice(TODO_SUBJ + CALL_SUBJ), bday(SNAP + D(R.randint(1, 21))), owner["Id"],
                     roles[0]["Id"] if roles else None, oid, a["Id"], priority=R.choice(["Normal", "High"]))
    return o


def win_prob_nb(a, source, d, attempt):
    p = NB_WIN[a["_seg"]] * LEAD_SOURCES.get(source, (0, 1.0))[1] ** .5 * (1 + .04 * (d.year - 2021))
    if attempt > 1:
        p *= .85
    return clip(p, .05, .7)


def cycle_days(seg):
    med, sig = CYCLE[seg]
    return int(clip(med * math.exp(R.gauss(0, sig)), 7, 420))


def term_months(seg):
    return {"SMB": 12, "Mid-Market": R.choice([12, 12, 12, 12, 24]), "Enterprise": R.choice([12, 12, 24, 36, 36])}[seg]


def run_customer(a, contract_start, term):
    seg = a["_seg"]
    while True:
        renew_date = add_months(contract_start, term)
        a["_contract_end"] = renew_date
        lam = UPSELL_RATE[seg] * term / 12 * (0.5 + a["_health"] / 100)
        lo, hi = max(contract_start + D(45), MIGRATION + D(1)), renew_date - D(75)
        if hi > lo:
            for d in sorted(bday(between(lo, hi)) for _ in range(poisson(lam))):
                if d > SNAP:
                    break
                o = make_opp(a, "Existing Business - Upsell", d, int(cycle_days(seg) * .5), .5 * (0.6 + a["_health"] / 125))
                if o and o["_closed"] and o["_won"]:
                    apply_subs(a, o["_lines"], "add", o["_close"])
        rc = max(MIGRATION, bday(renew_date - D(R.randint(60, 110))))  # legacy renewals open on migration day
        if rc > SNAP:
            return None
        p = clip(RENEW_BASE[seg] * (0.75 + 0.35 * a["_health"] / 100), .4, .985)
        o = make_opp(a, "Existing Business - Renewal", rc, 0, p, renew_date=renew_date)
        if o is None or not o["_closed"]:
            return None
        if o["_won"]:
            apply_subs(a, o["_lines"], "set", o["_close"])
            contract_start, term = renew_date, o["_term"]
            a["_health"] = clip(a["_health"] + R.gauss(0, 8), 5, 100)
        else:
            a["_subs"], a["_price"] = {}, {}
            a["_arr_hist"].append((renew_date, 0.0))
            return renew_date


def simulate(a, first_try, source=None, campaign=None, lead_owner=None):
    state = ("prospect", first_try) if first_try else None
    if a["_legacy"] and a["_subs"]:
        state = ("customer", a["_contract_start"])
    attempts = 0
    while state:
        kind, d = state[0], state[1]
        if kind == "prospect":
            if d is None or d > SNAP:
                break
            attempts += 1
            src = source if attempts == 1 else ("Outbound Prospecting" if a["_periods"] == [] else "Win-back")
            o = make_opp(a, "New Business", d, cycle_days(a["_seg"]), win_prob_nb(a, src, d, attempts), source=src,
                         campaign=campaign if attempts == 1 else (campaign_on("Outbound Prospecting", d) if R.random() < .2 else None),
                         lead_owner=lead_owner if attempts == 1 else None, attempt=attempts)
            if o is None or not o["_closed"]:
                break
            if o["_won"]:
                apply_subs(a, o["_lines"], "set", o["_close"])
                if a["Customer_Since__c"] is None:
                    a["Customer_Since__c"] = ds(o["_close"])
                state = ("customer", o["_close"], o["_term"])
            else:
                state = ("prospect", bday(o["_close"] + D(R.randint(150, 540)))) if R.random() < .4 and attempts < 3 else None
        else:
            start = d
            term = state[2] if len(state) > 2 else a["_term0"]
            churn = run_customer(a, start, term)
            a["_periods"].append((max(start, MIGRATION), churn))
            if churn is None:
                break
            a["Churn_Date__c"] = ds(churn)
            state = ("prospect", bday(churn + D(R.randint(180, 540)))) if R.random() < .12 else None
            attempts = 2


# ---- 1) Legacy (migrated) accounts ---------------------------------------------------------------
print("Accounts, contacts, opportunities ...")
for i in range(N_LEGACY_CUSTOMERS + N_LEGACY_PROSPECTS):
    cust = i < N_LEGACY_CUSTOMERS
    seg = wpick({"SMB": 45, "Mid-Market": 38, "Enterprise": 17} if cust else {"SMB": 55, "Mid-Market": 33, "Enterprise": 12})
    a = make_account(MIGRATION, seg, "legacy", legacy=True)
    lo, hi = CONTACTS_PER_SEG[seg]
    for j in range(R.randint(lo, hi)):
        make_contact(a, MIGRATION if j < 3 or R.random() < .5 else bday(between(MIGRATION, SNAP)))
    if cust:
        since = dt.date(R.randint(2015, 2020), R.randint(1, 12), R.randint(1, 28))
        a["Customer_Since__c"] = ds(since)
        term = term_months(seg)
        cs = add_months(START, -R.randint(0, term - 1))
        cs = dt.date(cs.year, cs.month, R.randint(1, 28))
        a["_contract_start"], a["_term0"] = cs, term
        legacy_disc = R.uniform(*DISC[seg])
        lines = newbiz_lines(a, START, legacy_disc)
        if seg == "SMB" and R.random() < .5:
            for ln in lines:
                if ln["code"] in EDITIONS:
                    ln.update(line("ALT-PLAT-LEG", ln["qty"], START, legacy_disc))
        for ln in lines:
            ln["unit"] = round(ln["unit"] * .93, 2)  # older contracted pricing
        a["_disc"] = round(legacy_disc, 3)
        apply_subs(a, lines, "set", MIGRATION)
        simulate(a, None)
    else:
        first = bday(MIGRATION + D(R.randint(20, 1750))) if R.random() < .4 else None
        simulate(a, first)

# ---- 2) Accounts born from converted leads ------------------------------------------------------
conv_w = {s: v[0] * v[1] for s, v in LEAD_SOURCES.items()}
LEAD_FIELDS = ["Id", "FirstName", "LastName", "Company", "Title", "Email", "Phone", "LeadSource", "Status", "Rating", "Industry",
               "NumberOfEmployees", "AnnualRevenue", "Street", "City", "State", "PostalCode", "Country", "Region__c", "OwnerId",
               "CreatedDate", "IsConverted", "ConvertedDate", "ConvertedAccountId", "ConvertedContactId", "ConvertedOpportunityId",
               "Lead_Score__c", "Primary_Campaign__c", "Unqualified_Reason__c", "HasOptedOutOfEmail", "LastActivityDate", "Is_Duplicate__c"]


def lead_tasks(lead, owner, created, end, n):
    for _ in range(n):
        d = bday(between(created, end))
        if d > SNAP:
            continue
        add_task(R.choice(SDR_SUBJ), d, owner["Id"], who=lead["Id"])


for i in range(N_LEAD_ACCOUNTS):
    src = wpick(conv_w)
    while True:
        camp, ld = lead_core(src)
        conv = bday(ld + D(R.randint(2, 45)))
        if conv <= SNAP - D(3):
            break
    seg = wpick({"SMB": 60, "Mid-Market": 30, "Enterprise": 10})
    a = make_account(conv, seg, "lead")
    a["AccountSource"] = src
    sdr = pick("SDR", a["_region"], None, ld)
    t = pick_title(seg)
    first, last = person_name(a["_country"])
    c = make_contact(a, conv, first, last, t, source=src, from_lead=True)
    lead = dict(Id=sfid("00Q"), FirstName=first, LastName=last, Company=a["Name"], Title=t[0], Email=c["Email"], Phone=c["Phone"],
                LeadSource=src, Status="Qualified - Converted", Rating=wpick({"Hot": 55, "Warm": 40, "Cold": 5}),
                Industry=a["Industry"], NumberOfEmployees=a["NumberOfEmployees"], AnnualRevenue=a["AnnualRevenue"],
                Street=a["BillingStreet"], City=a["BillingCity"], State=a["BillingState"], PostalCode=a["BillingPostalCode"],
                Country=a["BillingCountry"], Region__c=a["_region"], OwnerId=sdr["Id"], CreatedDate=dtime(ld), IsConverted="true",
                ConvertedDate=ds(conv), ConvertedAccountId=a["Id"], ConvertedContactId=c["Id"], Lead_Score__c=R.randint(62, 100),
                Primary_Campaign__c=camp["Id"] if camp else None, HasOptedOutOfEmail="false", Is_Duplicate__c="false",
                _created=ld, _camp=camp)
    LEADS.append(lead)
    lead_tasks(lead, sdr, ld, conv, R.randint(3, 10))
    lo, hi = CONTACTS_PER_SEG[seg]
    add_contacts(a, R.randint(lo, hi) - 1)
    n_before = len(OPPS)
    simulate(a, conv, source=src, campaign=camp, lead_owner=sdr)
    lead["ConvertedOpportunityId"] = OPPS[n_before]["Id"] if len(OPPS) > n_before else None
    if camp:
        add_member(camp, ld, lead=lead, contact=c, status="Attended" if src in EVENT_SOURCES else "Responded")

# ---- 3) Outbound-sourced accounts ----------------------------------------------------------------
for i in range(N_OUTBOUND_ACCOUNTS):
    seg = wpick({"SMB": 35, "Mid-Market": 40, "Enterprise": 25})
    created = growth_date(ACCT_CUM)
    a = make_account(created, seg, "outbound")
    lo, hi = CONTACTS_PER_SEG[seg]
    add_contacts(a, R.randint(lo, hi))
    first = bday(created + D(R.randint(5, 200))) if R.random() < .55 else None
    simulate(a, first, source="Outbound Prospecting",
             campaign=campaign_on("Outbound Prospecting", first) if first and R.random() < .35 else None)

print(f"  accounts={len(ACCOUNTS):,} contacts={len(CONTACTS):,} opps={len(OPPS):,}  ({time.time() - t0:.0f}s)")

# ---- 4) Non-converted leads ---------------------------------------------------------------------
print("Leads ...")
UNQUAL = {"No Budget": 22, "Not a Fit": 25, "Competitor Customer": 10, "Student / Job Seeker": 8, "Bad Contact Info": 12,
          "No Response": 18, "Duplicate": 5}
share_w = {s: v[0] for s, v in LEAD_SOURCES.items()}
for i in range(N_OPEN_LEADS):
    src = wpick(share_w)
    camp, ld = lead_core(src)
    region = wpick(REGION_W)
    country, city = pick_city(region)
    industry = wpick({k: v[0] for k, v in INDUSTRIES.items()})
    seg = wpick({"SMB": 62, "Mid-Market": 28, "Enterprise": 10})
    emp = lognorm_int(*SEG_EMP[seg])
    comp = company_name(industry, country, unique=False)
    first, last = person_name(country)
    dom = domain_for(comp, country, industry)
    age = (SNAP - ld).days
    if age < 14:
        status = wpick({"Open - Not Contacted": 60, "Working - Contacted": 40})
    elif age < 90:
        status = wpick({"Open - Not Contacted": 5, "Working - Contacted": 45, "Nurturing": 30, "Unqualified": 20})
    else:
        status = wpick({"Working - Contacted": 4, "Nurturing": 44, "Unqualified": 52})
    sdr = pick("SDR", region, None, ld)
    t = pick_title(seg)
    lead = dict(Id=sfid("00Q"), FirstName=first, LastName=last, Company=comp, Title=t[0] if R.random() > .06 else None,
                Email=f"{slug(first)}.{slug(last)}@{dom}" if R.random() > .02 else None,
                Phone=phone(country, city[4]) if R.random() > .18 else None, LeadSource=src, Status=status,
                Rating=wpick({"Hot": 8, "Warm": 37, "Cold": 55}) if status != "Unqualified" else "Cold",
                Industry=industry if R.random() > .09 else None, NumberOfEmployees=emp if R.random() > .2 else None,
                AnnualRevenue=round(emp * INDUSTRIES[industry][2] * R.uniform(.55, 1.6), -4) if R.random() > .35 else None,
                Street=None, City=city[0] if R.random() > .1 else None, State=city[1], PostalCode=None, Country=country,
                Region__c=region, OwnerId=sdr["Id"], CreatedDate=dtime(ld), IsConverted="false", Lead_Score__c=R.randint(1, 75),
                Primary_Campaign__c=camp["Id"] if camp else None,
                Unqualified_Reason__c=wpick(UNQUAL) if status == "Unqualified" else None,
                HasOptedOutOfEmail=tf(R.random() < .06), Is_Duplicate__c="false", _created=ld, _camp=camp)
    LEADS.append(lead)
    n = {"Open - Not Contacted": 0, "Working - Contacted": R.randint(1, 6), "Nurturing": R.randint(2, 8), "Unqualified": R.randint(1, 5)}[status]
    lead_tasks(lead, sdr, ld, min(SNAP, ld + D(R.randint(10, 75))), n)
    if camp:
        add_member(camp, ld, lead=lead, status="Attended" if src in EVENT_SOURCES else "Responded")
# a sprinkle of duplicate leads (data-quality realism)
for src_lead in R.sample(LEADS, int(len(LEADS) * .008)):
    d = min(SNAP, src_lead["_created"] + D(R.randint(5, 400)))
    dup = dict(src_lead, Id=sfid("00Q"), CreatedDate=dtime(d), Status="Open - Not Contacted", IsConverted="false",
               ConvertedDate=None, ConvertedAccountId=None, ConvertedContactId=None, ConvertedOpportunityId=None,
               Is_Duplicate__c="true", Lead_Score__c=R.randint(1, 60), _created=d)
    LEADS.append(dup)

# ---- 5) Campaign members: newsletters, summit attendance, webinars --------------------------------
print("Campaign members ...")
CONTACTS.sort(key=lambda c: c["_created"])
LEADS_SORTED = sorted(LEADS, key=lambda l: l["_created"])
c_dates = [c["_created"] for c in CONTACTS]
l_dates = [l["_created"] for l in LEADS_SORTED]
import bisect


def sample_existing(objs, dates, d, k):
    n = bisect.bisect_right(dates, d)
    if n == 0:
        return []
    return [objs[R.randrange(n)] for _ in range(k)]


def is_customer_on(a, d):
    return any(s <= d and (e is None or d < e) for s, e in a["_periods"])


for c in CAMP_BY_TYPE["Email"]:
    d = c["_start"]
    if d > SNAP:
        continue
    g = 1.3 ** (d.year - 2021)
    seen = set()
    for obj in sample_existing(CONTACTS, c_dates, d, int(500 * g * SCALE)) + sample_existing(LEADS_SORTED, l_dates, d, int(700 * g * SCALE)):
        if obj["Id"] in seen or obj.get("HasOptedOutOfEmail") == "true":
            continue
        seen.add(obj["Id"])
        st = wpick({"Sent": 72, "Opened": 20, "Clicked": 8})
        if obj["Id"].startswith("003"):
            add_member(c, d, contact=obj, status=st)
        else:
            add_member(c, d, lead=obj, status=st)
    c["NumberSent"] = len(seen)
customers_by_date = {}
for c in CAMP_BY_TYPE["summit"] + CAMP_BY_TYPE["Webinar"] + CAMP_BY_TYPE["launch"]:
    d = c["_start"]
    if d > SNAP:
        continue
    g = 1.25 ** (d.year - 2021)
    kind = c.get("_kind")
    n = int((900 if kind == "summit" else 120 if kind == "summit_tour" else 400 if c["Type"] == "Product Launch" else 45) * g * SCALE)
    seen = set()
    for obj in sample_existing(CONTACTS, c_dates, d, n * 3):
        if len(seen) >= n:
            break
        a = obj["_acct"]
        if obj["Id"] in seen or not is_customer_on(a, d):
            continue
        if kind == "summit_tour" and a["_region"] != c["Region__c"]:
            continue
        seen.add(obj["Id"])
        st = wpick({"Attended": 62, "Registered": 18, "No Show": 20}) if c["Type"] != "Product Launch" else wpick({"Sent": 70, "Clicked": 30})
        add_member(c, d - D(R.randint(0, 20)) if st != "Sent" else d, contact=obj, status=st)
        if st == "Attended":
            touch(obj["Id"], d)
            touch(a["Id"], d)
    c["NumberSent"] = c["NumberSent"] or len(seen)

# ---- 6) Cases ----------------------------------------------------------------------------------
print("Cases ...")
CASES = []
CASE_RATE = {"SMB": .22, "Mid-Market": .7, "Enterprise": 2.2}
CASE_TEMPLATES = {
    "Problem": [("Unable to log in after SSO change", "Access / Login", "ALT-PLAT"), ("Dashboard loading slowly", "Performance", "ALT-ANL"),
                ("Integration Hub sync failing", "Integration", "ALT-INT"), ("Report export returns error 500", "Defect", "ALT-PLAT"),
                ("API rate limit errors", "Integration", "ALT-API"), ("Scheduled job did not run", "Defect", "ALT-PLAT"),
                ("Edge Gateway offline", "Hardware", "HW-EDGE"), ("Sensor readings missing", "Hardware", "HW-SENS"),
                ("Sandbox refresh stuck", "Configuration", "ALT-SBX"), ("AI Insights model not updating", "Defect", "ALT-AI"),
                ("Copilot returning incomplete answers", "Defect", "ALT-COPILOT")],
    "Question": [("How to configure role-based access", "User Training", "ALT-SEC"), ("Best practice for data retention", "Configuration", "ALT-PLAT"),
                 ("Question about seat allocation", "User Training", "ALT-PLAT"), ("How to build a custom dashboard", "User Training", "ALT-ANL"),
                 ("Setting up API authentication", "Integration", "ALT-API"), ("Admin certification enrollment", "User Training", "TRN-ADMIN")],
    "Feature Request": [("Request: bulk edit for records", "Feature Request", "ALT-PLAT"), ("Request: additional chart types", "Feature Request", "ALT-ANL"),
                        ("Request: Copilot support for more languages", "Feature Request", "ALT-COPILOT"), ("Request: webhook retries", "Feature Request", "ALT-INT")],
    "Incident": [("Service degradation - EU region", "Performance", "ALT-PLAT"), ("Data sync outage", "Integration", "ALT-INT"),
                 ("Unexpected data discrepancy after upgrade", "Data Issue", "ALT-PLAT"), ("Security alert investigation", "Security", "ALT-SEC")],
    "Billing": [("Invoice discrepancy", "Billing", None), ("Update billing contact", "Billing", None), ("Request W-9 / tax documents", "Billing", None),
                ("Question about renewal invoice", "Billing", None)],
}
CASE_TYPE_W = {"Problem": 40, "Question": 28, "Feature Request": 10, "Incident": 10, "Billing": 12}
SLA_H = {"Critical": 4, "High": 24, "Medium": 72, "Low": 120}
RES_MED = {"Critical": 6, "High": 20, "Medium": 60, "Low": 110}
for a in ACCOUNTS:
    if not a["_periods"]:
        continue
    seg = a["_seg"]
    rate = CASE_RATE[seg] * (1.4 - a["_health"] / 150)
    owned = set(a["_subs"]) | {ln for ln in ("ALT-PLAT",)}
    for s, e in a["_periods"]:
        m = dt.date(s.year, s.month, 1)
        stop = e or SNAP
        while m <= stop:
            for _ in range(poisson(rate)):
                cd = m + D(R.randint(0, 27))
                if cd < s or cd > stop or cd > SNAP:
                    continue
                if cd.weekday() >= 5 and R.random() < .7:
                    cd = bday(cd)
                    if cd > SNAP:
                        continue
                ctype = wpick(CASE_TYPE_W)
                subj, reason, prod = R.choice(CASE_TEMPLATES[ctype])
                if prod and prod.startswith("ALT-AI") and cd < dt.date(2023, 6, 6):
                    subj, reason, prod = CASE_TEMPLATES["Problem"][0]
                if prod == "ALT-COPILOT" and cd < dt.date(2024, 9, 17):
                    subj, reason, prod = CASE_TEMPLATES["Question"][2]
                if prod and prod.startswith("HW") and not a["_hw"]:
                    subj, reason, prod = CASE_TEMPLATES["Problem"][1]
                pw = {"SMB": {"Critical": 3, "High": 17, "Medium": 50, "Low": 30}, "Mid-Market": {"Critical": 5, "High": 22, "Medium": 48, "Low": 25},
                      "Enterprise": {"Critical": 8, "High": 27, "Medium": 45, "Low": 20}}[seg]
                pri = wpick(pw) if ctype not in ("Incident",) else wpick({"Critical": 40, "High": 50, "Medium": 10})
                if ctype in ("Billing", "Feature Request"):
                    pri = wpick({"Medium": 40, "Low": 60})
                origin = wpick({"Email": 35, "Web": 25, "Phone": 20, "Chat": 15 if cd >= dt.date(2022, 3, 1) else 0, "Community": 5})
                hrs = RES_MED[pri] * math.exp(R.gauss(0, .9)) * (1.25 if cd.year == 2022 else 1.0) * (1 - .04 * (cd.year - 2021))
                created_dt = dt.datetime(cd.year, cd.month, cd.day, R.randint(12, 23), R.randint(0, 59))
                closed_dt = created_dt + dt.timedelta(hours=hrs)
                is_closed = closed_dt.date() <= SNAP
                frm = max(2, int(R.expovariate(1 / {"Critical": 20, "High": 60, "Medium": 180, "Low": 300}[pri])))
                esc = R.random() < {"Critical": .35, "High": .12, "Medium": .04, "Low": .02}[pri]
                sla_met = hrs <= SLA_H[pri]
                csat = None
                if is_closed and R.random() < .42:
                    base = 4.4 - (0 if sla_met else 1.0) - (0.6 if esc else 0) + R.gauss(0, .7)
                    csat = int(clip(round(base), 1, 5))
                avail = [c for c in a["_contacts"] if c["_created"] <= cd] or a["_contacts"][:1]
                cont = R.choice(avail)
                agent = pick("Support", "Global", None, cd)
                CASES.append(dict(AccountId=a["Id"], ContactId=cont["Id"], OwnerId=agent["Id"], Subject=subj, Type=ctype, Reason=reason,
                                  Priority=pri, Origin=origin,
                                  Status="Closed" if is_closed else wpick({"New": 25, "Working": 40, "Escalated": 10, "Waiting on Customer": 25}),
                                  IsClosed=tf(is_closed), IsEscalated=tf(esc),
                                  Description=f"{subj}. Reported via {origin.lower()} by {cont['FirstName']} {cont['LastName']}.",
                                  Product__c=next((PROD[c]["name"] for c in a["_subs"] if prod and c.startswith(prod)), None) if prod else None,
                                  CreatedDate=created_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                  ClosedDate=closed_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z") if is_closed else None,
                                  Resolution_Hours__c=round(hrs, 1) if is_closed else None, First_Response_Minutes__c=frm,
                                  SLA_Target_Hours__c=SLA_H[pri], SLA_Met__c=tf(sla_met) if is_closed else None, CSAT_Score__c=csat,
                                  Support_Tier__c="Platinum" if "SUP-PLAT" in a["_subs"] else "Premium" if "SUP-PREM" in a["_subs"] else "Standard",
                                  _dt=created_dt, _cd=cd, _a=a, _agent=agent, _cont=cont))
                touch(a["Id"], cd)
            m = add_months(m, 1)
CASES.sort(key=lambda c: c["_dt"])
for i, c in enumerate(CASES):
    c["Id"] = sfid("500")
    c["CaseNumber"] = f"{1001 + i:08d}"
    if R.random() < .3:
        add_task(R.choice(["Follow up with customer on case", "Email: Case resolution summary", "Call customer re: case"]),
                 bday(c["_cd"] + D(R.randint(0, 5))), c["_agent"]["Id"], c["_cont"]["Id"], c["Id"], c["AccountId"])

# ---- 7) CSM QBR events & account roll-ups -------------------------------------------------------
print("Roll-ups ...")
for a in ACCOUNTS:
    # owner as of snapshot
    if not active(a["_owner"], SNAP):
        a["_owner"] = pick("AE", a["_region"], a["_seg"], SNAP)
    a["OwnerId"] = a["_owner"]["Id"]
    for c in a["_contacts"]:
        c["OwnerId"] = a["OwnerId"]
    if a["_periods"]:
        csm = pick("CSM", a["_region"], None, SNAP)
        a["CSM__c"] = csm["Id"]
        if a["_seg"] != "SMB":
            every = 3 if a["_seg"] == "Enterprise" else 6
            for s, e in a["_periods"]:
                m = add_months(s, every)
                while m <= (e or SNAP):
                    cs = pick("CSM", a["_region"], None, m)
                    add_event("Quarterly Business Review" if every == 3 else "Customer Success Check-in", bday(m), cs["Id"],
                              R.choice(a["_contacts"])["Id"], a["Id"], a["Id"], etype="Meeting")
                    m = add_months(m, every)
    current = a["_periods"] and a["_periods"][-1][1] is None and a["_subs"]
    if current:
        a["Type"] = "Customer"
    elif a["_periods"] or (a["_legacy"] and a["Customer_Since__c"]):
        a["Type"] = "Former Customer"
    else:
        a["Type"] = "Prospect"
    if a["Type"] != "Former Customer":
        a["Churn_Date__c"] = None
    a["Current_ARR__c"] = arr_of(a) if current else 0
    a["Licensed_Seats__c"] = next((q for c, q in a["_subs"].items() if c in EDITIONS), 0) if current else 0
    a["Primary_Edition__c"] = next((PROD[c]["name"].split(" - ")[1] for c in a["_subs"] if c in EDITIONS), None) if current else None
    a["Contract_End_Date__c"] = ds(a["_contract_end"]) if current else None
    a["Health_Score__c"] = int(clip(a["_health"] + R.gauss(0, 6), 1, 100)) if a["_periods"] else None
    a["Rating"] = ("Hot" if a["Type"] == "Customer" and a["_health"] > 75 else "Warm") if a["Type"] == "Customer" else wpick({"Hot": 10, "Warm": 35, "Cold": 55})
    a["Description"] = f"{a['Industry']} organization headquartered in {a['BillingCity']}, {a['BillingCountry']}."
    la = LAST_ACT.get(a["Id"])
    a["LastActivityDate"] = ds(la)
    a["LastModifiedDate"] = dtime(max([a["_created"]] + ([la] if la else [])))

won_by_acct = defaultdict(float)
for o in OPPS:
    if o["_closed"] and o["_won"]:
        won_by_acct[o["AccountId"]] += o["Amount"]
    if not o["_closed"]:
        o["OwnerId"] = o["_a"]["OwnerId"] if not active(o["_owner"], SNAP) else o["OwnerId"]
    la = LAST_ACT.get(o["Id"])
    o["LastActivityDate"] = ds(la)
    o["LastModifiedDate"] = dtime(o["_close"] if o["_closed"] else SNAP - D(R.randint(0, 40)))
for a in ACCOUNTS:
    a["Lifetime_Bookings__c"] = round(won_by_acct[a["Id"]], 2)
for c in CONTACTS:
    c["LastActivityDate"] = ds(LAST_ACT.get(c["Id"]))
for l in LEADS:
    l["LastActivityDate"] = ds(LAST_ACT.get(l["Id"]))

# Campaign roll-ups
camp_opps = defaultdict(lambda: [0, 0, 0.0, 0.0])
for o in OPPS:
    if o["CampaignId"]:
        s = camp_opps[o["CampaignId"]]
        s[0] += 1
        s[2] += o["Amount"]
        if o["_closed"] and o["_won"]:
            s[1] += 1
            s[3] += o["Amount"]
for c in CAMPAIGNS:
    st = CM_STATS[c["Id"]]
    s = camp_opps[c["Id"]]
    c.update(NumberOfLeads=st["leads"], NumberOfConvertedLeads=st["converted"], NumberOfContacts=st["contacts"],
             NumberOfResponses=st["responses"], NumberOfOpportunities=s[0], NumberOfWonOpportunities=s[1],
             AmountAllOpportunities=round(s[2], 2), AmountWonOpportunities=round(s[3], 2),
             ExpectedRevenue=round(c["BudgetedCost"] * R.uniform(3, 8), -3), NumberSent=c["NumberSent"] or st["sent"])

# Quotas
QUOTAS = []
Q_BASE = {"SMB": 160_000, "Mid-Market": 520_000, "Enterprise": 1_100_000}
for u in USERS:
    if u["_role"] != "AE":
        continue
    for y in range(2021, 2026):
        for q in range(1, 5):
            qs = dt.date(y, q * 3 - 2, 1)
            qe = quarter_end(qs)
            if u["_hire"] > qe or (u["_term"] and u["_term"] < qs):
                continue
            tenure_q = ((qs - u["_hire"]).days // 91)
            ramp = 0.25 if tenure_q <= 0 else 0.5 if tenure_q == 1 else 0.75 if tenure_q == 2 else 1.0
            amt = round(Q_BASE[u["_seg"]] * (1.12 ** (y - 2021)) * ramp * (1.25 if q == 4 else 0.9 if q == 1 else 1.0), -3)
            QUOTAS.append(dict(Id=sfid("a0Q"), OwnerId=u["Id"], Fiscal_Year__c=y, Fiscal_Quarter__c=q, Period_Start__c=ds(qs),
                               Period_End__c=ds(qe), Quota_Amount__c=amt, Ramp_Factor__c=ramp, Segment__c=u["_seg"],
                               Region__c=u["_region"], Quota_Type__c="Closed Won Bookings (New + Upsell)"))

# --------------------------------------------------------------------------------------
# Write in-memory objects
# --------------------------------------------------------------------------------------
print("Writing CSVs ...")
for o in (OLI_OUT, HIST_OUT, OCR_OUT, TASK_OUT, EVENT_OUT, CM_OUT):
    o.close()
COUNTS = {o.name: o.n for o in (OLI_OUT, HIST_OUT, OCR_OUT, TASK_OUT, EVENT_OUT, CM_OUT)}
COUNTS["User"] = write_all("User", ["Id", "Username", "FirstName", "LastName", "Name", "Alias", "Email", "Title", "Department", "Division",
                                    "UserRole", "Profile", "ManagerId", "IsActive", "Region__c", "Segment__c", "Hire_Date__c",
                                    "Termination_Date__c", "TimeZoneSidKey", "CreatedDate"], USERS)
COUNTS["Product2"] = write_all("Product2", list(PROD_ROWS[0].keys()), PROD_ROWS)
COUNTS["Pricebook2"] = write_all("Pricebook2", list(PB_ROWS[0].keys()), PB_ROWS)
COUNTS["PricebookEntry"] = write_all("PricebookEntry", list(PBE_ROWS[0].keys()), PBE_ROWS)
COUNTS["Campaign"] = write_all("Campaign", ["Id", "Name", "Type", "Status", "StartDate", "EndDate", "IsActive", "ParentId", "BudgetedCost",
                                            "ActualCost", "ExpectedRevenue", "ExpectedResponse", "NumberSent", "NumberOfLeads",
                                            "NumberOfConvertedLeads", "NumberOfContacts", "NumberOfResponses", "NumberOfOpportunities",
                                            "NumberOfWonOpportunities", "AmountAllOpportunities", "AmountWonOpportunities", "OwnerId",
                                            "Region__c", "Description", "CreatedDate"], CAMPAIGNS)
COUNTS["Account"] = write_all("Account", ["Id", "Name", "Type", "Industry", "Segment__c", "Region__c", "AnnualRevenue", "NumberOfEmployees",
                                          "Ownership", "Rating", "BillingStreet", "BillingCity", "BillingState", "BillingPostalCode",
                                          "BillingCountry", "Phone", "Website", "AccountSource", "OwnerId", "CSM__c", "Customer_Since__c",
                                          "Churn_Date__c", "Contract_End_Date__c", "Current_ARR__c", "Lifetime_Bookings__c",
                                          "Licensed_Seats__c", "Primary_Edition__c", "Health_Score__c", "Description", "CreatedDate",
                                          "CreatedById", "LastModifiedDate", "LastActivityDate"],
                              sorted(ACCOUNTS, key=lambda a: a["CreatedDate"]))
COUNTS["Contact"] = write_all("Contact", ["Id", "AccountId", "FirstName", "LastName", "Title", "Department", "Level__c", "Email", "Phone",
                                          "MobilePhone", "MailingCity", "MailingState", "MailingCountry", "LeadSource", "OwnerId",
                                          "HasOptedOutOfEmail", "DoNotCall", "Converted_From_Lead__c", "CreatedDate", "LastActivityDate"],
                              CONTACTS)
COUNTS["Lead"] = write_all("Lead", LEAD_FIELDS, LEADS_SORTED)
COUNTS["Opportunity"] = write_all("Opportunity", ["Id", "Name", "AccountId", "OwnerId", "CreatedById", "Type", "StageName", "Amount",
                                                  "Probability", "ExpectedRevenue", "CloseDate", "IsClosed", "IsWon", "ForecastCategoryName",
                                                  "FiscalYear", "FiscalQuarter", "Fiscal", "LeadSource", "CampaignId", "Pricebook2Id",
                                                  "NextStep", "Loss_Reason__c", "Primary_Competitor__c", "Contract_Term_Months__c", "ARR__c",
                                                  "One_Time_Amount__c", "TCV__c", "Discount_Percent__c", "Segment__c", "Region__c",
                                                  "Sales_Cycle_Days__c", "Push_Count__c", "Attempt_Number__c", "HasOpportunityLineItem",
                                                  "Description", "CreatedDate", "LastModifiedDate", "LastActivityDate"],
                                  sorted(OPPS, key=lambda o: o["CreatedDate"]))
COUNTS["Case"] = write_all("Case", ["Id", "CaseNumber", "AccountId", "ContactId", "OwnerId", "Subject", "Description", "Type", "Reason",
                                    "Priority", "Origin", "Status", "IsClosed", "IsEscalated", "Product__c", "Support_Tier__c",
                                    "SLA_Target_Hours__c", "First_Response_Minutes__c", "Resolution_Hours__c", "SLA_Met__c",
                                    "CSAT_Score__c", "CreatedDate", "ClosedDate"], CASES)
COUNTS["Quota__c"] = write_all("Quota__c", list(QUOTAS[0].keys()), QUOTAS)
print(f"  done ({time.time() - t0:.0f}s)")

# --------------------------------------------------------------------------------------
# KPI summary
# --------------------------------------------------------------------------------------
yrs = range(2021, 2026)
k = {y: Counter() for y in yrs}
for l in LEADS:
    if l["_created"].year in k:
        k[l["_created"].year]["leads"] += 1
    if l["IsConverted"] == "true":
        k[dt.date.fromisoformat(l["ConvertedDate"]).year]["conv"] += 1
for o in OPPS:
    y = o["_close"].year
    if o["_created"].year in k:
        k[o["_created"].year]["opps_created"] += 1
    if not o["_closed"] or y not in k:
        continue
    t = o["_kind"]
    if t == "New Business":
        k[y]["nb_closed"] += 1
        k[y]["cycle"] += o["Sales_Cycle_Days__c"]
    if o["_won"]:
        k[y]["won_" + t] += o["Amount"]
        k[y]["won_amt"] += o["Amount"]
        if t == "New Business":
            k[y]["nb_won"] += 1
            k[y]["nb_won_amt"] += o["Amount"]
    elif t == "Existing Business - Renewal":
        k[y]["churn_arr"] += o["ARR__c"]
        k[y]["churned"] += 1
for c in CASES:
    k[c["_cd"].year]["cases"] += 1
    if c["CSAT_Score__c"]:
        k[c["_cd"].year]["csat_n"] += 1
        k[c["_cd"].year]["csat"] += c["CSAT_Score__c"]
for y in yrs:
    ye = dt.date(y, 12, 31)
    arr = cust = 0
    for a in ACCOUNTS:
        v = None
        for d, val in a["_arr_hist"]:
            if d <= ye:
                v = val
        if v:
            arr += v
            cust += 1
    k[y]["arr"], k[y]["cust"] = arr, cust

M = lambda x: f"${x / 1e6:,.1f}M"
lines = [f"# Data summary - {COMPANY} synthetic Salesforce org", "",
         f"Generated with seed `{ARGS.seed}`, scale `{SCALE}`. Snapshot date: **{SNAP}**. Coverage: **{START} to {END}** (FY = calendar year).", "",
         "## Row counts", "", "| Object | Rows |", "|---|---:|"]
for name in sorted(COUNTS, key=lambda n: -COUNTS[n]):
    lines.append(f"| {name} | {COUNTS[name]:,} |")
lines.append(f"| **Total** | **{sum(COUNTS.values()):,}** |")
lines += ["", "## Yearly KPIs (computed from the generated data)", "",
          "| FY | Leads created | Leads converted | Opps created | New-biz win rate | New logos | Avg new-biz deal | Avg cycle (days) | New-biz bookings | Upsell bookings | Renewal bookings | Total bookings | Churned logos | Ending customers | Ending ARR | Cases | Avg CSAT |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for y in yrs:
    s = k[y]
    lines.append(f"| {y} | {s['leads']:,} | {s['conv']:,} | {s['opps_created']:,} | {s['nb_won'] / max(1, s['nb_closed']):.1%} | {s['nb_won']:,} | "
                 f"${s['nb_won_amt'] / max(1, s['nb_won']):,.0f} | {s['cycle'] / max(1, s['nb_closed']):.0f} | {M(s['won_New Business'])} | "
                 f"{M(s['won_Existing Business - Upsell'])} | {M(s['won_Existing Business - Renewal'])} | {M(s['won_amt'])} | {s['churned']:,} | "
                 f"{s['cust']:,} | {M(s['arr'])} | {s['cases']:,} | {s['csat'] / max(1, s['csat_n']):.2f} |")
open_opps = [o for o in OPPS if not o["_closed"]]
lines += ["", f"Open pipeline at snapshot: **{len(open_opps):,} opportunities, {M(sum(o['Amount'] for o in open_opps))}** "
          f"(of which {sum(1 for o in open_opps if o['_close'] <= SNAP):,} are stale - close date already passed).",
          f"Account mix at snapshot: " + ", ".join(f"{t}: {n:,}" for t, n in Counter(a['Type'] for a in ACCOUNTS).most_common()) + "."]
with open(os.path.join(ROOT, "data_summary.md"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))

# --------------------------------------------------------------------------------------
# SQLite
# --------------------------------------------------------------------------------------
if not ARGS.no_sqlite:
    print("Building SQLite database ...")
    db = os.path.join(ROOT, "salesforce_crm.sqlite")
    if os.path.exists(db):
        os.remove(db)
    con = sqlite3.connect(db)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    import re
    INT, REAL = re.compile(r"^-?(0|[1-9]\d{0,17})$"), re.compile(r"^-?\d+\.\d+$")
    for name in sorted(COUNTS):
        path = os.path.join(DATA_DIR, name + ".csv")
        with open(path, newline="", encoding="utf-8") as f:
            rd = csv.reader(f)
            header = next(rd)
            rows = [[v if v != "" else None for v in r] for r in rd]
        types = []
        for j, col in enumerate(header):
            vals = [r[j] for r in rows[:30000] if r[j] is not None]
            if col == "Id" or col.endswith("Id") or col in ("CaseNumber", "BillingPostalCode", "PostalCode", "Phone", "MobilePhone"):
                types.append("TEXT")
            elif vals and all(INT.match(v) for v in vals):
                types.append("INTEGER")
            elif vals and all(INT.match(v) or REAL.match(v) for v in vals):
                types.append("REAL")
            else:
                types.append("TEXT")
        tname = f'"{name}"'
        con.execute(f"CREATE TABLE {tname} ({', '.join(f'\"{c}\" {t}' + (' PRIMARY KEY' if c == 'Id' else '') for c, t in zip(header, types))})")
        con.executemany(f"INSERT INTO {tname} VALUES ({','.join('?' * len(header))})", rows)
        for col in header:
            if col != "Id" and (col.endswith("Id") or col in ("CloseDate", "CreatedDate", "ActivityDate", "CSM__c")):
                con.execute(f'CREATE INDEX "ix_{name}_{col}" ON {tname} (\"{col}\")')
    con.commit()
    con.execute("VACUUM")
    con.close()
print(f"Finished in {time.time() - t0:.0f}s")
