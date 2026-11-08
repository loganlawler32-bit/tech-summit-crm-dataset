# Data dictionary

## `orvane_unified_timeline.csv` (the single CSV)

| Column | Meaning |
|---|---|
| `event_id` | Unique event id |
| `event_timestamp` | UTC timestamp |
| `event_date` | Date |
| `fiscal_year` | Orvane FY (Feb-Jan) |
| `fiscal_quarter` | Orvane fiscal quarter |
| `source_system` | CRM / ERP / Support / Telemetry / Product Security / Marketing / Survey / News / Consumer Store |
| `event_type` | Kind of event |
| `event_subtype` | Detail (disposition, status, category...) |
| `account_id` | CRM account (blank when the source system could not attribute it) |
| `account_name` | Name as recorded in that system at that time |
| `erp_customer_number` | Primary ERP customer number |
| `parent_account_id` | Parent as linked in CRM at the time (blank if not linked) |
| `parent_account_name` |  |
| `ultimate_parent_name` |  |
| `segment` | Segment as recorded for that fiscal year |
| `coverage_status` | Retention/Development/Acquisition as recorded at that FY's realignment |
| `sales_region` | Region label as recorded (old labels before FY24) |
| `industry` | Industry picklist value as recorded |
| `employees` | 3rd-party employee count for that FY |
| `annual_revenue` | 3rd-party revenue for that FY |
| `account_owner` | Who owned the account on that date (or vacancy label) |
| `rep_name` | Orvane person who did/owned the event |
| `rep_role` | Their role on the account |
| `partner_name` | Channel partner involved |
| `contact_name` | Customer person |
| `contact_title` |  |
| `contact_email` |  |
| `opportunity_id` |  |
| `quote_number` |  |
| `order_number` |  |
| `invoice_number` |  |
| `case_number` |  |
| `asset_serial` |  |
| `product_sku` |  |
| `product_name` |  |
| `product_family` |  |
| `product_category` |  |
| `quantity` |  |
| `list_price` |  |
| `unit_price` | Net price |
| `discount_pct` |  |
| `amount` | Amount in record currency |
| `currency` | USD or CAD |
| `amount_usd` |  |
| `po_number` | As typed (messy) |
| `payment_method` |  |
| `status` |  |
| `stage` |  |
| `channel` | Direct - Field / Direct - Inside / Online Store / Premier Portal / Partner |
| `subject` |  |
| `text` | Free text: notes, call summaries, email bodies, case comments, verbatims, news |
| `details_json` | Event-specific extra fields (JSON) |
| `record_table` | Source table in tables/ |
| `record_id` | Source record id |

## Relational tables (`tables/`)

### `Account` - 21,130 rows
Customer, prospect, partner and duplicate account records exactly as they sit in Salesforce at 2026-01-31 (stale segment/status fields, broken parent links, duplicate records, inconsistent formats).

Columns: `Id`, `Name`, `Legal_Name__c`, `DBA_Name__c`, `Type`, `ParentId`, `Segment__c`, `Coverage_Status__c`, `Coverage_Status_As_Of__c`, `Region__c`, `Territory__c`, `OwnerId`, `Partner_Of_Record__c`, `Industry`, `Sub_Industry__c`, `NAICS__c`, `Ownership`, `TickerSymbol`, `NumberOfEmployees`, `AnnualRevenue`, `Fiscal_Year_End_Month__c`, `BillingStreet`, `BillingCity`, `BillingState`, `BillingPostalCode`, `BillingCountry`, `Phone`, `Website`, `ERP_Customer_Number__c`, `BizGraph_Id__c`, `Customer_Since__c`, `Last_Purchase_Date__c`, `Total_Spend_Last_FY__c`, `Primary_Competitor__c`, `Hypervisor__c`, `Public_Cloud__c`, `Contract_Pricing_Agreement__c`, `Credit_Limit__c`, `Payment_Terms__c`, `Tax_Exempt__c`, `AccountSource`, `Description`, `Source_System__c`, `Legacy_Quillon_Id__c`, `IsDeleted`, `MasterRecordId`, `CreatedDate`, `CreatedById`, `LastModifiedDate`, `LastActivityDate`

### `AccountHistory` - 89,443 rows
Field-change history: owner, segment, coverage status, region, name, parent, partner of record.

Columns: `Id`, `AccountId`, `Field`, `OldValue`, `NewValue`, `CreatedDate`, `CreatedById`

### `AccountTeamMember` - 415,117 rows
Every Orvane person who covered the account and when (owner, inside AE, specialists, SA, TAM, RAM, SDM) with start/end dates.

Columns: `Id`, `AccountId`, `UserId`, `TeamMemberRole`, `Start_Date__c`, `End_Date__c`, `Is_Current__c`, `CreatedDate`

### `Account_Partner__c` - 5,721 rows
Channel partner of record over time.

Columns: `Id`, `Account__c`, `Partner_Account__c`, `Role__c`, `Start_Date__c`, `End_Date__c`, `Is_Primary__c`

### `Account_Firmographics__c` - 118,129 rows
Yearly employees / revenue / IT budget / sites from a 3rd-party provider (lagged, sometimes stale) plus occasional rep-entered values that disagree.

Columns: `Id`, `Account__c`, `Fiscal_Year__c`, `Source__c`, `Employees__c`, `Annual_Revenue__c`, `Est_IT_Budget__c`, `Number_Of_Sites__c`, `Employee_Growth_Pct__c`, `Credit_Rating__c`, `As_Of_Date__c`

### `Account_Segment_History__c` - 100,000 rows
Segment, coverage status (Retention/Development/Acquisition), region, territory and assigned owner at each February realignment.

Columns: `Id`, `Account__c`, `Fiscal_Year__c`, `Segment__c`, `Coverage_Status__c`, `Region__c`, `Territory__c`, `Assigned_Owner__c`, `Realignment_Date__c`, `Notes__c`

### `Account_Environment__c` - 100,000 rows
Yearly technology environment: client OS / Windows 11 progress, hypervisor, cloud, ITSM, backup approach, estimated endpoints/servers/storage, competitor footprint, strategic initiatives.

Columns: `Id`, `Account__c`, `Fiscal_Year__c`, `Client_OS__c`, `Hypervisor__c`, `Public_Cloud__c`, `ITSM_Tool__c`, `Backup_Approach__c`, `Est_Endpoints__c`, `Est_Servers__c`, `Est_Storage_TB__c`, `Primary_Competitor__c`, `Competitor_Install_Pct__c`, `Strategic_Initiatives__c`, `Source__c`

### `Contact` - 433,440 rows
Customer people incl. shared mailboxes (AP, purchasing, help desk); leavers often still marked Active; duplicates; reports-to chains; buying roles.

Columns: `Id`, `AccountId`, `FirstName`, `LastName`, `Title`, `Department`, `Level__c`, `Email`, `Phone`, `MobilePhone`, `ReportsToId`, `Buying_Role__c`, `Status__c`, `HasOptedOutOfEmail`, `Email_Bounced__c`, `MailingCity`, `MailingState`, `MailingCountry`, `OwnerId`, `LeadSource`, `Start_Date__c`, `Left_Company_Date__c`, `IsDeleted`, `MasterRecordId`, `CreatedDate`, `LastModifiedDate`, `LastActivityDate`

### `ContactHistory` - 6,275 rows
Recorded title changes (many promotions were never recorded).

Columns: `Id`, `ContactId`, `Field`, `OldValue`, `NewValue`, `CreatedDate`

### `Lead` - 28,648 rows
Inbound/marketing leads; many duplicate existing contacts or use inconsistent company names.

Columns: `Id`, `FirstName`, `LastName`, `Company`, `Title`, `Email`, `Phone`, `LeadSource`, `Status`, `Rating`, `Industry`, `NumberOfEmployees`, `City`, `State`, `Country`, `OwnerId`, `Campaign__c`, `Interest__c`, `IsConverted`, `ConvertedDate`, `ConvertedAccountId`, `ConvertedContactId`, `Matched_Account_Hint__c`, `CreatedDate`

### `User` - 4,460 rows
Orvane employees (sales, specialists, support, finance, marketing) with hire/termination dates; boomerang rehires create second user records.

Columns: `Id`, `EmployeeNumber`, `FirstName`, `LastName`, `Name`, `Email`, `Title`, `Department`, `Sales_Role__c`, `Region__c`, `ManagerId`, `IsActive`, `Hire_Date__c`, `Termination_Date__c`, `Rehire_Of__c`, `CreatedDate`

### `User_Role_History__c` - 4,684 rows
Every role/region stint per person: promotions (SB -> MB -> LE -> Select), FY24 restructure moves, terminations.

Columns: `Id`, `User__c`, `Sales_Role__c`, `Role_Title__c`, `Region__c`, `Start_Date__c`, `End_Date__c`, `Change_Reason__c`

### `Opportunity` - 2,249,670 rows
Won, lost, open and stale deals; owners vary by product group (AE vs specialist); legacy stage values from before FY24; pushes and original close dates.

Columns: `Id`, `Name`, `AccountId`, `End_Customer_Account__c`, `OwnerId`, `Owner_Role__c`, `Type`, `Product_Group__c`, `StageName`, `Amount`, `CurrencyIsoCode`, `Probability`, `ForecastCategoryName`, `CloseDate`, `IsClosed`, `IsWon`, `LeadSource`, `CampaignId`, `Partner_Account__c`, `Deal_Registration__c`, `Primary_Competitor__c`, `Loss_Reason__c`, `Next_Step__c`, `Push_Count__c`, `Original_Close_Date__c`, `Sales_Motion__c`, `Fiscal_Quarter__c`, `ERP_Order_Number__c`, `Legacy_Quillon_Opp_Id__c`, `Description`, `CreatedDate`, `CreatedById`, `LastModifiedDate`

### `OpportunityHistory` - 12,212,329 rows
Stage/amount/close-date progression for each opportunity.

Columns: `Id`, `OpportunityId`, `StageName`, `Amount`, `CloseDate`, `Probability`, `ForecastCategory`, `CreatedDate`, `CreatedById`

### `OpportunityLineItem` - 7,396,572 rows
Products on each opportunity.

Columns: `Id`, `OpportunityId`, `Product2Id`, `ProductCode`, `Name`, `Quantity`, `ListPrice`, `UnitPrice`, `Discount`, `TotalPrice`

### `OpportunityTeamMember` - 6,373,417 rows
Who worked each deal (owner, account owner, SA, inside AE, TAM, partner manager).

Columns: `Id`, `OpportunityId`, `UserId`, `TeamMemberRole`

### `OpportunitySplit` - 3,609,471 rows
Revenue and overlay credit splits (some over-allocated).

Columns: `Id`, `OpportunityId`, `SplitOwnerId`, `SplitType`, `SplitPercentage`, `SplitAmount`

### `Quote` - 4,658,018 rows
Quote versions per opportunity (discount tightening over versions, configuration errors).

Columns: `Id`, `QuoteNumber`, `OpportunityId`, `AccountId`, `Version__c`, `Status`, `ExpirationDate`, `Subtotal`, `Discount`, `TotalPrice`, `CurrencyIsoCode`, `Configuration_Validated__c`, `Config_Error__c`, `CreatedDate`, `CreatedById`

### `QuoteLineItem` - 5,818,115 rows
Lines on the final quote.

Columns: `Id`, `QuoteId`, `Product2Id`, `ProductCode`, `Quantity`, `ListPrice`, `UnitPrice`, `Discount`, `TotalPrice`

### `Deal_Registration__c` - 150,723 rows
Partner deal registrations, approvals/rejections and conflicting registrations.

Columns: `Id`, `Name`, `Partner_Account__c`, `End_Customer_Account__c`, `End_Customer_Name_As_Submitted__c`, `Opportunity__c`, `Product_Group__c`, `Est_Value__c`, `Submitted_Date__c`, `Status__c`, `Decision_Date__c`, `Expiration_Date__c`, `Rejection_Reason__c`, `Partner_Rep_Name__c`

### `Discount_Approval__c` - 630,422 rows
Discount approvals vs policy threshold (policy tightened in FY25); missing approvals are planted issues.

Columns: `Id`, `Opportunity__c`, `Quote__c`, `Requested_By__c`, `Approver__c`, `Approval_Level__c`, `Requested_Discount_Pct__c`, `Policy_Threshold_Pct__c`, `Status__c`, `Justification__c`, `Requested_Date__c`, `Decision_Date__c`

### `Forecast_Submission__c` - 430,053 rows
Weekly commit/best-case/pipeline calls per rep per quarter (sandbaggers and happy-ears visible vs actuals).

Columns: `Id`, `User__c`, `Fiscal_Quarter__c`, `Week_Of__c`, `Commit_Amount__c`, `Best_Case_Amount__c`, `Pipeline_Amount__c`, `Quota__c`, `Closed_To_Date__c`

### `Quota__c` - 33,081 rows
Quarterly quota per quota-carrying rep with new-hire ramp.

Columns: `Id`, `User__c`, `Sales_Role__c`, `Fiscal_Year__c`, `Fiscal_Quarter__c`, `Quota_Amount__c`, `Ramp_Pct__c`

### `Task` - 4,718,653 rows
Calls (duration, disposition, direction) and emails (subject + body) written in each rep's own style; topics follow what is actually happening on the account.

Columns: `Id`, `WhoId`, `WhatId`, `AccountId`, `OwnerId`, `Subject`, `Description`, `TaskSubtype`, `Type`, `CallDurationInSeconds`, `CallDisposition`, `Call_Direction__c`, `ActivityDate`, `Status`, `Priority`, `Topic__c`, `CreatedDate`

### `Event` - 601,597 rows
Meetings (discovery, demos, deep dives, architecture workshops, QBRs, exec briefings, negotiations) with attendees and meeting notes.

Columns: `Id`, `WhoId`, `WhatId`, `AccountId`, `OwnerId`, `Subject`, `Type`, `StartDateTime`, `EndDateTime`, `DurationInMinutes`, `Location`, `Attendees__c`, `Description`, `CreatedDate`

### `Note` - 95,836 rows
Long-form notes: annual account plans, win reviews, hand-written showcase account notes.

Columns: `Id`, `ParentId`, `AccountId`, `OwnerId`, `Title`, `Body`, `Note_Type__c`, `CreatedDate`

### `FeedItem` - 280,602 rows
Internal chatter posts about accounts (handoffs, champion changes, escalations, partner conflicts).

Columns: `Id`, `ParentId`, `CreatedById`, `Body`, `Type`, `CreatedDate`

### `Case` - 930,285 rows
Support cases tied to installed assets: priority, SLA, dispatch, escalation, resolution time.

Columns: `Id`, `CaseNumber`, `AccountId`, `ContactId`, `AssetId`, `Asset_Serial__c`, `Product__c`, `OwnerId`, `Subject`, `Description`, `Category__c`, `Priority`, `Severity__c`, `Origin`, `Status`, `IsEscalated`, `Dispatch_Type__c`, `Parts_Dispatched__c`, `SLA_Hours__c`, `Resolution_Hours__c`, `SLA_Met__c`, `CreatedDate`, `ClosedDate`

### `CaseComment` - 1,797,793 rows
Support engineer / customer case comments with log snippets and part numbers.

Columns: `Id`, `ParentId`, `CommentBody`, `IsPublished`, `CreatedById`, `Author_Type__c`, `CreatedDate`

### `Survey_Response__c` - 279,177 rows
Post-case NPS/CSAT with verbatims.

Columns: `Id`, `Account__c`, `Contact__c`, `Case__c`, `Survey_Type__c`, `NPS_Score__c`, `CSAT_Score__c`, `Verbatim__c`, `Response_Date__c`

### `Campaign` - 71 rows
Orvane Tech Summit (5 years), regional roadshows, webinars, Select Executive Forum, Windows 10 end-of-support program.

Columns: `Id`, `Name`, `Type`, `Status`, `StartDate`, `EndDate`, `Region__c`, `BudgetedCost`, `ActualCost`, `Description`

### `CampaignMember` - 85,375 rows
Contact invitations/attendance with session interests.

Columns: `Id`, `CampaignId`, `ContactId`, `LeadId`, `Status`, `HasResponded`, `Session_Interest__c`, `CreatedDate`

### `Web_Intent_Signal__c` - 384,109 rows
Monthly web/3rd-party intent by topic (leading indicator before purchases).

Columns: `Id`, `Account__c`, `Week_Of__c`, `Topic__c`, `Intent_Score__c`, `Page_Views__c`, `Content_Downloads__c`, `Source__c`

### `News_Item__c` - 23,122 rows
News about customer companies (funding, layoffs, acquisitions, exec hires, HQ moves, rebrands, cyber incidents, bankruptcies).

Columns: `Id`, `Account__c`, `Company_Name_In_Article__c`, `Published_Date__c`, `News_Type__c`, `Headline__c`, `Summary__c`, `Source__c`, `URL__c`

### `ERP_Customer` - 20,643 rows
ERP customer master (sold-to numbers; duplicates; Quillon legacy customers; names that differ from CRM).

Columns: `Customer_Number`, `Customer_Name`, `Customer_Type`, `Parent_Customer_Number`, `Bill_To_Address`, `City`, `State_Province`, `Postal_Code`, `Country_Code`, `Currency`, `Payment_Terms`, `Credit_Limit`, `Tax_Exempt`, `Tax_Cert_Expiration`, `Status`, `Source_System`, `Created_Date`

### `ERP_Ship_To` - 91,647 rows
Ship-to sites per customer (incl. stale HQ after relocations).

Columns: `Ship_To_Number`, `Customer_Number`, `Site_Type`, `Address`, `City`, `State_Province`, `Postal_Code`, `Country_Code`, `Active`, `Created_Date`

### `CRM_ERP_Crosswalk` - 16,718 rows
Mapping between CRM accounts and ERP customer numbers - incomplete and partly wrong on purpose.

Columns: `CRM_Account_Id`, `ERP_Customer_Number`, `Match_Method`, `Match_Confidence`, `Last_Verified_Date`

### `Sales_Order` - 1,629,406 rows
Every order: channel (field/inside/online/portal/partner), PO numbers (messy), holds (missing PO, credit), payment method, currency, contract pricing applied or not.

Columns: `Order_Number`, `Source_System`, `Order_Date`, `Booked_Date`, `Customer_Number`, `Bill_To_Customer_Number`, `Ship_To_Number`, `End_User_Account_Id`, `End_User_Name`, `Channel`, `Partner_Customer_Number`, `Sales_Rep_Code`, `Sales_Rep_Name`, `CRM_Opportunity_Id`, `Quote_Number`, `PO_Number`, `PO_Received_Date`, `PO_Amount`, `Blanket_PO`, `Payment_Method`, `Payment_Terms`, `Currency`, `FX_Rate_To_USD`, `Subtotal`, `Discount_Amount`, `Tax_Amount`, `Order_Total`, `Order_Total_USD`, `Contract_Pricing_Agreement`, `Status`, `Hold_Reason`, `Hold_Start`, `Hold_Released`, `Cancel_Reason`, `Notes`

### `Sales_Order_Line` - 5,090,926 rows
Order lines with list, net price, discount, cost and margin, promised vs ship dates.

Columns: `Order_Number`, `Line_Number`, `SKU`, `Legacy_Item_Code`, `Item_Description`, `Product_Category`, `Quantity`, `List_Price`, `Unit_Price`, `Discount_Pct`, `Extended_Price`, `Unit_Cost`, `Extended_Cost`, `Gross_Margin`, `Line_Status`, `Requested_Date`, `Promised_Date`, `Ship_Date`, `Warranty_SKU`, `Is_Recurring`, `Term_Months`

### `Shipment` - 1,579,043 rows
Shipments with carriers, delays, damage, address exceptions, backorders after the snapshot.

Columns: `Shipment_Number`, `Order_Number`, `Ship_To_Number`, `Carrier`, `Tracking_Number`, `Ship_Date`, `Delivered_Date`, `Promised_Date`, `Status`, `Exception`, `Units`, `Lines`

### `Invoice` - 3,010,309 rows
Invoices with tax, balances, past-due/disputed/written-off status, dunning level, days to pay.

Columns: `Invoice_Number`, `Order_Number`, `Customer_Number`, `Bill_To_Customer_Number`, `Invoice_Date`, `Due_Date`, `Currency`, `Subtotal`, `Tax_Type`, `Tax_Amount`, `Invoice_Total`, `Invoice_Total_USD`, `Amount_Paid`, `Balance`, `Status`, `Days_To_Pay`, `Dispute_Reason`, `Dunning_Level`, `Written_Off`

### `Payment` - 3,047,901 rows
Payments: ACH, wire, check, card, partner remittance, lease funding; short-pays and unapplied cash.

Columns: `Payment_Number`, `Customer_Number`, `Invoice_Number`, `Payment_Date`, `Amount`, `Currency`, `Method`, `Reference`, `Applied_Status`, `Remitter_Name`, `Notes`

### `Credit_Memo` - 47,350 rows
Returns and price-adjustment credits.

Columns: `Credit_Memo_Number`, `Customer_Number`, `Invoice_Number`, `Order_Number`, `RMA_Number`, `Memo_Date`, `Reason`, `Amount`, `Currency`, `Status`

### `RMA` - 38,312 rows
Return authorizations with reasons and disposition.

Columns: `RMA_Number`, `Order_Number`, `SKU`, `Quantity`, `Reason`, `Request_Date`, `Received_Date`, `Disposition`, `Serials`

### `Credit_Hold_Event` - 103,087 rows
Credit holds with open AR at hold and release info.

Columns: `Hold_Id`, `Customer_Number`, `Order_Number`, `Hold_Type`, `Hold_Date`, `Release_Date`, `Released_By`, `Open_AR_At_Hold`, `Credit_Limit_At_Hold`, `Notes`

### `Contract_Pricing_Agreement` - 4,400 rows
Parent-level master agreements by category (should apply to subsidiaries - often doesn't).

Columns: `Agreement_Number`, `Customer_Number`, `CRM_Account_Id`, `Agreement_Name`, `Start_Date`, `End_Date`, `Category`, `Discount_Pct`, `Applies_To_Subsidiaries`, `Status`, `Signed_By`

### `Lease_Contract` - 52,274 rows
Orvane Financial Services leases with term end dates and end-of-term options.

Columns: `Lease_Number`, `Customer_Number`, `CRM_Account_Id`, `Order_Number`, `Lease_Type`, `Start_Date`, `End_Date`, `Term_Months`, `Monthly_Payment`, `Financed_Amount`, `Units`, `End_Of_Term_Option`, `Status`

### `Flex_Usage_Monthly` - 51,644 rows
Pay-per-use (Orvane Flex) and Device-as-a-Service monthly committed vs used vs overage.

Columns: `Contract_Number`, `Customer_Number`, `CRM_Account_Id`, `Service`, `Month`, `Committed_Units`, `Used_Units`, `Overage_Units`, `Committed_Charge`, `Overage_Charge`, `Invoice_Number`

### `Legacy_Order_Summary` - 395,615 rows
Pre-Salesforce order history FY17-FY21 by category (Orvane legacy ERP and Quillon ERP).

Columns: `Customer_Number`, `Source_System`, `Fiscal_Year`, `Product_Category`, `Order_Count`, `Revenue_USD`, `Last_Order_Date`

### `Consumer_Order` - 24,546 rows
Consumer web store and employee purchase program orders by people tied to business accounts (mostly not linked).

Columns: `Consumer_Order_Number`, `Order_Date`, `Customer_Name`, `Email`, `Ship_Address`, `City`, `State_Province`, `Postal_Code`, `SKU`, `Item_Description`, `Quantity`, `Unit_Price`, `Order_Total`, `Payment_Method`, `Program`, `Linked_Account_Id`, `Employer_Text`

### `Asset` - 5,174,842 rows
Installed base: serialized infrastructure (one row per system) and client device lots (serial ranges), install site, status, firmware, warranty end, end of support.

Columns: `Id`, `Name`, `AccountId`, `Product2Id`, `SKU`, `SerialNumber`, `Serial_Range_End__c`, `Quantity`, `Order_Number__c`, `Ship_To_Site__c`, `Site_City__c`, `InstallDate`, `Status`, `Usage_End_Date__c`, `Configuration__c`, `Firmware_Version__c`, `Firmware_Updated__c`, `Warranty_SKU__c`, `Warranty_End_Date__c`, `End_Of_Support_Date__c`, `Source__c`

### `ServiceContract` - 4,953,779 rows
Warranty / ProCare contracts per asset with start/end and status.

Columns: `Id`, `Name`, `AccountId`, `AssetId`, `SKU`, `Tier__c`, `StartDate`, `EndDate`, `Term_Months__c`, `Status`, `Order_Number__c`, `Auto_Renew__c`

### `Asset_Telemetry_Monthly__c` - 3,056,793 rows
Monthly phone-home telemetry for storage/backup/HCI arrays: capacity, used %, growth, alerts, firmware.

Columns: `Id`, `Asset__c`, `Account__c`, `Month__c`, `Capacity_TB__c`, `Used_TB__c`, `Used_Pct__c`, `Growth_TB_Per_Month__c`, `Health_Alerts__c`, `Predictive_Failures__c`, `Firmware_Version__c`, `Phone_Home__c`

### `Security_Advisory__c` - 10 rows
Product security advisories (BMC, firmware, storage OS).

Columns: `Id`, `Advisory_Number__c`, `Title__c`, `Severity__c`, `CVSS__c`, `Published_Date__c`, `Affected_Products__c`, `Fixed_Firmware__c`, `Description__c`

### `Advisory_Exposure__c` - 3,792,565 rows
Which installed systems were exposed to which advisory, and whether they were remediated.

Columns: `Id`, `Advisory__c`, `Asset__c`, `Account__c`, `Firmware_At_Publish__c`, `Status__c`, `Remediated_Date__c`, `Notified_Date__c`

### `Product2` - 500 rows
500 Orvane SKUs: generations, launch/end-of-life, list price, cost %, specs.

Columns: `Id`, `ProductCode`, `Name`, `Family`, `Product_Line__c`, `Business_Unit__c`, `Category__c`, `Generation__c`, `List_Price__c`, `Standard_Cost_Pct__c`, `Launch_Date__c`, `End_Of_Life_Date__c`, `IsActive`, `QuantityUnitOfMeasure`, `Is_Recurring__c`, `Term_Months__c`, `Serialized__c`, `Specs__c`

### `Price_History` - 2,009 rows
List price changes over time (shortage increases, PC-slump cuts, prior-generation markdowns).

Columns: `SKU`, `Effective_Date`, `List_Price`, `Change_Reason`
