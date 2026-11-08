"""~500-SKU fictional Orvane catalog with generations, launch/EOL dates, list price history and margin."""
import datetime as dt
from core import R, D, chance, add_months

PRODUCTS = []
BY_SKU = {}

# client generations (launch dates); infra generations
CGEN = {"G1": dt.date(2020, 4, 14), "G2": dt.date(2021, 4, 20), "G3": dt.date(2022, 5, 10), "G4": dt.date(2023, 5, 16),
        "G5": dt.date(2024, 5, 21), "G6": dt.date(2025, 5, 13)}
DGEN = {"G2": dt.date(2020, 9, 15), "G3": dt.date(2022, 3, 8), "G4": dt.date(2023, 9, 12), "G5": dt.date(2025, 3, 11)}
SGEN = {"G3": dt.date(2021, 3, 16), "G4": dt.date(2023, 2, 7), "G5": dt.date(2024, 10, 15)}
NGEN = {"G1": dt.date(2020, 6, 1), "G2": dt.date(2023, 6, 6)}
CPU = {"G1": "10th-gen", "G2": "11th-gen", "G3": "12th-gen", "G4": "13th-gen", "G5": "Core Ultra S1", "G6": "Core Ultra S2"}

_n = [0]


def add(name, family, line, bu, category, group, price, cost_pct, launch, eol=None, gen=None, unit="Each",
        recurring=False, term=None, serialized=False, wfam=None, specs="", per=None):
    _n[0] += 1
    prefix = {"Client Solutions": "C", "Infrastructure Solutions": "I", "Software": "S", "Services": "V",
              "Financing": "F", "Consumer": "N"}[bu]
    sku = f"{prefix}{R.randint(10, 99)}-{_n[0]:04d}{R.choice('ABCDEFGHJKLMNPRSTUVWXYZ')}"
    p = dict(sku=sku, name=name, family=family, line=line, bu=bu, category=category, group=group, list=float(price),
             cost_pct=cost_pct, launch=launch, eol=eol, gen=gen, unit=unit, recurring=recurring, term=term,
             serialized=serialized, wfam=wfam, specs=specs, per=per)
    PRODUCTS.append(p)
    BY_SKU[sku] = p
    return p


def _eol(gens, g, months_after_next=8):
    keys = list(gens)
    i = keys.index(g)
    if i + 1 < len(keys):
        return add_months(gens[keys[i + 1]], months_after_next)
    return None


# ---------------------------------------------------------------- Client: Aster laptops
ASTER = {
    "Aster 3": [("14", 819), ("15", 869)],
    "Aster 5": [("13", 1249), ("14", 1299), ("16", 1399)],
    "Aster 7": [("13", 1749), ("14", 1849), ("16", 1999)],
    "Aster 9": [("13 2-in-1", 2299), ("14", 2449)],
}
CFG = [("i5 / 16GB / 512GB", 0, "16GB RAM, 512GB NVMe"), ("i7 / 32GB / 1TB", 380, "32GB RAM, 1TB NVMe"),
       ("i7 / 64GB / 2TB", 820, "64GB RAM, 2TB NVMe")]
for line, sizes in ASTER.items():
    for g in ("G1", "G2", "G3", "G4", "G5", "G6"):
        for size, base in sizes:
            cfgs = CFG[:2] if line == "Aster 3" else CFG if line in ("Aster 7", "Aster 9") else CFG[:2] if g in ("G1", "G2") else CFG
            for cname, up, spec in cfgs:
                add(f"{line} {size} {g} ({cname.replace('i5', 'C5').replace('i7', 'C7')})", "Aster Laptops", line, "Client Solutions",
                    "Notebooks", "client", base + up, .85, CGEN[g], _eol(CGEN, g), g, serialized=False, wfam="laptop",
                    specs=f"{CPU[g]} CPU, {spec}, {size}\" display")
for g in ("G2", "G4", "G6"):
    for m, price in (("Bastion 14 Rugged", 3499), ("Bastion 12 Rugged Tablet", 3899)):
        add(f"{m} {g}", "Bastion Rugged", "Bastion", "Client Solutions", "Rugged", "client", price, .80, CGEN[g],
            _eol(CGEN, g, 20), g, wfam="laptop", specs=f"{CPU[g]} CPU, MIL-STD-810H, hot-swap battery")
# Desktops / AIO
for g in ("G2", "G3", "G4", "G5"):
    for ff, ffp in (("Tower", 0), ("SFF", -40), ("Micro", -60)):
        for tier, tp in (("3", 699), ("5", 949), ("7", 1349)):
            add(f"Cadence {tier} {ff} {g}", "Cadence Desktops", f"Cadence {tier}", "Client Solutions", "Desktops", "client",
                tp + ffp, .84, DGEN[g], _eol(DGEN, g), g, wfam="desktop", specs=f"{ff} form factor, 16GB RAM, 512GB NVMe")
    for sz, pr in (("24", 1199), ("27", 1549)):
        add(f"Cadence {sz} All-in-One {g}", "Cadence Desktops", "Cadence AIO", "Client Solutions", "Desktops", "client", pr, .84,
            DGEN[g], _eol(DGEN, g), g, wfam="desktop", specs=f"{sz}\" FHD/QHD touch, 16GB RAM")
# Workstations
for g in ("G2", "G3", "G4", "G5"):
    for m, pr, fam in (("Forge M16 Mobile Workstation", 2699, "mobile"), ("Forge M18 Mobile Workstation", 3499, "mobile"),
                       ("Forge T5 Tower Workstation", 2399, "tower"), ("Forge T7 Tower Workstation", 4299, "tower")):
        for cn, up, gpu in (("Std", 0, "mid-range pro GPU 12GB"), ("Perf", 2100, "high-end pro GPU 48GB")):
            add(f"{m} {g} {cn}", "Forge Workstations", m.split()[1], "Client Solutions", "Workstations", "workstation", pr + up, .80,
                DGEN[g], _eol(DGEN, g), g, wfam="workstation", serialized=True, specs=f"{gpu}, 64GB ECC")
for g in ("G2", "G4"):
    for m, pr in (("Wisp 3000 Thin Client", 399), ("Wisp 5000 Thin Client", 549), ("Wisp 7000 Mobile Thin Client", 899)):
        add(f"{m} {g}", "Wisp Thin Clients", "Wisp", "Client Solutions", "Thin Clients", "client", pr, .82, DGEN[g], _eol(DGEN, g, 18), g,
            wfam="desktop", specs="VDI-optimized, 8GB RAM")
# Monitors, docks, peripherals
for g, ld in (("2021", dt.date(2021, 3, 2)), ("2024", dt.date(2024, 2, 6))):
    for m, pr in (("Clarity 22 Monitor", 149), ("Clarity 24 Monitor", 189), ("Clarity 24 USB-C Hub Monitor", 289),
                  ("Clarity 27 Monitor", 279), ("Clarity 27 4K USB-C Monitor", 529), ("Clarity 32 4K Monitor", 749),
                  ("Clarity 34 Curved Ultrawide", 899), ("Clarity 43 4K Conference Display", 1399), ("Clarity 49 Dual-QHD Ultrawide", 1899)):
        add(f"{m} ({g})", "Clarity Monitors", "Clarity", "Client Solutions", "Monitors", "client", pr, .86, ld,
            add_months(ld, 44) if g == "2021" else None, g, wfam=None)
    for m, pr in (("Tether USB-C Dock", 229), ("Tether Thunderbolt Dock", 329), ("Tether Dual-Charge Dock", 349)):
        add(f"{m} ({g})", "Tether Docks", "Tether", "Client Solutions", "Docks & Peripherals", "client", pr, .82, ld,
            add_months(ld, 44) if g == "2021" else None, g)
for m, pr in (("Orvane Wireless Keyboard", 49), ("Orvane Wireless Mouse", 29), ("Orvane Keyboard & Mouse Combo", 69),
              ("Orvane Pro Headset", 129), ("Orvane Speakerphone", 189), ("Orvane 4K Webcam", 149), ("Orvane Pro Backpack 16", 79),
              ("Orvane Sleeve 14", 39), ("USB-C to HDMI Adapter", 29), ("USB-C to Ethernet Adapter", 35), ("65W USB-C Power Adapter", 59),
              ("90W USB-C Power Adapter", 79), ("130W Power Adapter", 99), ("Privacy Screen 14", 69), ("Replacement Battery (Aster)", 129),
              ("Cable Lock", 39)):
    add(m, "Peripherals & Accessories", "Accessories", "Client Solutions", "Docks & Peripherals", "client", pr, .70, dt.date(2020, 1, 1))
# Consumer
for g in ("G4", "G5", "G6"):
    for m, pr in (("Nova 13", 699), ("Nova 15", 799), ("Nova 16 Plus", 1099), ("Nova X 16 Gaming", 1699), ("Nova X 18 Gaming", 2299)):
        add(f"{m} {g}", "Nova Consumer", "Nova", "Consumer", "Consumer Notebooks", "consumer", pr, .88, CGEN[g], _eol(CGEN, g), g,
            wfam="laptop", specs=f"{CPU[g]} CPU")
for g in ("G2", "G3"):
    for m, pr in (("Nova 15", 749), ("Nova Desktop", 649)):
        add(f"{m} {g}", "Nova Consumer", "Nova", "Consumer", "Consumer Notebooks", "consumer", pr, .88, CGEN[g], _eol(CGEN, g), g, wfam="laptop")

# ---------------------------------------------------------------- Infrastructure
for g in ("G3", "G4", "G5"):
    for m, pr, spec in (("Atlas 120", 3900, "1U 1-socket"), ("Atlas 140", 7200, "1U 2-socket"), ("Atlas 240", 11800, "2U 2-socket"),
                        ("Atlas 260", 16500, "2U 2-socket high-density"), ("Atlas 280", 19800, "2U storage-dense, 24 NVMe")):
        for cn, mult, cfg in (("Base", 1.0, "2x 16-core, 256GB RAM"), ("Perf", 1.55, "2x 32-core, 1TB RAM")):
            add(f"{m} {g} {cn}", "Atlas Rack Servers", m, "Infrastructure Solutions", "Servers", "server", round(pr * mult, -1), .70,
                SGEN[g], _eol(SGEN, g, 10), g, serialized=True, wfam="server", specs=f"{spec}, {cfg if '1-socket' not in spec else '1x 16-core, 128GB RAM'}")
    for m, pr in (("Atlas T110 Tower", 2600), ("Atlas T350 Tower", 6900)):
        add(f"{m} {g}", "Atlas Tower Servers", m, "Infrastructure Solutions", "Servers", "server", pr, .72, SGEN[g], _eol(SGEN, g, 10), g,
            serialized=True, wfam="server", specs="tower, 8-core to 24-core")
for g in ("G4", "G5"):
    for m, pr, spec in (("Atlas AI 440", 118000, "4x 80GB accelerators, 2x 48-core, 1TB RAM"),
                        ("Atlas AI 880", 312000, "8x 141GB accelerators, 2x 56-core, 2TB RAM")):
        add(f"{m} {g}", "Atlas AI Servers", m, "Infrastructure Solutions", "AI Servers", "server", pr if g == "G4" else pr * 1.12, .76,
            SGEN[g] + D(60), None, g, serialized=True, wfam="server", specs=spec)
add("Atlas AI 880 G5 Liquid-Cooled", "Atlas AI Servers", "Atlas AI 880", "Infrastructure Solutions", "AI Servers", "server", 389000, .77,
    dt.date(2025, 6, 10), None, "G5", serialized=True, wfam="server", specs="8x 192GB accelerators, direct liquid cooling")
for g in ("G3", "G5"):
    add(f"Atlas MX7 Modular Chassis {g}", "Atlas Modular", "Atlas MX7", "Infrastructure Solutions", "Modular", "server", 17800, .70,
        SGEN[g], _eol(SGEN, g, 18), g, serialized=True, wfam="server", specs="7U, 8 compute sleds")
    for m, pr in (("Atlas MX750c Compute Sled", 12400), ("Atlas MX760c Compute Sled", 19600)):
        add(f"{m} {g}", "Atlas Modular", "Atlas MX7", "Infrastructure Solutions", "Modular", "server", pr, .70, SGEN[g], _eol(SGEN, g, 18), g,
            serialized=True, wfam="server")
for g in ("G3", "G4"):
    for m, pr in (("Converge HX-200 Node", 34000), ("Converge HX-400 Node", 56000), ("Converge HX-600 Node", 88000)):
        add(f"{m} {g}", "Converge HCI", "Converge HX", "Infrastructure Solutions", "HCI", "server", pr, .68, SGEN[g], _eol(SGEN, g, 14), g,
            serialized=True, wfam="server", specs="all-NVMe, 25GbE")
for g in ("G3", "G4"):
    for m, pr, tb in (("Strata 300 Unified Array", 46000, 60), ("Strata 500 Unified Array", 112000, 240), ("Strata 700 Unified Array", 268000, 960)):
        add(f"{m} {g}", "Strata Storage", m.split(" Unified")[0], "Infrastructure Solutions", "Storage", "storage", pr, .64, SGEN[g],
            _eol(SGEN, g, 14), g, serialized=True, wfam="storage", specs=f"{tb}TB raw base, dual controller, NVMe")
    add(f"Strata Scale File Node {g}", "Strata Storage", "Strata Scale", "Infrastructure Solutions", "Storage", "storage", 41000, .65,
        SGEN[g], _eol(SGEN, g, 14), g, serialized=True, wfam="storage", specs="scale-out NAS node, 184TB raw")
    add(f"Strata Object Node {g}", "Strata Storage", "Strata Object", "Infrastructure Solutions", "Storage", "storage", 54000, .65,
        SGEN[g], _eol(SGEN, g, 14), g, serialized=True, wfam="storage", specs="S3-compatible object node, 400TB raw")
    add(f"Strata Expansion Shelf 24-NVMe {g}", "Strata Storage", "Strata Shelves", "Infrastructure Solutions", "Storage", "storage", 23500,
        .66, SGEN[g], _eol(SGEN, g, 18), g, serialized=True, wfam="storage")
for m, pr in (("Strata Drive Pack 6x 7.68TB SSD", 8900), ("Strata Drive Pack 6x 15.36TB NVMe", 16800), ("Strata Drive Pack 12x 20TB NL-SAS", 9800)):
    add(m, "Strata Storage", "Strata Drive Packs", "Infrastructure Solutions", "Storage", "storage", pr, .62, dt.date(2021, 3, 16))
for g in ("G3", "G4"):
    for m, pr in (("Vault DP2400 Backup Appliance", 28500), ("Vault DP5900 Backup Appliance", 96000), ("Vault DP8900 Backup Appliance", 224000)):
        add(f"{m} {g}", "Vault Data Protection", "Vault DP", "Infrastructure Solutions", "Data Protection", "data_protection", pr, .62,
            SGEN[g], _eol(SGEN, g, 14), g, serialized=True, wfam="storage", specs="deduplicating backup target, immutable snapshots")
for g in ("G1", "G2"):
    for m, pr in (("Mesh S1124 1GbE 24-port PoE Switch", 2900), ("Mesh S1148 1GbE 48-port PoE Switch", 4800),
                  ("Mesh S3148 10GbE 48-port Switch", 11800), ("Mesh S4148 25GbE 48-port Switch", 17900),
                  ("Mesh S5232 100GbE Spine Switch", 39500), ("Mesh SD-WAN Edge 300", 1900), ("Mesh SD-WAN Edge 800", 5400)):
        add(f"{m} {g}", "Mesh Networking", "Mesh", "Infrastructure Solutions", "Networking", "networking", pr, .66, NGEN[g],
            _eol(NGEN, g, 14), g, serialized=True, wfam="network")
for m, pr in (("25GbE SFP28 Optic", 89), ("100GbE QSFP28 Optic", 399), ("DAC Cable 3m 25GbE", 59), ("DAC Cable 3m 100GbE", 149)):
    add(m, "Mesh Networking", "Optics & Cables", "Infrastructure Solutions", "Networking", "networking", pr, .55, dt.date(2020, 1, 1))
for g in ("G3", "G5"):
    for m, pr in (("Outpost XE2 Edge Server", 4300), ("Outpost XE4 Rugged Edge Server", 7100)):
        add(f"{m} {g}", "Outpost Edge", "Outpost", "Infrastructure Solutions", "Edge", "server", pr, .70, SGEN[g], _eol(SGEN, g, 18), g,
            serialized=True, wfam="server")
for m, pr in (("32GB DDR5 RDIMM", 310), ("64GB DDR5 RDIMM", 590), ("128GB DDR5 RDIMM", 1590), ("1.92TB NVMe Drive", 520),
              ("3.84TB NVMe Drive", 980), ("7.68TB NVMe Drive", 1890), ("2.4TB 10K SAS HDD", 390), ("48GB Inference Accelerator Card", 9400),
              ("80GB Training Accelerator Card", 27800), ("25GbE Dual-Port NIC", 610), ("100GbE Dual-Port NIC", 1390),
              ("Sliding Ready Rails", 129), ("1400W Hot-Plug PSU", 349), ("Boot Optimized Storage (2x 480GB)", 690)):
    add(m, "Server Options", "Options", "Infrastructure Solutions", "Server Options", "server", pr, .60, dt.date(2021, 3, 16))
for m, pr in (("Orvane 42U Rack Enclosure", 1850), ("Metered Rack PDU 30A", 920), ("3kVA Rack UPS", 3250)):
    add(m, "Racks & Power", "Racks & Power", "Infrastructure Solutions", "Racks & Power", "server", pr, .68, dt.date(2020, 1, 1))

# ---------------------------------------------------------------- Software
SW = [("Orvane Manage (per device / yr)", 24, .15, "client", True, 12), ("Orvane Insight (per node / yr)", 360, .18, "server", True, 12),
      ("Orvane Shield Standard (per endpoint / yr)", 36, .20, "software", True, 12), ("Orvane Shield Advanced XDR (per endpoint / yr)", 68, .22, "software", True, 12),
      ("Vault Backup Software (per front-end TB / yr)", 420, .2, "data_protection", True, 12), ("Vault Backup for M365 (per user / yr)", 30, .25, "data_protection", True, 12),
      ("Server OS Standard 16-Core License (resale)", 1069, .9, "software", False, None), ("Server OS Datacenter 16-Core License (resale)", 6155, .9, "software", False, None),
      ("Hypervisor Enterprise Plus per Core (resale, 1yr)", 350, .88, "software", True, 12), ("Hypervisor Standard per Core (resale, 1yr)", 150, .88, "software", True, 12),
      ("Client OS Pro Upgrade (resale)", 99, .9, "software", False, None), ("Productivity Suite Business (per user / yr, resale)", 264, .92, "software", True, 12),
      ("Database Standard 2-Core License (resale)", 3900, .9, "software", False, None), ("Container Platform Subscription (per node / yr)", 2400, .85, "software", True, 12),
      ("Remote Access Gateway (per concurrent user / yr)", 48, .5, "software", True, 12), ("Orvane AI Factory Software Stack (per GPU / yr)", 4500, .3, "server", True, 12)]
for m, pr, cp, grp, rec, term in SW:
    add(m, "Software", "Orvane Software" if m.startswith(("Orvane", "Vault")) else "Resale Software", "Software", "Software", grp, pr, cp,
        dt.date(2020, 1, 1) if "AI Factory" not in m else dt.date(2024, 3, 19), recurring=rec, term=term, unit="License")

# ---------------------------------------------------------------- Services (warranty + deployment + consulting)
WARR = {}
for fam, base in (("laptop", 179), ("desktop", 129), ("workstation", 289)):
    for tier, mult in (("ProCare", 1.0), ("ProCare Plus", 1.65)):
        for yrs, ym in ((3, 1.0), (4, 1.35), (5, 1.7)):
            p = add(f"{tier} {yrs}-Year ({fam.title()})", "Support Services", tier, "Services", "Support Services", "services",
                    round(base * mult * ym, -1) - 1, .45, dt.date(2020, 1, 1), unit="Per Device", term=12 * yrs, wfam=fam,
                    specs="Next-business-day onsite, 24x7 phone" + (", accidental damage, KYHD" if "Plus" in tier else ""))
            WARR[(fam, tier, yrs)] = p
for fam, base in (("server", 1450), ("storage", 6200), ("network", 520)):
    for tier, mult in (("ProCare NBD", 1.0), ("ProCare Mission Critical 4-Hour", 1.9)):
        for yrs, ym in ((3, 1.0), (5, 1.55)):
            p = add(f"{tier} {yrs}-Year ({fam.title()})", "Support Services", tier, "Services", "Support Services", "services",
                    round(base * mult * ym, -1), .42, dt.date(2020, 1, 1), unit="Per System", term=12 * yrs, wfam=fam,
                    specs="4-hour onsite parts & labor, TAM, proactive monitoring" if "Mission" in tier else "Next-business-day onsite parts & labor")
            WARR[(fam, tier, yrs)] = p
for fam, pr in (("laptop", 119), ("desktop", 89), ("server", 1100), ("storage", 4800)):
    WARR[(fam, "ext", 1)] = add(f"ProCare 1-Year Extension ({fam.title()})", "Support Services", "Extensions", "Services",
                                "Support Services", "services", pr, .40, dt.date(2020, 1, 1), unit="Per Device", term=12, wfam=fam)
add("Keep Your Hard Drive (per system)", "Support Services", "Add-ons", "Services", "Support Services", "services", 49, .3, dt.date(2020, 1, 1), unit="Per Device")
DEPLOY = [("Factory Imaging & Configuration (per device)", 25, "Deployment"), ("Asset Tagging & Reporting (per device)", 6, "Deployment"),
          ("Zero-Touch Enrollment Setup (per device)", 12, "Deployment"), ("Onsite Desk-Side Install (per device)", 85, "Deployment"),
          ("Rack & Stack Installation (per server)", 650, "Deployment"), ("Storage Array Implementation", 14500, "Deployment"),
          ("HCI Cluster Deployment", 22000, "Deployment"), ("Network Configuration Service", 8500, "Deployment"),
          ("Data Migration Service (per 50TB block)", 9500, "Deployment"), ("Asset Recovery / ITAD (per device)", 18, "Deployment"),
          ("Certified Data Sanitization (per drive)", 14, "Deployment"), ("Onsite Residency Engineer (per month)", 21500, "Consulting"),
          ("Managed Device Service (per device / month)", 9, "Managed"), ("Managed Infrastructure Service (per node / month)", 145, "Managed"),
          ("AI Readiness Assessment", 38000, "Consulting"), ("Data Center Modernization Assessment", 29000, "Consulting"),
          ("Cyber Recovery Workshop", 18500, "Consulting"), ("VMware Exit Planning Workshop", 24000, "Consulting"),
          ("Orvane Education Credits (block of 10)", 5500, "Consulting"), ("Windows 11 Migration Readiness Service", 16000, "Consulting")]
for m, pr, cat in DEPLOY:
    add(m, "Deployment & Consulting Services", cat, "Services",
        {"Deployment": "Deployment Services", "Consulting": "Consulting & Managed Services", "Managed": "Consulting & Managed Services"}[cat],
        "services", pr, .50 if cat != "Managed" else .62, dt.date(2020, 1, 1) if "VMware" not in m else dt.date(2024, 2, 20),
        unit="Service", recurring=cat == "Managed", term=12 if cat == "Managed" else None)
# ---------------------------------------------------------------- Financing / as-a-service
for m, pr, rec in (("Device-as-a-Service Essentials (per device / month)", 39, True), ("Device-as-a-Service Standard (per device / month)", 55, True),
                   ("Device-as-a-Service Premium (per device / month)", 72, True), ("Orvane Flex Storage - Committed (per TB / month)", 21, True),
                   ("Orvane Flex Storage - Overage (per TB / month)", 27, True), ("Orvane Flex Compute - Committed (per core / month)", 11, True),
                   ("Orvane Flex Compute - Overage (per core / month)", 14, True)):
    add(m, "As-a-Service", "Orvane Flex" if "Flex" in m else "Device-as-a-Service", "Financing", "As-a-Service", "financing", pr, .55,
        dt.date(2021, 8, 3) if "Flex" in m else dt.date(2021, 2, 1), unit="Per Unit / Month", recurring=rec, term=36)


# ---------------------------------------------------------------- price history
def price_mult(p, d):
    """List-price movement over time: shortage-era increases, PC slump cuts, memory cycle."""
    m = 1.0
    hw = p["bu"] in ("Client Solutions", "Infrastructure Solutions", "Consumer")
    if hw:
        if d >= dt.date(2021, 7, 1):
            m *= 1.04 if p["bu"] != "Infrastructure Solutions" else 1.07
        if d >= dt.date(2022, 2, 1):
            m *= 1.05
        if d >= dt.date(2023, 2, 1) and p["bu"] != "Infrastructure Solutions":
            m *= 0.94
        if d >= dt.date(2024, 8, 1) and p["bu"] == "Infrastructure Solutions":
            m *= 1.06
        if d >= dt.date(2025, 4, 1):
            m *= 1.04
        if p["eol"] is None and p["gen"] and p["launch"] and d > p["launch"]:
            pass
        # older generations erode once replaced
        if p["eol"] and d > p["eol"] - D(240):
            m *= 0.93
    else:
        if d >= dt.date(2023, 2, 1):
            m *= 1.05
        if d >= dt.date(2025, 2, 1):
            m *= 1.04
    return m


def list_price(p, d):
    return round(p["list"] * price_mult(p, d), 2)


def sellable(p, d):
    return p["launch"] <= d and (p["eol"] is None or d <= p["eol"])


def pick_current(pred, d, prefer_new=0.7):
    """Pick a sellable product matching predicate; newest generations favored."""
    c = [p for p in PRODUCTS if pred(p) and sellable(p, d)]
    if not c:
        c = [p for p in PRODUCTS if pred(p)]
        c.sort(key=lambda p: abs((p["launch"] - d).days))
        return c[0] if c else None
    if chance(prefer_new):
        newest = max(p["launch"] for p in c)
        c2 = [p for p in c if p["launch"] == newest]
        return R.choice(c2)
    return R.choice(c)


if __name__ == "__main__":
    from collections import Counter
    print(len(PRODUCTS), Counter(p["bu"] for p in PRODUCTS), Counter(p["category"] for p in PRODUCTS).most_common())
