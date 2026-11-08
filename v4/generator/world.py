"""Pass 1: build the whole world in memory (lightweight): accounts, families, trajectories, spend plans,
segments/status by fiscal year, contacts and their job moves, partners, the sales org with turnover, and coverage."""
import math
from collections import defaultdict, Counter
from core import *
import refdata as RD
import catalog as CAT

FYS = list(range(FY_FIRST, FY_LAST + 1))
ALL_FYS = list(range(LEGACY_FY_FIRST, FY_LAST + 1))
SEGS = ("Small Business", "Medium Business", "Large Enterprise", "Select")

ACCOUNTS, BY_ID, PARTNERS, CONTACTS, PEOPLE, STINTS = [], {}, [], [], [], []
SHOWCASE = {}
_used_names, _used_domains = set(), set()
FREEZE_BASE_CONTACTS = False   # V4+: when growing, people who leave an existing company only move to other new companies, so earlier contacts stay untouched


# ------------------------------------------------------------------ names & places
def person(first_pool=None):
    f = R.choice(RD.FIRST_EXTRA) if chance(.14) else R.choice(RD.FIRST)
    return f, R.choice(RD.LAST)


def pick_city(country=None, region=None):
    pool = RD.CA_CITIES if country == "Canada" else RD.US_CITIES
    if region:
        pool = [c for c in pool if c[0] == region] or pool
    return R.choices(pool, weights=[c[5] for c in pool])[0]


def street():
    s = f"{R.randint(1, 9890)} {R.choice(RD.STREETS)} {R.choice(RD.STREET_TYPES)}"
    if chance(.3):
        s += R.choice([", Suite ", ", Ste ", " #", ", Floor ", ", Unit "]) + str(R.randint(1, 2400) if chance(.8) else R.randint(2, 40))
    return s


def postal(country, prefix):
    if country == "Canada":
        L = "ABCEGHJKLMNPRSTVWXYZ"
        return f"{prefix} {R.randint(1, 9)}{R.choice(L)}{R.randint(1, 9)}"
    return prefix + f"{R.randint(0, 99):02d}"


def phone(area):
    return f"({area}) 555-{R.randint(100, 9999):04d}"


def company_name(industry, country, unique=True):
    words = RD.INDUSTRIES[industry][1]
    for _ in range(60):
        p = R.random()
        if industry == "State & Local Government":
            n = f"{R.choice(RD.ADJ)} {R.choice(RD.NOUN)} {R.choice(words)}" if chance(.6) else f"{R.choice(RD.ADJ)} {R.choice(words)}"
        elif industry == "Education":
            n = R.choice([f"{R.choice(RD.ADJ)} {R.choice(RD.NOUN)} {R.choice(words)}", f"{R.choice(RD.ADJ)} {R.choice(words)}",
                          f"{R.choice(RD.LAST)} {R.choice(words)}"])
        elif p < .34:
            n = f"{R.choice(RD.ADJ)} {R.choice(RD.NOUN)} {R.choice(words)}"
        elif p < .55:
            n = f"{R.choice(RD.ADJ)} {R.choice(words)}"
        elif p < .74:
            ln = R.choice(RD.LAST)
            n = f"{ln} {R.choice(words)}" if chance(.65) else f"{ln} & {R.choice(RD.LAST)} {R.choice(words)}"
        elif p < .90:
            n = R.choice(RD.SYL1) + R.choice(RD.SYL2) + (" " + R.choice(words) if chance(.6) else "")
        else:
            n = "".join(w[0] for w in (R.choice(RD.ADJ), R.choice(RD.NOUN), R.choice(words))).upper() + " " + R.choice(words)
        if not unique or n not in _used_names:
            _used_names.add(n)
            return n
    n = f"{n} {R.randint(2, 99)}"
    _used_names.add(n)
    return n


def legal_suffix(country, industry):
    if industry in RD.PUBLIC_SECTOR:
        return ""
    return R.choice(RD.LEGAL_SUFFIX_CA if country == "Canada" else RD.LEGAL_SUFFIX_US)


def domain_for(name):
    parts = [slug(w) for w in name.replace("&", " ").split() if slug(w) not in ("inc", "llc", "corp", "co", "ltd", "limited", "the")]
    d = "".join(parts)[:24] or "company"
    if len(d) > 16 and chance(.4):
        d = "".join(p[0] for p in parts) + parts[-1][:8]
    tld = R.choice([".com"] * 8 + [".net", ".org", ".co", ".io"])
    dom, i = d + tld, 2
    while dom in _used_domains:
        dom, i = f"{d}{i}{tld}", i + 1
    _used_domains.add(dom)
    return dom


# ------------------------------------------------------------------ account skeleton
def new_account(seg_end, role, country, industry=None, parent=None, name=None):
    industry = industry or wpick({k: v[0] for k, v in RD.INDUSTRIES.items()})
    city = pick_city(country)
    base = name or company_name(industry, country)
    sfx = legal_suffix(country, industry)
    legal = f"{base} {sfx}".strip() if sfx else base
    a = dict(id=sfid("001"), erp=str(seq("erp", 1_000_000, 7, 6)), base_name=base, legal=legal, dba=None,
             industry=industry, sub_industry=R.choice(RD.INDUSTRIES[industry][4]), naics=RD.NAICS[industry] + str(R.randint(10, 99)),
             country=country, city=city, region=city[0], state=city[1], street=street(), zip=postal(country, city[3]),
             phone=phone(city[4]), domain=domain_for(base), seg_end=seg_end, role=role, parent=parent, children=[],
             fye_month=wpick({12: 55, 6: 12, 9: 10, 3: 6, 1: 5, 4: 4, 10: 4, 7: 4}) if industry not in ("Education", "State & Local Government")
             else (6 if industry == "Education" else wpick({6: 50, 9: 40, 12: 10})),
             founded=R.randint(1890, 2019), news=[], name_hist=[], sites=[], partner_hist=[], flags=set(), status_end=None)
    a["ownership"] = ("Government" if industry == "State & Local Government" else "Education" if industry == "Education"
                      else "Nonprofit" if industry == "Nonprofit" else None)
    ACCOUNTS.append(a)
    BY_ID[a["id"]] = a
    if parent:
        parent["children"].append(a)
    return a


EMP = {"Small Business": (32, .7, 5, 99), "Medium Business": (290, .6, 100, 999), "Large Enterprise": (3400, .8, 1000, 60000),
       "Select": (38000, .7, 9000, 350000)}


def build_accounts(n):
    canada = lambda: "Canada" if chance(.05) else "United States"
    n_sel = max(5, round(n * .005))
    n_le_fam, n_mb_fam = max(4, round(n * .0225)), max(3, round(n * .0125))
    quotas = {"Large Enterprise": round(n * .30), "Medium Business": round(n * .45)}
    quotas["Small Business"] = n - n_sel - quotas["Large Enterprise"] - quotas["Medium Business"]
    used = Counter()

    def mk_sub(parent, seg):
        same_ind = chance(.7)
        ctry = parent["country"] if chance(.85) else canada()
        if chance(.5):  # branded subsidiary
            tail = R.choice(["Services", "Holdings", "Solutions", "International", "Distribution", "Manufacturing", "Health",
                             "Technologies", "Logistics", "Labs", "Financial", "Retail Group", "Operations", "Canada" if ctry == "Canada" else "West",
                             "Midwest", "Southeast", "Northeast", "Pacific", "Texas", "Digital"])
            nm = f"{parent['base_name'].split(' ')[0]} {parent['base_name'].split(' ')[1] if len(parent['base_name'].split()) > 2 else ''} {tail}".replace("  ", " ").strip()
            nm = nm if nm not in _used_names else None
        else:
            nm = None  # acquired brand with an unrelated name -> hard to discover
        s = new_account(seg, "subsidiary", ctry, parent["industry"] if same_ind else None, parent, nm)
        if nm:
            _used_names.add(nm)
        used[seg] += 1
        return s

    for i in range(n_sel):
        p = new_account("Select", "parent", "United States" if chance(.94) else "Canada")
        used["Select"] += 1
        for _ in range(R.randint(3, 15)):
            s = mk_sub(p, wpick({"Large Enterprise": 60, "Medium Business": 35, "Small Business": 5}))
            if chance(.18):
                for _ in range(R.randint(1, 3)):
                    mk_sub(s, wpick({"Medium Business": 70, "Small Business": 30}))
    for i in range(n_le_fam):
        p = new_account("Large Enterprise", "parent", canada())
        used["Large Enterprise"] += 1
        for _ in range(R.choice([1, 1, 2, 2, 2, 3, 3, 4, 5, 6])):
            mk_sub(p, wpick({"Large Enterprise": 40, "Medium Business": 50, "Small Business": 10}))
    for i in range(n_mb_fam):
        p = new_account("Medium Business", "parent", canada())
        used["Medium Business"] += 1
        for _ in range(R.choice([1, 1, 2, 2, 3])):
            mk_sub(p, wpick({"Medium Business": 60, "Small Business": 40}))
    for seg in ("Large Enterprise", "Medium Business", "Small Business"):
        for _ in range(max(0, quotas[seg] - used[seg])):
            new_account(seg, "standalone", canada())
    # hierarchy depth / ultimate parent
    for a in ACCOUNTS:
        u, depth = a, 0
        while u["parent"]:
            u, depth = u["parent"], depth + 1
        a["ultimate"], a["depth"] = u, depth
        # subsidiaries nobody linked in CRM -> covered (and priced) as if standalone
        if a["role"] == "subsidiary" and chance(.3):
            a["unlinked"] = True
            a["linked_on"] = rand_bday(fy_start(25), SNAP) if chance(.25) else None


# ------------------------------------------------------------------ trajectories (employees, revenue, IT budget)
GROWTH = {"hypergrowth": 10, "steady_growth": 34, "stable": 27, "declining": 10, "layoff_shock": 10, "acquisitive": 9}


def build_trajectories():
    for a in ACCOUNTS:
        seg = a["seg_end"]
        med, sig, lo, hi = EMP[seg]
        if a["role"] == "subsidiary":
            pe = a["parent"].get("emp_end") or EMP[a["parent"]["seg_end"]][0]
            hi = min(hi, max(lo + 1, int(pe * .6)))
        end = int(clip(lognorm(med, sig), lo, hi))
        a["emp_end"] = end
        ga = wpick(GROWTH)
        if seg == "Select":
            ga = wpick({"steady_growth": 50, "stable": 25, "acquisitive": 15, "layoff_shock": 10})
        if seg == "Small Business" and chance(.15):
            ga = "hypergrowth"
        a["growth"] = ga
        g = {}
        shock_fy = R.choice([24, 24, 25, 23]) if ga == "layoff_shock" else R.choice([23, 24, 25, 26]) if ga == "acquisitive" else None
        for f in ALL_FYS[1:]:
            if ga == "hypergrowth":
                rate = R.uniform(.25, .75) if f >= 22 else R.uniform(.1, .4)
            elif ga == "steady_growth":
                rate = R.uniform(.03, .13)
            elif ga == "stable":
                rate = R.uniform(-.03, .035)
            elif ga == "declining":
                rate = R.uniform(-.13, -.03)
            elif ga == "layoff_shock":
                rate = -R.uniform(.1, .3) if f == shock_fy else R.uniform(-.01, .05)
            else:
                rate = R.uniform(.25, 1.2) if f == shock_fy else R.uniform(.0, .08)
            if f == 21 and a["industry"] in ("Hospitality", "Retail", "Transportation & Logistics") and chance(.6):
                rate -= R.uniform(.05, .2)  # pandemic-era dip in the legacy year
            g[f] = rate
        a["shock_fy"] = shock_fy
        emp = {FY_LAST: end}
        for f in range(FY_LAST, LEGACY_FY_FIRST, -1):
            emp[f - 1] = max(3, int(round(emp[f] / (1 + g[f]))))
        a["emp"] = emp
        rpe = RD.INDUSTRIES[a["industry"]][2] * R.uniform(.6, 1.5)
        itp = RD.INDUSTRIES[a["industry"]][3] * R.uniform(.7, 1.4)
        a["rev"] = {f: round(emp[f] * rpe * (1 + R.gauss(0, .04)), -3) for f in ALL_FYS}
        a["itb"] = {f: a["rev"][f] * itp * (1 + R.gauss(0, .06)) for f in ALL_FYS}
        a["ownership"] = a["ownership"] or (wpick({"Public": 45, "Private": 35, "PE-Backed": 20}) if seg in ("Select", "Large Enterprise")
                                            else wpick({"Private": 70, "PE-Backed": 15, "Public": 5, "Family-Owned": 10}))
        if a["role"] == "subsidiary":
            a["ownership"] = "Subsidiary"
        a["ticker"] = ("".join(R.choice("ABCDEFGHIJKLMNOPRSTUVWXYZ") for _ in range(R.choice([3, 4]))) if a["ownership"] == "Public" else None)


# ------------------------------------------------------------------ status (Retention / Development / Acquisition) targets + buying windows
def build_status():
    for a in ACCOUNTS:
        seg = a["seg_end"]
        if seg == "Select" or (a["ultimate"]["seg_end"] == "Select" and chance(.8)):
            st = "retention"
        else:
            st = wpick({"never": 12, "retention": 53, "development": 27, "lapsed": 8})
        a["status_end"] = st
        if st == "never":
            a.update(first_buy=None, last_buy=None, gap=None)
            continue
        if st == "retention":
            last = SNAP - D(int(min(330, R.expovariate(1 / 30))))
        elif st == "development":
            last = SNAP - D(R.randint(380, 1080))
        else:
            last = SNAP - D(R.randint(1110, 1800)) if chance(.55) else SNAP - D(R.randint(1830, 3400))
        legacy = chance({"retention": .72, "development": .75, "lapsed": .95}[st]) or seg == "Select"
        if legacy:
            first = dt.date(R.randint(2008, 2020), R.randint(1, 12), R.randint(1, 28))
            if first >= last:
                first = last - D(R.randint(200, 1500))
        else:
            lo = WIN_START
            first = between(lo, max(lo, last - D(60)))
        gap = None
        if st == "retention" and chance(.15) and first < SNAP - D(1300):
            gs = between(max(first, WIN_START) + D(90), SNAP - D(900))
            gap = (gs, gs + D(R.randint(400, 760)))
            if gap[1] > last - D(60):
                gap = None
        a.update(first_buy=first, last_buy=last, gap=gap, legacy=legacy)


def buying(a, d):
    """True if account is in a buying period on date d."""
    if a["first_buy"] is None or d < a["first_buy"] or d > a["last_buy"]:
        return False
    if a["gap"] and a["gap"][0] <= d <= a["gap"][1]:
        return False
    return True


def buy_fraction(a, f):
    s, e = fy_start(f), fy_end(f)
    if a["first_buy"] is None:
        return 0.0
    days = sum(1 for k in range(0, 365, 7) if buying(a, s + D(k)))
    return days / 53


# ------------------------------------------------------------------ spend plan
MIX = {  # category share of hardware+services spend by segment
    "Small Business": {"client": .74, "workstation": .03, "server": .07, "storage": .02, "data_protection": .01, "networking": .04, "software": .04, "services": .05},
    "Medium Business": {"client": .52, "workstation": .05, "server": .14, "storage": .07, "data_protection": .04, "networking": .05, "software": .05, "services": .08},
    "Large Enterprise": {"client": .40, "workstation": .06, "server": .17, "storage": .11, "data_protection": .05, "networking": .05, "software": .06, "services": .10},
    "Select": {"client": .36, "workstation": .06, "server": .20, "storage": .12, "data_protection": .05, "networking": .05, "software": .06, "services": .10},
}
SHARE_MED = {"Small Business": .30, "Medium Business": .19, "Large Enterprise": .13, "Select": .24}


def build_spend():
    for a in ACCOUNTS:
        seg = a["seg_end"]
        base = clip(lognorm(SHARE_MED[seg], .55), .015, .85)
        drift = R.choice([0, .03, .06, .09, .12, .15, -.04, -.08])
        if a["status_end"] in ("development", "lapsed"):
            drift = -abs(drift) - .05
        a["share"] = {}
        a["spend"] = {}
        for f in ALL_FYS:
            sh = clip(base * (1 + drift) ** (f - 22), .005, .9)
            a["share"][f] = sh
            frac = buy_fraction(a, f) if f >= 22 else (1.0 if a["first_buy"] and a["first_buy"] <= fy_end(f) and a["last_buy"] >= fy_start(f) else 0)
            amt = a["itb"][f] * .4 * sh * frac * {22: 1.0, 23: .96, 24: .97, 25: 1.1, 26: 1.2}.get(f, 1.0)   # PC slump, then AI + Win11 wave
            if a["first_buy"] and fy_start(f) <= a["first_buy"] <= fy_end(f):
                amt *= R.uniform(.3, .8)  # first-year land
            a["spend"][f] = round(amt, 2) if amt > 300 else 0.0
        a["mix"] = dict(MIX[seg])


# ------------------------------------------------------------------ segments by fiscal year (lifecycle movement)
def seg_rule(emp, spend):
    s = "Small Business" if emp < 100 else "Medium Business" if emp < 1000 else "Large Enterprise"
    if spend >= 900_000:
        s = "Large Enterprise"
    elif spend >= 160_000 and s == "Small Business":
        s = "Medium Business"
    return s


def build_segments():
    sel_parents = [a for a in ACCOUNTS if a["seg_end"] == "Select"]
    for a in sel_parents:
        a["select_since"] = R.choice([18, 19, 20, 21, 22, 22, 23, 24, 25, 26]) if chance(.85) else 26
    le_parents = sorted([a for a in ACCOUNTS if a["role"] == "parent" and a["seg_end"] == "Large Enterprise"],
                        key=lambda a: -a["emp_end"])
    former = le_parents[:max(1, len(sel_parents) // 7)]
    for a in former:
        a["former_select"] = (22, R.choice([23, 24, 25]))
        a["growth"] = "declining"
        a["flags"].add("former_select")
    for a in ACCOUNTS:
        a["seg"] = {}
        for f in ALL_FYS:
            if a["seg_end"] == "Select" and f >= a["select_since"]:
                s = "Select"
            elif a.get("former_select") and a["former_select"][0] <= f < a["former_select"][1]:
                s = "Select"
            else:
                s = seg_rule(a["emp"][f - 1] if f - 1 in a["emp"] else a["emp"][f], a["spend"].get(f - 1, 0))
            a["seg"][f] = s
        # consumer-origin: founders who bought personally before the company had an account
        a["consumer_origin"] = (a["first_buy"] is not None and a["first_buy"] >= WIN_START and a["emp"][22] < 60
                                and chance(.45)) or (a["seg_end"] in ("Small Business", "Medium Business") and chance(.12))


# ------------------------------------------------------------------ news / company events (drive behavior)
def build_news():
    accs = [a for a in ACCOUNTS if a["role"] != "parent" or True]
    for a in ACCOUNTS:
        ga = a["growth"]
        if ga == "hypergrowth":
            for f in R.sample(FYS, R.randint(1, 3)):
                a["news"].append((rand_bday(fy_start(f), fy_end(f)), "funding"))
        if ga == "layoff_shock":
            a["news"].append((rand_bday(fy_start(a["shock_fy"]), fy_start(a["shock_fy"]) + D(150)), "layoffs"))
        if ga == "acquisitive":
            a["news"].append((rand_bday(fy_start(a["shock_fy"]) - D(120), fy_start(a["shock_fy"]) + D(60)), "acquisition"))
        if ga == "declining" and a["ownership"] == "Public":
            a["news"].append((rand_bday(fy_start(24), SNAP), "earnings_miss"))
        if a["ownership"] == "Public":
            for f in R.sample(FYS, 2):
                a["news"].append((rand_bday(fy_start(f), fy_end(f)), "earnings_beat" if a["growth"] in ("steady_growth", "hypergrowth") else R.choice(["earnings_beat", "earnings_miss"])))
        if chance(.22 if a["seg_end"] in ("Large Enterprise", "Select") else .1):
            a["news"].append((rand_bday(WIN_START + D(60), SNAP - D(20)), "exec_hire"))
        if chance(.06):
            a["news"].append((rand_bday(WIN_START + D(60), SNAP - D(60)), "hq_move"))
        if chance(.12 if a["seg_end"] != "Small Business" else .05):
            a["news"].append((rand_bday(WIN_START, SNAP), "expansion"))
        if chance(.035):
            a["news"].append((rand_bday(WIN_START + D(100), SNAP - D(100)), "rebrand"))
        if chance(.05):
            a["news"].append((rand_bday(WIN_START, SNAP), R.choice(["award", "partnership", "contract_win"])))
        if chance(.025 if a["industry"] in ("Healthcare", "Education", "State & Local Government", "Manufacturing") else .012):
            a["news"].append((rand_bday(WIN_START, SNAP), "cyber_incident"))
        if a["status_end"] == "lapsed" and a["last_buy"] > WIN_START and chance(.12):
            a["news"].append((a["last_buy"] + D(R.randint(30, 200)), "bankruptcy"))
            a["flags"].add("bankrupt")
        if a["growth"] == "hypergrowth" and chance(.1):
            a["news"].append((rand_bday(fy_start(25), SNAP), "ipo"))
        a["news"].sort()
        for d, t in a["news"]:
            if t == "rebrand":
                nb = company_name(a["industry"], a["country"])
                a["name_hist"].append((d, nb))
                a["flags"].add("renamed")
            if t == "hq_move":
                nc = pick_city(a["country"])
                a["hq_move"] = (d, nc, a["city"])
    # customer-to-customer M&A: an acquisitive account buys another account in the dataset
    buyers = [a for a in ACCOUNTS if a["growth"] == "acquisitive" and a["seg_end"] in ("Large Enterprise", "Select")]
    targets = [a for a in ACCOUNTS if a["role"] == "standalone" and a["seg_end"] in ("Medium Business", "Small Business")
               and a["status_end"] in ("development", "lapsed") and a["last_buy"] and a["last_buy"] > WIN_START + D(200)]
    R.shuffle(targets)
    for b, t in zip(buyers, targets[: max(1, len(buyers) // 3)]):
        d = t["last_buy"] + D(R.randint(10, 90))
        if d > SNAP - D(30):
            continue
        t["acquired_by"] = (b, d)
        t["news"].append((d, "acquired"))
        b["news"].append((d, "acquisition"))
        t["flags"].add("acquired_by_customer")


# ------------------------------------------------------------------ sites (ship-tos)
SITE_TYPES = {"Healthcare": ["Clinic", "Hospital", "Outpatient Center", "Lab"], "Retail": ["Store", "Distribution Center", "Store", "Warehouse"],
              "Manufacturing": ["Plant", "Warehouse", "R&D Center"], "Education": ["Campus", "School", "Admin Building"],
              "Transportation & Logistics": ["Terminal", "Warehouse", "Distribution Center"]}


def build_sites():
    for a in ACCOUNTS:
        a["sites"].append(dict(id=f"ST-{a['erp']}-01", type="Headquarters", city=a["city"], street=a["street"], zip=a["zip"],
                               region=a["region"], state=a["state"], country=a["country"], opened=None))
        n = {"Small Business": R.choice([0, 0, 0, 1]), "Medium Business": R.randint(0, 4), "Large Enterprise": R.randint(2, 14),
             "Select": R.randint(10, 60)}[a["seg_end"]]
        for i in range(n):
            c = pick_city(a["country"] if chance(.9) else None)
            st = R.choice(SITE_TYPES.get(a["industry"], ["Branch Office", "Regional Office", "Warehouse", "Data Center"]))
            if a["seg_end"] in ("Large Enterprise", "Select") and i < 2 and chance(.6):
                st = "Data Center" if i == 0 else "Colocation Facility"
            a["sites"].append(dict(id=f"ST-{a['erp']}-{i + 2:02d}", type=st, city=c, street=street(), zip=postal("Canada" if c in RD.CA_CITIES else "United States", c[3]),
                                   region=c[0], state=c[1], country="Canada" if c in RD.CA_CITIES else "United States",
                                   opened=rand_bday(WIN_START, SNAP) if chance(.15) else None))
        if a.get("hq_move"):
            d, nc, old = a["hq_move"]
            a["sites"].append(dict(id=f"ST-{a['erp']}-HQ2", type="Headquarters (new)", city=nc, street=street(), zip=postal(a["country"], nc[3]),
                                   region=nc[0], state=nc[1], country=a["country"], opened=d))


# ------------------------------------------------------------------ technology environment + initiatives by FY
INIT = ["Windows 11 migration", "PC refresh", "Data center refresh", "VMware exit / hypervisor change", "AI pilot", "AI production rollout",
        "Cloud repatriation", "Ransomware resilience", "VDI expansion", "Edge / IoT rollout", "Storage consolidation",
        "Network modernization", "Hybrid work enablement", "Cost reduction program", "M&A integration", "New site build-out",
        "ERP migration", "EHR upgrade", "Zero-trust security"]


def build_environment():
    for a in ACCOUNTS:
        e = a["emp_end"]
        seg = a["seg_end"]
        a["env"] = dict(hypervisor=R.choice(RD.HYPERVISORS[:3] + ["Hyper-V"]) if seg != "Small Business" else R.choice(["None (bare metal)", "Hyper-V", "VMware vSphere 7"]),
                        cloud=R.choice(RD.CLOUDS), itsm=R.choice(RD.ITSM) if seg != "Small Business" else R.choice(["None", "Zendesk", "In-house"]),
                        backup=R.choice(RD.BACKUP), client_os_fy22="Windows 10",
                        primary_competitor=wpick(RD.COMPETITORS), competitor_share=round(R.uniform(.1, .7), 2))
        a["inits"] = defaultdict(list)
        for f in FYS:
            k = 0 if seg == "Small Business" else R.randint(0, 2) if seg == "Medium Business" else R.randint(1, 4)
            pool = list(INIT)
            if f < 24:
                pool = [x for x in pool if not x.startswith("AI") and "VMware" not in x]
            if f >= 25:
                pool += ["Windows 11 migration"] * 3 + ["AI pilot"] * 2
            if a["industry"] != "Healthcare":
                pool = [x for x in pool if x != "EHR upgrade"]
            for x in set(R.sample(pool, min(k, len(pool)))):
                a["inits"][f].append(x)
        for d, t in a["news"]:
            if t in ("acquisition", "acquired"):
                a["inits"][fy(d)].append("M&A integration")
            if t == "layoffs":
                a["inits"][fy(d)].append("Cost reduction program")


# ------------------------------------------------------------------ finance profile
PO_FORMATS = ["45{n:08d}", "PO-{y}-{n4:04d}", "{n6:06d}", "P{n7:07d}", "{abbr}-{n5:05d}", "PO{n6:06d}", "{y}{n5:05d}"]


def build_finance():
    for a in ACCOUNTS:
        seg = a["seg_end"]
        a["pay_style"] = wpick({"prompt": 45, "slow": 30, "disputer": 12, "chaotic": 8, "card_heavy": 5}) if seg != "Small Business" \
            else wpick({"prompt": 40, "card_heavy": 35, "slow": 15, "chaotic": 10})
        a["terms"] = wpick({"Net 30": 60, "Net 45": 25, "Net 60": 15}) if seg in ("Large Enterprise", "Select") else \
            wpick({"Net 30": 75, "Net 45": 10, "Due on Receipt": 15}) if seg == "Medium Business" else wpick({"Due on Receipt": 60, "Net 30": 40})
        a["po_required"] = seg in ("Large Enterprise", "Select") or (seg == "Medium Business" and chance(.7)) or a["industry"] in RD.PUBLIC_SECTOR
        a["po_fmt"] = R.choice(PO_FORMATS)
        a["abbr"] = "".join(w[0] for w in a["base_name"].split()[:3]).upper()
        a["credit_limit"] = human_round(max(5000, (sum(a["spend"].get(f, 0) for f in (24, 25, 26)) / 3) * R.uniform(.2, .5)))
        a["tax_exempt"] = a["industry"] in RD.PUBLIC_SECTOR or a["industry"] == "Healthcare" and chance(.3)
        a["tax_cert_exp"] = dt.date(R.randint(2022, 2027), R.randint(1, 12), 28) if a["tax_exempt"] else None
        a["blanket_po"] = seg in ("Large Enterprise", "Select") and chance(.35)
        a["currency"] = "CAD" if a["country"] == "Canada" and chance(.85) else "USD"
        a["lease_pref"] = chance(.12 if seg != "Small Business" else .04)
        a["flex"] = seg in ("Large Enterprise", "Select") and chance(.18)
        a["daas"] = seg in ("Medium Business", "Large Enterprise") and chance(.07)
        # parent-level contract pricing agreement
        if a["role"] == "parent" and seg in ("Select", "Large Enterprise"):
            a["agreement"] = dict(id=f"CPA-{R.randint(10000, 99999)}", start=fy_start(R.choice([21, 22, 23])),
                                  disc={"client": R.uniform(.12, .26), "workstation": R.uniform(.12, .24), "server": R.uniform(.18, .38),
                                        "storage": R.uniform(.25, .45), "data_protection": R.uniform(.22, .4), "networking": R.uniform(.18, .35),
                                        "software": R.uniform(.03, .1), "services": R.uniform(.05, .18)})
        else:
            a["agreement"] = None


# ------------------------------------------------------------------ partners & Quillon (acquired rival) & duplicates
def build_partners():
    for name, ptype, region, focus, segs in RD.PARTNERS:
        c = pick_city("Canada" if "Canadian" in ptype else "United States", region)
        p = dict(id=sfid("001"), erp=str(seq("erp", 1_000_000, 7, 6)), base_name=name, legal=name + (" Inc." if "IT" not in name else " LLC"),
                 type=ptype, region=region, focus=focus, segs=segs, city=c, state=c[1], country="Canada" if "Canadian" in ptype else "United States",
                 street=street(), zip=postal("Canada" if "Canadian" in ptype else "United States", c[3]), phone=phone(c[4]),
                 domain=domain_for(name), tier=R.choice(["Titanium", "Platinum", "Gold"]), joined=dt.date(R.randint(2009, 2019), R.randint(1, 12), 1))
        PARTNERS.append(p)
    for a in ACCOUNTS:
        seg = a["seg_end"]
        if seg == "Select":
            continue
        p_rate = {"Small Business": .28, "Medium Business": .30, "Large Enterprise": .12}[seg]
        if not chance(p_rate):
            continue
        elig = [p for p in PARTNERS if seg in p["segs"] and (p["country"] == a["country"] or p["base_name"] != "Maplegrid Systems")]
        if a["country"] == "Canada":
            elig = [p for p in PARTNERS if p["base_name"] == "Maplegrid Systems"] or elig
        else:
            elig = [p for p in elig if p["base_name"] != "Maplegrid Systems"]
        p = R.choice(elig)
        start = between(WIN_START - D(800), SNAP - D(200))
        a["partner_hist"].append((p, start, None))
        if chance(.18):  # switched partner of record
            sw = between(start + D(200), SNAP - D(30))
            p2 = R.choice([x for x in elig if x is not p] or [p])
            a["partner_hist"][-1] = (p, start, sw)
            a["partner_hist"].append((p2, sw, None))
        a["partner_share"] = R.uniform(.45, .95)


def partner_on(a, d):
    for p, s, e in a["partner_hist"]:
        if s <= d and (e is None or d < e):
            return p
    return None


def build_quillon():
    """Quillon Systems (acquired FY24) customers: their history lives in Quillon ERP; CRM records migrated on QUILLON_MIGRATION."""
    for a in ACCOUNTS:
        a["quillon"] = a["first_buy"] is not None and a["first_buy"] < QUILLON_MIGRATION and chance(.09)
        if a["quillon"]:
            a["quillon_only"] = a["legacy"] is False or chance(.55)   # was Quillon-only customer before
            a["quillon_erp"] = f"QC{R.randint(100000, 999999)}"
            a["quillon_name"] = R.choice([a["legal"], a["legal"].upper(), a["base_name"], a["base_name"] + " (QL)",
                                          a["legal"].replace("Inc.", "Incorporated").replace("Corp.", "Corporation")])


# ------------------------------------------------------------------ contacts (people at customers) with job moves
TITLES = {
    "exec": [("Chief Information Officer", "IT", "C-Level"), ("Chief Technology Officer", "IT", "C-Level"), ("Chief Financial Officer", "Finance", "C-Level"),
             ("Chief Information Security Officer", "Security", "C-Level"), ("Chief Operating Officer", "Operations", "C-Level"),
             ("Chief Data Officer", "Data & Analytics", "C-Level"), ("Chief Medical Information Officer", "Clinical IT", "C-Level")],
    "vp": [("VP of IT", "IT", "VP"), ("VP Infrastructure & Operations", "IT", "VP"), ("VP Engineering", "Engineering", "VP"),
           ("VP Enterprise Architecture", "IT", "VP"), ("VP Procurement", "Procurement", "VP"), ("VP Digital Transformation", "IT", "VP")],
    "dir": [("Director of IT", "IT", "Director"), ("Director of Infrastructure", "IT", "Director"), ("Director, End User Computing", "IT", "Director"),
            ("Director of Data Center Operations", "IT", "Director"), ("Director of Network Engineering", "IT", "Director"),
            ("Director of IT Procurement", "Procurement", "Director"), ("Director of Cybersecurity", "Security", "Director"),
            ("Director, AI & Data Platforms", "Data & Analytics", "Director")],
    "mgr": [("IT Manager", "IT", "Manager"), ("Infrastructure Manager", "IT", "Manager"), ("Desktop Support Manager", "IT", "Manager"),
            ("Storage & Backup Manager", "IT", "Manager"), ("Network Manager", "IT", "Manager"), ("IT Asset Manager", "IT", "Manager"),
            ("Procurement Manager", "Procurement", "Manager"), ("Accounts Payable Manager", "Finance", "Manager"), ("Facilities Manager", "Facilities", "Manager")],
    "ic": [("Systems Administrator", "IT", "Individual Contributor"), ("Senior Systems Engineer", "IT", "Individual Contributor"),
           ("Storage Administrator", "IT", "Individual Contributor"), ("Network Engineer", "IT", "Individual Contributor"),
           ("Cloud Architect", "IT", "Individual Contributor"), ("Solutions Architect", "IT", "Individual Contributor"),
           ("Desktop Engineer", "IT", "Individual Contributor"), ("Virtualization Engineer", "IT", "Individual Contributor"),
           ("Security Engineer", "Security", "Individual Contributor"), ("ML Engineer", "Data & Analytics", "Individual Contributor"),
           ("Buyer", "Procurement", "Individual Contributor"), ("AP Specialist", "Finance", "Individual Contributor"),
           ("IT Coordinator", "IT", "Individual Contributor")],
    "smb": [("Owner", "Executive", "C-Level"), ("President", "Executive", "C-Level"), ("Office Manager", "Operations", "Manager"),
            ("Operations Manager", "Operations", "Manager"), ("IT Consultant (outsourced)", "IT", "Individual Contributor"),
            ("Controller", "Finance", "Manager"), ("Managing Partner", "Executive", "C-Level")],
}
N_CONTACTS = {"Small Business": (2, 5), "Medium Business": (6, 14), "Large Enterprise": (14, 34), "Select": (40, 90)}


def _mk_contact(a, start, tier, end=None):
    f, l = person()
    t = R.choice(TITLES[tier])
    if a["industry"] != "Healthcare" and "Medical" in t[0]:
        t = TITLES["exec"][0]
    c = dict(id=sfid("003"), acct=a, first=f, last=l, title=t[0], dept=t[1], level=t[2], tier=tier, start=start, end=end,
             email=f"{slug(f)}.{slug(l)}@{a['domain']}", phone=phone(a["city"][4]), mobile=phone(a["city"][4]) if chance(.5) else None,
             reports_to=None, moved_to=None, moved_from=None, title_hist=[], roles=set(), shared=False, flags=set())
    if chance(.08):
        c["email"] = f"{slug(f)[0]}{slug(l)}@{a['domain']}"
    if chance(.04):
        c["email"] = f"{slug(f)}{slug(l)}{R.randint(1, 99)}@{R.choice(['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com'])}"
        c["flags"].add("personal_email")
    CONTACTS.append(c)
    a["contacts"].append(c)
    return c


def build_contacts():
    for a in ACCOUNTS:
        a["contacts"] = []
        seg = a["seg_end"]
        lo, hi = N_CONTACTS[seg]
        n = R.randint(lo, hi)
        a_start = min(a["first_buy"] or WIN_START, WIN_START) if a["first_buy"] else between(WIN_START - D(400), SNAP - D(200))
        if seg == "Small Business":
            tiers = ["smb"] * n
        else:
            mix = {"Medium Business": {"exec": 1, "vp": 1, "dir": 2, "mgr": 3, "ic": 4}, "Large Enterprise": {"exec": 2, "vp": 2, "dir": 4, "mgr": 5, "ic": 6},
                   "Select": {"exec": 3, "vp": 4, "dir": 8, "mgr": 9, "ic": 10}}[seg]
            tiers = ["exec"] + [wpick(mix) for _ in range(n - 1)]
        for t in tiers:
            st = a_start - D(R.randint(0, 900)) if chance(.7) else between(a_start, SNAP - D(30))
            _mk_contact(a, st, t)
        # shared mailboxes
        if seg != "Small Business":
            for box, ti in (("ap", "Accounts Payable"), ("purchasing", "Purchasing Team"), ("itsupport", "IT Help Desk")):
                if chance(.55):
                    c = _mk_contact(a, a_start, "ic")
                    c.update(first=ti.split()[0], last=" ".join(ti.split()[1:]) or "Team", title=ti, email=f"{box}@{a['domain']}", shared=True,
                             dept="Finance" if box == "ap" else "Procurement" if box == "purchasing" else "IT", level="Shared Mailbox")
        # turnover: people leave; replacements hired; some move to other customer accounts
        cur = [c for c in a["contacts"] if not c["shared"]]
        for c in list(cur):
            yrs = (SNAP - max(c["start"], WIN_START - D(365))).days / 365
            p_leave = 1 - math.exp(-yrs * (.13 if c["level"] in ("C-Level", "VP") else .11))
            if chance(p_leave):
                end = between(max(c["start"] + D(120), WIN_START), SNAP - D(10))
                c["end"] = end
                if c["tier"] != "smb" or chance(.5):
                    rep = _mk_contact(a, end + D(R.randint(14, 160)), c["tier"])
                    rep["title"], rep["dept"], rep["level"] = c["title"], c["dept"], c["level"]
                    rep["replaces"] = c
            elif chance(.12) and c["tier"] in ("mgr", "dir", "ic"):
                d = between(WIN_START, SNAP - D(30))
                up = {"ic": "mgr", "mgr": "dir", "dir": "vp"}[c["tier"]]
                nt = R.choice(TITLES[up])
                c["title_hist"].append((d, c["title"], nt[0]))
        # reports-to chain
        bosses = sorted([c for c in a["contacts"] if not c["shared"]], key=lambda c: ["C-Level", "VP", "Director", "Manager", "Individual Contributor"].index(c["level"]) if c["level"] in ("C-Level", "VP", "Director", "Manager", "Individual Contributor") else 9)
        for i, c in enumerate(bosses[1:], 1):
            higher = [b for b in bosses[:i] if b["level"] != c["level"]]
            if higher:
                c["reports_to"] = R.choice(higher[-3:])
    # job moves between customer accounts (same person, new record at new company)
    leavers = [c for c in CONTACTS if c["end"] and not c["shared"] and c["end"] < SNAP - D(60)]
    if FREEZE_BASE_CONTACTS:
        cur = {id(a) for a in ACCOUNTS}
        leavers = [c for c in leavers if id(c["acct"]) in cur]
    R.shuffle(leavers)
    accs = [a for a in ACCOUNTS if a["seg_end"] != "Small Business"]
    for c in leavers[: int(len(leavers) * .2)]:
        dest = R.choice(accs)
        if dest is c["acct"]:
            continue
        st = c["end"] + D(R.randint(10, 120))
        if st > SNAP:
            continue
        tier = c["tier"] if c["tier"] != "smb" else "mgr"
        if chance(.4) and tier in ("mgr", "dir", "vp"):
            tier = {"mgr": "dir", "dir": "vp", "vp": "exec"}[tier]
        n = _mk_contact(dest, st, tier)
        n.update(first=c["first"], last=c["last"])
        n["email"] = f"{slug(c['first'])}.{slug(c['last'])}@{dest['domain']}"
        n["moved_from"], c["moved_to"] = c, n
    for a in ACCOUNTS:
        for d, t in a["news"]:
            if t == "exec_hire":
                execs = [c for c in a["contacts"] if c["level"] == "C-Level" and c["start"] < d and (c["end"] is None or c["end"] > d)]
                old = execs[0] if execs else None
                if old:
                    old["end"] = d - D(R.randint(0, 45))
                new = _mk_contact(a, d, "exec")
                if old:
                    new["title"], new["dept"] = old["title"], old["dept"]
                new["new_exec_news"] = True
                a["new_exec"] = (d, new, old)


# ------------------------------------------------------------------ sales org (people, stints, attrition, promotions)
ROLES = {  # key: (title, capacity accounts, annual attrition, feeder role)
    "SB_REP": ("Small Business Inside Sales Representative", 260, .45, None),
    "MB_IAE": ("Inside Account Executive", 75, .32, "SB_REP"),
    "LE_FAE": ("Field Account Executive", 24, .18, "MB_IAE"),
    "SEL_GAD": ("Global Account Director", 1, .09, "LE_FAE"),
    "LE_IAE": ("Inside Account Executive - Enterprise", 70, .30, "SB_REP"),
    "SEL_RAM": ("Regional Account Manager - Select", 6, .12, "LE_IAE"),
    "MB_SPEC_CLIENT": ("Inside Client Solutions Specialist", 300, .28, "SB_REP"),
    "MB_SPEC_INFRA": ("Inside Infrastructure Specialist", 300, .25, None),
    "MB_SPEC_SW": ("Inside Software Specialist", 450, .25, None),
    "MB_SPEC_SVC": ("Inside Services Specialist", 450, .25, None),
    "OV_SERVER": ("Server Sales Specialist", 70, .18, "MB_SPEC_INFRA"),
    "OV_STORAGE": ("Storage Sales Specialist", 70, .18, "MB_SPEC_INFRA"),
    "OV_DP": ("Data Protection Specialist", 110, .18, None),
    "OV_NET": ("Networking Specialist", 120, .18, None),
    "OV_WKS": ("Workstation & Client Specialist", 150, .2, "MB_SPEC_CLIENT"),
    "OV_SW": ("Software Sales Specialist", 150, .2, "MB_SPEC_SW"),
    "OV_SVC": ("Services Sales Executive", 120, .17, "MB_SPEC_SVC"),
    "OV_FIN": ("Financial Services Specialist", 260, .15, None),
    "SA": ("Solutions Architect", 45, .12, None),
    "TAM": ("Technical Account Manager", 35, .14, None),
    "SDM": ("Services Delivery Manager", 4, .12, None),
}
OWNER_ROLE = {"Small Business": "SB_REP", "Medium Business": "MB_IAE", "Large Enterprise": "LE_FAE", "Select": "SEL_GAD"}
TEAM_ROLES = {"Small Business": [],
              "Medium Business": ["MB_SPEC_CLIENT", "MB_SPEC_INFRA", "MB_SPEC_SW", "MB_SPEC_SVC"],
              "Large Enterprise": ["LE_IAE", "OV_SERVER", "OV_STORAGE", "OV_DP", "OV_NET", "OV_WKS", "OV_SW", "OV_SVC", "OV_FIN", "SA", "TAM"],
              "Select": ["LE_IAE", "OV_SERVER", "OV_STORAGE", "OV_DP", "OV_NET", "OV_WKS", "OV_SW", "OV_SVC", "OV_FIN", "SA", "TAM", "SDM"]}
PERSONAS = {"by_the_book": 30, "star": 10, "sandbagger": 12, "happy_ears": 12, "discounter": 12, "non_logger": 12, "bulk_logger": 8, "sloppy": 4}


def region_scope(a, f):
    reg = a["region"]
    if a.get("hq_move") and a["hq_move"][0] < fy_start(f):
        reg = a["hq_move"][1][0]
    if f < 24:
        if a["country"] == "Canada":
            return "Canada"
        st = a["state"] if not (a.get("hq_move") and a["hq_move"][0] < fy_start(f)) else a["hq_move"][1][1]
        if reg == "Central":
            return "US West" if st in RD.CENTRAL_FROM_WEST else "US East"
        return RD.LEGACY_REGION[reg]
    return reg


def new_person(hire, region):
    f, l = person()
    p = dict(id=sfid("005"), emp_no=f"E{seq('emp', 104000, 3, 2)}", first=f, last=l, hire=hire, term=None, region=region,
             persona=wpick(PERSONAS), stints=[], rehire_of=None)
    base = f"{slug(f)}.{slug(l)}"
    p["email"] = f"{base}@orvane.com" if not any(x["email"] == f"{base}@orvane.com" for x in PEOPLE[-400:]) else f"{base}{R.randint(2, 9)}@orvane.com"
    PEOPLE.append(p)
    return p


def new_stint(person_, role, start, region):
    s = dict(person=person_, role=role, start=start, end=None, region=region, load=0)
    person_["stints"].append(s)
    STINTS.append(s)
    return s


def stint_active(s, d):
    return s["start"] <= d and (s["end"] is None or d < s["end"])


def build_org():
    """Simulate headcount per role/region/FY from coverage demand; attrition, backfills, promotions, boomerangs."""
    demand = defaultdict(Counter)   # (role) -> Counter[(fy, region)] accounts
    for a in ACCOUNTS:
        for f in FYS:
            seg = a["seg"][f]
            reg = region_scope(a, f)
            sel_family = a["ultimate"]["seg"][f] == "Select" and a["ultimate"] is not a and not a.get("unlinked")
            if sel_family:
                demand["SEL_RAM"][(f, reg)] += 1
                continue
            demand[OWNER_ROLE[seg]][(f, reg)] += 1
            for r in TEAM_ROLES[seg]:
                if r == "TAM" and not (seg == "Select" or chance(.35)):
                    continue
                demand[r][(f, reg)] += 1
    pools = defaultdict(list)  # role -> list of stints
    for role, (title, cap, attr, feeder) in ROLES.items():
        for f in FYS:
            regions = {r for (ff, r) in demand[role] if ff == f}
            for reg in sorted(regions):
                need = max(1, math.ceil(demand[role][(f, reg)] / cap))
                d0 = fy_start(f)
                act = [s for s in pools[role] if stint_active(s, d0) and s["region"] == reg]
                # FY24 restructure: legacy-region people re-homed into new regions
                if f == 24:
                    legacy = [s for s in pools[role] if stint_active(s, d0) and s["region"] in ("US West", "US East", "Canada")]
                    for s in legacy:
                        if len(act) >= need:
                            break
                        cand = {"US West": ("West", "Central"), "US East": ("East", "Central"), "Canada": ("East", "West", "Central")}[s["region"]]
                        if reg in cand:
                            s["end"] = d0
                            ns = new_stint(s["person"], role, d0, reg)
                            pools[role].append(ns)
                            act.append(ns)
                if f == 24:
                    pass
                while len(act) < need:
                    hire = d0 - D(R.randint(0, 45)) if f > 22 else d0 - D(R.randint(60, 2400))
                    p = None
                    if feeder and f > 22 and chance(.3):
                        fs = [s for s in pools[feeder] if stint_active(s, d0) and s["end"] is None and s["region"] == reg]
                        if fs:
                            src = R.choice(fs)
                            src["end"] = d0
                            src["promoted"] = True
                            p = src["person"]
                    if p is None:
                        p = new_person(hire, reg)
                    s = new_stint(p, role, d0 if f > 22 or p["stints"] else min(hire, d0), reg)
                    if f == 22:
                        s["start"] = min(p["hire"], d0)
                    pools[role].append(s)
                    act.append(s)
                if len(act) > need + 1 and f > 22:   # overstaffed: someone leaves at realignment
                    for s in R.sample(act, len(act) - need - 1):
                        s["end"] = d0
                        s["person"]["term"] = d0
                        act.remove(s)
            # mid-year attrition + backfill (time-ordered by FY)
            for s in [s for s in pools[role] if stint_active(s, fy_start(f)) and s["end"] is None]:
                if chance(attr * (1.3 if s["person"]["persona"] == "sloppy" else 1)):
                    t = rand_bday(fy_start(f) + D(20), fy_end(f) - D(5))
                    s["end"] = t
                    s["person"]["term"] = t
                    s["left"] = True
                    gap = R.randint(25, 110)
                    bf = t + D(gap)
                    if bf < fy_end(f) - D(20) and bf <= SNAP:
                        np_ = new_person(bf, s["region"])
                        if chance(.04) and [q for q in PEOPLE if q["term"] and q["term"] < bf - D(180)]:
                            old = R.choice([q for q in PEOPLE if q["term"] and q["term"] < bf - D(180)])
                            np_.update(first=old["first"], last=old["last"], rehire_of=old)
                            np_["email"] = f"{slug(old['first'])}.{slug(old['last'])}2@orvane.com"
                        ns = new_stint(np_, role, bf, s["region"])
                        ns["backfill_for"] = s
                        pools[role].append(ns)
    for p in PEOPLE:
        live = [s for s in p["stints"] if s["end"] is None]
        if not live and p["term"] is None:
            p["term"] = max(s["end"] for s in p["stints"])
        if live:
            p["term"] = None
    return pools


def build_leaders():
    leaders = {}
    for key, title, reg in (("CEO", "Chief Executive Officer", "HQ"), ("CRO", "Chief Revenue Officer", "HQ"),
                            ("VP_SEL", "VP, Select Accounts", "HQ"), ("VP_LE", "VP, Large Enterprise Sales", "HQ"),
                            ("VP_MB", "VP, Medium Business Sales", "HQ"), ("VP_SB", "VP, Small Business & Consumer", "HQ"),
                            ("VP_CH", "VP, Channel & Partners", "HQ"), ("VP_CS", "VP, Customer Experience & Support", "HQ"),
                            ("VP_FIN", "VP, Order-to-Cash", "HQ"), ("RVP_W", "Regional VP - West", "West"),
                            ("RVP_C", "Regional VP - Central", "Central"), ("RVP_E", "Regional VP - East", "East")):
        p = new_person(dt.date(R.randint(2012, 2020), R.randint(1, 12), 1), reg)
        p["title_override"] = title
        p["persona"] = "by_the_book"
        new_stint(p, key, p["hire"], reg)
        leaders[key] = p
    for role, n, title in (("PAM", 5, "Partner Account Manager"), ("COLL", 6, "Collections Specialist"), ("CREDIT", 2, "Credit Analyst"),
                           ("DEALDESK", 3, "Deal Desk Analyst"), ("ORDERS", 5, "Order Management Specialist"), ("SUPPORT", 22, "Technical Support Engineer"),
                           ("MKT", 6, "Field Marketing Manager"), ("SOPS", 3, "Sales Operations Analyst"), ("SDR", 8, "Sales Development Representative")):
        for i in range(n):
            reg = ["West", "Central", "East"][i % 3]
            p = new_person(dt.date(R.randint(2016, 2021), R.randint(1, 12), 1), reg)
            p["title_override"] = title
            s = new_stint(p, role, min(p["hire"], WIN_START), reg)
            if chance(.25):
                t = rand_bday(WIN_START + D(200), SNAP - D(60))
                s["end"], p["term"] = t, t
                p2 = new_person(t + D(R.randint(20, 80)), reg)
                p2["title_override"] = title
                new_stint(p2, role, p2["hire"], reg)
    return leaders


def pool_of(role):
    return [s for s in STINTS if s["role"] == role]


# ------------------------------------------------------------------ coverage: who owned / covered the account when
def build_coverage(pools):
    """For every account and FY: owner stints and team stints with mid-year turnover gaps (truth)."""
    by_role_reg = defaultdict(list)
    for s in STINTS:
        by_role_reg[(s["role"], s["region"])].append(s)

    def pick_stint(role, reg, d, prev=None):
        if prev and prev["role"] == role and prev["region"] == reg and stint_active(prev, d):
            return prev
        c = [s for s in by_role_reg[(role, reg)] if stint_active(s, d)]
        if not c:
            c = [s for s in STINTS if s["role"] == role and stint_active(s, d)]
        if not c:
            return None
        c.sort(key=lambda s: s["load"])
        s = c[0] if chance(.7) else R.choice(c)
        s["load"] += 1
        return s

    def successor(s, d):
        bf = [x for x in STINTS if x.get("backfill_for") is s]
        if bf:
            return bf[0]
        if s.get("promoted") or s["end"] and s["end"] == fy_start(fy(s["end"])):
            nxt = [x for x in STINTS if x["person"] is s["person"] and x["start"] == s["end"]]
            if nxt and nxt[0]["role"] == s["role"]:
                return nxt[0]
        c = [x for x in by_role_reg[(s["role"], s["region"])] if stint_active(x, d) and x is not s]
        return R.choice(c) if c else None

    for a in ACCOUNTS:
        a["cov"] = defaultdict(list)    # role_label -> [(start, end, stint or None)]
        prev = {}
        for f in FYS:
            seg = a["seg"][f]
            reg = region_scope(a, f)
            d0, d1 = fy_start(f), fy_end(f) + D(1)
            sel_family = a["ultimate"]["seg"][f] == "Select" and a["ultimate"] is not a and not a.get("unlinked")
            roles = {"OWNER": "SEL_RAM" if sel_family else OWNER_ROLE[seg]}
            for r in TEAM_ROLES[seg if not sel_family else "Large Enterprise"]:
                if r == "TAM" and not (seg == "Select" or a.get("tam") or chance(.35)):
                    continue
                if r == "TAM":
                    a["tam"] = True
                roles[r] = r
            for label, role in roles.items():
                s = pick_stint(role, reg, d0, prev.get(label))
                t = d0
                while s is not None and t < d1:
                    end = min(d1, s["end"] or d1)
                    a["cov"][label].append((t, end, s))
                    if end >= d1:
                        break
                    gap_end = end + D(R.randint(10, 90))
                    nxt = successor(s, gap_end)
                    if gap_end < d1:
                        a["cov"][label].append((end, gap_end, None))
                    t = gap_end
                    s = nxt
                prev[label] = s
        # merge contiguous identical intervals
        for label, iv in a["cov"].items():
            merged = []
            for x in iv:
                if merged and merged[-1][2] is x[2] and merged[-1][1] >= x[0]:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], x[1]), x[2])
                else:
                    merged.append(x)
            a["cov"][label] = merged


def owner_on(a, d, label="OWNER"):
    for s, e, st in a["cov"].get(label, []):
        if s <= d < e:
            return st
    return None


def any_rep(a, d, labels):
    for lab in labels:
        st = owner_on(a, d, lab)
        if st:
            return st, lab
    return owner_on(a, d), "OWNER"


# ------------------------------------------------------------------ status history (truth) per quarter from last purchase
def status_on(last_purchase, d, ever):
    if last_purchase is None:
        return "Acquisition"
    days = (d - last_purchase).days
    if days <= 365:
        return "Retention"
    if days <= 3 * 365:
        return "Development"
    return "Acquisition"


# ------------------------------------------------------------------ showcase accounts (deliberate storylines for demos)
def pick_showcases():
    def take(pred, key):
        c = [a for a in ACCOUNTS if pred(a) and not a.get("showcase")]
        if not c:
            return None
        a = R.choice(c)
        a["showcase"] = key
        SHOWCASE[key] = a
        return a

    sf = take(lambda a: a["seg_end"] == "Select" and len(a["children"]) >= 6, "select_family_misrouting")
    if sf:
        for c in sf["children"][:3]:
            c["unlinked"], c["linked_on"] = True, None
            c["seg_end"] = "Large Enterprise" if c["seg_end"] == "Small Business" else c["seg_end"]
            c["status_end"] = "retention"
            if c["first_buy"] is None or c["last_buy"] < SNAP - D(200):
                c["first_buy"], c["last_buy"], c["gap"], c["legacy"] = dt.date(2017, 5, 1), SNAP - D(12), None, True
    take(lambda a: a["seg_end"] == "Large Enterprise" and a["status_end"] == "retention" and a["role"] != "subsidiary", "storage_capacity_crunch")
    take(lambda a: a["seg_end"] == "Large Enterprise" and a["status_end"] == "retention" and a["role"] == "standalone", "champion_left_mid_deal")
    take(lambda a: a["seg_end"] in ("Large Enterprise", "Medium Business") and a["status_end"] == "retention" and a["role"] == "standalone", "headcount_jump_flat_pc_spend")
    take(lambda a: a["seg_end"] == "Large Enterprise" and a["status_end"] == "retention" and a["role"] == "standalone" and a.get("legacy"), "missed_po_credit_hold")
    take(lambda a: a["seg_end"] == "Medium Business" and a["status_end"] == "retention" and a["role"] == "standalone" and a.get("legacy") and not a["gap"], "rep_carousel_partner_conflict")
    take(lambda a: a["seg_end"] == "Large Enterprise" and a["status_end"] == "retention" and a["role"] != "subsidiary", "security_advisory_exposure")
    take(lambda a: a["seg_end"] in ("Large Enterprise", "Medium Business") and a["status_end"] == "development" and a["role"] == "standalone"
         and a["last_buy"] < SNAP - D(420), "ai_reacquisition")
    take(lambda a: a.get("early_consumer"), "consumer_to_mb_journey")
    take(lambda a: a["seg_end"] in ("Large Enterprise", "Medium Business") and a["status_end"] == "retention" and a["role"] == "standalone", "lease_end_refresh")
    s = SHOWCASE.get("headcount_jump_flat_pc_spend")
    if s:
        s["growth"] = "acquisitive"
        s["flags"].add("headcount_jump")
        for f in ALL_FYS:
            if f <= 25:
                s["emp"][f] = max(60, int(s["emp"][f] / 1.65))
        jd = dt.date(2025, 3, 3)
        s["news"].append((jd, "acquisition"))
        s["news"].sort()
        s["shock_fy"] = 26
        for f in ALL_FYS:
            s["seg"][f] = seg_rule(s["emp"].get(f - 1, s["emp"][f]), s["spend"].get(f - 1, 0))
    s = SHOWCASE.get("consumer_to_mb_journey")
    if s:
        s["consumer_origin"] = True
        s["growth"] = "hypergrowth"
        s["legacy"] = False
        s["first_buy"] = dt.date(2021, 9, 14)
    s = SHOWCASE.get("rep_carousel_partner_conflict")
    if s and not s["partner_hist"]:
        s["partner_hist"].append((PARTNERS[0], WIN_START - D(300), None))
        s["partner_share"] = .6
    s = SHOWCASE.get("lease_end_refresh")
    if s:
        s["lease_pref"] = True
    s = SHOWCASE.get("storage_capacity_crunch")
    if s:
        s["env"]["primary_competitor"] = "Lumora"


def force_storylines():
    a = SHOWCASE.get("champion_left_mid_deal")
    if a:
        execs = [c for c in a["contacts"] if c["level"] in ("C-Level", "VP") and c["end"] is None and not c["shared"]]
        if execs:
            ch = execs[0]
            ch["end"] = dt.date(2025, 7, 18)
            ch["champion"] = True
            dest = R.choice([x for x in ACCOUNTS if x["seg_end"] in ("Large Enterprise", "Select") and x is not a and x["status_end"] == "retention"])
            n = _mk_contact(dest, dt.date(2025, 8, 25), "exec")
            n.update(first=ch["first"], last=ch["last"], title="Chief Information Officer", email=f"{slug(ch['first'])}.{slug(ch['last'])}@{dest['domain']}")
            n["moved_from"], ch["moved_to"] = ch, n
            rep = _mk_contact(a, dt.date(2025, 10, 6), "exec")
            rep["title"], rep["dept"] = ch["title"], ch["dept"]
            a["champion"] = (ch, n, dest, rep)
    a = SHOWCASE.get("rep_carousel_partner_conflict")
    if a:
        role = OWNER_ROLE[a["seg"][26]]
        iv, t = [], WIN_START
        while t < SNAP + D(1):
            end = min(SNAP + D(1), t + D(R.randint(150, 260)))
            c = [s for s in STINTS if s["role"] in (role, OWNER_ROLE[a["seg"][fy(t)]]) and stint_active(s, t)]
            s = R.choice(c) if c else None
            if iv and chance(.35):
                gap = min(end, t + D(R.randint(20, 70)))
                iv.append((t, gap, None))
                t = gap
            iv.append((t, end, s))
            t = end
        a["cov"]["OWNER"] = iv
        a["partner_share"] = .55


def build(n):
    build_accounts(n)
    build_trajectories()
    build_status()
    pick_showcases_early()
    build_spend()
    build_segments()
    build_news()
    build_sites()
    build_environment()
    build_partners()
    pick_showcases()
    build_spend()          # re-derive after showcase overrides
    build_segments()
    hj = SHOWCASE.get("headcount_jump_flat_pc_spend")
    if hj:
        for f in ALL_FYS:
            hj["seg"][f] = seg_rule(hj["emp"].get(f - 1, hj["emp"][f]), hj["spend"].get(f - 1, 0))
    build_finance()
    build_quillon()
    build_contacts()
    pools = build_org()
    leaders = build_leaders()
    build_coverage(pools)
    force_storylines()
    return leaders


def pick_showcases_early():
    """Consumer-journey showcase needs its trajectory fixed before spend/segments are derived."""
    c = [a for a in ACCOUNTS if a["seg_end"] == "Medium Business" and a["role"] == "standalone" and a["status_end"] == "retention"
         and a["industry"] in ("Technology", "Professional Services", "Media & Entertainment", "Life Sciences", "Consumer Goods")]
    if c:
        a = R.choice(c)
        a["growth"] = "hypergrowth"
        a["legacy"] = False
        a["first_buy"] = dt.date(2021, 9, 14)
        a["emp"] = {f: max(3, int(a["emp_end"] / (1.55 ** (FY_LAST - f)))) for f in ALL_FYS}
        a["rev"] = {f: a["emp"][f] * 210_000 for f in ALL_FYS}
        a["itb"] = {f: a["rev"][f] * .05 for f in ALL_FYS}
        a["early_consumer"] = True


# ====================================================================== V3: extend an existing world
def _add_accounts(n_new, n_sel, n_le_fam, n_mb_fam, quotas):
    """Same rules as build_accounts, explicit counts, appended to ACCOUNTS."""
    canada = lambda: "Canada" if chance(.05) else "United States"
    used = Counter()
    start = len(ACCOUNTS)

    def mk_sub(parent, seg):
        same_ind = chance(.7)
        ctry = parent["country"] if chance(.85) else canada()
        if chance(.5):
            tail = R.choice(["Services", "Holdings", "Solutions", "International", "Distribution", "Manufacturing", "Health",
                             "Technologies", "Logistics", "Labs", "Financial", "Retail Group", "Operations", "Canada" if ctry == "Canada" else "West",
                             "Midwest", "Southeast", "Northeast", "Pacific", "Texas", "Digital"])
            parts = parent["base_name"].split(" ")
            nm = f"{parts[0]} {parts[1] if len(parts) > 2 else ''} {tail}".replace("  ", " ").strip()
            nm = nm if nm not in _used_names else None
        else:
            nm = None
        s = new_account(seg, "subsidiary", ctry, parent["industry"] if same_ind else None, parent, nm)
        if nm:
            _used_names.add(nm)
        used[seg] += 1
        return s

    for _ in range(n_sel):
        p = new_account("Select", "parent", "United States" if chance(.94) else "Canada")
        used["Select"] += 1
        for _ in range(R.randint(3, 15)):
            s = mk_sub(p, wpick({"Large Enterprise": 60, "Medium Business": 35, "Small Business": 5}))
            if chance(.18):
                for _ in range(R.randint(1, 3)):
                    mk_sub(s, wpick({"Medium Business": 70, "Small Business": 30}))
    for _ in range(n_le_fam):
        p = new_account("Large Enterprise", "parent", canada())
        used["Large Enterprise"] += 1
        for _ in range(R.choice([1, 1, 2, 2, 2, 3, 3, 4, 5, 6])):
            mk_sub(p, wpick({"Large Enterprise": 40, "Medium Business": 50, "Small Business": 10}))
    for _ in range(n_mb_fam):
        p = new_account("Medium Business", "parent", canada())
        used["Medium Business"] += 1
        for _ in range(R.choice([1, 1, 2, 2, 3])):
            mk_sub(p, wpick({"Medium Business": 60, "Small Business": 40}))
    for seg in ("Large Enterprise", "Medium Business", "Small Business"):
        for _ in range(max(0, quotas[seg] - used[seg])):
            new_account(seg, "standalone", canada())
    new = ACCOUNTS[start:]
    for a in new:
        u, depth = a, 0
        while u["parent"]:
            u, depth = u["parent"], depth + 1
        a["ultimate"], a["depth"] = u, depth
        if a["role"] == "subsidiary" and chance(.3):
            a["unlinked"] = True
            a["linked_on"] = rand_bday(fy_start(25), SNAP) if chance(.25) else None
    return new


def _assign_partners(accs):
    for a in accs:
        seg = a["seg_end"]
        if seg == "Select":
            continue
        if not chance({"Small Business": .28, "Medium Business": .30, "Large Enterprise": .12}[seg]):
            continue
        elig = [p for p in PARTNERS if seg in p["segs"]]
        elig = [p for p in PARTNERS if p["base_name"] == "Maplegrid Systems"] if a["country"] == "Canada" else [p for p in elig if p["base_name"] != "Maplegrid Systems"]
        p = R.choice(elig)
        start = between(WIN_START - D(800), SNAP - D(200))
        a["partner_hist"].append((p, start, None))
        if chance(.18):
            sw = between(start + D(200), SNAP - D(30))
            p2 = R.choice([x for x in elig if x is not p] or [p])
            a["partner_hist"][-1] = (p, start, sw)
            a["partner_hist"].append((p2, sw, None))
        a["partner_share"] = R.uniform(.45, .95)


def _org_ext(all_accounts):
    """Grow the existing org to cover all accounts. Existing (V2) people keep their exact history."""
    frozen = {id(s) for s in STINTS}
    demand = defaultdict(Counter)
    for a in all_accounts:
        for f in FYS:
            seg = a["seg"][f]
            reg = region_scope(a, f)
            if a["ultimate"]["seg"][f] == "Select" and a["ultimate"] is not a and not a.get("unlinked"):
                demand["SEL_RAM"][(f, reg)] += 1
                continue
            demand[OWNER_ROLE[seg]][(f, reg)] += 1
            for r in TEAM_ROLES[seg]:
                if r == "TAM" and not (seg == "Select" or chance(.35)):
                    continue
                demand[r][(f, reg)] += 1
    pools = defaultdict(list)
    for s in STINTS:
        pools[s["role"]].append(s)
    for role, (title, cap, attr, feeder) in ROLES.items():
        for f in FYS:
            regions = {r for (ff, r) in demand[role] if ff == f}
            for reg in sorted(regions):
                need = max(1, math.ceil(demand[role][(f, reg)] / cap))
                d0 = fy_start(f)
                act = [s for s in pools[role] if stint_active(s, d0) and s["region"] == reg]
                while len(act) < need:
                    hire = d0 - D(R.randint(0, 45)) if f > 22 else d0 - D(R.randint(60, 2400))
                    p = None
                    if feeder and f > 22 and chance(.3):
                        fs = [s for s in pools[feeder] if stint_active(s, d0) and s["end"] is None and s["region"] == reg and id(s) not in frozen]
                        if fs:
                            src = R.choice(fs)
                            src["end"] = d0
                            src["promoted"] = True
                            p = src["person"]
                    if p is None:
                        p = new_person(hire, reg)
                    s = new_stint(p, role, d0 if f > 22 or len(p["stints"]) else min(hire, d0), reg)
                    if f == 22:
                        s["start"] = min(p["hire"], d0)
                    pools[role].append(s)
                    act.append(s)
            for s in [s for s in pools[role] if stint_active(s, fy_start(f)) and s["end"] is None and id(s) not in frozen]:
                if chance(attr * (1.3 if s["person"]["persona"] == "sloppy" else 1)):
                    t = rand_bday(fy_start(f) + D(20), fy_end(f) - D(5))
                    s["end"] = t
                    s["person"]["term"] = t
                    s["left"] = True
                    bf = t + D(R.randint(25, 110))
                    if bf < fy_end(f) - D(20) and bf <= SNAP:
                        np_ = new_person(bf, s["region"])
                        ns = new_stint(np_, role, bf, s["region"])
                        ns["backfill_for"] = s
                        pools[role].append(ns)
    for p in PEOPLE:
        live = [s for s in p["stints"] if s["end"] is None]
        if live:
            p["term"] = None
        elif p["stints"] and p["term"] is None:
            p["term"] = max(s["end"] for s in p["stints"])
    return pools


def extend(n_total):
    """Keep every account built so far (identity, contacts, reps, coverage untouched) and grow the world to n_total."""
    base = list(ACCOUNTS)
    n_new = n_total - len(base)
    seg_now = Counter(a["seg_end"] for a in base)
    q = {"Large Enterprise": round(n_total * .30) - seg_now["Large Enterprise"], "Medium Business": round(n_total * .45) - seg_now["Medium Business"]}
    n_sel = 100 - seg_now["Select"]
    q["Small Business"] = n_new - n_sel - q["Large Enterprise"] - q["Medium Business"]
    new = _add_accounts(n_new, n_sel, round(n_new * .0225), round(n_new * .0125), q)
    ACCOUNTS[:] = new                      # run the per-account builders on the new accounts only
    try:
        build_trajectories()
        build_status()
        build_spend()
        build_segments()
        build_news()
        build_sites()
        build_environment()
        _assign_partners(new)
        build_finance()
        build_quillon()
        build_contacts()
    finally:
        ACCOUNTS[:] = base + new
    _org_ext(ACCOUNTS)
    ACCOUNTS[:] = new
    try:
        build_coverage(None)
    finally:
        ACCOUNTS[:] = base + new
    for a in base:
        a["v2_base"] = True
    return new
