"""Turns phrasebank templates + account facts into rep-written text with each rep's own writing habits."""
import re
from collections import defaultdict
from core import R, chance, money, ds
import phrasebank as PB
import random as _random
RT = _random.Random(99)   # side stream: all wording choices live here so text tweaks never disturb the simulated data
R = RT


def chance(p):
    return RT.random() < p

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
_SH = sorted(PB.SHORTHAND.items(), key=lambda kv: -len(kv[0]))
_SH_RE = [(re.compile(r"\b" + re.escape(k) + r"\b", re.I), v) for k, v in _SH]


class Slots(dict):
    def __missing__(self, k):
        return ""


def nice_date(d):
    return f"{MONTHS[d.month - 1]} {d.day}" if chance(.6) else f"{d.month}/{d.day}" if chance(.6) else d.strftime("%b %d")


def make_slots(**kw):
    s = Slots(account="the customer", contact_first="", contact_last="", contact_name="", contact_title="", contact2_name="",
              contact2_title="", rep_first="", rep_name="", se_name="", old_rep="", partner="", competitor="Corsalis",
              product="Aster 5 14", product_line="Aster laptops", infra_product="Atlas 240", storage_product="Strata 500",
              qty=str(R.randint(20, 400)), seats=str(R.randint(200, 5000)), servers=str(R.randint(4, 60)), amount="$120,000",
              budget="$1.1M", pct=str(R.randint(8, 30)), discount=str(R.choice([10, 12, 15, 18, 20, 22, 25])), tb=str(R.randint(40, 900)),
              util=str(R.randint(62, 94)), growth=str(R.randint(2, 6)), weeks=str(R.randint(2, 14)), date="next Tuesday", quarter="Q3",
              fy="FY25", po_number="", order_number="", quote_number="", case_number="", invoice_number="", site_city="", hq_city="",
              new_exec="", exec_title="CIO", firmware="2.14.1", advisory="OSA-2024-017", model="Atlas 240 G3", os="Windows 11",
              hypervisor="VMware vSphere 7", cloud="Azure", gpu_count="4", lease_end="June 30", days=str(R.randint(10, 75)),
              initiative="data center refresh")
    for k, v in kw.items():
        if v is not None:
            s[k] = str(v)
    return s


def fill(tpl, slots):
    try:
        return tpl.format_map(slots)
    except (ValueError, IndexError, KeyError):
        return tpl


def typo(word):
    if len(word) < 5 or not word.isalpha():
        return word
    i = R.randint(1, len(word) - 3)
    r = R.random()
    if r < .4:
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    if r < .7:
        return word[:i] + word[i + 1:]
    return word[:i] + word[i] + word[i:]


def stylize(text, persona):
    """Rep-specific writing habits: shorthand, lowercase, typos, truncation."""
    if not text:
        return text
    p = {"sloppy": .9, "non_logger": .7, "bulk_logger": .6, "happy_ears": .35, "discounter": .3, "sandbagger": .3,
         "by_the_book": .12, "star": .08}.get(persona, .25)
    if chance(p):
        for rx, v in _SH_RE:
            if chance(.75):
                text = rx.sub(v, text)
    if chance(p * .5):
        text = text[0].lower() + text[1:]
        if chance(.4):
            text = text.lower()
    if chance(p * .6):
        words = text.split(" ")
        for _ in range(R.randint(1, 3)):
            j = R.randrange(len(words))
            words[j] = typo(words[j])
        text = " ".join(words)
    if chance(p * .25) and len(text) > 140:
        text = text[: R.randint(80, len(text) - 20)].rstrip() + R.choice(["...", "", " (cont)", " --"])
    if persona == "bulk_logger" and chance(.3):
        text = R.choice(["[logged late] ", "(catching up on notes) ", "backlog: ", ""]) + text
    return text


def topic_text(topic, part, slots, persona="by_the_book"):
    t = PB.TOPICS.get(topic) or PB.TOPICS["relationship_check_in"]
    if part in ("emails_out", "emails_in"):
        subj, body = R.choice(t[part])
        body = fill(body, slots)
        if part == "emails_in" and chance(.25):
            body += "\n\n" + fill(R.choice(PB.SIGNATURES), slots)
        return fill(subj, slots), body
    txt = fill(R.choice(t[part]), slots)
    return stylize(txt, persona) if part in ("summaries", "chatter", "next_steps") else txt


def call_log(topic, slots, persona, disposition="connected"):
    if disposition != "connected":
        line = fill(R.choice(PB.CALL_DISPOSITIONS_TEXT.get(disposition, PB.CALL_DISPOSITIONS_TEXT["left_voicemail"])), slots)
        return stylize(line, persona)
    body = topic_text(topic, "summaries", slots, persona)
    if chance(.6):
        body += ("\n" if chance(.5) else " ") + ("Next: " if chance(.5) else "NS: " if chance(.5) else "") + \
            topic_text(topic, "next_steps", slots, persona)
    return body


KEYS = {"client": ("laptop", "aster", "dock", "endpoint", "image", "windows", "monitor", "device", "fleet", "intune", "desktop"),
        "workstation": ("workstation", "forge", "gpu", "cad", "render"),
        "server": ("server", "atlas", "rack", "cluster", "vm", "hypervisor", "core", "socket", "gpu", "converge", "hci", "node"),
        "storage": ("storage", "strata", "array", "tb", "capacity", "replication", "nvme", "snapshot"),
        "data_protection": ("backup", "vault", "recovery", "immutable", "ransomware", "rpo", "rto"),
        "networking": ("switch", "mesh", "network", "vlan", "spine", "port", "25gbe", "100gbe"),
        "software": ("licens", "subscription", "renewal", "seat", "software"),
        "services": ("deploy", "service", "migration", "residen", "itad", "imaging", "rack and stack", "rack & stack")}


def matching(pool, cat):
    """Prefer templates that talk about the same product area as the deal."""
    if not cat or cat not in KEYS:
        return pool
    good = [t for t in pool if any(k in (t if isinstance(t, str) else " ".join(t)).lower() for k in KEYS[cat])]
    others = [k for c, ks in KEYS.items() if c != cat for k in ks if k not in KEYS[cat]]
    best = [t for t in good if not any(k in (t if isinstance(t, str) else " ".join(t)).lower() for k in others[:12])]
    return best or good or pool


def meeting_note(mtype, slots, attendees, persona, cat=None):
    pool = matching(PB.MEETING_NOTES.get(mtype) or PB.MEETING_NOTES["discovery"], cat)
    body = fill(R.choice(pool), slots)
    head = "Attendees: " + "; ".join(attendees) + "\n"
    if persona in ("sloppy", "non_logger") and chance(.5):
        body = stylize(body, persona)
    return head + body


CASE_AREA = {"Notebooks": "client", "Desktops": "client", "Servers": "server", "Storage": "storage", "Networking": "networking"}


def case_text(cat, slots, n_comments, area=None):
    c = PB.CASE.get(cat) or PB.CASE["hardware_failure"]
    subj = R.choice(c["subjects"])
    comments = R.sample(c["comments"], min(n_comments, len(c["comments"])))
    if area:
        subs, coms = matching(c["subjects"], area), matching(c["comments"], area)
        subj = RT.choice(subs)
        comments = RT.sample(coms, min(n_comments, len(coms)))
    return fill(subj, slots), [fill(x, slots) for x in comments]


def pick(lst, slots, cat=None):
    return fill(R.choice(matching(lst, cat)), slots)


def account_plan(slots):
    parts = []
    for sec in ("executive_summary", "business_priorities", "it_environment", "whitespace", "relationship_map",
                "competitive_landscape", "risks", "action_plan"):
        if sec in PB.ACCOUNT_PLAN:
            title = sec.replace("_", " ").title()
            k = 1 if sec not in ("action_plan", "whitespace", "risks") else 2
            lines = R.sample(PB.ACCOUNT_PLAN[sec], min(k, len(PB.ACCOUNT_PLAN[sec])))
            parts.append(f"## {title}\n" + "\n".join(("- " if k > 1 else "") + fill(x, slots) for x in lines))
    return "\n\n".join(parts)


def news(ntype, slots):
    pool = PB.NEWS.get(ntype) or PB.NEWS["award"]
    h, s = R.choice(pool)
    return fill(h, slots), fill(s, slots)
