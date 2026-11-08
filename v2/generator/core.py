"""Core helpers shared by every V2 generator module: RNG, ids, fiscal calendar, writers."""
import csv
import datetime as dt
import json
import math
import os
import random
import unicodedata
from collections import Counter, defaultdict
from itertools import accumulate

SEED = 2026
R = random.Random(SEED)


def reseed(seed):
    global SEED
    SEED = seed
    R.seed(seed)


# ------------------------------------------------------------------ calendar (FY = Feb..Jan)
WIN_START = dt.date(2021, 2, 1)        # FY22 day 1 = Salesforce go-live
SNAP = dt.date(2026, 1, 31)            # last day of FY26 = data snapshot
FY_FIRST, FY_LAST = 22, 26
LEGACY_FY_FIRST = 17                   # ERP summary history goes back to FY17
QUILLON_MIGRATION = dt.date(2023, 9, 18)   # acquired rival's CRM/ERP merged in (FY24 Q3)
RESTRUCTURE = dt.date(2023, 2, 1)          # FY24: two US regions + Canada -> West/Central/East
D = lambda n: dt.timedelta(days=n)


def fy(d):
    return (d.year + 1 if d.month >= 2 else d.year) - 2000


def fy_start(f):
    return dt.date(2000 + f - 1, 2, 1)


def fy_end(f):
    return dt.date(2000 + f, 1, 31)


def fq(d):
    return ((d.month - 2) % 12) // 3 + 1


def fq_label(d):
    return f"FY{fy(d)} Q{fq(d)}"


def quarter_start(d):
    k = (d.month - 2) % 12
    m = (k // 3 * 3 + 1) % 12 + 1
    return dt.date(d.year - 1 if d.month == 1 else d.year, m, 1)


def quarter_end(d):
    return add_months(quarter_start(d), 3) - D(1)


def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    m += 1
    last = (dt.date(y + m // 12, m % 12 + 1, 1) - D(1)).day
    return dt.date(y, m, min(d.day, last))


def month_start(d):
    return dt.date(d.year, d.month, 1)


def months_between(a, b):
    return (b.year - a.year) * 12 + b.month - a.month


US_HOLIDAYS = set()
for _y in range(2016, 2027):
    for _md in ((1, 1), (7, 4), (12, 25), (12, 24), (12, 31), (11, 11)):
        US_HOLIDAYS.add(dt.date(_y, *_md))
    # thanksgiving (4th thu nov) + day after, memorial (last mon may), labor (1st mon sep)
    _n = dt.date(_y, 11, 1)
    _th = _n + D((3 - _n.weekday()) % 7 + 21)
    US_HOLIDAYS |= {_th, _th + D(1)}
    _m = dt.date(_y, 5, 31)
    US_HOLIDAYS.add(_m - D(_m.weekday()))
    _l = dt.date(_y, 9, 1)
    US_HOLIDAYS.add(_l + D((0 - _l.weekday()) % 7))


def is_bday(d):
    return d.weekday() < 5 and d not in US_HOLIDAYS


def bday(d):
    while not is_bday(d):
        d += D(1)
    return d


def bday_back(d):
    while not is_bday(d):
        d -= D(1)
    return d


def between(a, b):
    if b <= a:
        return a
    return a + D(R.randint(0, (b - a).days))


def rand_bday(a, b):
    d = between(a, b)
    if not is_bday(d):
        d2 = bday(d)
        d = d2 if d2 <= b else bday_back(d)
    return d


def ts(d, lo=8, hi=18, tz_offset=5):
    """Local business-hours time -> UTC iso string (Salesforce style)."""
    h = R.randint(lo, hi - 1)
    t = dt.datetime(d.year, d.month, d.day, h, R.randint(0, 59), R.randint(0, 59)) + dt.timedelta(hours=tz_offset)
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def ts_dt(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def ds(d):
    return d.isoformat() if d else None


# ------------------------------------------------------------------ random helpers
def clip(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def wpick(d):
    k = list(d.keys())
    return R.choices(k, weights=list(d.values()))[0]


def chance(p):
    return R.random() < p


def poisson(lam):
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, int(round(R.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= R.random()
        if p < L:
            return k
        k += 1


def lognorm(median, sigma):
    return median * math.exp(R.gauss(0, sigma))


def human_round(x):
    """People type round-ish numbers."""
    if x <= 0:
        return 0
    mag = 10 ** max(0, int(math.log10(x)) - 1)
    if chance(.6):
        return int(round(x / mag) * mag)
    return int(round(x))


def human_pct(x):
    """Discounts cluster on 5s and whole numbers."""
    r = R.random()
    if r < .45:
        return round(x / 5) * 5
    if r < .85:
        return round(x)
    return round(x, 1)


def ascii_fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def slug(s):
    return "".join(ch for ch in ascii_fold(s).lower() if ch.isalnum())


def money(x, cur="USD"):
    sym = "C$" if cur == "CAD" else "$"
    if x >= 1e6:
        return f"{sym}{x / 1e6:.1f}M"
    if x >= 10000:
        return f"{sym}{x / 1000:,.0f}K" if chance(.5) else f"{sym}{x:,.0f}"
    return f"{sym}{x:,.0f}"


# ------------------------------------------------------------------ ids
B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
SFX = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"
_idc = Counter()


def sfid(prefix):
    _idc[prefix] += 1
    n = 4_100_000_000 + _idc[prefix] * 6151 + R.randint(0, 6000)
    s = ""
    while n:
        n, r = divmod(n, 62)
        s = B62[r] + s
    base = prefix + "5f0" + s.rjust(9, "0")
    suf = ""
    for i in range(3):
        chunk = base[i * 5:(i + 1) * 5]
        suf += SFX[sum(1 << j for j, c in enumerate(chunk) if "A" <= c <= "Z")]
    return base + suf


_seq = Counter()


def seq(name, start, step=1, jitter=0):
    _seq[name] += 1
    return start + _seq[name] * step + (R.randint(0, jitter) if jitter else 0)


# ------------------------------------------------------------------ output
class Table:
    """Streaming CSV writer. Keys starting with '_' are private."""

    def __init__(self, folder, name, fields):
        os.makedirs(folder, exist_ok=True)
        self.name, self.fields, self.n = name, fields, 0
        self.f = open(os.path.join(folder, name + ".csv"), "w", newline="", encoding="utf-8")
        self.w = csv.DictWriter(self.f, fieldnames=fields, extrasaction="ignore")
        self.w.writeheader()

    def add(self, row):
        self.w.writerow(row)
        self.n += 1

    def close(self):
        self.f.close()


def jdump(d):
    return json.dumps({k: v for k, v in d.items() if v not in (None, "")}, separators=(",", ":"), default=str)


def tf(x):
    return "true" if x else "false"
