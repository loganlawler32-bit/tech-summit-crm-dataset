"""Pass 2a (per account): order plans -> ERP orders/lines, POs, holds, shipments, invoices, payments, returns,
leases, Flex/DaaS usage, legacy history, consumer orders and the installed base (assets, warranties, telemetry)."""
import math
from collections import defaultdict
from core import *
import refdata as RD
import catalog as CAT
import world as W

O = None            # set by main
FX = {}             # month -> CAD per USD
ADVISORIES = []


def fx(d):
    return FX[(d.year, d.month)]


def init_fx():
    v = 1.27
    for y in range(2016, 2027):
        for m in range(1, 13):
            v = clip(v + R.gauss(0, .012), 1.20, 1.40)
            if (y, m) >= (2022, 5):
                v = clip(v + .003, 1.24, 1.41)
            FX[(y, m)] = round(v, 4)


# ------------------------------------------------------------------ date weighting
_FY_DAYS = {}


def fy_days(f):
    if f not in _FY_DAYS:
        days, w = [], []
        d = fy_start(f)
        while d <= fy_end(f):
            if is_bday(d):
                qe = quarter_end(d)
                wt = 1.0 + (1.6 if (qe - d).days <= 14 else 0) + (0.9 if d.month == 1 else 0) - (0.35 if d.month in (7, 8, 12) else 0)
                days.append(d)
                w.append(wt)
            d += D(1)
        _FY_DAYS[f] = (days, w)
    return _FY_DAYS[f]


def sample_dates(a, f, n, style):
    days, w = fy_days(f)
    season = RD.INDUSTRIES[a["industry"]][5] or ()
    ww = []
    for d, x in zip(days, w):
        if not W.buying(a, d):
            ww.append(0)
            continue
        if d.month == a["fye_month"]:
            x *= 2.6 if style == "yearend_flush" else 1.3
        if d.month in season:
            x *= 1.7
        ww.append(x)
    if not any(ww):
        return []
    return sorted(R.choices(days, weights=ww, k=n))


AVG_ORDER = {  # typical order size by category / segment
    "client": {"Small Business": 4200, "Medium Business": 19000, "Large Enterprise": 62000, "Select": 125000},
    "workstation": {"Small Business": 6500, "Medium Business": 21000, "Large Enterprise": 58000, "Select": 95000},
    "server": {"Small Business": 9000, "Medium Business": 38000, "Large Enterprise": 92000, "Select": 210000},
    "storage": {"Small Business": 30000, "Medium Business": 85000, "Large Enterprise": 190000, "Select": 360000},
    "data_protection": {"Small Business": 12000, "Medium Business": 60000, "Large Enterprise": 125000, "Select": 210000},
    "networking": {"Small Business": 5500, "Medium Business": 14000, "Large Enterprise": 42000, "Select": 85000},
    "software": {"Small Business": 2500, "Medium Business": 12000, "Large Enterprise": 45000, "Select": 95000},
    "services": {"Small Business": 3500, "Medium Business": 16000, "Large Enterprise": 55000, "Select": 120000},
}
STYLE = {"Small Business": {"sporadic": 50, "owner_refresh": 30, "steady_small": 20},
         "Medium Business": {"refresh_cycler": 30, "steady_runrate": 30, "project_based": 20, "yearend_flush": 20},
         "Large Enterprise": {"steady_runrate": 45, "refresh_waves": 30, "yearend_flush": 25},
         "Select": {"steady_runrate": 70, "refresh_waves": 30}}


def adjust_mix(a, f):
    m = dict(a["mix"])
    inits = a["inits"].get(f, [])
    if "Windows 11 migration" in inits or "PC refresh" in inits:
        m["client"] *= 1.6
        m["services"] *= 1.2
    if "Data center refresh" in inits:
        m["server"] *= 1.6
    if any(x.startswith("AI") for x in inits):
        m["server"] *= 1.5
    if "Storage consolidation" in inits or "Ransomware resilience" in inits:
        m["storage"] *= 1.4
        m["data_protection"] *= 1.6
    if "VMware exit / hypervisor change" in inits:
        m["server"] *= 1.3
        m["services"] *= 1.3
    if "Network modernization" in inits:
        m["networking"] *= 2
    if a.get("showcase") == "headcount_jump_flat_pc_spend" and f >= 25:
        m["client"] *= .55
    if a["industry"] in ("Media & Entertainment", "Life Sciences", "Construction") or a["sub_industry"] in ("Architecture & Engineering",):
        m["workstation"] *= 3
    tot = sum(m.values())
    return {k: v / tot for k, v in m.items()}


def plan_orders(a):
    seg_end = a["seg_end"]
    a["style"] = wpick(STYLE[seg_end])
    plans = []
    for f in W.FYS:
        S = a["spend"][f]
        if S <= 0:
            continue
        seg = a["seg"][f]
        mix = adjust_mix(a, f)
        for cat, share in mix.items():
            amt = S * share * R.uniform(.75, 1.25)
            avg = AVG_ORDER[cat][seg] * (1.6 if a["style"] in ("refresh_waves", "project_based", "owner_refresh") and cat == "client" else 1)
            if amt < avg * .25:
                if chance(amt / (avg * .25)):
                    amt = avg * R.uniform(.2, .6)
                else:
                    continue
            n = max(1, min(400, int(round(amt / avg))))
            wts = [lognorm(1, .85) for _ in range(n)]
            tot = sum(wts)
            dates = sample_dates(a, f, n, a["style"])
            for dd, wv in zip(dates, wts):
                plans.append(dict(date=dd, cat=cat, target=amt * wv / tot, fy=f))
    plans.sort(key=lambda p: p["date"])
    return plans


# ------------------------------------------------------------------ line recipes
def disc_for(a, cat, d, rep_persona, competitive, sub_leak):
    seg = a["seg"][fy(d)]
    lo, hi = {"Small Business": (.02, .09), "Medium Business": (.07, .19), "Large Enterprise": (.13, .30), "Select": (.18, .38)}[seg]
    x = R.uniform(lo, hi)
    if cat in ("storage", "data_protection", "server"):
        x += .06
    if cat in ("software",):
        x *= .35
    if cat == "services":
        x *= .6
    ag = a["ultimate"].get("agreement") or a.get("agreement")
    if ag and not sub_leak and d >= ag["start"]:
        x = max(x, ag["disc"][cat] + R.uniform(-.01, .02))
    if rep_persona == "discounter":
        x += R.uniform(.04, .1)
    if (quarter_end(d) - d).days <= 10:
        x += .03
    if competitive:
        x += R.uniform(.03, .08)
    return human_pct(clip(x, 0, .62) * 100) / 100


def L(p, qty, d, disc):
    lp = CAT.list_price(p, d)
    disc = min(disc, .62)
    unit = round(lp * (1 - disc), 2)
    cost = round(p["list"] * CAT.price_mult(p, d) * p["cost_pct"] * R.uniform(.96, 1.04), 2)
    return dict(p=p, qty=max(1, int(qty)), list=lp, unit=unit, disc=round(disc * 100, 1), cost=cost)


def warranty_for(p, a, d, tier_pref=None):
    fam = p["wfam"]
    if fam in ("laptop", "desktop", "workstation"):
        seg = a["seg"][fy(d)]
        tier = tier_pref or ("ProCare Plus" if (fam == "laptop" and chance(.35)) else "ProCare")
        yrs = wpick({3: 55, 4: 25, 5: 20}) if seg != "Small Business" else wpick({3: 80, 4: 15, 5: 5})
        return CAT.WARR.get((fam, tier, yrs))
    if fam in ("server", "storage", "network"):
        tier = "ProCare Mission Critical 4-Hour" if (a["seg"][fy(d)] in ("Large Enterprise", "Select") and chance(.55)) or fam == "storage" and chance(.5) else "ProCare NBD"
        return CAT.WARR.get((fam, tier, R.choice([3, 3, 5])))
    return None


def tier_line(seg):
    return {"Small Business": wpick({"Aster 3": 45, "Aster 5": 45, "Aster 7": 10}),
            "Medium Business": wpick({"Aster 3": 20, "Aster 5": 55, "Aster 7": 20, "Aster 9": 5}),
            "Large Enterprise": wpick({"Aster 3": 10, "Aster 5": 50, "Aster 7": 30, "Aster 9": 10}),
            "Select": wpick({"Aster 5": 45, "Aster 7": 40, "Aster 9": 15})}[seg]


def lines_client(a, target, d, disc):
    seg = a["seg"][fy(d)]
    ls = []
    kind = wpick({"laptop": 68, "desktop": 22, "aio": 4, "thin": 3 if seg != "Small Business" else 0, "rugged": 3 if a["industry"] in ("Energy & Utilities", "Construction", "Transportation & Logistics", "State & Local Government", "Manufacturing") else .3})
    if kind == "laptop":
        tl = tier_line(seg)
        dev = CAT.pick_current(lambda p: p["line"] == tl, d)
    elif kind == "desktop":
        dev = CAT.pick_current(lambda p: p["category"] == "Desktops" and "All-in-One" not in p["name"] and p["line"] != "Cadence AIO", d)
    elif kind == "aio":
        dev = CAT.pick_current(lambda p: p["line"] == "Cadence AIO", d)
    elif kind == "thin":
        dev = CAT.pick_current(lambda p: p["category"] == "Thin Clients", d)
    else:
        dev = CAT.pick_current(lambda p: p["category"] == "Rugged", d)
    attach = 0
    w = warranty_for(dev, a, d) if chance({"Small Business": .35, "Medium Business": .65, "Large Enterprise": .85, "Select": .92}[seg]) else None
    dock = CAT.pick_current(lambda p: p["family"] == "Tether Docks", d) if kind == "laptop" and chance(.55) else None
    mon = CAT.pick_current(lambda p: p["family"] == "Clarity Monitors" and "43" not in p["name"] and "49" not in p["name"], d) if chance(.45) else None
    unit_est = CAT.list_price(dev, d) * (1 - disc)
    unit_est += (CAT.list_price(w, d) * (1 - disc * .5) if w else 0) + (CAT.list_price(dock, d) * (1 - disc) * .6 if dock else 0) + \
        (CAT.list_price(mon, d) * (1 - disc) * (1.3 if chance(.3) else .7) if mon else 0)
    if seg in ("Large Enterprise", "Select"):
        unit_est += 40
    qty = max(1, int(round(target / unit_est)))
    if seg == "Small Business":
        qty = min(qty, R.choice([1, 2, 3, 5, 8, 12, 20]) if chance(.5) else qty)
    ls.append(L(dev, qty, d, disc))
    if w:
        ls.append(L(w, qty, d, disc * .5))
    if dock:
        ls.append(L(dock, max(1, int(qty * R.uniform(.4, .9))), d, disc))
    if mon:
        ls.append(L(mon, max(1, int(qty * R.choice([.5, 1, 1, 2]))), d, disc))
    if seg in ("Large Enterprise", "Select", "Medium Business") and qty >= 25:
        if chance(.6):
            ls.append(L(CAT.BY_SKU[_svc("Factory Imaging")], qty, d, 0))
        if chance(.35):
            ls.append(L(CAT.BY_SKU[_svc("Asset Tagging")], qty, d, 0))
        if chance(.3):
            ls.append(L(CAT.BY_SKU[_svc("Zero-Touch")], qty, d, 0))
        if chance(.3):
            ls.append(L(CAT.BY_SKU[_svc("Asset Recovery")], int(qty * R.uniform(.5, 1)), d, 0))
        if chance(.15):
            ls.append(L(CAT.BY_SKU[_svc("Onsite Desk-Side")], qty, d, disc * .3))
    if chance(.3):
        acc = CAT.pick_current(lambda p: p["family"] == "Peripherals & Accessories", d, .2)
        ls.append(L(acc, max(1, int(qty * R.uniform(.1, 1))), d, disc))
    return ls


_SVC = {}


def _svc(prefix):
    if prefix not in _SVC:
        _SVC[prefix] = next(p["sku"] for p in CAT.PRODUCTS if p["name"].startswith(prefix))
    return _SVC[prefix]


def lines_workstation(a, target, d, disc):
    dev = CAT.pick_current(lambda p: p["category"] == "Workstations", d, .6)
    w = warranty_for(dev, a, d, "ProCare")
    unit = CAT.list_price(dev, d) * (1 - disc) + (CAT.list_price(w, d) if w else 0) * .9 + 400
    q = max(1, int(round(target / unit)))
    ls = [L(dev, q, d, disc)]
    if w:
        ls.append(L(w, q, d, disc * .5))
    ls.append(L(CAT.pick_current(lambda p: p["name"].startswith(("Clarity 27 4K", "Clarity 32 4K")), d), q * R.choice([1, 2]), d, disc))
    return ls


def lines_server(a, target, d, disc):
    seg = a["seg"][fy(d)]
    f = fy(d)
    ai = any(x.startswith("AI") for x in a["inits"].get(f, [])) and d >= dt.date(2023, 11, 1)
    hci = "VMware exit / hypervisor change" in a["inits"].get(f, []) and chance(.5)
    edge = a["industry"] in ("Manufacturing", "Retail", "Transportation & Logistics", "Energy & Utilities") and chance(.15)
    if ai and target > 90000 and chance(.6):
        srv = CAT.pick_current(lambda p: p["category"] == "AI Servers", d)
    elif hci:
        srv = CAT.pick_current(lambda p: p["category"] == "HCI", d)
    elif edge:
        srv = CAT.pick_current(lambda p: p["category"] == "Edge", d)
    elif seg == "Small Business":
        srv = CAT.pick_current(lambda p: p["family"] == "Atlas Tower Servers" or p["line"] == "Atlas 120", d)
    elif seg == "Select" and chance(.15):
        srv = CAT.pick_current(lambda p: p["family"] == "Atlas Modular" and "Sled" in p["name"], d)
    else:
        srv = CAT.pick_current(lambda p: p["family"] == "Atlas Rack Servers", d, .65)
    w = warranty_for(srv, a, d)
    opts_per = (CAT.list_price(srv, d) * .18) if srv["category"] not in ("AI Servers",) else 0
    unit = CAT.list_price(srv, d) * (1 - disc) + opts_per * (1 - disc) + (CAT.list_price(w, d) * .85 if w else 0) + 650
    q = max(1, int(round(target / unit)))
    if srv["category"] == "AI Servers":
        q = max(1, min(q, 32))
    ls = [L(srv, q, d, disc)]
    if w:
        ls.append(L(w, q, d, disc * .6))
    if opts_per and chance(.75):
        for nm in R.sample(["64GB DDR5 RDIMM", "128GB DDR5 RDIMM", "3.84TB NVMe Drive", "7.68TB NVMe Drive", "25GbE Dual-Port NIC",
                            "100GbE Dual-Port NIC", "Boot Optimized Storage", "48GB Inference Accelerator Card"], R.randint(1, 3)):
            p = CAT.BY_SKU[_opt(nm)]
            per = {"64GB": 4, "128G": 4, "3.84": 4, "7.68": 4, "25Gb": 1, "100G": 1, "Boot": 1, "48GB": 2}[nm[:4]]
            ls.append(L(p, q * per, d, disc))
        ls.append(L(CAT.BY_SKU[_opt("Sliding Ready Rails")], q, d, disc))
    if seg != "Small Business" and chance(.55):
        ls.append(L(CAT.BY_SKU[_svc("Rack & Stack")], q, d, disc * .3))
    if chance(.45):
        sw = R.choice(["Server OS Standard", "Server OS Datacenter", "Hypervisor Enterprise Plus", "Orvane Insight"])
        p = next(x for x in CAT.PRODUCTS if x["name"].startswith(sw))
        ls.append(L(p, q * (2 if "OS" in sw else 32 if "Hypervisor" in sw else 1), d, disc * .3))
    if srv["category"] == "AI Servers":
        ls.append(L(next(x for x in CAT.PRODUCTS if x["name"].startswith("Orvane AI Factory")), q * (8 if "880" in srv["name"] else 4), d, disc * .4))
        if chance(.5):
            ls.append(L(CAT.BY_SKU[_svc("AI Readiness")], 1, d, disc * .3))
    if srv["category"] == "HCI":
        ls.append(L(CAT.BY_SKU[_svc("HCI Cluster")], 1, d, disc * .3))
        if chance(.4):
            ls.append(L(CAT.BY_SKU[_svc("VMware Exit")], 1, d, disc * .3))
    if seg in ("Large Enterprise", "Select") and q >= 8 and chance(.25):
        ls.append(L(CAT.BY_SKU[_opt("Orvane 42U Rack")], max(1, q // 12), d, disc))
        ls.append(L(CAT.BY_SKU[_opt("Metered Rack PDU")], max(2, q // 6), d, disc))
    return ls


_OPT = {}


def _opt(prefix):
    if prefix not in _OPT:
        _OPT[prefix] = next(p["sku"] for p in CAT.PRODUCTS if p["name"].startswith(prefix))
    return _OPT[prefix]


def lines_storage(a, target, d, disc):
    seg = a["seg"][fy(d)]
    if chance(.3) and a.get("has_array"):
        p = CAT.pick_current(lambda p: p["line"] in ("Strata Shelves", "Strata Drive Packs"), d, .5)
        u = CAT.list_price(p, d) * (1 - disc)
        return [L(p, max(1, int(round(target / u))), d, disc)]
    tier = "Strata 300" if target < 90000 else "Strata 500" if target < 260000 else "Strata 700"
    if chance(.15):
        arr = CAT.pick_current(lambda p: p["line"] in ("Strata Scale", "Strata Object"), d)
    else:
        arr = CAT.pick_current(lambda p: p["line"] == tier, d)
    w = warranty_for(arr, a, d)
    unit = CAT.list_price(arr, d) * (1 - disc) + (CAT.list_price(w, d) * .85 if w else 0)
    q = max(1, int(round(target / (unit * 1.35))))
    q = min(q, 12)
    ls = [L(arr, q, d, disc)]
    if w:
        ls.append(L(w, q, d, disc * .6))
    if chance(.6):
        ls.append(L(CAT.pick_current(lambda p: p["line"] in ("Strata Shelves", "Strata Drive Packs"), d, .5), q * R.randint(1, 4), d, disc))
    if chance(.6):
        ls.append(L(CAT.BY_SKU[_svc("Storage Array Implementation")], q, d, disc * .3))
    if chance(.35):
        ls.append(L(CAT.BY_SKU[_svc("Data Migration")], R.randint(1, 6), d, disc * .3))
    a["has_array"] = True
    return ls


def lines_dp(a, target, d, disc):
    dp = CAT.pick_current(lambda p: p["family"] == "Vault Data Protection", d)
    w = warranty_for(dp, a, d)
    unit = CAT.list_price(dp, d) * (1 - disc)
    q = max(1, min(6, int(round(target / (unit * 1.4)))))
    ls = [L(dp, q, d, disc)]
    if w:
        ls.append(L(w, q, d, disc * .6))
    sw = next(p for p in CAT.PRODUCTS if p["name"].startswith("Vault Backup Software"))
    ls.append(L(sw, max(10, int(target * .25 / CAT.list_price(sw, d))), d, disc * .5))
    if chance(.3):
        ls.append(L(CAT.BY_SKU[_svc("Cyber Recovery")], 1, d, disc * .3))
    return ls


def lines_network(a, target, d, disc):
    sw = CAT.pick_current(lambda p: p["family"] == "Mesh Networking" and p["serialized"], d)
    w = warranty_for(sw, a, d)
    unit = CAT.list_price(sw, d) * (1 - disc) + (CAT.list_price(w, d) * .8 if w else 0)
    q = max(1, int(round(target / (unit * 1.15))))
    ls = [L(sw, q, d, disc)]
    if w:
        ls.append(L(w, q, d, disc * .6))
    if "25GbE" in sw["name"] or "100GbE" in sw["name"] or chance(.4):
        o = CAT.pick_current(lambda p: p["line"] == "Optics & Cables", d, .3)
        ls.append(L(o, q * R.randint(4, 24), d, disc))
    if chance(.3):
        ls.append(L(CAT.BY_SKU[_svc("Network Configuration")], 1, d, disc * .3))
    return ls


def lines_software(a, target, d, disc):
    p = R.choice([x for x in CAT.PRODUCTS if x["bu"] == "Software" and CAT.sellable(x, d) and "AI Factory" not in x["name"]])
    u = CAT.list_price(p, d) * (1 - disc)
    return [L(p, max(1, int(round(target / u))), d, disc)]


def lines_services(a, target, d, disc):
    seg = a["seg"][fy(d)]
    pool = [x for x in CAT.PRODUCTS if x["bu"] == "Services" and CAT.sellable(x, d) and x["category"] != "Support Services"]
    pool += [CAT.WARR[k] for k in CAT.WARR if k[1] == "ext"] * 3
    if seg == "Small Business":
        pool = [x for x in pool if x["list"] < 10000]
    p = R.choice(pool)
    u = CAT.list_price(p, d) * (1 - disc)
    q = max(1, int(round(target / u)))
    if "per month" in p["name"]:
        q = min(q, 24) if "Residency" in p["name"] else q
    if p["unit"] == "Service" and p["list"] > 10000:
        q = min(q, 3)
    return [L(p, q, d, disc)]


RECIPES = {"client": lines_client, "workstation": lines_workstation, "server": lines_server, "storage": lines_storage,
           "data_protection": lines_dp, "networking": lines_network, "software": lines_software, "services": lines_services}
CAT_ROLE = {"client": ("OWNER", "MB_SPEC_CLIENT", "LE_IAE"), "workstation": ("OV_WKS", "MB_SPEC_CLIENT"),
            "server": ("OV_SERVER", "MB_SPEC_INFRA"), "storage": ("OV_STORAGE", "MB_SPEC_INFRA"),
            "data_protection": ("OV_DP", "MB_SPEC_INFRA"), "networking": ("OV_NET", "MB_SPEC_INFRA"),
            "software": ("OV_SW", "MB_SPEC_SW"), "services": ("OV_SVC", "MB_SPEC_SVC")}
GROUP_NAME = {"client": "Client Devices", "workstation": "Workstations", "server": "Servers & HCI", "storage": "Storage",
              "data_protection": "Data Protection", "networking": "Networking", "software": "Software", "services": "Services"}


# ------------------------------------------------------------------ the order itself
def po_number(a, d, n=None):
    n = n or R.randint(1, 99999999)
    return a["po_fmt"].format(n=n % 100000000, y=d.year, n4=n % 10000, n5=n % 100000, n6=n % 1000000, n7=n % 10000000, abbr=a["abbr"][:4])


def tax_for(a, site, d, subtotal):
    if a["tax_exempt"] and (a["tax_cert_exp"] is None or d <= a["tax_cert_exp"]):
        return "Exempt", 0.0, False
    if site["country"] == "Canada":
        t, r = RD.CA_TAX.get(site["state"], ("GST", 5))
        return t, round(subtotal * r / 100, 2), a["tax_exempt"]
    r = RD.US_STATE_TAX.get(site["state"], 6)
    return "Sales Tax", round(subtotal * (r + R.choice([0, 0, .5, 1, 1.5, 2])) / 100, 2), a["tax_exempt"]


def pay_method(a, d, total, channel):
    if channel == "Partner":
        return "Partner Remittance"
    if channel == "Online Store":
        return "Credit Card" if chance(.9) else "PayPal"
    if a["pay_style"] == "card_heavy" and total <= 25000:
        return "Credit Card"
    if a["lease_pref"] and total > 15000 and chance(.45):
        return "Lease - Orvane Financial Services"
    seg = a["seg"][fy(d)]
    if seg == "Small Business":
        return wpick({"Credit Card": 55, "ACH": 25, "Check": 15, "Wire": 5})
    return wpick({"ACH": 55, "Wire": 25 if seg in ("Large Enterprise", "Select") else 10, "Check": 12, "Credit Card": 6})


ORDER_ACCUM = None   # filled per account: list of order dicts (truth) for CRM pass


def make_order(a, p, ctx, rep_for):
    d, cat = p["date"], p["cat"]
    f = fy(d)
    seg = a["seg"][f]
    partner = W.partner_on(a, d)
    if partner and chance(a.get("partner_share", .7)) and cat not in ("services",):
        channel = "Partner"
    elif seg == "Small Business" and chance(.55):
        channel = "Online Store"
    elif seg == "Medium Business" and chance(.12) and cat in ("client", "software"):
        channel = "Online Store"
    elif seg in ("Large Enterprise", "Select") and cat == "client" and chance(.2):
        channel = "Premier Portal"
    else:
        channel = "Direct - Field" if seg in ("Large Enterprise", "Select") else "Direct - Inside"
    rep_st, rep_role = rep_for(a, d, cat)
    persona = rep_st["person"]["persona"] if rep_st else "by_the_book"
    sub_leak = a["role"] == "subsidiary" and a.get("unlinked") and a["ultimate"].get("agreement") is not None
    competitive = chance(.25)
    disc = disc_for(a, cat, d, persona, competitive, sub_leak)
    lines = RECIPES[cat](a, p["target"], d, disc / 100 if disc > 1 else disc)
    if not lines:
        return None
    sub = round(sum(l["qty"] * l["unit"] for l in lines), 2)
    listv = round(sum(l["qty"] * l["list"] for l in lines), 2)
    on = f"SO-{seq('so', 30_000_000, 11, 9)}"
    o = dict(force_lease=p.get("force_lease"), on=on, a=a, d=d, cat=cat, channel=channel, partner=partner if channel == "Partner" else None, rep=rep_st, rep_role=rep_role,
             persona=persona, lines=lines, sub=sub, list=listv, disc=disc, competitive=competitive, sub_leak=sub_leak, fy=f,
             currency=a["currency"], status="Closed", hold=None, po=None, opp=None)
    if sub_leak:
        ag = a["ultimate"]["agreement"]
        missed = sum(l["qty"] * l["list"] * max(0, ag["disc"][cat] - l["disc"] / 100) for l in lines if d >= ag["start"])
        o["leak"] = round(missed, 2)
    return o


def finance_order(a, o, ship_site, open_ar):
    """POs, holds, payment method, tax, currency; returns the ERP order row."""
    d = o["d"]
    rate = fx(d) if o["currency"] == "CAD" else 1.0
    total_usd = o["sub"]
    method = pay_method(a, d, total_usd, o["channel"]) if not o.get("force_lease") else "Lease - Orvane Financial Services"
    o["method"] = method
    po = po_recv = po_amt = None
    hold = hold_start = hold_rel = None
    status = "Closed"
    cancel = None
    po_note = None
    needs_po = a["po_required"] and o["channel"] not in ("Online Store",) and method not in ("Credit Card", "PayPal")
    if o["channel"] == "Partner":
        needs_po = True
    if needs_po:
        po = po_number(a, d)
        if a["blanket_po"] and chance(.6):
            po = a.setdefault("blanket", {}).setdefault(o["fy"], po_number(a, fy_start(o["fy"])))
            o["blanket"] = True
        r = R.random()
        po_recv = d - D(R.randint(0, 6))
        if r < .07 or a.get("showcase") == "missed_po_credit_hold" and d > SNAP - D(160) and chance(.5):
            hold, hold_start = "Awaiting PO", d
            late = R.randint(3, 48)
            po_recv = d + D(late)
            hold_rel = po_recv
            o["po_late"] = late
        elif r < .09 or (a.get("showcase") == "missed_po_credit_hold" and d > SNAP - D(75)):
            hold, hold_start = "Awaiting PO", d
            po_recv = None
            if d < SNAP - D(60):
                status, cancel = "Cancelled", "No PO received"
                hold_rel = d + D(R.randint(30, 90))
            else:
                status = "On Hold"
            o["po_missing"] = True
        po_amt = round(total_usd * rate, 2)
        if chance(.04):
            po_amt = round(po_amt * R.choice([.9, .93, .95, .97]), 2)
            o["po_short"] = True
            if hold is None:
                hold, hold_start, hold_rel = "PO Amount Mismatch", d, d + D(R.randint(2, 15))
        if chance(.035):
            po_note = R.choice(["verbal", "TBD", "PO to follow", "see email", "per John", "N/A", "pending", "will send", "PO#"])
            o["po_placeholder"] = po
    o["po"] = po_note or po
    o["po_true"] = po
    # credit hold
    if status == "Closed" and a["pay_style"] in ("slow", "chaotic", "disputer") and open_ar + total_usd > a["credit_limit"] and chance(.35):
        hold = hold or "Credit Limit Exceeded"
        hold_start = hold_start or d
        hold_rel = max(hold_rel or d, d + D(R.randint(1, 21)))
        o["credit_hold"] = (d, hold_rel, open_ar)
    if a.get("showcase") == "missed_po_credit_hold" and d > SNAP - D(45) and status == "Closed":
        hold, hold_start, hold_rel, status = "Credit Limit Exceeded", d, None, "On Hold"
        o["credit_hold"] = (d, None, open_ar)
    o["status"] = status
    o["hold"], o["hold_start"], o["hold_rel"], o["cancel"] = hold, hold_start, hold_rel, cancel
    o["po_recv"], o["po_amt"] = po_recv, po_amt
    o["booked"] = hold_rel if hold and hold_rel and status == "Closed" else d
    ttype, tax, cert_problem = tax_for(a, ship_site, d, total_usd)
    o["tax_type"], o["tax"], o["cert_problem"] = ttype, tax, cert_problem
    o["rate"] = rate
    return o


# ------------------------------------------------------------------ writing orders + downstream finance & logistics
LEAD = {"client": (4, 18), "workstation": (6, 20), "server": (10, 35), "storage": (14, 40), "data_protection": (12, 35),
        "networking": (7, 25), "software": (0, 1), "services": (0, 3)}
SHORTAGE = (dt.date(2021, 6, 1), dt.date(2023, 3, 31))
FW_BASE = {"Servers": 2, "AI Servers": 3, "Modular": 2, "HCI": 5, "Storage": 6, "Data Protection": 4, "Networking": 10, "Edge": 1, "Workstations": 1}


def fw_version(p, d):
    """Firmware release train per product family."""
    major = FW_BASE.get(p["category"], 1) + (int(p["gen"][1]) - 3 if p["gen"] and p["gen"][1:].isdigit() else 0)
    months = max(0, months_between(p["launch"], d))
    return f"{max(1, major)}.{months // 4}.{(months * 7) % 5}"


def ship_plan(o):
    d = o["booked"] if o["status"] == "Closed" else None
    if d is None:
        return []
    lo, hi = LEAD[o["cat"]]
    if SHORTAGE[0] <= d <= SHORTAGE[1] and o["cat"] in ("server", "storage", "networking", "data_protection", "client"):
        lo, hi = lo * 2, hi * (4 if o["cat"] != "client" else 2)
    hw = [l for l in o["lines"] if l["p"]["bu"] in ("Client Solutions", "Infrastructure Solutions", "Consumer") and l["p"]["category"] != "Support Services"]
    if not hw:
        return []
    promised = bday(d + D(lo + (hi - lo) // 3))
    nship = 1 if chance(.8) else R.randint(2, 3)
    if SHORTAGE[0] <= d <= SHORTAGE[1] and chance(.35):
        nship = max(nship, 2)
    groups = [[] for _ in range(nship)]
    for i, l in enumerate(hw):
        groups[i % nship if nship > 1 else 0].append(l)
    out = []
    for gi, g in enumerate(groups):
        if not g:
            continue
        sd = bday(d + D(R.randint(lo, hi) + gi * R.randint(5, 30)))
        out.append((sd, g, promised))
    return out


def write_commerce(a, orders, V):
    """Write ERP orders + finance + logistics + assets for one account. V = view helper."""
    T = O.add
    open_inv = []      # (invoice dict) for AR / payments
    ship_sites = a["sites"]
    for o in orders:
        d = o["d"]
        cust = V.order_customer(o)            # sold-to (may be duplicate / parent / partner)
        site = R.choice(ship_sites[:3]) if chance(.8) else R.choice(ship_sites)
        if a.get("hq_move") and d > a["hq_move"][0] and site["type"] == "Headquarters" and chance(.7):
            o["stale_ship_to"] = True
        if site.get("opened") and site["opened"] > d:
            site = ship_sites[0]
        rate = o["rate"]
        sub = o["sub"]
        disc_amt = round(o["list"] - sub, 2)
        tax = o["tax"]
        tot = round(sub + tax, 2)
        rep_name, rep_code = V.rep_label(o["rep"], d)
        opp_id = o["opp"]["Id"] if o.get("opp") else None
        if o.get("opp_missing_link"):
            opp_id = None
        notes = None
        if o.get("po_late"):
            notes = R.choice(["Held for PO - cust AP slow", "PO rec'd late, released", "waiting on PO from procurement", "PO came in after hold"])
        if o.get("credit_hold"):
            notes = (notes + "; " if notes else "") + "Credit hold - released by credit dept" if o["hold_rel"] else "Credit hold - open AR over limit"
        row = dict(Order_Number=o["on"], Source_System="ORV_ERP", Order_Date=ds(d), Booked_Date=ds(o["booked"]) if o["status"] != "Cancelled" else None,
                   Customer_Number=cust, Bill_To_Customer_Number=V.bill_to(o, cust), Ship_To_Number=site["id"],
                   End_User_Account_Id=V.end_user_id(o), End_User_Name=V.end_user_name(o), Channel=o["channel"],
                   Partner_Customer_Number=o["partner"]["erp"] if o["partner"] else None, Sales_Rep_Code=rep_code, Sales_Rep_Name=rep_name,
                   CRM_Opportunity_Id=opp_id, Quote_Number=o.get("quote_no"), PO_Number=o["po"], PO_Received_Date=ds(o["po_recv"]),
                   PO_Amount=o["po_amt"], Blanket_PO="Y" if o.get("blanket") else "N", Payment_Method=o["method"], Payment_Terms=a["terms"],
                   Currency=o["currency"], FX_Rate_To_USD=round(1 / rate, 4) if rate != 1 else 1.0,
                   Subtotal=round(sub * rate, 2), Discount_Amount=round(disc_amt * rate, 2), Tax_Amount=round(tax * rate, 2),
                   Order_Total=round(tot * rate, 2), Order_Total_USD=tot,
                   Contract_Pricing_Agreement=V.agreement_no(o), Status=o["status"], Hold_Reason=o["hold"], Hold_Start=ds(o["hold_start"]),
                   Hold_Released=ds(o["hold_rel"]), Cancel_Reason=o["cancel"], Notes=notes)
        T("Sales_Order", row)
        if o.get("po_placeholder"):
            O.issue("po_placeholder_value", "Sales_Order", o["on"], "PO_Number", o["po"], o["po_placeholder"], a["id"],
                    "PO_Number not matching customer PO format", "Rep typed a placeholder instead of the real PO number.")
        if o.get("po_short"):
            O.issue("po_amount_mismatch", "Sales_Order", o["on"], "PO_Amount", o["po_amt"], round(tot * rate, 2), a["id"],
                    "PO_Amount < Order_Total", "Customer PO issued for less than the order total (tax/old quote).")
        if o.get("po_missing"):
            O.issue("missing_po", "Sales_Order", o["on"], "PO_Number", o["po"], "(no PO ever received)", a["id"],
                    "Hold_Reason=Awaiting PO and no PO_Received_Date", "Order booked/won without a customer PO; " +
                    ("order cancelled." if o["status"] == "Cancelled" else "still on hold at snapshot."), "High")
        if o.get("leak"):
            O.issue("contract_pricing_not_applied", "Sales_Order", o["on"], "Contract_Pricing_Agreement", None,
                    a["ultimate"]["agreement"]["id"], a["id"], "Subsidiary of agreement holder priced at standard discount",
                    f"Parent agreement not applied; est. overcharge/leakage ${o['leak']:,.0f} USD.", "High")
        if o.get("cert_problem"):
            O.issue("tax_cert_expired", "Sales_Order", o["on"], "Tax_Amount", round(tax * rate, 2), 0, a["id"],
                    "Tax-exempt customer charged tax", f"Exemption certificate expired {a['tax_cert_exp']}; tax charged.")
        V.event(a, d, "ERP", "Order", o["status"], record_table="Sales_Order", record_id=o["on"], order_number=o["on"],
                amount=round(tot * rate, 2), currency=o["currency"], amount_usd=tot, po_number=o["po"], payment_method=o["method"],
                status=o["status"], channel=o["channel"], rep=o["rep"], product_category=GROUP_NAME[o["cat"]],
                partner_name=o["partner"]["base_name"] if o["partner"] else None, opportunity_id=opp_id,
                subject=f"Order {o['on']} - {GROUP_NAME[o['cat']]} ({len(o['lines'])} lines)",
                text=notes, details=dict(hold=o["hold"], hold_released=ds(o["hold_rel"]), discount_amount=round(disc_amt * rate, 2),
                                         tax=round(tax * rate, 2), ship_to=site["id"], customer_number=cust, cancel_reason=o["cancel"]))
        if o.get("credit_hold"):
            hd, hr, ar = o["credit_hold"]
            T("Credit_Hold_Event", dict(Hold_Id=f"CH-{seq('ch', 50000, 3)}", Customer_Number=cust, Order_Number=o["on"], Hold_Type="Credit Limit",
                                        Hold_Date=ds(hd), Release_Date=ds(hr), Released_By=V.credit_user() if hr else None,
                                        Open_AR_At_Hold=round(ar, 2), Credit_Limit_At_Hold=a["credit_limit"],
                                        Notes=R.choice(["Released w/ mgr approval", "Customer paid past-due", "Temp limit increase", "Pending payment plan", None])))
        # lines
        ships = ship_plan(o)
        ship_of = {}
        for sd, g, prom in ships:
            for l in g:
                ship_of[id(l)] = (sd, prom)
        for i, l in enumerate(o["lines"], 1):
            p = l["p"]
            sd, prom = ship_of.get(id(l), (o["booked"] if o["status"] == "Closed" else None, None))
            ext = round(l["qty"] * l["unit"], 2)
            T("Sales_Order_Line", dict(Order_Number=o["on"], Line_Number=i * 10, SKU=p["sku"], Item_Description=p["name"],
                                       Product_Category=p["category"], Quantity=l["qty"], List_Price=round(l["list"] * rate, 2),
                                       Unit_Price=round(l["unit"] * rate, 2), Discount_Pct=l["disc"], Extended_Price=round(ext * rate, 2),
                                       Unit_Cost=round(l["cost"] * rate, 2), Extended_Cost=round(l["cost"] * l["qty"] * rate, 2),
                                       Gross_Margin=round((ext - l["cost"] * l["qty"]) * rate, 2),
                                       Line_Status="Cancelled" if o["status"] == "Cancelled" else ("Awaiting Release" if o["status"] == "On Hold" else
                                                                                                  "Shipped" if sd and p["bu"] != "Services" and p["bu"] != "Software" else "Fulfilled"),
                                       Requested_Date=ds(d + D(R.randint(3, 30))), Promised_Date=ds(prom), Ship_Date=ds(sd),
                                       Is_Recurring="Y" if p["recurring"] else "N", Term_Months=p["term"]))
            V.event(a, d, "ERP", "Order Line", p["category"], record_table="Sales_Order_Line", record_id=f"{o['on']}-{i * 10}",
                    order_number=o["on"], product=p, quantity=l["qty"], list_price=round(l["list"] * rate, 2), unit_price=round(l["unit"] * rate, 2),
                    discount_pct=l["disc"], amount=round(ext * rate, 2), currency=o["currency"], amount_usd=ext, status=o["status"], rep=o["rep"])
        if o["status"] != "Closed":
            continue
        # shipments
        for k, (sd, g, prom) in enumerate(ships):
            if sd > SNAP:   # backordered / scheduled after the snapshot: no shipment yet, nothing invoiced
                O.add("Shipment", dict(Shipment_Number=f"SHP-{seq('shp', 70_000_000, 13, 11)}", Order_Number=o["on"], Ship_To_Number=site["id"],
                                       Promised_Date=ds(prom), Status="Scheduled - Backordered" if sd > prom else "Scheduled", Units=sum(l["qty"] for l in g), Lines=len(g)))
                continue
            exc, st = None, "Delivered"
            dd = bday(sd + D(R.randint(1, 6)))
            if o.get("stale_ship_to") and k == 0:
                exc, st, dd = "Address Correction - Returned to Sender", "Delivered (Re-shipped)", bday(dd + D(R.randint(5, 15)))
                O.issue("stale_ship_to_address", "Shipment", None, "Ship_To_Number", site["id"], [s["id"] for s in a["sites"] if "new" in s["type"]][:1],
                        a["id"], "Shipment exception after HQ move", "Order shipped to old HQ after the customer relocated.", "Low")
            elif chance(.015):
                exc = "Damaged in Transit"
            elif chance(.05):
                exc, dd = "Delayed - Carrier", bday(dd + D(R.randint(2, 9)))
            if dd > SNAP:
                st, dd = "In Transit", None
            shn = f"SHP-{seq('shp', 70_000_000, 13, 11)}"
            car = wpick(RD.CARRIERS)
            T("Shipment", dict(Shipment_Number=shn, Order_Number=o["on"], Ship_To_Number=site["id"], Carrier=car,
                               Tracking_Number=f"1Z{R.randint(10**15, 10**16 - 1)}" if car == "UPS" else str(R.randint(10**11, 10**12 - 1)),
                               Ship_Date=ds(sd), Delivered_Date=ds(dd), Promised_Date=ds(prom), Status=st, Exception=exc,
                               Units=sum(l["qty"] for l in g), Lines=len(g)))
            if sd > prom + D(10) or exc:
                V.event(a, sd, "ERP", "Shipment", exc or "Late vs promise", record_table="Shipment", record_id=shn, order_number=o["on"],
                        status=st, subject=f"Shipment {shn} via {car}", text=exc,
                        details=dict(promised=ds(prom), shipped=ds(sd), delivered=ds(dd), days_late=(sd - prom).days))
            if exc == "Damaged in Transit":
                rma_line(a, o, g[0], sd, "Damaged in transit", cust)
            assets_from(a, o, g, sd, site)
        # invoices (one for shipped hardware per shipment; one for non-shipping lines)
        inv_groups = [(sd, g) for sd, g, _ in ships if sd <= SNAP]
        nonship = [l for l in o["lines"] if id(l) not in ship_of]
        if nonship:
            inv_groups.append((o["booked"], nonship))
        for sd, g in inv_groups:
            if sd > SNAP:
                continue
            gsub = round(sum(l["qty"] * l["unit"] for l in g), 2)
            share = gsub / o["sub"] if o["sub"] else 1
            invoice(a, o, cust, sd, gsub, round(o["tax"] * share, 2), open_inv)
        if o["method"].startswith("Lease"):
            lease_for(a, o, cust)
        if chance(.012):
            hw = [l for l in o["lines"] if l["p"]["bu"] in ("Client Solutions", "Infrastructure Solutions")]
            if hw:
                rma_line(a, o, R.choice(hw), o["booked"] + D(R.randint(5, 40)), wpick({"DOA": 30, "Wrong configuration shipped": 20,
                         "Customer ordered wrong item": 25, "Defective - failed burn-in": 15, "Duplicate order": 10}), cust)
        if o.get("leak") and chance(.2):
            cm = f"CM-{seq('cm', 800000, 7)}"
            T("Credit_Memo", dict(Credit_Memo_Number=cm, Customer_Number=cust, Order_Number=o["on"], Memo_Date=ds(o["booked"] + D(R.randint(30, 200))),
                                  Reason="Price adjustment - contract pricing", Amount=round(o["leak"] * rate, 2), Currency=o["currency"], Status="Applied"))
    payments(a, open_inv)


def rma_line(a, o, l, d, reason, cust):
    if d > SNAP:
        return
    rn = f"RMA-{seq('rma', 4_000_000, 7)}"
    q = 1 if l["qty"] < 5 or chance(.7) else R.randint(1, max(1, l["qty"] // 4))
    O.add("RMA", dict(RMA_Number=rn, Order_Number=o["on"], SKU=l["p"]["sku"], Quantity=q, Reason=reason, Request_Date=ds(d),
                      Received_Date=ds(d + D(R.randint(4, 20))) if d + D(20) < SNAP else None,
                      Disposition=R.choice(["Credit issued", "Replacement shipped", "Replacement shipped", "Refurbish", "Scrap"]), Serials=None))
    rate = o["rate"]
    O.add("Credit_Memo", dict(Credit_Memo_Number=f"CM-{seq('cm', 800000, 7)}", Customer_Number=cust, Order_Number=o["on"], RMA_Number=rn,
                              Memo_Date=ds(d + D(R.randint(10, 35))), Reason=f"Return - {reason}", Amount=round(q * l["unit"] * rate, 2),
                              Currency=o["currency"], Status="Applied" if chance(.85) else "Open"))
    O.view.event(a, d, "ERP", "Return (RMA)", reason, record_table="RMA", record_id=rn, order_number=o["on"], product=l["p"], quantity=q,
                 amount=round(q * l["unit"] * rate, 2), currency=o["currency"], amount_usd=round(q * l["unit"], 2), subject=f"RMA {rn}: {reason}")


def invoice(a, o, cust, d, sub, tax, open_inv):
    rate = o["rate"]
    inv = f"INV-{seq('inv', 90_000_000, 17, 15)}"
    due_days = {"Net 30": 30, "Net 45": 45, "Net 60": 60, "Due on Receipt": 0}[a["terms"]]
    if o["method"] in ("Credit Card", "PayPal"):
        due_days = 0
    tot = round((sub + tax) * rate, 2)
    rec = dict(inv=inv, o=o, cust=cust, d=d, due=d + D(due_days), tot=tot, usd=round(sub + tax, 2), cur=o["currency"], sub=round(sub * rate, 2),
               tax=round(tax * rate, 2))
    open_inv.append(rec)


def payments(a, invs):
    style = a["pay_style"]
    bankrupt = next((d for d, t in a["news"] if t == "bankruptcy"), None)
    for v in invs:
        o, d, due = v["o"], v["d"], v["due"]
        paid, status, dispute, dunning, wo, dtp = 0.0, "Open", None, 0, "N", None
        pays = []
        method = o["method"]
        if method in ("Credit Card", "PayPal"):
            pays.append((d, v["tot"], "Credit Card", f"AUTH{R.randint(100000, 999999)}"))
        elif method == "Partner Remittance":
            pd = due + D(R.randint(-5, 25))
            pays.append((pd, v["tot"], "ACH", f"{o['partner']['base_name'][:10].upper()} REMIT"))
        elif method.startswith("Lease"):
            pays.append((d + D(R.randint(10, 30)), v["tot"], "Lease Funding", "OFS FUNDING"))
        else:
            lag = {"prompt": R.randint(-5, 6), "slow": R.randint(10, 65), "disputer": R.randint(0, 40), "chaotic": R.randint(-10, 90),
                   "card_heavy": R.randint(0, 10)}[style]
            pd = due + D(lag)
            amt = v["tot"]
            if style == "disputer" and chance(.25) and o["disc"]:
                short = round(amt * R.uniform(.02, .08), 2)
                pays.append((pd, round(amt - short, 2), method, f"{R.randint(100000, 999999)}"))
                dispute = R.choice(["Customer disputes discount vs quote", "Pricing does not match contract", "Freight charged in error",
                                    "Tax charged - claims exempt", "Short-paid: missing units"])
                if chance(.6):
                    pays.append((pd + D(R.randint(20, 120)), short, method, "DISPUTE RESOLVED"))
            elif style == "chaotic" and chance(.3):
                part = round(amt * R.uniform(.3, .7), 2)
                pays.append((pd, part, method, "PARTIAL"))
                pays.append((pd + D(R.randint(15, 90)), round(amt - part, 2), method, "BAL"))
            else:
                pays.append((pd, amt, method, f"{R.randint(1000000, 9999999)}"))
        tot_paid = 0.0
        for pd, amt, m, ref in pays:
            if pd > SNAP or (bankrupt and pd > bankrupt):
                continue
            pn = f"PMT-{seq('pmt', 55_000_000, 9, 7)}"
            wrong_ref = chance(.02)
            O.add("Payment", dict(Payment_Number=pn, Customer_Number=v["cust"] if not wrong_ref else a["erp"], Invoice_Number=None if wrong_ref else v["inv"],
                                  Payment_Date=ds(pd), Amount=amt, Currency=v["cur"], Method=m, Reference=ref,
                                  Applied_Status="Unapplied" if wrong_ref else "Applied",
                                  Remitter_Name=(o["partner"]["legal"] if o["partner"] else a["legal"] if chance(.8) else a["legal"].upper()),
                                  Notes="No invoice reference on remittance" if wrong_ref else None))
            if wrong_ref:
                O.issue("unapplied_cash", "Payment", pn, "Invoice_Number", None, v["inv"], a["id"], "Applied_Status=Unapplied",
                        "Payment received without invoice reference; sits as unapplied cash.")
            tot_paid += amt
            if m not in ("Credit Card",) or chance(.1):
                O.view.event(a, pd, "ERP", "Payment", m, record_table="Payment", record_id=pn, invoice_number=v["inv"], order_number=o["on"],
                             amount=amt, currency=v["cur"], amount_usd=round(amt / o["rate"], 2), payment_method=m, status="Received")
            dtp = (pd - v["d"]).days
        bal = round(v["tot"] - tot_paid, 2)
        if bal <= 0.5:
            status = "Paid"
        elif tot_paid > 0:
            status = "Partially Paid"
        elif SNAP > due:
            status = "Past Due"
        if bal > 0.5 and SNAP > due:
            over = (SNAP - due).days
            dunning = 1 if over < 30 else 2 if over < 60 else 3
            if bankrupt and SNAP > bankrupt:
                wo, status = "Y", "Written Off"
        if dispute and bal > .5:
            status = "Disputed"
        O.add("Invoice", dict(Invoice_Number=v["inv"], Order_Number=o["on"], Customer_Number=v["cust"], Bill_To_Customer_Number=v["cust"],
                              Invoice_Date=ds(v["d"]), Due_Date=ds(due), Currency=v["cur"], Subtotal=v["sub"], Tax_Type=o["tax_type"],
                              Tax_Amount=v["tax"], Invoice_Total=v["tot"], Invoice_Total_USD=v["usd"], Amount_Paid=round(tot_paid, 2),
                              Balance=max(0, bal), Status=status, Days_To_Pay=dtp if status == "Paid" else None, Dispute_Reason=dispute,
                              Dunning_Level=dunning, Written_Off=wo))
        if status in ("Past Due", "Disputed", "Written Off") or (status == "Paid" and dtp and dtp > 75):
            O.view.event(a, min(SNAP, due + D(15)), "ERP", "Invoice", status, record_table="Invoice", record_id=v["inv"], invoice_number=v["inv"],
                         order_number=o["on"], amount=v["tot"], currency=v["cur"], amount_usd=v["usd"], status=status,
                         subject=f"Invoice {v['inv']} {status}", text=dispute, details=dict(balance=max(0, bal), dunning_level=dunning, days_to_pay=dtp))
        a.setdefault("ar_events", []).append((v["d"], due, status, bal, dispute, v["inv"], o["on"]))


def lease_for(a, o, cust):
    term = R.choice([24, 36, 36, 36, 48])
    start = o["booked"]
    if o.get("force_lease") and not a.get("lease_forced"):
        term = months_between(start, dt.date(2026, 4, 30)) or 36
        a["lease_forced"] = True
    end = add_months(start, term)
    fin = round(o["sub"] * o["rate"], 2)
    units = sum(l["qty"] for l in o["lines"] if l["p"]["bu"] in ("Client Solutions", "Infrastructure Solutions"))
    ln = f"LSE-{seq('lse', 300000, 3)}"
    O.add("Lease_Contract", dict(Lease_Number=ln, Customer_Number=cust, CRM_Account_Id=a["id"], Order_Number=o["on"],
                                 Lease_Type=R.choice(["Fair Market Value", "Fair Market Value", "$1 Buyout", "Device-as-a-Service Bundle"]),
                                 Start_Date=ds(start), End_Date=ds(end), Term_Months=term, Monthly_Payment=round(fin * 1.07 / term, 2),
                                 Financed_Amount=fin, Units=units, End_Of_Term_Option=R.choice(["Return", "Extend", "Buyout", "Refresh", None]) if end <= SNAP + D(180) else None,
                                 Status="Ended" if end < SNAP else "Active"))
    a.setdefault("leases", []).append((ln, start, end, units, fin))


def assets_from(a, o, lines, sd, site):
    for l in lines:
        p = l["p"]
        if p["category"] in ("Notebooks", "Desktops", "Workstations", "Thin Clients", "Rugged", "Consumer Notebooks") and not p["serialized"]:
            base = R.randint(1000, 9999)
            sn = f"{''.join(R.choice('BCDFGHJKLMNPQRSTVWXYZ0123456789') for _ in range(4))}{base}"
            add_asset(a, o, p, sd, site, l["qty"], sn, f"{sn[:4]}{base + l['qty'] - 1}")
        elif p["serialized"]:
            for _ in range(min(l["qty"], 400)):
                sn = "".join(R.choice("BCDFGHJKLMNPQRSTVWXYZ0123456789") for _ in range(7))
                add_asset(a, o, p, sd, site, 1, sn, None)


def add_asset(a, o, p, sd, site, qty, sn, sn_end, source="Order"):
    w = None
    if o:
        for l in o["lines"]:
            if l["p"]["category"] == "Support Services" and l["p"]["wfam"] == p["wfam"]:
                w = l["p"]
                break
    wend = add_months(sd, w["term"]) if w else add_months(sd, 12 if p["bu"] != "Infrastructure Solutions" else 36)
    eos = add_months(p["eol"], 60) if p["eol"] else None
    age_retire = R.randint(48, 72) if p["category"] in ("Notebooks", "Desktops", "Thin Clients", "Consumer Notebooks") else R.randint(66, 96)
    status, uend = "Installed", None
    if add_months(sd, age_retire) < SNAP:
        status, uend = R.choice(["Retired", "Retired", "Recycled (ITAD)", "Replaced"]), add_months(sd, age_retire)
    fw, fwd = None, None
    if p["serialized"] and p["category"] not in ("Workstations",):
        disc = a.setdefault("patch", wpick({"good": 45, "lagging": 35, "never": 20}))
        if disc == "good":
            fwd = max(sd, SNAP - D(R.randint(20, 200)))
        elif disc == "lagging":
            fwd = max(sd, SNAP - D(R.randint(300, 900)))
        else:
            fwd = sd
        if a.get("showcase") == "security_advisory_exposure":
            fwd = sd
        fw = fw_version(p, fwd)
    aid = sfid("02i")
    as_ = dict(id=aid, p=p, sd=sd, sn=sn, qty=qty, site=site, status=status, fw=fw, fwd=fwd, wend=wend, w=w, order=o["on"] if o else None)
    a["assets"].append(as_)
    O.add("Asset", dict(Id=aid, Name=f"{p['name']}" + (f" x{qty}" if qty > 1 else ""), AccountId=a["id"], Product2Id=p.get("Id"), SKU=p["sku"],
                        SerialNumber=sn, Serial_Range_End__c=sn_end, Quantity=qty, Order_Number__c=as_["order"], Ship_To_Site__c=site["id"],
                        Site_City__c=site["city"][2] if isinstance(site["city"], tuple) else site["city"], InstallDate=ds(sd), Status=status,
                        Usage_End_Date__c=ds(uend), Configuration__c=p["specs"], Firmware_Version__c=fw, Firmware_Updated__c=ds(fwd),
                        Warranty_SKU__c=w["sku"] if w else None, Warranty_End_Date__c=ds(wend), End_Of_Support_Date__c=ds(eos), Source__c=source))
    if w or p["bu"] == "Infrastructure Solutions":
        O.add("ServiceContract", dict(Id=sfid("810"), Name=(w["name"] if w else "Base Warranty") + f" - {sn}", AccountId=a["id"], AssetId=aid,
                                      SKU=w["sku"] if w else None, Tier__c=w["line"] if w else "Base Warranty", StartDate=ds(sd), EndDate=ds(wend),
                                      Term_Months__c=w["term"] if w else months_between(sd, wend), Status="Active" if wend >= SNAP else "Expired",
                                      Order_Number__c=as_["order"], Auto_Renew__c="false"))


# ------------------------------------------------------------------ legacy history (pre-Salesforce, FY17-FY21) + aging install base
def legacy(a, V):
    if not a["first_buy"]:
        return
    for f in range(LEGACY_FY_FIRST, FY_FIRST):
        S = a["spend"].get(f, 0)
        if S <= 0:
            continue
        src = "QUILLON_ERP" if a.get("quillon") and a.get("quillon_only") else "ORV_ERP_LEGACY"
        for cat, sh in a["mix"].items():
            amt = S * sh * R.uniform(.7, 1.3)
            if amt < 500:
                continue
            last = min(a["last_buy"], fy_end(f) - D(R.randint(0, 120)))
            O.add("Legacy_Order_Summary", dict(Customer_Number=a["quillon_erp"] if src == "QUILLON_ERP" else a["erp"], Source_System=src,
                                               Fiscal_Year=f"FY{f}", Product_Category=GROUP_NAME[cat], Order_Count=max(1, int(amt / AVG_ORDER[cat][a["seg"][f]])),
                                               Revenue_USD=round(amt, 2), Last_Order_Date=ds(last)))
        # aging install base from legacy years (drives refresh + warranty signals)
        if f >= 19 and a["spend"].get(f, 0) > 0:
            d = between(fy_start(f), min(fy_end(f), a["last_buy"]))
            if d < (a["first_buy"] or d):
                continue
            site = a["sites"][0]
            nb = CAT.pick_current(lambda p: p["family"] == "Aster Laptops" and p["gen"] == "G1", d) if f >= 21 else \
                next(p for p in CAT.PRODUCTS if p["family"] == "Aster Laptops" and p["gen"] == "G1")
            qty = max(1, int(a["spend"][f] * a["mix"]["client"] * .6 / 1100))
            add_asset(a, None, nb, d, site, qty, f"L{R.randint(1000000, 9999999)}", None, source="Legacy ERP Migration")
            if a["seg"][f] != "Small Business" and a["spend"][f] * a["mix"]["server"] > 15000:
                srv = next(p for p in CAT.PRODUCTS if p["family"] == "Atlas Rack Servers" and p["gen"] == "G3")
                legacy_srv = dict(srv, name=srv["name"].replace("G3", "G2"), gen="G2", launch=dt.date(2019, 4, 1), eol=dt.date(2021, 11, 30))
                for _ in range(min(60, max(1, int(a["spend"][f] * a["mix"]["server"] / 14000)))):
                    add_asset(a, None, legacy_srv, d, site, 1, "".join(R.choice("BCDFGHJKLMNPQRSTVWXYZ0123456789") for _ in range(7)), None,
                              source="Legacy ERP Migration")


# ------------------------------------------------------------------ Flex / DaaS monthly usage
def flex(a):
    if not (a.get("flex") or a.get("daas")):
        return
    if not a["first_buy"]:
        return
    start = max(WIN_START + D(R.randint(60, 600)), dt.date(2021, 9, 1))
    if not W.buying(a, start):
        return
    svc = "Orvane Flex Storage" if a.get("flex") else "Device-as-a-Service Standard"
    cn = f"FLX-{seq('flx', 100000, 3)}"
    commit = R.randint(150, 2000) if a.get("flex") else R.randint(80, 1500)
    used = commit * R.uniform(.55, .9)
    m = month_start(start)
    rate_c = 21 if a.get("flex") else 55
    rate_o = 27 if a.get("flex") else 55
    while m <= SNAP and W.buying(a, m) or (m <= SNAP and m < a["last_buy"]):
        used *= 1 + R.gauss(.025 if a.get("flex") else .008, .02)
        ov = max(0, used - commit)
        O.add("Flex_Usage_Monthly", dict(Contract_Number=cn, Customer_Number=a["erp"], CRM_Account_Id=a["id"], Service=svc, Month=ds(m),
                                         Committed_Units=commit, Used_Units=round(used, 1), Overage_Units=round(ov, 1),
                                         Committed_Charge=round(commit * rate_c, 2), Overage_Charge=round(ov * rate_o, 2),
                                         Invoice_Number=f"INV-{seq('inv', 90_000_000, 17, 15)}"))
        if ov > 0 and not a.get("flex_ov_ev"):
            a["flex_ov_ev"] = True
            O.view.event(a, m, "ERP", "Flex Usage", "Overage began", record_table="Flex_Usage_Monthly", record_id=cn,
                         subject=f"{svc} usage exceeded commitment", amount=round(ov * rate_o, 2), currency="USD", amount_usd=round(ov * rate_o, 2),
                         details=dict(committed=commit, used=round(used, 1)))
        m = add_months(m, 1)
        if m > a["last_buy"] + D(31):
            break
    a["flex_contract"] = (cn, svc, commit, round(used, 1))


# ------------------------------------------------------------------ consumer purchases (people tied to accounts)
def consumer(a):
    people = []
    if a.get("consumer_origin") or a.get("early_consumer"):
        founders = [c for c in a["contacts"] if c["level"] == "C-Level" or c["tier"] == "smb"][:2] or a["contacts"][:1]
        for c in founders:
            people.append((c, "founder", (a["first_buy"] or WIN_START) - D(R.randint(30, 500))))
    for c in a["contacts"]:
        if chance(.025) and not c["shared"]:
            people.append((c, "epp", between(max(c["start"], WIN_START), min(c["end"] or SNAP, SNAP))))
    for c, kind, d0 in people:
        d0 = max(d0, WIN_START)
        n = R.randint(1, 4) if kind == "founder" else R.randint(1, 2)
        home = W.pick_city(a["country"], a["region"])
        email = c["email"] if kind == "epp" and chance(.6) else f"{slug(c['first'])}{R.choice(['', '.', '_'])}{slug(c['last'])}{R.choice(['', str(R.randint(1, 99))])}@{R.choice(['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'hotmail.com'])}"
        for k in range(n):
            d = min(SNAP, d0 + D(R.randint(0, 400) * k))
            p = CAT.pick_current(lambda p: p["bu"] == "Consumer" or p["line"] in ("Aster 5", "Aster 7") or p["family"] in ("Clarity Monitors", "Peripherals & Accessories", "Tether Docks"), d, .5)
            q = 1 if p["list"] > 400 else R.randint(1, 3)
            price = round(CAT.list_price(p, d) * (1 - (R.choice([.1, .12, .15]) if kind == "epp" else R.choice([0, 0, .05, .1]))), 2)
            linked = a["id"] if (kind == "epp" and chance(.15)) or (kind == "founder" and chance(.3)) else None
            con = f"WEB-{seq('web', 7_000_000, 7, 5)}"
            O.add("Consumer_Order", dict(Consumer_Order_Number=con, Order_Date=ds(d), Customer_Name=f"{c['first']} {c['last']}" if chance(.8) else f"{c['first'][0]}. {c['last']}",
                                         Email=email, Ship_Address=W.street(), City=home[2], State_Province=home[1], Postal_Code=W.postal(a["country"], home[3]),
                                         SKU=p["sku"], Item_Description=p["name"], Quantity=q, Unit_Price=price, Order_Total=round(price * q, 2),
                                         Payment_Method=R.choice(["Visa", "Mastercard", "Amex", "PayPal", "Apple Pay"]),
                                         Program="Employee Purchase Program" if kind == "epp" else "Consumer Online Store", Linked_Account_Id=linked,
                                         Employer_Text=(a["base_name"] if kind == "epp" and chance(.6) else a["base_name"].lower() if kind == "epp" and chance(.3) else None)))
            if not linked:
                O.issue("consumer_purchase_unlinked", "Consumer_Order", con, "Linked_Account_Id", None, a["id"], a["id"],
                        "Match on name/email/employer to Contact", f"{'Founder' if kind == 'founder' else 'Employee'} consumer purchase belongs to this business account.", "Low")
            O.view.event(a, d, "Consumer Store", "Consumer Order", "Employee Purchase" if kind == "epp" else "Founder / owner purchase",
                         record_table="Consumer_Order", record_id=con, product=p, quantity=q, amount=round(price * q, 2), currency="USD",
                         amount_usd=round(price * q, 2), contact=c, payment_method="Credit Card", account_known=bool(linked))
