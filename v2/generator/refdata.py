"""Reference data: people names, North American geography, industries, partners, competitors."""

FIRST = ("James Mary Michael Jennifer David Linda Robert Patricia John Elizabeth William Susan Richard Jessica Thomas Sarah "
         "Christopher Karen Daniel Lisa Matthew Nancy Anthony Emily Mark Ashley Andrew Michelle Joshua Amanda Kevin Melissa "
         "Brian Rebecca Ryan Laura Jason Rachel Justin Megan Brandon Lauren Eric Hannah Tyler Olivia Scott Emma Gregory "
         "Chloe Benjamin Grace Samuel Natalie Patrick Kayla Nathan Abigail Taylor Jordan Morgan Casey Alex Jamie Avery Riley "
         "Quinn Cameron Dylan Ethan Madison Caleb Sophie Owen Claire Lucas Allison Connor Erin Heather Adam Kristen Sean "
         "Victoria Derek Brooke Travis Courtney Chad Lindsey Marcus Tiffany Jared Monica Shane Vanessa Trevor Danielle Cody "
         "Alicia Garrett Kelsey Wesley Brittany Dustin Jenna Colin Paige Brett Kendra Spencer Molly Darren Leah Grant Tara "
         "Mitchell Holly Cole Shannon Bryce Krista Gavin Carly Devin Whitney Kyle Robin Terrence Tamara Dominic Bianca").split()
LAST = ("Smith Johnson Williams Brown Jones Miller Davis Wilson Anderson Taylor Thomas Moore Jackson Martin Thompson White "
        "Harris Clark Lewis Robinson Walker Young Allen King Wright Scott Hill Green Adams Baker Nelson Carter Mitchell Roberts "
        "Turner Phillips Campbell Parker Evans Edwards Collins Stewart Morris Murphy Cook Rogers Reed Bailey Bell Cooper "
        "Richardson Cox Howard Ward Peterson Gray Watson Brooks Kelly Sanders Price Bennett Wood Barnes Ross Henderson Coleman "
        "Jenkins Perry Powell Long Patterson Hughes Butler Simmons Foster Bryant Russell Griffin Hayes Myers Ford Hamilton "
        "Graham Sullivan Wallace Woods Cole West Owens Reynolds Fisher Ellis Harrison Gibson McDonald Marshall Murray O'Brien "
        "Kennedy Wells Fletcher Doyle Burke Lawson Holt Spencer Brennan Hartley Vaughn Pruitt Gallagher Kowalski Novak "
        "Lindqvist Moretti Russo Romano Schultz Becker Weber Fischer Hoffman Kruger Dubois Lefebvre Tremblay Gagnon Roy "
        "Bouchard Gauthier Morin Lavoie Fortin Pelletier Chen Wang Li Zhang Liu Nguyen Tran Pham Kim Park Lee Choi Patel "
        "Shah Singh Kumar Gupta Reddy Iyer Nair Rao Mehta Desai Garcia Rodriguez Martinez Hernandez Lopez Gonzalez Perez "
        "Sanchez Ramirez Torres Flores Rivera Gomez Diaz Morales Reyes Cruz Ortiz Gutierrez Chavez Ramos Vargas Castillo "
        "Jimenez Romero Herrera Medina Aguilar Okafor Mensah Adeyemi Haddad Khalil Nasser Rahman Cohen Levy Katz Friedman "
        "Sato Tanaka Yamamoto Nakamura O'Connor MacDonald Fraser Campbell Robertson Stewart").split()
FIRST_EXTRA = ("Carlos Maria Jose Ana Luis Sofia Javier Lucia Miguel Valentina Diego Camila Priya Arjun Ananya Rohan Kavya "
               "Vikram Sneha Rahul Wei Mei Jun Hao Xin Ming Yan Jian Mohammed Fatima Ahmed Aisha Omar Layla Yusuf "
               "Chinedu Amara Kwame Ifeoma Hiro Kenji Yuki Min-jun Ji-woo Seo-yeon Thanh Linh Duc Mathieu Genevieve "
               "Etienne Isabelle Yannick Chantal Andre Sylvie").split()

# region, state, city, zip3/postal prefix, area code, weight(pop-ish)
US_CITIES = [
    ("West", "WA", "Seattle", "981", "206", 9), ("West", "WA", "Spokane", "992", "509", 2), ("West", "WA", "Bellevue", "980", "425", 3),
    ("West", "OR", "Portland", "972", "503", 5), ("West", "OR", "Eugene", "974", "541", 1),
    ("West", "CA", "San Francisco", "941", "415", 9), ("West", "CA", "San Jose", "951", "408", 7), ("West", "CA", "Los Angeles", "900", "213", 14),
    ("West", "CA", "San Diego", "921", "619", 7), ("West", "CA", "Irvine", "926", "949", 5), ("West", "CA", "Sacramento", "958", "916", 4),
    ("West", "CA", "Oakland", "946", "510", 3), ("West", "CA", "Fresno", "937", "559", 2), ("West", "NV", "Las Vegas", "891", "702", 4),
    ("West", "NV", "Reno", "895", "775", 2), ("West", "AZ", "Phoenix", "850", "602", 7), ("West", "AZ", "Tucson", "857", "520", 2),
    ("West", "AZ", "Scottsdale", "852", "480", 3), ("West", "UT", "Salt Lake City", "841", "801", 4), ("West", "UT", "Provo", "846", "801", 1),
    ("West", "CO", "Denver", "802", "303", 7), ("West", "CO", "Boulder", "803", "303", 2), ("West", "CO", "Colorado Springs", "809", "719", 2),
    ("West", "ID", "Boise", "837", "208", 2), ("West", "MT", "Billings", "591", "406", 1), ("West", "NM", "Albuquerque", "871", "505", 2),
    ("West", "HI", "Honolulu", "968", "808", 1), ("West", "AK", "Anchorage", "995", "907", 1),
    ("Central", "TX", "Dallas", "752", "214", 10), ("Central", "TX", "Houston", "770", "713", 11), ("Central", "TX", "Austin", "787", "512", 8),
    ("Central", "TX", "San Antonio", "782", "210", 5), ("Central", "TX", "Fort Worth", "761", "817", 3), ("Central", "TX", "Plano", "750", "972", 3),
    ("Central", "OK", "Oklahoma City", "731", "405", 2), ("Central", "OK", "Tulsa", "741", "918", 2), ("Central", "KS", "Wichita", "672", "316", 1),
    ("Central", "KS", "Overland Park", "662", "913", 2), ("Central", "MO", "Kansas City", "641", "816", 3), ("Central", "MO", "St. Louis", "631", "314", 4),
    ("Central", "NE", "Omaha", "681", "402", 2), ("Central", "IA", "Des Moines", "503", "515", 2), ("Central", "MN", "Minneapolis", "554", "612", 6),
    ("Central", "MN", "St. Paul", "551", "651", 2), ("Central", "WI", "Milwaukee", "532", "414", 3), ("Central", "WI", "Madison", "537", "608", 2),
    ("Central", "IL", "Chicago", "606", "312", 13), ("Central", "IL", "Naperville", "605", "630", 2), ("Central", "IN", "Indianapolis", "462", "317", 4),
    ("Central", "MI", "Detroit", "482", "313", 5), ("Central", "MI", "Grand Rapids", "495", "616", 2), ("Central", "OH", "Columbus", "432", "614", 5),
    ("Central", "OH", "Cleveland", "441", "216", 4), ("Central", "OH", "Cincinnati", "452", "513", 4), ("Central", "AR", "Little Rock", "722", "501", 1),
    ("Central", "AR", "Bentonville", "727", "479", 1), ("Central", "LA", "New Orleans", "701", "504", 2), ("Central", "LA", "Baton Rouge", "708", "225", 1),
    ("Central", "ND", "Fargo", "581", "701", 1), ("Central", "SD", "Sioux Falls", "571", "605", 1), ("Central", "TN", "Nashville", "372", "615", 5),
    ("Central", "TN", "Memphis", "381", "901", 2),
    ("East", "NY", "New York", "100", "212", 16), ("East", "NY", "Brooklyn", "112", "718", 4), ("East", "NY", "Buffalo", "142", "716", 2),
    ("East", "NY", "Rochester", "146", "585", 2), ("East", "NY", "Albany", "122", "518", 1), ("East", "NJ", "Newark", "071", "973", 3),
    ("East", "NJ", "Jersey City", "073", "201", 3), ("East", "NJ", "Princeton", "085", "609", 2), ("East", "PA", "Philadelphia", "191", "215", 6),
    ("East", "PA", "Pittsburgh", "152", "412", 4), ("East", "MA", "Boston", "021", "617", 9), ("East", "MA", "Cambridge", "021", "617", 3),
    ("East", "MA", "Worcester", "016", "508", 1), ("East", "CT", "Hartford", "061", "860", 2), ("East", "CT", "Stamford", "069", "203", 2),
    ("East", "RI", "Providence", "029", "401", 1), ("East", "NH", "Manchester", "031", "603", 1), ("East", "ME", "Portland", "041", "207", 1),
    ("East", "VT", "Burlington", "054", "802", 1), ("East", "MD", "Baltimore", "212", "410", 3), ("East", "MD", "Bethesda", "208", "301", 2),
    ("East", "DC", "Washington", "200", "202", 5), ("East", "VA", "Arlington", "222", "703", 4), ("East", "VA", "Richmond", "232", "804", 2),
    ("East", "VA", "Reston", "201", "703", 3), ("East", "NC", "Charlotte", "282", "704", 5), ("East", "NC", "Raleigh", "276", "919", 4),
    ("East", "NC", "Durham", "277", "919", 2), ("East", "SC", "Charleston", "294", "843", 1), ("East", "SC", "Greenville", "296", "864", 1),
    ("East", "GA", "Atlanta", "303", "404", 9), ("East", "GA", "Savannah", "314", "912", 1), ("East", "FL", "Miami", "331", "305", 6),
    ("East", "FL", "Tampa", "336", "813", 4), ("East", "FL", "Orlando", "328", "407", 4), ("East", "FL", "Jacksonville", "322", "904", 3),
    ("East", "FL", "Fort Lauderdale", "333", "954", 2), ("East", "KY", "Louisville", "402", "502", 2), ("East", "WV", "Charleston", "253", "304", 1),
    ("East", "AL", "Birmingham", "352", "205", 2), ("East", "MS", "Jackson", "392", "601", 1), ("East", "DE", "Wilmington", "198", "302", 1),
]
CA_CITIES = [
    ("West", "BC", "Vancouver", "V6B", "604", 6), ("West", "BC", "Burnaby", "V5H", "604", 2), ("West", "BC", "Victoria", "V8W", "250", 1),
    ("West", "AB", "Calgary", "T2P", "403", 5), ("West", "AB", "Edmonton", "T5J", "780", 3),
    ("Central", "MB", "Winnipeg", "R3C", "204", 2), ("Central", "SK", "Saskatoon", "S7K", "306", 1), ("Central", "SK", "Regina", "S4P", "306", 1),
    ("East", "ON", "Toronto", "M5V", "416", 12), ("East", "ON", "Mississauga", "L5B", "905", 3), ("East", "ON", "Ottawa", "K1P", "613", 4),
    ("East", "ON", "Waterloo", "N2L", "519", 2), ("East", "ON", "Hamilton", "L8P", "905", 1), ("East", "QC", "Montreal", "H3B", "514", 7),
    ("East", "QC", "Quebec City", "G1R", "418", 2), ("East", "NS", "Halifax", "B3J", "902", 1), ("East", "NB", "Moncton", "E1C", "506", 1),
]
# legacy (pre-FY24) region naming: US West / US East / Canada. Central states came from both.
LEGACY_REGION = {"West": "US West", "East": "US East"}
CENTRAL_FROM_WEST = {"TX", "OK", "KS", "NE", "ND", "SD", "MN", "IA", "MO", "AR", "LA"}
US_STATE_TAX = {"CA": 7.25, "WA": 6.5, "OR": 0, "NV": 6.85, "AZ": 5.6, "UT": 6.1, "CO": 2.9, "ID": 6, "MT": 0, "NM": 4.875,
                "HI": 4, "AK": 0, "TX": 6.25, "OK": 4.5, "KS": 6.5, "MO": 4.225, "NE": 5.5, "IA": 6, "MN": 6.875, "WI": 5,
                "IL": 6.25, "IN": 7, "MI": 6, "OH": 5.75, "AR": 6.5, "LA": 4.45, "ND": 5, "SD": 4.2, "TN": 7, "NY": 4,
                "NJ": 6.625, "PA": 6, "MA": 6.25, "CT": 6.35, "RI": 7, "NH": 0, "ME": 5.5, "VT": 6, "MD": 6, "DC": 6, "VA": 5.3,
                "NC": 4.75, "SC": 6, "GA": 4, "FL": 6, "KY": 6, "WV": 6, "AL": 4, "MS": 7, "DE": 0}
CA_TAX = {"BC": ("GST+PST", 12), "AB": ("GST", 5), "MB": ("GST+PST", 12), "SK": ("GST+PST", 11), "ON": ("HST", 13),
          "QC": ("GST+QST", 14.975), "NS": ("HST", 15), "NB": ("HST", 15)}
STATE_NAMES = {"WA": "Washington", "OR": "Oregon", "CA": "California", "NV": "Nevada", "AZ": "Arizona", "UT": "Utah", "CO": "Colorado",
               "ID": "Idaho", "MT": "Montana", "NM": "New Mexico", "HI": "Hawaii", "AK": "Alaska", "TX": "Texas", "OK": "Oklahoma",
               "KS": "Kansas", "MO": "Missouri", "NE": "Nebraska", "IA": "Iowa", "MN": "Minnesota", "WI": "Wisconsin", "IL": "Illinois",
               "IN": "Indiana", "MI": "Michigan", "OH": "Ohio", "AR": "Arkansas", "LA": "Louisiana", "ND": "North Dakota",
               "SD": "South Dakota", "TN": "Tennessee", "NY": "New York", "NJ": "New Jersey", "PA": "Pennsylvania",
               "MA": "Massachusetts", "CT": "Connecticut", "RI": "Rhode Island", "NH": "New Hampshire", "ME": "Maine", "VT": "Vermont",
               "MD": "Maryland", "DC": "District of Columbia", "VA": "Virginia", "NC": "North Carolina", "SC": "South Carolina",
               "GA": "Georgia", "FL": "Florida", "KY": "Kentucky", "WV": "West Virginia", "AL": "Alabama", "MS": "Mississippi",
               "DE": "Delaware", "BC": "British Columbia", "AB": "Alberta", "MB": "Manitoba", "SK": "Saskatchewan", "ON": "Ontario",
               "QC": "Quebec", "NS": "Nova Scotia", "NB": "New Brunswick"}
STREETS = ("Main Market Oak Pine Maple Cedar Elm Washington Park Lake Hill River Church High Mill Station Bridge Commerce Harbor "
           "Union Liberty Franklin Jefferson Madison Lincoln Spring Sunset Ridge Valley Industrial Technology Innovation "
           "Enterprise Corporate Gateway Summit Meridian Kingsway Victoria Queen King Airport Canal Riverside Lakeshore "
           "Northpoint Westlake Eastgate Southpark Parkway Crossroads Willow Birch Aspen Juniper Highland Prospect").split()
STREET_TYPES = ["St", "Ave", "Blvd", "Rd", "Way", "Dr", "Pkwy", "Ln", "Plaza", "Ct", "Street", "Avenue", "Drive", "Road"]

# industry: weight, name suffix words, revenue/employee, IT budget % of revenue, sub-industries, buying season (months)
INDUSTRIES = {
    "Technology": (11, ["Technologies", "Software", "Systems", "Digital", "Data", "Networks", "Labs", "Computing", "Analytics", "Cyber", "AI"],
                   280_000, .07, ["SaaS", "IT Services", "Semiconductors", "Cybersecurity", "Fintech Platforms", "Data Centers & Hosting"], None),
    "Financial Services": (9, ["Capital", "Financial", "Bank", "Partners", "Investments", "Wealth", "Credit Union", "Asset Management", "Bancorp", "Trust"],
                           420_000, .065, ["Regional Banking", "Credit Unions", "Asset Management", "Payments", "Mortgage Lending", "Private Equity"], None),
    "Healthcare": (10, ["Health", "Medical Group", "Healthcare", "Clinics", "Health System", "Care", "Medical Center", "Physicians"],
                   150_000, .038, ["Hospitals & Health Systems", "Physician Groups", "Home Health", "Behavioral Health", "Dental Groups", "Diagnostic Labs"], None),
    "Manufacturing": (11, ["Manufacturing", "Industries", "Fabrication", "Components", "Machinery", "Industrial", "Precision", "Tooling", "Metals", "Plastics"],
                      240_000, .022, ["Automotive Parts", "Industrial Machinery", "Electronics Manufacturing", "Metal Fabrication", "Packaging", "Aerospace Components"], None),
    "Retail": (6, ["Retail", "Outfitters", "Stores", "Market", "Goods", "Brands", "Supply", "Mercantile"],
               190_000, .02, ["Specialty Retail", "Grocery", "E-commerce", "Home Improvement", "Apparel Retail"], (2, 3, 4, 5, 6, 7, 8, 9)),
    "Education": (6, ["University", "College", "Academy", "Learning Group", "School District", "Institute", "Community College"],
                  95_000, .045, ["K-12 Districts", "Higher Education", "Community Colleges", "Charter Schools", "EdTech"], (5, 6, 7, 8)),
    "State & Local Government": (5, ["County", "Water Authority", "Port Authority", "Transit Authority", "Public Works", "Township", "Housing Authority"],
                                 110_000, .04, ["County Government", "Municipal", "Transit", "Utilities Authority", "Public Safety"], (6, 7, 8, 9)),
    "Media & Entertainment": (3, ["Media", "Studios", "Entertainment", "Productions", "Broadcasting", "Publishing", "Interactive"],
                              260_000, .05, ["Post-Production", "Broadcasting", "Game Studios", "Publishing", "Streaming"], None),
    "Telecommunications": (3, ["Telecom", "Communications", "Wireless", "Fiber", "Broadband", "Connect"],
                           390_000, .055, ["Regional Carriers", "Fiber Providers", "Managed Network Services"], None),
    "Energy & Utilities": (4, ["Energy", "Power", "Utilities", "Solar", "Renewables", "Electric Cooperative", "Midstream"],
                           520_000, .025, ["Oil & Gas", "Electric Utilities", "Renewables", "Midstream Pipelines"], None),
    "Transportation & Logistics": (6, ["Logistics", "Freight", "Transport", "Shipping", "Express", "Distribution", "Carriers", "Trucking"],
                                   210_000, .025, ["Trucking", "3PL & Warehousing", "Freight Brokerage", "Last-Mile Delivery", "Aviation Services"], None),
    "Professional Services": (8, ["Consulting", "Advisors", "Group", "Associates", "Partners", "Solutions", "LLP", "Engineering"],
                              180_000, .05, ["Law Firms", "Accounting & Tax", "Management Consulting", "Architecture & Engineering", "Staffing"], (11, 12, 1)),
    "Hospitality": (3, ["Hotels", "Resorts", "Hospitality", "Restaurant Group", "Inns", "Travel", "Gaming"],
                    95_000, .02, ["Hotels & Resorts", "Restaurant Groups", "Casinos & Gaming", "Travel Services"], None),
    "Construction": (4, ["Construction", "Builders", "Contractors", "Engineering", "Development", "Homes", "Excavating"],
                     250_000, .015, ["Commercial Construction", "Residential Builders", "Civil & Infrastructure", "Specialty Trades"], None),
    "Insurance": (4, ["Insurance", "Mutual", "Assurance", "Underwriters", "Indemnity", "Benefits"],
                  460_000, .06, ["P&C Carriers", "Life & Annuity", "Insurance Brokerage", "Benefits Administration"], None),
    "Life Sciences": (3, ["Biosciences", "Pharmaceuticals", "Therapeutics", "Genomics", "Bio", "Diagnostics", "Labs"],
                      400_000, .05, ["Biotech R&D", "Pharma Manufacturing", "Medical Devices", "CROs", "Genomics"], None),
    "Nonprofit": (2, ["Foundation", "Alliance", "Trust", "Society", "Charities", "Mission"],
                  80_000, .03, ["Healthcare Nonprofits", "Social Services", "Foundations", "Religious Organizations"], None),
    "Consumer Goods": (4, ["Foods", "Beverages", "Home", "Apparel", "Products", "Brands", "Nutrition"],
                       310_000, .03, ["Food & Beverage", "Personal Care", "Household Products", "Apparel Brands"], None),
    "Agriculture": (2, ["Farms", "Agri", "Growers", "Cooperative", "AgTech", "Seed"],
                    230_000, .015, ["Farming Cooperatives", "AgTech", "Food Processing"], None),
}
PUBLIC_SECTOR = {"Education", "State & Local Government", "Nonprofit"}
NAICS = {"Technology": "5112", "Financial Services": "5221", "Healthcare": "6221", "Manufacturing": "3329", "Retail": "4529",
         "Education": "6111", "State & Local Government": "9211", "Media & Entertainment": "5121", "Telecommunications": "5173",
         "Energy & Utilities": "2211", "Transportation & Logistics": "4841", "Professional Services": "5411", "Hospitality": "7211",
         "Construction": "2362", "Insurance": "5241", "Life Sciences": "3254", "Nonprofit": "8133", "Consumer Goods": "3119",
         "Agriculture": "1111"}

ADJ = ("Blue Silver Golden Red North South East West Summit Pinnacle Clear Bright Iron Granite Cedar Maple Oak Pine River Lake "
       "Harbor Prairie Meadow Crest Coastal Atlas Vertex Nova Stellar Evergreen Redwood Falcon Eagle Lion Fox Bear Wolf Orion "
       "Polaris Apex Keystone Liberty Pioneer Frontier Horizon Crescent Sterling Cobalt Emerald Sapphire Amber Onyx Quartz "
       "Copper Titan Union Heritage Legacy Unity Vista Beacon Lighthouse Anchor Compass Meridian Zenith Aurora Solstice "
       "Tidewater Highland Lakeshore Riverbend Stonebridge Willow Aspen Birch Juniper Sequoia Cypress Blackstone Whitewater "
       "Greenfield Brightwater Northwind Silverline Ironwood Clearview Bluewater Fairview Westbrook Eastgate Southport Northgate "
       "Kingfisher Bluebird Hawthorne Ashford Brookfield Oakridge Trident Paragon Cascade Sierra Mesa Canyon Badger Buckeye "
       "Lone Star Magnolia Palmetto Peachtree Gulf Bayou Ozark Appalachian Great Plains Heartland Prairie Wind Rocky Mountain "
       "Pacific Atlantic Midwest Tri-County Tri-State Twin Rivers Three Rivers Big Sky Red Rock Desert Sun Cardinal Patriot "
       "Freedom Constitution Commonwealth Founders Capitol Metro Central Premier First Allied United Integrated Advanced").split()
ADJ = [a for a in ADJ if a not in ("Star", "Plains", "Mountain", "Wind", "Sky", "Rock", "Sun", "Rivers", "County", "State")]
NOUN = ("Ridge Peak Valley Bay Point Field Stone Bridge Creek Grove Park Gate Harbor Path Forge Works Line Wave Spring Rock Hill "
        "Port Crossing Landing Haven Mill Shore Trail Hollow Mesa Canyon Glen Falls Isle Bluff Junction Pointe Commons").split()
SYL1 = "Vel Nov Tri Zen Aer Cor Lum Quan Syn Ver Xan Kel Ori Pyr Sol Tor Val Neo Omn Cyr Dyn Ev Ix Lyr Mav Nex Ray Sky Tek Vox Bry Cal Dex Fen Jor Kai Lux Mer Pax Rho Tal".split()
SYL2 = "ora ix ity ex ara is yn ent ium ova ia on ar us eo ana ica era ova ix ant ius eon ira".split()
LEGAL_SUFFIX_US = ["Inc.", "LLC", "Corp.", "Co.", "Inc", "Corporation", "Holdings", "Group, Inc.", "L.P."]
LEGAL_SUFFIX_CA = ["Inc.", "Ltd.", "Corp.", "Limited", "ULC"]

PARTNERS = [  # name, type, home region, focus, segments served
    ("Summit Point Solutions", "National Solution Provider", "Central", "Infrastructure + client refresh", ("Medium Business", "Large Enterprise")),
    ("Crestline Technology Group", "Regional VAR", "West", "Client devices + deployment services", ("Small Business", "Medium Business")),
    ("BlueHarbor IT", "Managed Service Provider", "East", "Managed devices, Device-as-a-Service", ("Small Business", "Medium Business")),
    ("Ironclad Data Partners", "Infrastructure Specialist", "Central", "Storage, data protection, HCI", ("Medium Business", "Large Enterprise")),
    ("Maplegrid Systems", "Canadian Solution Provider", "East", "Canada coverage, public sector", ("Small Business", "Medium Business", "Large Enterprise")),
]
COMPETITORS = {"Corsalis": 30, "Varenta": 25, "Lumora": 12, "Quorra Networks": 8, "Helixon": 10, "Public cloud": 10, "White-box / ODM": 5}
COMPETITOR_FOCUS = {"Corsalis": "servers/storage/PCs", "Varenta": "PCs/workstations", "Lumora": "storage", "Quorra Networks": "networking",
                    "Helixon": "HCI", "Public cloud": "cloud", "White-box / ODM": "servers"}
CARRIERS = {"UPS": 40, "FedEx": 35, "XPO Freight": 8, "Old Dominion": 7, "Purolator": 3, "Orvane Direct Logistics": 7}
HYPERVISORS = ["VMware vSphere 6.7", "VMware vSphere 7", "VMware vSphere 8", "Hyper-V", "Nutanix-like AHV", "Proxmox", "None (bare metal)"]
HYPERVISORS = [h for h in HYPERVISORS if "Nutanix" not in h] + ["KVM"]
CLOUDS = ["AWS", "Azure", "Google Cloud", "Azure + AWS", "None", "Oracle Cloud"]
OS_CLIENT = ["Windows 10", "Windows 11", "Windows 10/11 mixed", "macOS + Windows mix", "ChromeOS + Windows"]
ITSM = ["ServiceNow", "Jira Service Management", "Freshservice", "Zendesk", "In-house", "None"]
BACKUP = ["Vault Backup", "Veeam-style competitor", "Tape + scripts", "Cloud backup (SaaS)", "Corsalis DataGuard", "None documented"]
