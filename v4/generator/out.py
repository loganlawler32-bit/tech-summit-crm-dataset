"""Output registry: relational table schemas, the unified timeline CSV, and the answer-key issue log."""
import os
from core import Table, jdump, fy, fq, ds, sfid, Counter

SCHEMA = {
    # ---------------- CRM: accounts & people
    "Account": ["Id", "Name", "Legal_Name__c", "DBA_Name__c", "Type", "ParentId", "Segment__c", "Coverage_Status__c", "Coverage_Status_As_Of__c",
                "Region__c", "Territory__c", "OwnerId", "Partner_Of_Record__c", "Industry", "Sub_Industry__c", "NAICS__c", "Ownership",
                "TickerSymbol", "NumberOfEmployees", "AnnualRevenue", "Fiscal_Year_End_Month__c", "BillingStreet", "BillingCity",
                "BillingState", "BillingPostalCode", "BillingCountry", "Phone", "Website", "ERP_Customer_Number__c", "BizGraph_Id__c",
                "Customer_Since__c", "Last_Purchase_Date__c", "Total_Spend_Last_FY__c", "Primary_Competitor__c", "Hypervisor__c",
                "Public_Cloud__c", "Contract_Pricing_Agreement__c", "Credit_Limit__c", "Payment_Terms__c", "Tax_Exempt__c",
                "AccountSource", "Description", "Source_System__c", "Legacy_Quillon_Id__c", "IsDeleted", "MasterRecordId",
                "CreatedDate", "CreatedById", "LastModifiedDate", "LastActivityDate"],
    "AccountHistory": ["Id", "AccountId", "Field", "OldValue", "NewValue", "CreatedDate", "CreatedById"],
    "AccountTeamMember": ["Id", "AccountId", "UserId", "TeamMemberRole", "Start_Date__c", "End_Date__c", "Is_Current__c", "CreatedDate"],
    "Account_Partner__c": ["Id", "Account__c", "Partner_Account__c", "Role__c", "Start_Date__c", "End_Date__c", "Is_Primary__c"],
    "Account_Firmographics__c": ["Id", "Account__c", "Fiscal_Year__c", "Source__c", "Employees__c", "Annual_Revenue__c", "Est_IT_Budget__c",
                                 "Number_Of_Sites__c", "Employee_Growth_Pct__c", "Credit_Rating__c", "As_Of_Date__c"],
    "Account_Segment_History__c": ["Id", "Account__c", "Fiscal_Year__c", "Segment__c", "Coverage_Status__c", "Region__c", "Territory__c",
                                   "Assigned_Owner__c", "Realignment_Date__c", "Notes__c"],
    "Account_Environment__c": ["Id", "Account__c", "Fiscal_Year__c", "Client_OS__c", "Hypervisor__c", "Public_Cloud__c", "ITSM_Tool__c",
                               "Backup_Approach__c", "Est_Endpoints__c", "Est_Servers__c", "Est_Storage_TB__c", "Primary_Competitor__c",
                               "Competitor_Install_Pct__c", "Strategic_Initiatives__c", "Source__c"],
    "Contact": ["Id", "AccountId", "FirstName", "LastName", "Title", "Department", "Level__c", "Email", "Phone", "MobilePhone",
                "ReportsToId", "Buying_Role__c", "Status__c", "HasOptedOutOfEmail", "Email_Bounced__c", "MailingCity", "MailingState",
                "MailingCountry", "OwnerId", "LeadSource", "Start_Date__c", "Left_Company_Date__c", "IsDeleted", "MasterRecordId",
                "CreatedDate", "LastModifiedDate", "LastActivityDate"],
    "ContactHistory": ["Id", "ContactId", "Field", "OldValue", "NewValue", "CreatedDate"],
    "Lead": ["Id", "FirstName", "LastName", "Company", "Title", "Email", "Phone", "LeadSource", "Status", "Rating", "Industry",
             "NumberOfEmployees", "City", "State", "Country", "OwnerId", "Campaign__c", "Interest__c", "IsConverted", "ConvertedDate",
             "ConvertedAccountId", "ConvertedContactId", "Matched_Account_Hint__c", "CreatedDate"],
    "User": ["Id", "EmployeeNumber", "FirstName", "LastName", "Name", "Email", "Title", "Department", "Sales_Role__c", "Region__c",
             "ManagerId", "IsActive", "Hire_Date__c", "Termination_Date__c", "Rehire_Of__c", "CreatedDate"],
    "User_Role_History__c": ["Id", "User__c", "Sales_Role__c", "Role_Title__c", "Region__c", "Start_Date__c", "End_Date__c", "Change_Reason__c"],
    # ---------------- CRM: pipeline
    "Opportunity": ["Id", "Name", "AccountId", "End_Customer_Account__c", "OwnerId", "Owner_Role__c", "Type", "Product_Group__c",
                    "StageName", "Amount", "CurrencyIsoCode", "Probability", "ForecastCategoryName", "CloseDate", "IsClosed", "IsWon",
                    "LeadSource", "CampaignId", "Partner_Account__c", "Deal_Registration__c", "Primary_Competitor__c", "Loss_Reason__c",
                    "Next_Step__c", "Push_Count__c", "Original_Close_Date__c", "Sales_Motion__c", "Fiscal_Quarter__c", "ERP_Order_Number__c",
                    "Legacy_Quillon_Opp_Id__c", "Description", "CreatedDate", "CreatedById", "LastModifiedDate"],
    "OpportunityHistory": ["Id", "OpportunityId", "StageName", "Amount", "CloseDate", "Probability", "ForecastCategory", "CreatedDate", "CreatedById"],
    "OpportunityLineItem": ["Id", "OpportunityId", "Product2Id", "ProductCode", "Name", "Quantity", "ListPrice", "UnitPrice", "Discount", "TotalPrice"],
    "OpportunityTeamMember": ["Id", "OpportunityId", "UserId", "TeamMemberRole"],
    "OpportunitySplit": ["Id", "OpportunityId", "SplitOwnerId", "SplitType", "SplitPercentage", "SplitAmount"],
    "Quote": ["Id", "QuoteNumber", "OpportunityId", "AccountId", "Version__c", "Status", "ExpirationDate", "Subtotal", "Discount", "TotalPrice",
              "CurrencyIsoCode", "Configuration_Validated__c", "Config_Error__c", "CreatedDate", "CreatedById"],
    "QuoteLineItem": ["Id", "QuoteId", "Product2Id", "ProductCode", "Quantity", "ListPrice", "UnitPrice", "Discount", "TotalPrice"],
    "Deal_Registration__c": ["Id", "Name", "Partner_Account__c", "End_Customer_Account__c", "End_Customer_Name_As_Submitted__c", "Opportunity__c",
                             "Product_Group__c", "Est_Value__c", "Submitted_Date__c", "Status__c", "Decision_Date__c", "Expiration_Date__c",
                             "Rejection_Reason__c", "Partner_Rep_Name__c"],
    "Discount_Approval__c": ["Id", "Opportunity__c", "Quote__c", "Requested_By__c", "Approver__c", "Approval_Level__c", "Requested_Discount_Pct__c",
                             "Policy_Threshold_Pct__c", "Status__c", "Justification__c", "Requested_Date__c", "Decision_Date__c"],
    "Forecast_Submission__c": ["Id", "User__c", "Fiscal_Quarter__c", "Week_Of__c", "Commit_Amount__c", "Best_Case_Amount__c", "Pipeline_Amount__c",
                               "Quota__c", "Closed_To_Date__c"],
    "Quota__c": ["Id", "User__c", "Sales_Role__c", "Fiscal_Year__c", "Fiscal_Quarter__c", "Quota_Amount__c", "Ramp_Pct__c"],
    # ---------------- CRM: activity & text
    "Task": ["Id", "WhoId", "WhatId", "AccountId", "OwnerId", "Subject", "Description", "TaskSubtype", "Type", "CallDurationInSeconds",
             "CallDisposition", "Call_Direction__c", "ActivityDate", "Status", "Priority", "Topic__c", "CreatedDate"],
    "Event": ["Id", "WhoId", "WhatId", "AccountId", "OwnerId", "Subject", "Type", "StartDateTime", "EndDateTime", "DurationInMinutes",
              "Location", "Attendees__c", "Description", "CreatedDate"],
    "Note": ["Id", "ParentId", "AccountId", "OwnerId", "Title", "Body", "Note_Type__c", "CreatedDate"],
    "FeedItem": ["Id", "ParentId", "CreatedById", "Body", "Type", "CreatedDate"],
    "Case": ["Id", "CaseNumber", "AccountId", "ContactId", "AssetId", "Asset_Serial__c", "Product__c", "OwnerId", "Subject", "Description",
             "Category__c", "Priority", "Severity__c", "Origin", "Status", "IsEscalated", "Dispatch_Type__c", "Parts_Dispatched__c",
             "SLA_Hours__c", "Resolution_Hours__c", "SLA_Met__c", "CreatedDate", "ClosedDate"],
    "CaseComment": ["Id", "ParentId", "CommentBody", "IsPublished", "CreatedById", "Author_Type__c", "CreatedDate"],
    "Survey_Response__c": ["Id", "Account__c", "Contact__c", "Case__c", "Survey_Type__c", "NPS_Score__c", "CSAT_Score__c", "Verbatim__c", "Response_Date__c"],
    "Campaign": ["Id", "Name", "Type", "Status", "StartDate", "EndDate", "Region__c", "BudgetedCost", "ActualCost", "Description"],
    "CampaignMember": ["Id", "CampaignId", "ContactId", "LeadId", "Status", "HasResponded", "Session_Interest__c", "CreatedDate"],
    "Web_Intent_Signal__c": ["Id", "Account__c", "Week_Of__c", "Topic__c", "Intent_Score__c", "Page_Views__c", "Content_Downloads__c", "Source__c"],
    "News_Item__c": ["Id", "Account__c", "Company_Name_In_Article__c", "Published_Date__c", "News_Type__c", "Headline__c", "Summary__c", "Source__c", "URL__c"],
    # ---------------- ERP / finance
    "ERP_Customer": ["Customer_Number", "Customer_Name", "Customer_Type", "Parent_Customer_Number", "Bill_To_Address", "City", "State_Province",
                     "Postal_Code", "Country_Code", "Currency", "Payment_Terms", "Credit_Limit", "Tax_Exempt", "Tax_Cert_Expiration",
                     "Status", "Source_System", "Created_Date"],
    "ERP_Ship_To": ["Ship_To_Number", "Customer_Number", "Site_Type", "Address", "City", "State_Province", "Postal_Code", "Country_Code", "Active", "Created_Date"],
    "CRM_ERP_Crosswalk": ["CRM_Account_Id", "ERP_Customer_Number", "Match_Method", "Match_Confidence", "Last_Verified_Date"],
    "Sales_Order": ["Order_Number", "Source_System", "Order_Date", "Booked_Date", "Customer_Number", "Bill_To_Customer_Number", "Ship_To_Number",
                    "End_User_Account_Id", "End_User_Name", "Channel", "Partner_Customer_Number", "Sales_Rep_Code", "Sales_Rep_Name",
                    "CRM_Opportunity_Id", "Quote_Number", "PO_Number", "PO_Received_Date", "PO_Amount", "Blanket_PO", "Payment_Method",
                    "Payment_Terms", "Currency", "FX_Rate_To_USD", "Subtotal", "Discount_Amount", "Tax_Amount", "Order_Total", "Order_Total_USD",
                    "Contract_Pricing_Agreement", "Status", "Hold_Reason", "Hold_Start", "Hold_Released", "Cancel_Reason", "Notes"],
    "Sales_Order_Line": ["Order_Number", "Line_Number", "SKU", "Legacy_Item_Code", "Item_Description", "Product_Category", "Quantity",
                         "List_Price", "Unit_Price", "Discount_Pct", "Extended_Price", "Unit_Cost", "Extended_Cost", "Gross_Margin",
                         "Line_Status", "Requested_Date", "Promised_Date", "Ship_Date", "Warranty_SKU", "Is_Recurring", "Term_Months"],
    "Shipment": ["Shipment_Number", "Order_Number", "Ship_To_Number", "Carrier", "Tracking_Number", "Ship_Date", "Delivered_Date",
                 "Promised_Date", "Status", "Exception", "Units", "Lines"],
    "Invoice": ["Invoice_Number", "Order_Number", "Customer_Number", "Bill_To_Customer_Number", "Invoice_Date", "Due_Date", "Currency",
                "Subtotal", "Tax_Type", "Tax_Amount", "Invoice_Total", "Invoice_Total_USD", "Amount_Paid", "Balance", "Status",
                "Days_To_Pay", "Dispute_Reason", "Dunning_Level", "Written_Off"],
    "Payment": ["Payment_Number", "Customer_Number", "Invoice_Number", "Payment_Date", "Amount", "Currency", "Method", "Reference",
                "Applied_Status", "Remitter_Name", "Notes"],
    "Credit_Memo": ["Credit_Memo_Number", "Customer_Number", "Invoice_Number", "Order_Number", "RMA_Number", "Memo_Date", "Reason", "Amount", "Currency", "Status"],
    "RMA": ["RMA_Number", "Order_Number", "SKU", "Quantity", "Reason", "Request_Date", "Received_Date", "Disposition", "Serials"],
    "Credit_Hold_Event": ["Hold_Id", "Customer_Number", "Order_Number", "Hold_Type", "Hold_Date", "Release_Date", "Released_By", "Open_AR_At_Hold", "Credit_Limit_At_Hold", "Notes"],
    "Contract_Pricing_Agreement": ["Agreement_Number", "Customer_Number", "CRM_Account_Id", "Agreement_Name", "Start_Date", "End_Date",
                                   "Category", "Discount_Pct", "Applies_To_Subsidiaries", "Status", "Signed_By"],
    "Lease_Contract": ["Lease_Number", "Customer_Number", "CRM_Account_Id", "Order_Number", "Lease_Type", "Start_Date", "End_Date",
                       "Term_Months", "Monthly_Payment", "Financed_Amount", "Units", "End_Of_Term_Option", "Status"],
    "Flex_Usage_Monthly": ["Contract_Number", "Customer_Number", "CRM_Account_Id", "Service", "Month", "Committed_Units", "Used_Units",
                           "Overage_Units", "Committed_Charge", "Overage_Charge", "Invoice_Number"],
    "Legacy_Order_Summary": ["Customer_Number", "Source_System", "Fiscal_Year", "Product_Category", "Order_Count", "Revenue_USD", "Last_Order_Date"],
    "Consumer_Order": ["Consumer_Order_Number", "Order_Date", "Customer_Name", "Email", "Ship_Address", "City", "State_Province",
                       "Postal_Code", "SKU", "Item_Description", "Quantity", "Unit_Price", "Order_Total", "Payment_Method",
                       "Program", "Linked_Account_Id", "Employer_Text"],
    # ---------------- install base / telemetry
    "Asset": ["Id", "Name", "AccountId", "Product2Id", "SKU", "SerialNumber", "Serial_Range_End__c", "Quantity", "Order_Number__c",
              "Ship_To_Site__c", "Site_City__c", "InstallDate", "Status", "Usage_End_Date__c", "Configuration__c", "Firmware_Version__c",
              "Firmware_Updated__c", "Warranty_SKU__c", "Warranty_End_Date__c", "End_Of_Support_Date__c", "Source__c"],
    "ServiceContract": ["Id", "Name", "AccountId", "AssetId", "SKU", "Tier__c", "StartDate", "EndDate", "Term_Months__c", "Status", "Order_Number__c", "Auto_Renew__c"],
    "Asset_Telemetry_Monthly__c": ["Id", "Asset__c", "Account__c", "Month__c", "Capacity_TB__c", "Used_TB__c", "Used_Pct__c", "Growth_TB_Per_Month__c",
                                   "Health_Alerts__c", "Predictive_Failures__c", "Firmware_Version__c", "Phone_Home__c"],
    "Security_Advisory__c": ["Id", "Advisory_Number__c", "Title__c", "Severity__c", "CVSS__c", "Published_Date__c", "Affected_Products__c",
                             "Fixed_Firmware__c", "Description__c"],
    "Advisory_Exposure__c": ["Id", "Advisory__c", "Asset__c", "Account__c", "Firmware_At_Publish__c", "Status__c", "Remediated_Date__c", "Notified_Date__c"],
    "Product2": ["Id", "ProductCode", "Name", "Family", "Product_Line__c", "Business_Unit__c", "Category__c", "Generation__c",
                 "List_Price__c", "Standard_Cost_Pct__c", "Launch_Date__c", "End_Of_Life_Date__c", "IsActive", "QuantityUnitOfMeasure",
                 "Is_Recurring__c", "Term_Months__c", "Serialized__c", "Specs__c"],
    "Price_History": ["SKU", "Effective_Date", "List_Price", "Change_Reason"],
}

TL_FIELDS = ["event_id", "event_timestamp", "event_date", "fiscal_year", "fiscal_quarter", "source_system", "event_type", "event_subtype",
             "account_id", "account_name", "erp_customer_number", "parent_account_id", "parent_account_name", "ultimate_parent_name",
             "segment", "coverage_status", "sales_region", "industry", "employees", "annual_revenue", "account_owner", "rep_name",
             "rep_role", "partner_name", "contact_name", "contact_title", "contact_email", "opportunity_id", "quote_number",
             "order_number", "invoice_number", "case_number", "asset_serial", "product_sku", "product_name", "product_family",
             "product_category", "quantity", "list_price", "unit_price", "discount_pct", "amount", "currency", "amount_usd",
             "po_number", "payment_method", "status", "stage", "channel", "subject", "text", "details_json", "record_table", "record_id"]
ISSUE_FIELDS = ["issue_id", "issue_type", "severity", "table", "record_id", "field", "recorded_value", "correct_value", "account_id",
                "detected_by_hint", "description"]


class Out:
    def __init__(self, root):
        self.root = root
        self.load = os.path.join(root, "aible_load")
        self.tdir = os.path.join(self.load, "tables")
        self.kdir = os.path.join(root, "answer_key")
        self.t = {n: Table(self.tdir, n, f) for n, f in SCHEMA.items()}
        self.tl = Table(self.load, "orvane_unified_timeline", TL_FIELDS)
        self.iss = Table(self.kdir, "planted_issues", ISSUE_FIELDS)
        self.ic = Counter()
        self._ev = 0

    def add(self, name, row):
        self.t[name].add(row)

    def issue(self, itype, table, rid, field, bad, good, acct, hint, desc, sev="Medium"):
        self.ic[itype] += 1
        self.iss.add(dict(issue_id=f"ISS-{sum(self.ic.values()):07d}", issue_type=itype, severity=sev, table=table, record_id=rid,
                          field=field, recorded_value=bad, correct_value=good, account_id=acct, detected_by_hint=hint, description=desc))

    def event(self, row):
        self._ev += 1
        row["event_id"] = f"EV{self._ev:09d}"
        d = row.get("_d")
        if d:
            row["event_date"] = ds(d)
            row["fiscal_year"] = f"FY{fy(d)}"
            row["fiscal_quarter"] = f"FY{fy(d)} Q{fq(d)}"
        self.tl.add(row)

    def close(self):
        for t in self.t.values():
            t.close()
        self.tl.close()
        self.iss.close()

    def counts(self):
        c = {n: t.n for n, t in self.t.items()}
        c["orvane_unified_timeline"] = self.tl.n
        return c
