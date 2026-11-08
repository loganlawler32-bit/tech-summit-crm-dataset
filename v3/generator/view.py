"""What the systems *recorded* (vs. truth): lagging segment/status/region labels, stale owners, renamed accounts,
duplicate/parent/partner customer numbers. Also emits rows to the unified timeline with account context."""
import bisect
from core import *
import refdata as RD
import world as W

O = None
LEADERS = {}
REGION_RVP = {}


def pname(p):
    return f"{p['first']} {p['last']}" if p else None


def stint_name(s):
    return pname(s["person"]) if s else None


ROLE_LABEL = {"OWNER": "Account Owner", "SB_REP": "Small Business Inside Sales Rep", "MB_IAE": "Inside Account Executive",
              "LE_FAE": "Field Account Executive", "SEL_GAD": "Global Account Director", "SDR": "Sales Development Rep", "SEL_RAM": "Regional Account Manager - Select", "LE_IAE": "Inside Account Executive",
              "OV_SERVER": "Server Specialist", "OV_STORAGE": "Storage Specialist", "OV_DP": "Data Protection Specialist",
              "OV_NET": "Networking Specialist", "OV_WKS": "Workstation Specialist", "OV_SW": "Software Specialist",
              "OV_SVC": "Services Sales Executive", "OV_FIN": "Financial Services Specialist", "SA": "Solutions Architect",
              "TAM": "Technical Account Manager", "SDM": "Services Delivery Manager", "MB_SPEC_CLIENT": "Inside Client Specialist",
              "MB_SPEC_INFRA": "Inside Infrastructure Specialist", "MB_SPEC_SW": "Inside Software Specialist",
              "MB_SPEC_SVC": "Inside Services Specialist", "PAM": "Partner Account Manager"}


class View:
    def __init__(self, a, orders):
        self.a = a
        a["view"] = self
        purch = sorted(o["d"] for o in orders if o["status"] != "Cancelled")
        if a["first_buy"] and a["first_buy"] < WIN_START:
            purch = [min(a["last_buy"], WIN_START - D(R.randint(1, 90)))] + purch
        self.purch = purch
        a["purchases"] = purch
        # ---- recorded labels per FY
        self.seg, self.status, self.region = {}, {}, {}
        prev_s = prev_st = None
        stuck_region = chance(.08)
        a["stuck_region"] = stuck_region
        for f in W.FYS:
            s = a["seg"][f]
            if prev_s and s != prev_s and chance(.22):
                s = prev_s
            elif chance(.015):
                s = R.choice([x for x in W.SEGS if x != s])
            self.seg[f] = s
            truth_st = self.true_status(fy_start(f))
            st = truth_st if not (prev_st and chance(.12)) else prev_st
            self.status[f] = st
            r = W.region_scope(a, f)
            if f >= 24 and stuck_region:
                r = W.region_scope(a, 23)
            self.region[f] = r
            prev_s, prev_st = s, st
        # ---- name as recorded over time
        self.name_changes = list(a["name_hist"])
        self.crm_name_lag = {}
        for d, nb in self.name_changes:
            self.crm_name_lag[d] = d + D(R.randint(5, 400)) if chance(.7) else None   # None = never updated in CRM

    # ------------------------------------------------ truth helpers
    def last_purchase(self, d):
        i = bisect.bisect_right(self.purch, d)
        return self.purch[i - 1] if i else None

    def true_status(self, d):
        lp = self.last_purchase(d)
        if lp is None:
            return "Acquisition"
        days = (d - lp).days
        return "Retention" if days <= 365 else "Development" if days <= 1095 else "Acquisition"

    def true_name(self, d):
        n = self.a["legal"]
        for dd, nb in self.name_changes:
            if d >= dd:
                n = nb
        return n

    def crm_name(self, d):
        n = self.a["legal"]
        for dd, nb in self.name_changes:
            upd = self.crm_name_lag.get(dd)
            if upd and d >= upd:
                n = nb
        return n

    # ------------------------------------------------ ERP references
    def order_customer(self, o):
        a = self.a
        if o["channel"] == "Partner":
            return o["partner"]["erp"]
        if a.get("quillon") and a.get("quillon_only") and o["d"] < QUILLON_MIGRATION:
            return a["quillon_erp"]
        if a.get("erp_dupe") and chance(.35):
            return a["erp_dupe"]
        return a["erp"]

    def bill_to(self, o, cust):
        a = self.a
        if a["parent"] and not a.get("unlinked") and chance(.3):
            return a["ultimate"]["erp"]
        return cust

    def end_user_id(self, o):
        if o["channel"] != "Partner":
            return self.a["id"]
        if chance(.35):
            if not o.get("_eu_logged"):
                o["_eu_logged"] = True
                O.issue("partner_order_missing_end_user", "Sales_Order", o["on"], "End_User_Account_Id", None, self.a["id"], self.a["id"],
                        "Channel=Partner and End_User_Account_Id blank", "Partner-sold order not attributed to the end customer account.")
            return None
        return self.a["id"]

    def end_user_name(self, o):
        n = self.true_name(o["d"])
        if o["channel"] == "Partner":
            return R.choice([n, n.upper(), self.a["base_name"], n.replace(",", ""), self.a["base_name"] + " - " + self.a["city"][2]])
        return n

    def rep_label(self, st, d):
        if st is None:
            return "House Account", "HOUSE"
        p = st["person"]
        return pname(p), "R" + p["emp_no"][1:]

    def agreement_no(self, o):
        ag = self.a["ultimate"].get("agreement") or self.a.get("agreement")
        if ag and not o.get("sub_leak") and o["d"] >= ag["start"]:
            return ag["id"]
        return None

    def credit_user(self):
        return R.choice(["J. Ambrose (Credit)", "credit.ops", "M. Delacroix", "auto-release", "S. Patel (Credit)"])

    # ------------------------------------------------ timeline
    def ctx(self, d, erp=False):
        a = self.a
        f = clip(fy(d), FY_FIRST, FY_LAST)
        par = a["parent"]
        if par and a.get("unlinked") and not (a.get("linked_on") and d >= a["linked_on"]):
            par = None
        own = W.owner_on(a, d)
        prov = a.get("prov", {}).get(f, {})
        return dict(account_id=a["id"], account_name=(a.get("quillon_name") if erp == "Q" else self.true_name(d) if erp else self.crm_name(d)),
                    erp_customer_number=a["erp"], parent_account_id=par["id"] if par else None,
                    parent_account_name=self_name(par, d) if par else None,
                    ultimate_parent_name=self_name(a["ultimate"], d) if par else None,
                    segment=self.seg[f], coverage_status=self.status[f], sales_region=self.region[f], industry=a.get("industry_rec", a["industry"]),
                    employees=prov.get("emp"), annual_revenue=prov.get("rev"),
                    account_owner=stint_name(own) if own else (a.get("vacant_label") or "Unassigned"))

    def event(self, a, d, source, etype, subtype, record_table=None, record_id=None, rep=None, contact=None, product=None,
              details=None, account_known=True, **kw):
        if d is None or d > SNAP + D(200):
            return
        row = self.ctx(min(d, SNAP), erp=(source == "ERP"))
        if not account_known:
            for k in ("account_id", "parent_account_id", "parent_account_name", "ultimate_parent_name", "account_owner", "segment",
                      "coverage_status", "sales_region", "erp_customer_number"):
                row[k] = None
            row["account_name"] = None
        row.update(_d=d, event_timestamp=kw.pop("timestamp", None) or ts(d), source_system=source, event_type=etype, event_subtype=subtype,
                   record_table=record_table, record_id=record_id)
        if rep is not None:
            row["rep_name"] = stint_name(rep) if isinstance(rep, dict) and "person" in rep else pname(rep) if isinstance(rep, dict) else rep
            row["rep_role"] = kw.pop("rep_role", None) or (ROLE_LABEL.get(rep.get("role"), rep.get("role")) if isinstance(rep, dict) and "role" in rep else None)
        if contact:
            row.update(contact_name=f"{contact['first']} {contact['last']}", contact_title=contact["title"], contact_email=contact["email"])
        if product:
            row.update(product_sku=product["sku"], product_name=product["name"], product_family=product["family"], product_category=product["category"])
        if details:
            row["details_json"] = jdump(details)
        for k, v in kw.items():
            if k in ("rep_role",):
                continue
            row[k] = v
        O.event(row)


def self_name(acc, d):
    v = acc.get("view")
    return v.crm_name(d) if v else acc["legal"]
