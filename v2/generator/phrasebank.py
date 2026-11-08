"""
phrasebank.py - wording library for the Orvane Technologies synthetic CRM dataset.

Every string in this module is a template filled with ``str.format_map(slots)``.
``slots`` always provides every key listed in ``SLOT_NAMES`` (string values), so a
template may use any subset of them and nothing else. No literal braces appear in
any template.

Orvane product lines referenced here: Aster (business laptops), Bastion (rugged),
Cadence (desktops/AIO), Forge (workstations), Wisp (thin clients), Clarity
(monitors), Tether (docks), Nova (consumer), Atlas (servers / Atlas AI), Converge
(HCI), Strata (storage), Vault (data protection), Mesh (switching), Outpost
(edge), Orvane Manage, Orvane Insight, Orvane Shield, ProCare tiers, Orvane Flex,
Orvane Device-as-a-Service, Orvane Financial Services.

Competitors are fictional: Corsalis, Varenta, Lumora, Quorra Networks, Helixon.
"""

SLOT_NAMES = (
    "account", "contact_first", "contact_last", "contact_name", "contact_title",
    "contact2_name", "contact2_title", "rep_first", "rep_name", "se_name", "old_rep",
    "partner", "competitor", "product", "product_line", "infra_product",
    "storage_product", "qty", "seats", "servers", "amount", "budget", "pct",
    "discount", "tb", "util", "growth", "weeks", "date", "quarter", "fy",
    "po_number", "order_number", "quote_number", "case_number", "invoice_number",
    "site_city", "hq_city", "new_exec", "exec_title", "firmware", "advisory", "model",
    "os", "hypervisor", "cloud", "gpu_count", "lease_end", "days", "initiative",
)

# =============================================================================
# 1. TOPICS
# =============================================================================

TOPICS = {}

TOPICS["intro_discovery"] = {
    "subjects": [
        "Intro call - {account}",
        "Discovery: {contact_name} ({contact_title})",
        "First mtg w/ {account} IT",
        "Discovery - current environment + priorities",
        "Intro / qualification - {contact_first}",
        "Initial conversation re: {initiative}",
        "Cold call connect - {contact_name}",
        "Discovery follow-up w/ {contact2_name}",
        "Whiteboard session - {account} infra overview",
    ],
    "summaries": [
        "Spoke w/ {contact_name} ({contact_title}). ~{seats} users across 3 sites, HQ in {hq_city}. Mostly a {competitor} shop on the server side, mixed on clients. Biggest pain right now is inconsistent imaging - they still build machines by hand in the IT room. Open to a conversation about {product_line} if we can show a real deployment story.",
        "Intro call. {contact_first} was guarded at first, warmed up once we got into specifics. {servers} hosts on {hypervisor}, oldest gear is 6+ yrs. No formal refresh cycle - they replace when things break. Budget gets set in {quarter}.",
        "Quick 15 min intro. Not a fit for infra right now, but {contact_first} owns endpoint purchasing and buys ~{qty} laptops a year from whoever has stock. Worth working.",
        "Met with {contact_name} and {contact2_name} ({contact2_title}). Walked through who we are beyond PCs - they had no idea we sold storage or HCI. Environment: {servers} servers, a {competitor} array at ~{util}% full, backups to tape plus a bucket in {cloud}. {contact2_name} is the technical decision maker; {contact_first} controls budget. Next step is a proper discovery w/ {se_name}.",
        "Discovery. Key facts: {seats} employees, growing ~{growth}% YoY, IT team of 6. Standardized on {os} and Microsoft 365, Intune on some devices but not all. Break/fix contract with {partner}. They want fewer vendors, not more - position as consolidation.",
        "{contact_first} took the call from the car so kept it short. They kick off {initiative} in {quarter} and want to understand options before they write requirements. Asked for a 1-pager and references in their vertical.",
        "Good first conversation. {contact_title} came in ~8 months ago from a larger org and is clearly cleaning house - said 'technical debt' four times. No incumbent loyalty. Wants a roadmap conversation, not a quote.",
        "Spoke w/ {contact_name}. They're midway through a 3-yr plan, year 2 is infrastructure. Current DC is a colo cage in {hq_city}, 4 racks at ~30A each, power-constrained. Anything we propose has to fit inside that envelope or they buy more power, which they hate.",
        "Inbound from the website asking about {product}. Real need is bigger - {qty} devices for field ops plus a handful of {infra_product}-class servers for the branch. Qualified: budget yes ({budget}), timing {quarter}, authority sits with {contact2_name}.",
        "Discovery w/ {se_name}. Notes: 8-host cluster on {hypervisor}, dual-socket, 512GB per host, FC SAN, 10GbE everywhere except the core which is 25. Licensing renewal coming and they're nervous about cost. Opened the door on {infra_product} and Converge.",
        "Not much to go on - {contact_first} is new to the role and still figuring out what they own. Agreed to reconnect in {weeks} wks once they've done an inventory.",
        "{contact_name} gave a frank rundown: {competitor} oversold, under-delivered on services, and the account team turned over twice in a year. They'll listen but trust has to be earned. Small first deal likely - maybe {qty} units of {product} as a pilot.",
        "Asked about decision process. IT recommends, finance ({contact2_name}) approves anything over $50k, board approves over $250k. Procurement runs a 3-bid policy unless it's off a cooperative contract. Need to confirm which co-ops they can buy from.",
        "Talked through pain points: 1) helpdesk tickets on aging laptops 2) a single storage array with no replication 3) zero visibility into hardware health. {contact_first} ranked them 2, 1, 3. Storage is the opener.",
        "~40 min w/ {contact_first}. Very technical, runs a homelab, asked about BMC features and Redfish support before anything else. Wants {infra_product} spec sheets and the Orvane Insight API docs. Not the buyer but clearly the influencer.",
    ],
    "next_steps": [
        "Send overview deck + 2 customer refs in their vertical",
        "Schedule technical discovery w/ {se_name} week of {date}",
        "Get org chart - confirm who signs over $50k",
        "Check co-op contract eligibility for {account}",
        "Request current hardware inventory export",
        "Reconnect in {weeks} wks after their budget cycle",
        "Set {contact_first} up with Orvane Insight trial",
        "Find out what {contact2_name} actually cares about before next call",
        "Confirm whether {partner} has an existing relationship here",
    ],
    "emails_out": [
        ("Great speaking today - next steps", "Hi {contact_first},\n\nThanks for the time today. Quick recap of what I heard:\n- ~{seats} users across 3 sites\n- {hypervisor} running on hosts that are well past their prime\n- imaging is manual and eating your team's week\n- budget gets set in {quarter}\n\nI'd like to bring in {se_name}, our systems engineer, for a 45-minute technical discovery. Does {date} work?\n\nThanks,\n{rep_name}"),
        ("Orvane + {account} - a couple of references", "{contact_first},\n\nAs promised, two customers in a similar spot who'd be happy to talk. Both moved from {competitor} in the last 18 months - one on the client side, one on servers and storage. Let me know which is more useful and I'll make the intro.\n\nBest,\n{rep_name}"),
        ("Following up", "Hi {contact_first} - circling back on my note from last week. 20 minutes to see whether there's a fit. If the timing is wrong just tell me and I'll get out of your inbox until {quarter}.\n\n{rep_name}"),
        ("Discovery questions ahead of {date}", "Hi {contact_first},\n\nTo make the session with {se_name} worth your time, it would help to have a rough answer to these beforehand (rough is fine):\n1. Host count, CPU gen and RAM per host\n2. Total usable storage and how much is free\n3. Backup software + target, and your retention policy\n4. Rack space and power available in the cage\n5. Anything coming off maintenance in the next 12 months\n\nThanks,\n{rep_first}"),
        ("Quick intro - Orvane", "Hi {contact_first},\n\nI cover {account} for Orvane. I noticed you're hiring for a systems engineer focused on {initiative}, which usually means a project with a deadline. We help teams your size stand that kind of thing up without adding headcount. Open to a short call next week?\n\n{rep_name}"),
    ],
    "emails_in": [
        ("Re: Great speaking today - next steps", "Thursday works. Please send an invite and include {contact2_name}. We're on Teams, not Zoom.\n\n{contact_first}"),
        ("Re: Following up", "Hi {rep_first}, sorry for the delay. We're buried in a migration this month. Can we revisit after {date}?"),
        ("question", "Do you guys have anything on a state or co-op contract? Purchasing won't let me do a one-off without 3 quotes otherwise.\n\nsent from my phone"),
        ("RE: Orvane + {account}", "Thanks. Honestly we've been a {competitor} shop for 10 years and they've been fine. What would make it worth switching? Not trying to be difficult, I just need something to take to my boss."),
        ("inventory export", "{rep_first},\n\nAttached is a raw export from our RMM. Its messy - about 20% of the serials are blank and the server tab is out of date. Let me know if you need anything else.\n\nThanks\n{contact_name}\n{contact_title}"),
    ],
    "chatter": [
        "New logo convo w/ {account} - {seats} users, {competitor} on servers, no refresh cycle. @{se_name} can you join discovery on {date}?",
        "anyone know {contact_name} at {account}? pretty sure they came from one of {old_rep}'s old accounts",
        "fyi {account} is a real opp, not just a PC deal. {servers} hosts + storage aging out. putting it in pipe at {amount} for now",
        "heads up - {account} sits in {partner}'s footprint, checking whether they already have a relationship before I go further",
        "discovery went well. {contact_first} is technical and skeptical, which honestly is my favorite kind of customer",
        "@{rep_first} do we have a reference in their vertical w/ roughly {seats} seats? need one for {account} by {date}",
    ],
}

TOPICS["client_refresh"] = {
    "subjects": [
        "PC refresh planning - {account}",
        "{product} pilot units",
        "Client refresh: config review",
        "Refresh wave 2 timing",
        "Laptop standard discussion w/ {contact_first}",
        "Dock + monitor bundle for refresh",
        "Refresh pricing - {qty} units",
        "Pilot feedback call",
        "Knowledge worker vs. field persona configs",
    ],
    "summaries": [
        "Spoke w/ {contact_first} re: refresh. {qty} laptops aging out - mostly 5-yr-old units with failing batteries. Want to standardize on 2 configs: {product} for knowledge workers, Forge for engineering. Targeting {quarter} for wave 1.",
        "Pilot of 25 {product} units wrapped. Feedback: battery life good, keyboard well liked, a few complaints about the webcam in low light. Tether dock firmware needed an update before displays would daisy-chain - {se_name} sorted that. Green light for wave 1.",
        "Config review w/ {contact_name}. Landed on 16GB/512GB for standard, 32GB/1TB for power users. They asked about 5G WWAN for ~10% of the fleet - pricing it as an option. Also want Clarity 27in monitors x2 per desk at HQ only.",
        "Refresh is real but slipping. {contact_first} says finance wants to stretch the current fleet another 6 months. Countered with a TCO view: helpdesk tickets on the old fleet are up {pct}% YoY and battery swaps alone are running ~$90/unit.",
        "Personas finalized: (1) office/hybrid - {product} + Tether dock (2) field - Bastion rugged w/ hot-swap battery (3) shared kiosk/front desk - Wisp thin client. Total ~{qty} units over 3 waves.",
        "{contact_first} wants everything shipped pre-imaged with asset tags applied. Talked through factory imaging vs. Autopilot-style zero-touch - they're on Intune so zero-touch is the cleaner path. Need their tenant ID to register hardware hashes at the factory.",
        "Quick call. They approved {qty} units for {quarter}. Waiting on budget confirmation from {contact2_name} before PO.",
        "Long conversation about displays. Half the org has been asking for bigger screens since going hybrid. Proposing Clarity 24in at the desk w/ single-cable USB-C through the Tether dock. They also want to recycle ~400 old monitors - looping in ITAD.",
        "Refresh check-in. Wave 1 ({qty} units) deployed with very few issues. Wave 2 is the harder one - engineering wants Forge mobile workstations with discrete GPUs for CAD, and those are on a {weeks}-wk lead right now.",
        "Discussed device lifecycle. They run 4 years on laptops, 5 on desktops. Pitched Device-as-a-Service w/ a 3-yr cycle: predictable per-seat monthly, ProCare Plus included, ITAD at end of term. {contact2_name} liked the opex angle.",
        "{competitor} quoted them aggressively on a comparable config. Our edge is the dock compatibility and the deployment service, not unit price. {contact_first} admitted their last rollout with {competitor} took twice as long as planned.",
        "Pilot kicked off. 15 units to IT, 10 to sales. Running for {weeks} weeks. Success criteria: battery through a full day of Teams calls, no dock disconnects, image boots clean.",
        "Spoke w/ {contact_name}. They need to replace ~{qty} desktops in the call center. Cadence small form factor fits the existing under-desk mounts. Want TPM 2.0 and vPro-class remote management on every unit.",
        "Wave 3 is the long tail - remote employees in 30+ states. Talked through drop-ship to home addresses with return labels for the old device in the box. They loved that.",
        "Quick one: {contact_first} asked us to hold pricing through {date} while they finalize headcount. Told them I'd check with deal desk.",
    ],
    "next_steps": [
        "Send config matrix for 3 personas w/ pricing",
        "Ship 25 pilot units to {site_city}",
        "Get Intune tenant ID for factory registration",
        "Quote Clarity monitors + Tether docks as a bundle",
        "Build TCO comparison: stretch fleet vs. refresh now",
        "Confirm drop-ship address file format with {contact_first}",
        "Loop in services for asset tagging + ITAD quote",
        "Check Forge lead times with supply before committing dates",
        "Ask deal desk to extend pricing on {quote_number} to {date}",
    ],
    "emails_out": [
        ("Refresh configs - for review", "Hi {contact_first},\n\nAttached are the three configs we discussed:\n- Standard: {product}, 16GB / 512GB, Tether dock\n- Power user: 32GB / 1TB, same dock\n- Field: Bastion w/ hot-swap battery and WWAN\n\nPricing on {quote_number} is good through {date}. Shout with any changes.\n\n{rep_first}"),
        ("Pilot units shipped", "Hi {contact_first} - the 25 pilot units shipped today on {order_number}, should land in {site_city} within 3 business days. {se_name} will join the first unboxing remotely if helpful. Tracking to follow once the carrier scans them."),
        ("Lifecycle option - Device-as-a-Service", "{contact_first},\n\nFollowing up on {contact2_name}'s question about spreading the cost. Rough numbers for {qty} seats on a 36-month DaaS term are attached - includes ProCare Plus, deployment and end-of-term recovery. Happy to walk finance through it.\n\nBest,\n{rep_name}"),
        ("Wave 2 lead times", "Hi {contact_first},\n\nHeads up: Forge mobile workstations with the discrete GPU are running about {weeks} weeks right now. If we can get the PO in by {date} I can lock a build slot. The standard {product} units for wave 2 are in stock.\n\n{rep_first}"),
        ("Re: monitors", "Yes, the Clarity 24 runs off a single USB-C cable through the dock - power, video and network. Spec sheet attached. For the 27s at HQ I'd go with the USB-C hub model so you can daisy-chain."),
    ],
    "emails_in": [
        ("Re: Refresh configs - for review", "Looks good. Can we swap the 512 for 1TB on standard? Our users hoard files locally even though we tell them not to. What's the delta?"),
        ("pilot feedback", "{rep_first},\n\nGeneral consensus is positive. Three things:\n1. two docks dropped the second monitor after sleep\n2. webcam is grainy in our conference rooms\n3. people want the backlit keyboard\n\nCan you have someone look at #1 before we sign off?\n\n{contact_first}"),
        ("refresh on hold??", "Just heard from finance that they may push us to {quarter}. Not final yet. Will update when I know more, sorry."),
        ("RE: Lifecycle option - Device-as-a-Service", "Finance had questions on the end-of-term buyout and what happens if we lose a device mid-term. Can you send the T&Cs?"),
        ("Approved", "We're approved for {qty} units for wave 1. PO coming from procurement this week. Please make sure the quote reflects the 1TB change.\n\nThanks,\n{contact_name}"),
    ],
    "chatter": [
        "{account} pilot feedback in - mostly good. dock dropping 2nd display after sleep on 2 units. @{se_name} firmware?",
        "refresh at {account} is real: {qty} units wave 1, PO expected by {date}. committing it",
        "anyone have current lead times on Forge w/ discrete GPU? {account} wave 2 depends on it",
        "fyi {competitor} is in at {account} on the refresh. we're fine on deployment story, weaker on unit price",
        "heads up @{rep_first} - {account} wants DaaS numbers for {qty} seats, can you loop in Orvane Financial Services",
        "big win for the pilot - {contact_first} said it was the smoothest one they've done. wave 1 approved",
    ],
}

TOPICS["win11_migration"] = {
    "subjects": [
        "{os} migration planning",
        "Win 11 readiness assessment results",
        "Hardware compatibility review - TPM / CPU",
        "Migration timeline w/ {contact_first}",
        "In-place upgrade vs. replace discussion",
        "Win 11 pilot group status",
        "End of support - remaining devices",
        "Image + driver pack review",
    ],
    "summaries": [
        "Spoke w/ {contact_first} about Windows 11. Ran Orvane Manage readiness against their fleet: ~{pct}% of devices fail on CPU or TPM. That's roughly {qty} machines that have to be replaced, not upgraded.",
        "They are behind. Still ~{qty} devices on Windows 10 and the extended-support quote they got was eye-watering. {contact_title} wants a plan to be off 10 by end of {quarter}.",
        "Walked through in-place upgrade vs. wipe-and-load. Their image is 4 years of accumulated cruft, so recommended a clean Autopilot-style rebuild on new hardware and in-place only on devices under 3 yrs old.",
        "Readiness results: TPM disabled in BIOS on ~300 otherwise-compatible units - fixable with a BIOS config push from Orvane Manage, no hands needed. Remaining {qty} are pre-8th-gen CPUs and have to go.",
        "Driver pack discussion. Their packaging team got burned on a previous migration by a bad audio driver. Showed them the Orvane driver catalog and the model-specific packs for SCCM/Intune. {se_name} will build a test task sequence with them.",
        "App compatibility is the real blocker, not hardware. Two line-of-business apps haven't been certified on 11. {contact_first} is chasing the vendors. Hardware order is on hold until then.",
        "Pilot group of 50 upgraded. 3 issues: VPN client needed an update, a printer driver for the shop floor, and BitLocker recovery prompts after a BIOS update on 4 units. All resolved.",
        "Quick check-in. They want to bundle the Win 11 replacements with the broader client refresh so they only touch each user once. Makes sense.",
        "{contact_first} asked whether Copilot-key / NPU devices matter for them yet. Honest answer: not for most users today, but anything bought now will live 4+ years, so worth a modest premium on the power-user config.",
        "Migration is ~70% done. Remaining stragglers are mostly shared devices in warehouses and a lab running an old instrument controller that can't move. Recommended isolating that one on its own VLAN rather than holding up the rest.",
        "Talked to {contact2_name} about end-of-support exposure. Their cyber insurance renewal now asks specifically about unsupported OS. That got finance's attention fast.",
        "Their MSP {partner} was handling the migration but is behind schedule. {contact_first} asked if our deployment services team could pick up the remaining {qty} devices.",
        "Spoke w/ {contact_name}. Kiosks and shared front-desk PCs are the problem - can't upgrade, low usage. Pitched Wisp thin clients w/ VDI instead of replacing like-for-like.",
        "Readiness review done. 1,100 compatible, {qty} incompatible, ~200 unknown (offline / never check in). Unknowns are probably in drawers.",
    ],
    "next_steps": [
        "Run Orvane Manage readiness report on full fleet",
        "Push BIOS config to enable TPM on compatible units",
        "Quote replacements for {qty} incompatible devices",
        "{se_name} to build test task sequence w/ driver packs",
        "Get LOB app vendor certification dates from {contact_first}",
        "Propose deployment services for remaining devices",
        "Send Wisp + VDI sizing for shared devices",
        "Confirm cutoff date for Windows 10 extended support decision",
    ],
    "emails_out": [
        ("Windows 11 readiness - summary", "Hi {contact_first},\n\nResults from the readiness scan:\n- Ready now: ~1,100\n- TPM off in BIOS (fixable remotely): ~300\n- Hardware incompatible: {qty}\n- Not reporting: ~200\n\nThe TPM group we can fix with a config push this week. Want to set up 30 min to plan the rest?\n\n{rep_first}"),
        ("Driver packs for your models", "{contact_first} - links to the current driver packs for the 6 models in your fleet are in the attached sheet. {se_name} flagged that the audio driver on the older Aster 5 should be pinned to the version listed; the newer one has a known issue with some headsets."),
        ("Windows 10 end of support", "Hi {contact_first},\n\nI know this is on your radar, but given the cyber insurance question {contact2_name} raised I put together a one-page view of the {qty} devices that can't go to 11 and what replacing them in {quarter} would look like. Attached.\n\n{rep_name}"),
        ("Deployment help for remaining devices", "{contact_first},\n\nOur deployment team can take the remaining {qty} devices: user data backup, rebuild to your Intune profile, and swap at desk. Typical throughput is 60-80 devices per tech per week on site. Scope + pricing attached."),
        ("Re: BitLocker prompts", "That's expected after a BIOS update if BitLocker isn't suspended first. Orvane Manage can suspend for one reboot automatically - setting is under the BIOS update policy. {se_name} can walk your team through it."),
    ],
    "emails_in": [
        ("Win 11", "{rep_first}, our CIO wants a number for replacing everything that can't upgrade. Can I get that by Friday? Ballpark is fine."),
        ("Re: Windows 11 readiness - summary", "Thanks. The not-reporting ones are probably in a closet somewhere. I'll have the desk sweep sites. Go ahead with the TPM push on the pilot OU first."),
        ("BitLocker recovery keys", "We had 4 machines ask for BitLocker recovery after the BIOS update last night. Users were not happy. Is this expected?? Need to know before we push to the rest."),
        ("RE: Deployment help", "This is helpful. {partner} is supposed to finish this but they're way behind. Let me talk to my director about whether we can bring you in for the rest. Don't send anything to {partner} yet please."),
        ("app compat update", "Vendor says their app will be certified on 11 by {date}. I don't believe them but that's what they said."),
    ],
    "chatter": [
        "{account} has {qty} devices that can't go to Win 11. that's a refresh, not a migration. working it",
        "@{se_name} {account} hit BitLocker recovery prompts after BIOS push - was suspend enabled in the policy?",
        "fyi {partner} is behind on the {account} Win 11 project. customer asking us to take over the tail. tread carefully",
        "win 11 readiness report on {account} is a great door opener btw - 15 min of work and they now see the whole fleet",
        "heads up: {account} cyber insurance renewal asks about unsupported OS. finance suddenly cares",
        "anyone done Wisp + VDI for shared kiosks recently? {account} wants to stop buying full PCs for front desks",
    ],
}

TOPICS["server_refresh"] = {
    "subjects": [
        "Server refresh - {account}",
        "{infra_product} sizing review",
        "Host consolidation discussion",
        "Atlas config + power budget",
        "Server refresh: rack layout",
        "Refresh timing vs. maintenance renewal",
        "Compute sizing w/ {se_name}",
        "Server quote review - {quote_number}",
    ],
    "summaries": [
        "Spoke w/ {contact_first}. {servers} hosts, mostly {model} and older, coming off {competitor} maintenance in {quarter}. Renewal quote was ~{pct}% higher than last year. Opened the refresh conversation in earnest.",
        "Sizing session w/ {se_name}. Current: {servers} hosts at ~{util}% avg CPU, RAM is the real constraint. New {infra_product} with current-gen CPUs and 1TB per host consolidates to roughly half the hosts. Fewer sockets also helps their {hypervisor} licensing.",
        "Power and cooling are the gating factor. Colo gives them 2 x 30A circuits per rack. {se_name} did the math - consolidated config draws ~{pct}% less at typical load, so they can pull a rack out of the contract.",
        "Talked about core licensing. Their {hypervisor} renewal is per-core now, so 2 x 32-core sockets per host is a very different bill than 2 x 16. Leaning toward fewer, denser hosts. Running both scenarios.",
        "{contact_first} wants local NVMe in each host for a future HCI play even though they're staying on the SAN for now. 4 x 3.84TB NVMe per node plus 2 x M.2 boot in RAID 1.",
        "Refresh is a go for {quarter}. {servers} x {infra_product}, dual 25GbE, BMC on a dedicated mgmt VLAN, ProCare Mission Critical w/ 4-hr onsite. {contact2_name} still has to sign off on the number.",
        "They asked about rack & stack. Their team is 3 people and they don't want to spend a weekend cabling. Quoting rack integration in our facility - ships as a full rack, power on and hand off.",
        "Short call. They want a quote with and without the GPU option on 2 hosts for an upcoming {initiative}. Sending both.",
        "Firmware baseline conversation. Bad experience with mismatched firmware across their old cluster causing vMotion issues. Showed how Orvane Insight baselines BIOS, BMC, NIC and RAID firmware across the cluster and flags drift.",
        "{competitor} came in with a trade-in credit for their old gear. Our counter: ITAD buyback on the {model} units plus a cleaner consolidation story. Need to see their number.",
        "Discussed tower vs. rack for the 4 branch offices. Branches have no rack, just a closet - Atlas tower w/ a small UPS is the right fit. HQ goes rack.",
        "Spoke w/ {contact_name}. Main DB server is still a single physical box running SQL Server Enterprise. Licensing is per core - moving to a newer CPU with fewer, faster cores could save them real money. Want {se_name} to model it.",
        "Asked about memory configs. Recommended populating all channels for bandwidth - 16 x 64GB rather than 8 x 128GB even though the bigger DIMMs leave more upgrade room.",
        "Refresh slipped a quarter. Not lost - their datacenter move is taking priority and nobody wants to rack new gear twice.",
        "Detailed BOM review w/ their engineer. Swapped the RAID controller for an HBA on the storage-heavy nodes, added a second PSU on all, dropped the optical drive nobody needed.",
    ],
    "next_steps": [
        "Model consolidation: {servers} hosts -> new {infra_product} count",
        "Send power/heat calcs for colo",
        "Quote rack integration + on-site handoff",
        "Run per-core licensing comparison for 2 CPU options",
        "Get {competitor} maintenance end dates per host",
        "Price ITAD buyback on retired {model} units",
        "Build firmware baseline plan in Orvane Insight",
        "Confirm ProCare tier and response time per site",
        "Revise BOM per engineer's markup",
    ],
    "emails_out": [
        ("Server refresh - sizing summary", "Hi {contact_first},\n\nSummary of what {se_name} and I worked through:\n- Today: {servers} hosts, avg CPU ~{util}%, memory constrained\n- Proposed: consolidate onto current-gen {infra_product}, 1TB RAM each, dual 25GbE\n- Power: ~{pct}% lower draw at typical load\n- Licensing: fewer cores to license on {hypervisor}\n\nFull BOM and pricing on {quote_number}. Let's find 30 min to go through it.\n\n{rep_first}"),
        ("Rack integration option", "{contact_first},\n\nWe can build and cable the racks in our integration center, burn them in for 48 hours and ship them ready to power on. Your team plugs in power and uplinks. Turnaround is about {weeks} weeks from PO. Pricing added as a separate line."),
        ("Two configs - with and without GPU", "Hi {contact_first} - per your ask, two versions on {quote_number}. Version B adds GPUs to two nodes for the {initiative} work. Note the GPU nodes need 2400W PSUs; I've reflected that."),
        ("ITAD buyback on old hosts", "{contact_first},\n\nOur asset recovery team put a preliminary value on the retired {model} units - attached. Final number depends on condition and config at pickup. Drives are wiped to NIST 800-88 or shredded on site, your choice, with certificates."),
        ("Checking in on the refresh", "Hi {contact_first}, any update on timing for the server refresh? I want to make sure we hold build capacity if you're still targeting {quarter}."),
    ],
    "emails_in": [
        ("RE: Server refresh - sizing summary", "This is good. Can you rerun it assuming 20% growth over 3 yrs? I don't want to be back here in 18 months asking for more hosts."),
        ("quote", "{rep_first} - procurement needs the quote broken out by site and with maintenance on a separate line. Also needs to say 'valid through' a date or they reject it."),
        ("Re: Two configs - with and without GPU", "We'll go with A for now. GPU project isn't funded yet. Can we add GPUs later or does that need a different chassis?"),
        ("power", "Colo says we're at 82% of contracted power on rack 3 already. Need the actual measured draw per node under load, not nameplate. Do you have that?"),
        ("refresh timing", "The DC move is pushing everything. Realistically {quarter}. Please don't send me reminders every week lol I'll reach out."),
    ],
    "chatter": [
        "{account} server refresh committed for {quarter} - {servers} hosts consolidating. @{se_name} great work on the licensing model, that's what sold it",
        "anyone have measured (not nameplate) power numbers for {infra_product} at 70% load? colo customer needs it",
        "heads up {competitor} is offering trade-in credit at {account}. need ITAD buyback numbers asap",
        "fyi {account} pushed refresh a qtr due to DC move. not at risk, just timing",
        "@{rep_first} can we do rack integration for 3 racks in {weeks} wks? customer wants it before their change freeze",
        "the per-core licensing angle is killing it right now. every {hypervisor} customer is looking at their renewal and panicking",
    ],
}

TOPICS["storage_capacity"] = {
    "subjects": [
        "Storage capacity - {account}",
        "{storage_product} sizing",
        "Array at {util}% - options",
        "Storage refresh w/ {contact_first}",
        "Dedupe/compression assumptions review",
        "Storage tiering discussion",
        "Capacity expansion quote",
        "Performance data review - storage",
    ],
    "summaries": [
        "{contact_first} called - their {competitor} array is at {util}% and growing ~{growth}TB a month. They're out of runway by {quarter}. Expansion shelf from {competitor} is quoted at a price they called 'insulting'.",
        "Sizing w/ {se_name}. Raw need is ~{tb}TB usable after 3 yrs growth. Data mix is mostly VMs and SQL, some file shares. Using a conservative 3:1 data reduction for VMs, 1.5:1 for the file data. Landed on a {storage_product} with room for one expansion shelf.",
        "Pulled 30 days of perf data off the current array. Peak ~85k IOPS, 95th percentile latency 4ms but spiking to 20+ during the backup window. Most of the pain is backups and month-end SQL jobs colliding.",
        "They want block and file on the same box. {storage_product} handles both natively; walked through SMB/NFS shares alongside iSCSI and FC LUNs. Their file server VM goes away.",
        "Talked tiering. ~70% of their data hasn't been touched in a year. Proposed all-flash for primary and an object tier for cold data, with policy-based movement. Cuts the flash they need to buy roughly in half.",
        "Short call. They asked whether {storage_product} supports synchronous replication between {hq_city} and the DR site. Yes, under 5ms RTT. Their link is ~3ms. Good.",
        "{contact_name} is skeptical of data reduction guarantees after {competitor} missed theirs. Explained our effective capacity guarantee - if we miss we ship drives at no cost. That landed.",
        "Spoke w/ {contact2_name}. Finance wants to know why storage keeps costing more every year. Showed the growth curve - data is up {growth}x in 4 yrs, cost per TB is actually down. Reframed it.",
        "Discussed NVMe over fabrics. Their hosts are on 25GbE, switches can do RoCE, but honestly the latency gain isn't worth the complexity for them yet. Stay on iSCSI, revisit at next refresh.",
        "Expansion is approved: one additional shelf, ~{tb}TB raw. Install during their maintenance window on {date}. Non-disruptive add, no data migration.",
        "Their Splunk retention requirement went from 90 days to a year for compliance. That alone is ~{tb}TB they didn't plan for. Pitched a capacity-optimized {storage_product} as a separate tier for logs.",
        "Spoke w/ {contact_first}. Array is 6 yrs old, controllers out of support, one failed last month and they ran on a single controller for 9 days waiting on a part. That scared everyone. Refresh is now urgent.",
        "Migration plan discussed: storage vMotion for the VMs over 2 weekends, robocopy w/ ACLs for the file shares, SQL via log shipping cutover. {se_name} estimates 3 weekends total.",
        "Snapshots vs. backups conversation. They were treating snapshots as backups. Gently pointed out that if the array dies, so do the snapshots. Opened a Vault conversation.",
    ],
    "next_steps": [
        "Pull 30 days perf data via Orvane Insight collector",
        "Size {storage_product} for {tb}TB usable w/ 3-yr growth",
        "Send effective capacity guarantee terms",
        "Quote expansion shelf + install services",
        "Draft migration runbook w/ {se_name}",
        "Confirm replication RTT between sites",
        "Schedule install window for {date}",
        "Price capacity tier for Splunk retention",
    ],
    "emails_out": [
        ("Storage sizing - draft", "Hi {contact_first},\n\nDraft sizing attached. Assumptions:\n- {tb}TB usable target at year 3\n- 3:1 reduction on VM data, 1.5:1 on file\n- ~{growth}TB/month growth\n- Sync replication to DR at ~3ms RTT\n\nIf any of those feel off, tell me now - it's much easier to fix before we quote.\n\n{rep_first}"),
        ("Effective capacity guarantee", "{contact_first},\n\nPer our conversation, the guarantee terms are attached. Short version: if the array doesn't hit the effective capacity in the sizing after 90 days of production data, we ship additional capacity at no charge. No fine print about 'qualifying workloads' beyond excluding already-encrypted or compressed data."),
        ("Perf data - what we saw", "Hi {contact_first} - headline from the 30-day collection: your array isn't slow, it's overloaded at very specific times. Backup window and month-end SQL overlap between 1 and 3am. Moving the backup start alone would help. Full report attached."),
        ("Expansion shelf - install {date}", "{contact_first},\n\nConfirming the shelf install on {date}, 7pm local. It's non-disruptive, but I'd still recommend no major changes that night. The field engineer will call 30 minutes before arrival. Order {order_number}."),
        ("Re: snapshots", "Snapshots are great for quick rollback, but they live on the same array, so they don't protect you from losing the array itself or from ransomware with admin access. Worth a separate conversation on Vault - 30 min?"),
    ],
    "emails_in": [
        ("array", "We're at {util}% on the main array as of this morning. Need to talk this week please."),
        ("RE: Storage sizing - draft", "3:1 on VMs feels optimistic. {competitor} promised us 4:1 and we got 2.2. Can you show me sizing at 2:1 as the worst case?"),
        ("controller failure", "{rep_first}, we lost a controller on the old array again. Same as last month. Mgmt is asking where we are on the replacement. Please call me."),
        ("Re: Expansion shelf - install", "Confirmed. Building security needs the engineer's full name and ID 24 hours ahead. Send to me and I'll forward."),
        ("file + block", "Quick q - can the file side do SMB3 with AD auth and access-based enumeration? We need ABE for HR shares."),
    ],
    "chatter": [
        "{account} array at {util}% and a controller already died once. this is happening in {quarter} whether they like it or not",
        "@{se_name} customer wants worst-case sizing at 2:1 reduction, {competitor} burned them on 4:1. can you rerun?",
        "fyi perf data at {account} shows backup + month-end SQL colliding 1-3am. easy win to show value before we quote",
        "{storage_product} expansion at {account} approved, install {date}. nice add-on",
        "anyone have a reference customer who actually measured their data reduction on {storage_product}? skeptical buyer",
        "heads up - {account} thinks snapshots = backup. opening Vault convo, @{rep_first} fyi",
    ],
}

TOPICS["data_protection"] = {
    "subjects": [
        "Backup / DR review - {account}",
        "Vault sizing and retention",
        "Ransomware recovery discussion",
        "Immutable backup requirements",
        "DR test results debrief",
        "Backup window issue",
        "RPO/RTO workshop",
        "Vault POC planning",
    ],
    "summaries": [
        "Spoke w/ {contact_first}. Backups run nightly to a dedupe appliance from {competitor} that's out of support in {quarter}. Backup window is 10 hours and growing. They miss SLAs a couple of times a week.",
        "RPO/RTO workshop. Tier 1 (ERP, SQL): RPO 15 min, RTO 4 hrs. Tier 2: RPO 24h, RTO 24h. Tier 3: best effort. They currently meet tier 2 for everything, which means tier 1 is badly underserved.",
        "Ransomware was the main topic. A peer company got hit and couldn't restore because the backup server was domain-joined and got encrypted too. {contact_title} wants immutable, air-gapped copies, full stop.",
        "Walked through Vault with immutable retention lock and a separate admin domain. Retention locks can't be shortened even by an admin with full creds. {contact_first} asked good questions about MFA on the management plane.",
        "DR test debrief. They failed over 12 VMs to the DR site, took 9 hours vs. a 4-hour target. Bottleneck was manual re-IP and DNS changes. Orchestrated failover would have cut it to under 1.",
        "Sizing: ~{tb}TB front-end protected data, daily change ~3%, 30 dailies, 12 monthlies, 7 yearly for finance. With dedupe that lands at roughly {storage_product}-class backup capacity, plus a cloud copy to {cloud}.",
        "{contact_first} asked about Microsoft 365 backup - they assumed Microsoft keeps everything forever. Explained retention gaps and the shared responsibility model. Vault Backup covers Exchange, OneDrive, SharePoint and Teams.",
        "Insurance renewal requires immutable backups, MFA on backup admin, and a tested restore in the last 12 months. They have none of the three. This is now a {quarter} must-do.",
        "Short call. POC approved - Vault appliance on loan for {weeks} wks, protecting a subset of ~50 VMs.",
        "POC results: full backup of the 50 VMs in 2h40m, incrementals under 15 min, instant VM recovery booted the test SQL server in 6 minutes. {contact_first} was visibly impressed by the instant recovery.",
        "Spoke w/ {contact2_name} on cost. Their concern is ongoing cloud storage spend for the offsite copy. Showed tiering to archive after 30 days - ~70% cheaper for the long-term retention.",
        "Discussed tape. Legal requires a copy outside the network for 7 years. Their tape library is ancient. Options: keep tape for yearlies only, or object storage with object lock. Legal needs to sign off either way.",
        "{competitor} is pushing a SaaS-only backup. {contact_first} likes the simplicity but restore times for {tb}TB over their internet link would be days. Showed the math.",
        "Backup failures traced to VSS timeouts on two SQL servers during heavy load. Not a backup product problem. Recommended shifting the SQL job schedule.",
    ],
    "next_steps": [
        "Schedule RPO/RTO workshop w/ app owners",
        "Size Vault for {tb}TB w/ 30/12/7 retention",
        "Ship POC appliance to {site_city}",
        "Send immutability + retention lock technical brief",
        "Quote Vault Backup for Microsoft 365 ({seats} users)",
        "Help customer run a documented restore test for insurance",
        "Model cloud tier costs in {cloud} for long-term retention",
        "Get legal sign-off on object lock vs. tape for 7-yr copies",
    ],
    "emails_out": [
        ("Backup and recovery - recap", "Hi {contact_first},\n\nRecap of today:\n- Tier 1 target: RPO 15 min / RTO 4 hrs (not met today)\n- DR test took 9 hrs, mostly manual re-IP and DNS\n- Insurance needs immutable copies + MFA + a tested restore\n\nI'd propose a {weeks}-week Vault POC on ~50 VMs to prove the recovery times. Want to set it up?\n\n{rep_first}"),
        ("Vault POC - results", "{contact_first},\n\nNumbers from the POC:\n- Full backup, 50 VMs: 2h40m\n- Incrementals: under 15 min\n- Instant recovery of SQL test VM: 6 min to boot\n- Restore of a 400GB file share: 38 min\n\nFull report attached. I'd like to walk {contact2_name} through it before the appliance goes back."),
        ("M365 retention gaps", "Hi {contact_first} - one-pager on what Microsoft does and doesn't retain by default. The short version is that deleted items and departed-employee mailboxes are the biggest gaps we see. Pricing for {seats} users is on {quote_number}."),
        ("Restore test for insurance", "{contact_first},\n\nWe can help you run and document a restore test that should satisfy the insurer's requirement. Takes about half a day. The output is a dated report with recovery times and screenshots. Want to grab a slot before {date}?"),
        ("Re: SaaS backup", "Rough math on full restore from a SaaS-only service: {tb}TB over a 1Gbps link at realistic throughput is several days. Fine for a single file, painful for a site-wide event. That's why we pair local instant recovery with a cloud copy."),
    ],
    "emails_in": [
        ("backup failures again", "{rep_first}, three failed jobs again last night. Same SQL servers. I need this fixed before the auditors are here on {date}."),
        ("RE: Vault POC - results", "The instant recovery demo sold my boss. Send pricing for the full environment. And please confirm the retention lock really can't be overridden by a domain admin - security will ask."),
        ("insurance questionnaire", "Attached is the questionnaire from our broker. Can you help me answer the backup section accurately? I don't want to overstate anything."),
        ("Re: Backup and recovery - recap", "Good summary. One correction - the DR site is in {site_city}, not {hq_city}. Changes the latency assumptions?"),
        ("POC", "When can the box ship? We have a rack slot ready and an IP reserved on the backup VLAN."),
    ],
    "chatter": [
        "Vault POC at {account} crushed it - 6 min instant recovery on their SQL box. pricing going out this week",
        "@{se_name} {account} security wants written confirmation retention lock can't be overridden by domain admin. do we have a doc?",
        "fyi insurance requirements are driving every backup deal I have right now. immutability + MFA + tested restore",
        "{competitor} pitching SaaS-only backup at {account}. restore time math is our friend here",
        "heads up {account} has auditors on site {date}. backup failures need to be fixed before then even though it's not our product",
        "M365 backup is an easy add on every Vault deal. nobody realizes Microsoft doesn't keep departed users' mail forever",
    ],
}

TOPICS["hci_virtualization"] = {
    "subjects": [
        "Virtualization strategy - {account}",
        "Licensing renewal impact",
        "Converge HCI overview",
        "Hypervisor migration options",
        "Converge POC scoping",
        "VM migration planning",
        "HCI sizing review",
        "Exit plan - {hypervisor}",
    ],
    "summaries": [
        "Spoke w/ {contact_first}. Their {hypervisor} renewal came in at roughly 3x last year after the licensing changes - per-core subscription, minimum core counts, bundle they don't need. {contact_title} wants options on the table before signing anything.",
        "Walked through three paths: 1) renew and right-size cores 2) move to Hyper-V on existing hardware 3) Converge HCI with its built-in hypervisor or with a supported alternative. They're most interested in 3 but nervous about migration risk.",
        "Sizing w/ {se_name}: ~400 VMs, {servers} hosts today, 3-tier with a SAN. Proposed a 6-node Converge cluster, all-NVMe, 2 x 25GbE for storage traffic. Fits in half a rack vs. the 2 racks they use now.",
        "Migration discussion. Converge migration tool does warm migration from the existing environment - initial sync while running, short cutover per VM. {contact_first} wants to see it on their oddest VMs first: a legacy Oracle box and two appliances with weird NIC configs.",
        "Not everyone is aligned. The infra team wants out of {hypervisor}, but the app team supporting SAP is worried about certification. Need to confirm SAP support status on our stack before this goes further.",
        "POC scoped: 3-node Converge cluster for {weeks} weeks. Success criteria: migrate 20 test VMs, failover a node under load, 1-click upgrade of firmware + hypervisor, backup integration with their existing tool.",
        "POC readout: node pull test passed, VMs restarted on surviving nodes in under 2 min. Rolling upgrade took 50 min across 3 nodes with no VM downtime. The backup integration needed a plugin update - resolved.",
        "{contact2_name} asked the right finance question: what does year 3 look like? Modeled 5-yr TCO: renewal path vs. Converge. Converge is ~{pct}% lower over 5 yrs, mostly licensing.",
        "Quick call. They signed a 1-year {hypervisor} renewal as a bridge. Buys time for the migration but they want to be off by {lease_end} next year.",
        "Talked about Kubernetes. Dev team runs a few clusters on VMs today. Converge can run containers alongside VMs, which helps the 'one platform' story for {contact_title}.",
        "{competitor} is pitching their HCI with a 'free migration' offer. Their nodes are cheaper but the support model is partner-only. {contact_first} has been burned by partner-only support before.",
        "Spoke w/ {contact_name}. They're not leaving {hypervisor} - too much tooling built around it. But they want to cut core count. Proposed fewer, denser {infra_product} hosts with higher clock speeds. Different deal, still a deal.",
        "Detailed networking review for HCI. Need jumbo frames end to end on the storage VLAN, LACP vs. active/standby decision, and their core switches are near end of life. Mesh came up naturally.",
        "Edge question: 14 retail sites each with 2 old servers. A 2-node Converge with a witness in the cloud would standardize them. Big potential expansion if HQ goes well.",
    ],
    "next_steps": [
        "Collect VM inventory export (RVTools-style) for sizing",
        "Confirm SAP certification status on Converge",
        "Build 5-yr TCO: renew vs. Converge",
        "Ship 3-node POC cluster",
        "Schedule migration test on the legacy Oracle VM",
        "Network design review w/ {se_name} - jumbo frames, LACP",
        "Price 2-node edge config for retail sites",
        "Get exact {hypervisor} renewal date and core count",
    ],
    "emails_out": [
        ("Options after the licensing change", "Hi {contact_first},\n\nAs discussed, three paths:\n1. Renew and reduce cores with denser {infra_product} hosts\n2. Move to Hyper-V on existing hardware\n3. Converge HCI\n\nEach has a different risk/cost profile. I've attached a one-page comparison. My honest view: 3 makes the most sense for you, but 1 is a legit bridge if timing is tight.\n\n{rep_first}"),
        ("Converge POC - success criteria", "{contact_first},\n\nDraft success criteria for the POC:\n- Migrate 20 test VMs incl. the Oracle box\n- Node failure under load, VMs back in under 5 min\n- Rolling firmware + hypervisor upgrade with no VM downtime\n- Backups via your current tool\n\nAnything missing? I'd rather add it now than argue about it later."),
        ("5-year TCO", "Hi {contact2_name},\n\nAttached is the 5-year view {contact_first} asked me to share with you. It includes hardware, licensing, support and power. The biggest swing is licensing, which accounts for most of the ~{pct}% difference. Happy to walk through assumptions.\n\n{rep_name}"),
        ("Re: SAP support", "Confirmed: SAP is supported on Converge for the versions you're running. Support note attached. {se_name} can join a call with your SAP Basis team to answer specifics."),
        ("Edge sites", "{contact_first} - you mentioned 14 retail sites with two aging servers each. A 2-node Converge with a cloud witness standardizes them on the same platform as HQ. Rough pricing per site attached, no pressure on timing."),
    ],
    "emails_in": [
        ("renewal quote", "Just got the {hypervisor} renewal. It's 3x last year. Can we talk tomorrow?"),
        ("RE: Converge POC - success criteria", "Add: must integrate with our existing monitoring (we use Splunk). And we need to test what happens when the witness is unreachable."),
        ("Re: Options after the licensing change", "We're leaning toward option 3 but my director wants to talk to a customer who has actually done the migration at our scale. Can you set that up?"),
        ("POC issue", "Backup job failed on the POC cluster overnight. Error says snapshot quiesce timed out on 2 VMs. Is this a known thing?"),
        ("bridge renewal", "FYI we signed a 1 year renewal to buy time. Doesn't change the plan, just the timeline."),
    ],
    "chatter": [
        "{hypervisor} renewal at {account} came in 3x. third one this month. Converge pipeline is going to be huge this year",
        "@{se_name} POC backup job failing on quiesce at {account} - plugin version? they're on the old one I think",
        "anyone have a Converge reference at ~400 VMs w/ SAP? {account} director wants to talk to a real customer",
        "fyi {account} signed a 1-yr bridge renewal. migration still on, just moved to next {fy}",
        "{competitor} offering 'free migration' on HCI at {account}. partner-only support though, customer hates that",
        "Converge POC at {account} passed every test. node pull, rolling upgrade, all clean. TCO going to finance {date}",
    ],
}

TOPICS["ai_gpu_initiative"] = {
    "subjects": [
        "AI infrastructure - {account}",
        "GPU server sizing for {initiative}",
        "Atlas AI discussion",
        "Inference vs. training requirements",
        "AI pilot scoping",
        "GPU lead times + power",
        "On-prem vs. {cloud} for AI workloads",
        "AI workstation options",
    ],
    "summaries": [
        "Spoke w/ {contact_first}. Leadership wants an {initiative} running by {quarter}. Nobody has defined the use case clearly. Current thinking is internal document search with a RAG pattern on their own data. Data can't leave the building, so on-prem is likely.",
        "Sizing call w/ {se_name}. They want to fine-tune a 7-8B parameter model and serve inference to ~500 internal users. Recommended a single Atlas AI node with {gpu_count} GPUs, 80GB+ memory each, NVMe scratch, 2 x 200Gb networking. Training at 70B would be a different conversation.",
        "{contact_title} burned ~$40k in {cloud} GPU instances in 6 weeks on experiments. Finance noticed. Now asking what it costs to own the gear. Built a breakeven model - at their utilization, owned hardware pays back in ~{days} days of steady use.",
        "Power is the problem. An Atlas AI node with {gpu_count} GPUs pulls ~10kW. Their server room has 2 x 30A circuits per rack. Options: colo, a dedicated high-density rack, or start smaller with 4 GPUs. They need facilities involved.",
        "Short call. Data science team doesn't need a server yet - 3 people running notebooks. Forge workstations with a single high-memory GPU each is the right starting point.",
        "Discussed software stack. They want Kubernetes with the GPU operator, a model serving layer, and a vector DB. We don't sell the software but {se_name} has a validated design and reference architecture.",
        "GPU lead times came up - currently {weeks} weeks for the high-end config. {contact_first} was surprised. Need to lock an allocation if they want hardware by {quarter}.",
        "Inference-only discussion. Their use case is a customer service copilot. Latency matters more than throughput. Smaller GPUs across 2 nodes for redundancy beats one big box here.",
        "{competitor} offered them a GPU cluster at a price that suggests they're buying the logo. Our angle: delivery date, validated reference design, and services to get to first model in weeks.",
        "Storage for AI: training data set is ~{tb}TB of documents and images. They want high-throughput parallel reads. Current NAS won't keep up. Proposed {storage_product} with a fast file tier.",
        "Spoke w/ {contact2_name}. Board approved {budget} for AI this {fy}. Half is earmarked for infrastructure. They want a proof of value within {days} days of hardware landing.",
        "Pilot is live. Inference cluster is serving the internal search tool to 200 users. GPU utilization avg ~{util}%. They're already asking about a second node.",
        "Concerns about governance. Legal wants to know where prompts and outputs are stored and for how long. Not our call, but it's slowing the hardware decision.",
        "{contact_first} was clear: they don't want a science project, they want a turnkey stack. Positioned the Atlas AI factory bundle with deployment services and ProCare Mission Critical.",
    ],
    "next_steps": [
        "Define use case + success criteria w/ {contact_first}",
        "Size Atlas AI node(s) for {initiative}",
        "Engage facilities re: 10kW+ rack power",
        "Build own vs. {cloud} breakeven model",
        "Request GPU allocation for {quarter} delivery",
        "Send validated reference architecture",
        "Quote Forge workstations for data science team",
        "Set up proof-of-value plan for {days} days post-delivery",
    ],
    "emails_out": [
        ("AI infrastructure - starting point", "Hi {contact_first},\n\nBased on what you described (fine-tune a ~8B model, serve ~500 internal users), a single Atlas AI node is a sensible starting point:\n- {gpu_count} GPUs, 80GB+ each\n- local NVMe for checkpoints and scratch\n- 2 x 200Gb networking\n\nPower draw is the thing to plan for first - roughly 10kW under load. Can we get facilities on the next call?\n\n{rep_first}"),
        ("Cloud vs. owned GPUs", "{contact2_name},\n\nAttached is the breakeven model. Inputs are your actual {cloud} spend over the last 6 weeks and a 60% sustained utilization assumption. At that level the owned node pays for itself in about {days} days. Below ~25% utilization, cloud stays cheaper - worth being honest about that."),
        ("GPU allocation", "Hi {contact_first} - current lead time on the {gpu_count}-GPU config is {weeks} weeks. I can request a build slot for {quarter} if we have a signed quote by {date}. Not trying to pressure you, but I'd rather tell you now than after."),
        ("Reference architecture", "{contact_first},\n\n{se_name}'s validated design for RAG on Atlas AI is attached - Kubernetes w/ GPU operator, model serving, vector DB, and how the storage tier is laid out. Not a sales doc, it's the actual build guide."),
        ("Workstations for the data science team", "Hi {contact_first} - for the three data scientists, Forge tower with a single high-memory GPU, 128GB RAM and 4TB NVMe each. Pricing on {quote_number}. Ships in ~2 weeks."),
    ],
    "emails_in": [
        ("AI", "My CEO came back from a conference and now we need an AI strategy by next month. Can you help me figure out what we actually need? Not looking to buy anything yet."),
        ("RE: AI infrastructure - starting point", "Facilities says we max out at 17kW per rack in the main room and that's if we don't put anything else in it. Can you send the exact power spec? They want the PSU ratings and typical draw."),
        ("Re: GPU allocation", "Lead time is a problem. {competitor} says they can do 4 weeks. Is that real?"),
        ("pilot results", "{rep_first} - pilot is going well. GPU util is higher than expected and people are actually using the thing. Can you price a second node? Same config."),
        ("legal questions", "Legal wants to know if the GPU servers phone home or send any telemetry to Orvane. Please confirm in writing."),
    ],
    "chatter": [
        "{account} wants AI by {quarter}, no use case defined. classic. @{se_name} can you do a 1hr workshop to shape it?",
        "power is the real constraint on every AI deal. {account} has 17kW/rack max. that's one Atlas AI node and nothing else",
        "fyi {competitor} quoting 4 wks on GPUs at {account}. I don't believe it but customer does. what's our real date?",
        "{account} AI pilot at {util}% GPU util after 3 weeks. second node is coming",
        "heads up - legal at {account} wants written confirmation on telemetry from Atlas AI. who owns that answer?",
        "breakeven model vs {cloud} is landing well. finance teams are seeing those GPU bills and freaking out",
    ],
}

TOPICS["networking_upgrade"] = {
    "subjects": [
        "Network refresh - {account}",
        "Mesh switching overview",
        "Core / access switch sizing",
        "Campus refresh: PoE budget",
        "Data center fabric discussion",
        "Network design review",
        "Switch EOL replacement",
        "Mesh POC",
    ],
    "summaries": [
        "Spoke w/ {contact_first}. Core switches from {competitor} go end-of-support in {quarter}. They also have ~40 access switches across 3 floors, mix of 1G, no PoE+ for the new APs. Full refresh is on the table.",
        "Campus design: 48-port PoE+ access with mGig ports for Wi-Fi 7 APs, 2 x 25G uplinks per stack, collapsed core. PoE budget per switch needs to cover APs, phones and ~20 cameras per floor. {se_name} is running the math.",
        "DC fabric conversation. They're running a classic 3-tier with spanning tree and hate it. Proposed a leaf-spine with Mesh 25/100G - EVPN-VXLAN, 2 spines, 4 leaves to start.",
        "Their network team is 2 people who both know {competitor}'s CLI cold. Biggest objection is retraining. Showed the Mesh CLI - it's very close to what they know. Fewer objections after that.",
        "Short call. They need 6 x 48-port switches for a new floor, quickly. Standard config, no design work. Quote today.",
        "Discussed VLAN design for the HCI cluster: separate VLANs for management, storage, vMotion and VM traffic, jumbo frames on storage, BMCs on an isolated OOB network. Their current network is flat. That's a security conversation too.",
        "Security wants 802.1X on every access port and dynamic VLAN assignment. Mesh supports it with their existing RADIUS. Need to confirm their NAC integration.",
        "Mesh POC: 2 leaves, 2 spines in their lab for {weeks} weeks. Testing EVPN, failover, and automation via the REST API with their Ansible playbooks.",
        "POC results: link failover under 200ms, spine reboot with no dropped pings on the test VMs, Ansible playbooks worked after small tweaks. They want to proceed with the DC fabric.",
        "{contact2_name} asked about subscription vs. perpetual licensing on switches. {competitor} moved to subscription and they hate it. Mesh is perpetual with optional support - that was a big point in our favor.",
        "Wi-Fi isn't us, but the switches have to power whatever APs they choose. Recommended mGig ports anywhere they might put Wi-Fi 7.",
        "Branch network: 22 branches, each with a small switch and a firewall. Proposed a standard branch kit - one Mesh 24-port PoE switch, pre-configured, zero-touch provisioning. Ship and plug in.",
        "Spoke w/ {contact_name}. Network refresh is unfunded this year. They'll patch and pray until next {fy}. Staying in touch.",
        "Outage postmortem came up - a single access stack lost both uplinks when someone reseated an SFP in the wrong closet, and spanning tree took 40+ seconds to reconverge. Took down the warehouse scanners for a shift. That incident is why the budget suddenly exists.",
    ],
    "next_steps": [
        "Collect current switch inventory + port utilization",
        "Calculate PoE budget per floor",
        "Draft leaf-spine design w/ {se_name}",
        "Quote 6 x 48-port PoE+ access switches",
        "Ship Mesh POC gear to lab",
        "Confirm RADIUS/NAC integration for 802.1X",
        "Build branch kit standard config",
        "Share Mesh CLI comparison doc with network team",
    ],
    "emails_out": [
        ("Network refresh - first pass", "Hi {contact_first},\n\nFirst pass at the campus refresh:\n- 48-port PoE+ access with mGig for future APs\n- 2 x 25G uplinks per stack\n- collapsed core pair\n- perpetual licensing, no subscription required\n\nI need port utilization and the AP/camera count per floor to finalize the PoE budget.\n\n{rep_first}"),
        ("Mesh POC - test plan", "{contact_first},\n\nProposed POC tests:\n1. EVPN-VXLAN between 2 leaves\n2. Spine failure with no traffic loss\n3. Link failover time\n4. Ansible automation via REST API\n5. Config rollback\n\nGear can ship by {date}."),
        ("Quote - 6 x 48-port switches", "Hi {contact_first} - quote {quote_number} attached for the 6 access switches, optics and stacking cables. In stock, ships in 3-5 days once we have a PO."),
        ("Branch kit", "{contact_first},\n\nHere's what a standard branch kit looks like: one Mesh 24-port PoE switch, pre-staged with your config template, zero-touch provisioning on first boot. Branch staff plug it in and you see it in the console. Pricing per site attached."),
        ("CLI comparison", "For your network team - side-by-side of common {competitor} commands and the Mesh equivalents. Most of it is identical or close. {se_name} is happy to do a 1-hr hands-on session."),
    ],
    "emails_in": [
        ("switches", "Need 6 switches for the 4th floor buildout. 48 port PoE+. Need them by {date}. Can you do it?"),
        ("Re: Mesh POC - test plan", "Add one: we need to test interop with our existing {competitor} core during the migration since we won't cut over everything at once."),
        ("PoE", "Floor counts attached. Heads up the cameras on 2 are PoE++ so budget accordingly."),
        ("RE: Network refresh - first pass", "Port utilization is low, most switches under 40% used. Can we go with fewer ports?"),
        ("licensing q", "Confirm there's no subscription required to keep the switches running. That's a dealbreaker for us after what {competitor} did."),
    ],
    "chatter": [
        "{account} core switches EOL in {quarter}. full campus + DC refresh on the table. @{se_name} let's do design together",
        "perpetual licensing on Mesh is winning deals. {competitor}'s subscription move is our best sales tool",
        "fyi {account} needs 6 switches by {date}, simple deal, just need stock confirmation",
        "Mesh POC at {account} passed. EVPN, failover under 200ms, Ansible worked. moving to proposal",
        "heads up {account} has PoE++ cameras on 2 floors - make sure the access config has enough budget",
        "branch kit standard is a great expansion play - {account} has 22 branches",
    ],
}

TOPICS["edge_deployment"] = {
    "subjects": [
        "Edge compute - {account}",
        "Outpost sizing for remote sites",
        "Store / plant edge standard",
        "Edge rollout plan - {qty} sites",
        "Ruggedized edge discussion",
        "Edge site survey results",
        "Remote management for edge",
        "Edge pilot - {site_city}",
    ],
    "summaries": [
        "Spoke w/ {contact_first}. {qty} sites, each with a tower server in a closet running POS backend, a camera NVR and a file share. Half are 7+ yrs old. Nobody on site is technical. They want something they can ship and forget.",
        "Edge standard proposed: Outpost short-depth server, 2-node w/ a cloud witness for the bigger sites, single node for the small ones. Fits in a wall-mount rack. Orvane Insight for remote monitoring and firmware updates.",
        "Site survey at {site_city} plant: server sits next to a press line, ambient temp hits 40C in summer, lots of dust. Standard rack gear will cook. Outpost's extended temp rating and filtered bezel matter here.",
        "Remote management was the main topic. They've had techs drive 3 hours to power-cycle a box. BMC with out-of-band access over a cellular modem would have saved that trip. Strong interest.",
        "Pilot at {site_city} is live. Install took 90 minutes - store manager plugged in power and network, rest was remote. Workloads migrated overnight. {contact_first} wants to roll out to 20 more sites in {quarter}.",
        "Spoke w/ {contact2_name} about rollout logistics. Ship to a staging center, pre-image, ship to sites in waves of 25. Store hours are 7a-10p so installs have to happen early morning. Field services quote needed.",
        "Security conversation: edge boxes sit in unsecured closets. They need secure boot, TPM, encrypted drives with remote key management, and chassis intrusion alerts. All checkboxes on Outpost.",
        "Video analytics is the reason the budget exists. Loss prevention wants AI on camera feeds at each store - needs a small GPU per site. Outpost with a single low-profile GPU fits.",
        "Bandwidth to sites is limited - some are on 50Mbps broadband. Anything that needs constant cloud connectivity is a non-starter. Local processing with sync to {cloud} overnight.",
        "{competitor} is pitching a cheaper box with no BMC. {contact_first} hasn't realized what that means operationally yet. Planned a demo of a remote BIOS update over OOB.",
        "Quick check-in. 60 of {qty} sites done. Two DOA units, replaced next-day. Overall smooth.",
        "Talked through power: several sites have unreliable power. Recommended a small UPS per site with network shutdown integration so the Outpost shuts down gracefully.",
        "Oil & gas use case - remote well pads, no climate control, satellite link. Bastion rugged laptops for techs plus a hardened Outpost at the field office. They're also looking at {competitor} but not seriously.",
        "{contact_first} asked about lifecycle - they want 7 years on edge gear, not 5. ProCare can be extended to year 7 on Outpost; pricing on the out-years is the question.",
    ],
    "next_steps": [
        "Send Outpost spec + extended temp rating",
        "Quote 2-node and single-node site configs",
        "Plan staging + wave shipping for {qty} sites",
        "Demo remote BIOS update over OOB",
        "Price field services for early-morning installs",
        "Get UPS model list for network shutdown integration",
        "Confirm 7-yr ProCare pricing on Outpost",
        "Schedule pilot readout with {contact2_name}",
    ],
    "emails_out": [
        ("Edge standard - proposal", "Hi {contact_first},\n\nProposed site standard:\n- Large sites: 2 x Outpost w/ cloud witness\n- Small sites: 1 x Outpost\n- Wall-mount short-depth rack\n- OOB management over cellular\n- Orvane Insight for monitoring and firmware\n\nPilot at {site_city} first, then waves of 25. Pricing on {quote_number}.\n\n{rep_first}"),
        ("Pilot recap - {site_city}", "{contact_first},\n\nPilot recap: 90-minute install, store manager did the physical part, everything else was remote. Workloads moved overnight, no impact to trading hours. I'd like to lock dates for the next 20 sites."),
        ("Rollout logistics", "Hi {contact2_name} - attached is the logistics plan. Staging center images and labels each unit with the site ID, ships in waves of 25, field tech on site by 6am for the swap. Old units come back for ITAD in the same box."),
        ("Remote BIOS update demo", "{contact_first}, I'd like to show your team a full BIOS + BMC update on an Outpost over the OOB link with no one on site. 20 minutes. Worth it before you compare against boxes without a BMC."),
        ("Re: 7-year support", "ProCare on Outpost can be extended through year 7. Years 6-7 are priced annually; quote attached for the full term so finance can see it."),
    ],
    "emails_in": [
        ("site 114", "The server at store 114 is down again. That's the third time this quarter. Can we accelerate the new hardware for that site?"),
        ("RE: Edge standard - proposal", "Looks good. What happens if the cellular modem dies? Is there a fallback for OOB?"),
        ("Re: Pilot recap", "Store manager said it was the easiest IT thing they've ever done. That's a first. Let's go."),
        ("install schedule", "Need to move sites 22-30 out one week, they have a promo event. Sorry for the late notice."),
        ("temperature", "Plant manager at {site_city} sent a pic of the closet thermometer, 43C this afternoon. Will the Outpost survive that?"),
    ],
    "chatter": [
        "{account} edge pilot at {site_city} done in 90 min, store mgr did the plugging in. {qty} sites to go, nice",
        "@{se_name} customer has a closet hitting 43C at {site_city}. Outpost extended temp should cover it, can you confirm?",
        "fyi {competitor} pitching no-BMC edge boxes at {account}. we're doing a remote BIOS update demo to make the point",
        "edge rollout at {account} 60/{qty} sites done. 2 DOAs, both replaced next day",
        "heads up ops - {account} moved sites 22-30 out a week. please update the field schedule",
        "anyone have a hardened Outpost reference in oil & gas? {account} has well pads w/ satellite links",
    ],
}

TOPICS["pricing_negotiation"] = {
    "subjects": [
        "Pricing discussion - {quote_number}",
        "Negotiation call w/ procurement",
        "Discount request - {discount}%",
        "Best and final - {account}",
        "Pricing review w/ {contact2_name}",
        "Price match request vs. {competitor}",
        "Deal desk approval needed",
        "Payment terms discussion",
    ],
    "summaries": [
        "Procurement ({contact2_name}) came back asking for {discount}% off the quote. Currently at {pct}%. Said I'd take it to deal desk but needed something in return - multi-year commit or bigger initial order.",
        "Price match request against {competitor}. Their quote is ~8% lower but excludes deployment and only includes basic warranty. Built a line-by-line comparison. Once ProCare Plus and services were in, we were within 2%.",
        "Spoke w/ {contact_name}. They need to come in under {budget} or the project doesn't happen this year. Gap is ~{amount}. Options: trim the config, phase it, or finance it through Orvane Financial Services.",
        "Negotiation call. They want net 60 instead of net 30, price protection for 12 months, and free shipping. Agreed to free shipping, countered on net 45, price protection for 6 months on the same configs.",
        "Deal desk approved {discount}% contingent on PO by {date}. Communicated the deadline clearly to {contact_first}. They know it's real.",
        "{contact2_name} was tough. Opened with 'we've never paid list for anything in our lives' and asked for {discount}%. Explained we're already well below list. They didn't care. Will get a final number to them Friday.",
        "Short call. Procurement wants a single price per unit inclusive of everything - no separate lines for services and support. Reformatting the quote.",
        "Bundling helped. Adding the Clarity monitors and Tether docks to the laptop order unlocked a bigger tier discount across the whole deal.",
        "{contact_first} admitted the discount ask is a procurement KPI - they get measured on % saved off first quote. Noted for next time: open with room.",
        "Reverse auction. Procurement ran an e-auction with 4 vendors. We came in second on price. They're still talking to us because of delivery date - {competitor} can't ship until {quarter}.",
        "Price increase notice from us lands {date}. Told {contact_first} that anything quoted before then is protected if they PO within 30 days. That moved them.",
        "Spoke w/ {contact2_name}. Year-end budget flush - they need to spend {amount} before {date} or lose it. Less about discount, more about what can ship and invoice in time.",
        "Their CFO personally reviewed the quote and asked why support is {pct}% of the total. Walked through ProCare Mission Critical vs. ProCare Plus. They downgraded the non-production hosts to ProCare Plus, which cut ~{amount}.",
        "Asked for MFN pricing. Legal won't agree to that. Offered price protection on their configs for 12 months instead.",
        "Best and final submitted at {discount}% off. Walk-away point is next quarter's pricing, they know that.",
    ],
    "next_steps": [
        "Submit deal desk request for {discount}%",
        "Build line-by-line vs. {competitor} quote",
        "Reformat quote as all-in unit price",
        "Get Orvane Financial Services payment options",
        "Confirm PO deadline of {date} in writing",
        "Re-quote w/ ProCare Plus on non-prod hosts",
        "Send best and final on {quote_number}",
        "Check what can ship + invoice before {date}",
    ],
    "emails_out": [
        ("Updated pricing - {quote_number}", "Hi {contact2_name},\n\nUpdated quote attached at {discount}% off list. This is contingent on a PO by {date}; after that it reverts to the original quote. I pushed hard internally for this one.\n\nBest,\n{rep_name}"),
        ("Comparison vs. {competitor}", "{contact_first},\n\nLine-by-line attached. Once you normalize for warranty level (their quote is basic, ours is ProCare Plus 3-yr next-business-day onsite) and deployment services, the gap is about 2%. Happy to walk procurement through it."),
        ("Payment options", "Hi {contact2_name} - Orvane Financial Services can structure this as a 36-month lease, or 90-day deferred payment with the same total. Either keeps you under {budget} this fiscal year. Details attached."),
        ("Best and final", "{contact2_name},\n\nThis is the best I can do: {discount}% off, free shipping, net 45, and 6-month price protection on the same configs. It's valid through {date}. I'd love to get this done.\n\n{rep_name}"),
        ("Re: price increase", "Confirming: anything on {quote_number} is protected at current pricing if the PO is received within 30 days of the quote date, even after the {date} increase."),
    ],
    "emails_in": [
        ("RE: Updated pricing", "Thanks {rep_first}. Still above budget. {competitor} is lower and our CFO has their number. Is there anything else you can do?"),
        ("pricing", "Need your best price by EOD Thursday. We are making a decision Friday."),
        ("Re: Best and final", "We'll take it. PO to follow. Please confirm shipping is included and send a W-9."),
        ("quote format", "Procurement says the quote needs to be all-inclusive per unit. No separate service lines. Our system can't handle it otherwise. Sorry."),
        ("RE: Comparison vs. {competitor}", "I see your point on warranty but finance only sees the top line number. Can you get closer?"),
    ],
    "chatter": [
        "deal desk - need {discount}% on {quote_number} for {account}. {competitor} in at lower number, PO committed by {date} if we get there",
        "{account} procurement gets bonused on % saved off first quote. always open with room on this one",
        "fyi reverse auction at {account}, we came in 2nd on price but 1st on delivery. still alive",
        "@{rep_first} year-end flush at {account} - {amount} has to ship and invoice by {date}. what's in stock?",
        "got the {account} deal over the line at {discount}%. thanks deal desk",
        "heads up: price increase {date} is creating real urgency. use it, but honestly",
    ],
}

TOPICS["po_followup"] = {
    "subjects": [
        "PO status - {quote_number}",
        "Following up on PO",
        "PO received - {po_number}",
        "PO discrepancy",
        "Procurement status check",
        "PO stuck in approval",
        "Vendor setup for PO",
        "PO revision needed",
    ],
    "summaries": [
        "Checked w/ {contact_first} on the PO. It's sitting in their approval queue with {contact2_name}. Should release this week.",
        "PO {po_number} received for {amount}. Doesn't match the quote - they used old pricing from the previous version. Sent back for revision.",
        "Spoke w/ procurement. PO is approved but they need us set up as a vendor in their system first. Sent W-9, banking form, and insurance cert.",
        "PO stuck - their system flagged it because ship-to is a new location not in their address master. {contact_first} is chasing it.",
        "Left VM for {contact_first} re: PO timing. Quote expires {date}.",
        "PO {po_number} received. Quantity is {qty}, quote said 250. Confirmed with {contact_first} it's intentional - they cut the last batch. Booked as-is.",
        "Procurement says PO goes out after their board meeting on {date}. Nothing I can do until then.",
        "{contact_first} said the PO was sent last Tuesday. We never got it - turns out it went to an old rep's email. Re-sent to the order inbox, booked same day.",
        "PO needs a revision - they want to split it across two cost centers. New PO numbers coming.",
        "Spoke w/ {contact2_name}. PO approved, but they need a signed copy of our terms on their paper. Sent to legal.",
        "Quick one. PO received, booked as {order_number}. Ship date confirmed.",
        "PO references the wrong quote number. Same items, but it'll bounce in order entry. Asked {contact_first} to issue a change order referencing {quote_number}.",
        "Procurement switched systems mid-quarter and every PO in flight got stuck. They're manually releasing them one by one. Ours is somewhere in that pile.",
        "Following up on PO for 3rd time. {contact_first} is responsive but procurement isn't. Asked if I can talk to procurement directly. They agreed to set up a call.",
    ],
    "next_steps": [
        "Follow up w/ {contact_first} on PO {date}",
        "Send W-9 + vendor setup forms",
        "Request PO revision to match {quote_number}",
        "Book order once PO received",
        "Send legal the customer's terms for review",
        "Call procurement directly re: approval",
        "Confirm ship-to address is in their system",
        "Extend quote if PO slips past {date}",
    ],
    "emails_out": [
        ("PO for {quote_number}", "Hi {contact_first}, just checking in on the PO for {quote_number}. The quote is good through {date}. Anything I can help with on the procurement side?\n\n{rep_first}"),
        ("Vendor setup docs", "{contact_first},\n\nAttached for your vendor setup:\n- W-9\n- Remit-to / banking form\n- Certificate of insurance\n\nLet me know if your AP team needs anything else.\n\n{rep_name}"),
        ("PO {po_number} - revision needed", "Hi {contact_first},\n\nThanks for the PO. It reflects pricing from the previous quote version - the current version is {quote_number} at {amount}. Can procurement issue a revision? Once I have it I can book same day.\n\n{rep_first}"),
        ("PO received - thank you", "{contact_first},\n\nGot PO {po_number}, booked as {order_number}. Estimated ship {date}. I'll send tracking as soon as it's out.\n\nThanks again,\n{rep_first}"),
        ("Quote expiring {date}", "Hi {contact_first} - quick heads up that {quote_number} expires {date}. If the PO won't make it by then, let me know and I'll request an extension before it lapses."),
    ],
    "emails_in": [
        ("PO", "PO attached. Please confirm receipt."),
        ("RE: PO for {quote_number}", "Its in approvals. {contact2_name} is out until Monday. Should be next week."),
        ("vendor registration", "Hi, you need to register in our supplier portal before we can issue the PO. Link is in the attached instructions. It usually takes 5-7 business days."),
        ("Re: PO revision", "Sorry about that. Revised PO attached. Same number with a -1 at the end."),
        ("po delay", "Board meeting got pushed to {date}. PO won't go out before then. Can you hold pricing?"),
    ],
    "chatter": [
        "PO {po_number} from {account} landed! booked as {order_number}",
        "{account} PO went to {old_rep}'s old email, ugh. rebooked same day. ops can we check that forwarding?",
        "heads up {account} PO stuck in procurement system migration. could slip into next qtr",
        "anyone know who handles vendor setup at {account}? they want a W-9 and insurance cert",
        "@{rep_first} {account} PO doesn't match quote, they used old pricing. sent back",
        "fyi {account} board meets {date}, PO after that. moving close date",
    ],
}

TOPICS["order_status_delay"] = {
    "subjects": [
        "Order status - {order_number}",
        "Ship date slipped - {order_number}",
        "Backorder update",
        "Partial shipment question",
        "Delivery delay - customer escalation",
        "Lead time update for {product}",
        "Order tracking request",
        "Supply constraint - alternatives",
    ],
    "summaries": [
        "{contact_first} called asking where {order_number} is. Checked: it's on backorder, component shortage on the {product}. New estimated ship {date}. Customer not happy - they have new hires starting next week.",
        "Order slipped {weeks} wks due to a memory shortage. Offered alternatives: 1) ship the units we have now in partial shipments 2) swap to a similar config that's in stock. {contact_first} wants to talk to their team.",
        "Spoke w/ {contact_first}. They agreed to the config swap - 32GB instead of 16GB at no extra cost because the 16GB part is constrained. Re-booked as a new line. Ship in 5 days.",
        "Partial shipment of {qty} units went out today. Remainder expected {date}. Sent tracking.",
        "Escalation: {contact2_name} called my manager directly about the delay. Fair - we committed to {date} and missed it. Got supply chain on a call, they found inventory in another region. Shipping Monday.",
        "Order is complete but stuck at the carrier - delivery attempted, nobody at the dock. Customer's receiving closes at 3pm. Re-scheduled with a delivery appointment.",
        "Proactive call to {contact_first}: GPU allocation for their order is delayed by the supplier. Now {weeks} weeks. Better they hear it from me than from the portal.",
        "Short one - customer confirmed receipt of {order_number}, all {qty} boxes. Closing the loop.",
        "Order shipped to the wrong site - ship-to was HQ, they wanted {site_city}. Their PO had HQ though. Arranged a re-route at our cost as goodwill, carrier picks up tomorrow.",
        "Rack integration order delayed because one of the switches came in DOA at our integration center. Replacement in 3 days, then 48-hr burn-in. New ship {date}.",
        "{contact_first} asked if they can cancel the backordered portion and keep what shipped. Checked with order management - yes, no restocking fee since we caused the delay.",
        "Customs hold on the Canadian portion of the order. Broker needs a commercial invoice correction. Order ops is working it.",
        "Spoke w/ {contact_name}. They're understanding about the delay but need a firm date, not 'estimated'. Explained what we know and what we don't. Committed to updates every Tuesday until it ships.",
        "Order on hold - not a supply issue, it's a credit hold. Looped in finance. Customer had an open invoice past 60 days.",
    ],
    "next_steps": [
        "Send updated ETA on {order_number} to {contact_first}",
        "Get supply chain to confirm firm ship date",
        "Offer in-stock config alternative",
        "Book replacement line on new config",
        "Arrange delivery appointment w/ receiving",
        "Re-route shipment to {site_city}",
        "Weekly Tuesday update until shipped",
        "Check with finance on credit hold",
    ],
    "emails_out": [
        ("Order {order_number} - updated ship date", "Hi {contact_first},\n\nI wanted you to hear it from me: {order_number} is now estimated to ship {date}, about {weeks} weeks later than planned, because of a component shortage on the {product}. Two options to get you moving sooner:\n1. Partial shipment of what's available now\n2. Swap to an in-stock config with 32GB at the same price\n\nLet me know which you prefer.\n\n{rep_first}"),
        ("Tracking - partial shipment", "{contact_first}, {qty} units shipped today on {order_number}. Tracking attached. The remaining units are expected {date} and I'll update you if that moves."),
        ("Apology and next steps", "Hi {contact2_name},\n\nI'm sorry - we committed to {date} and missed it. Supply chain found inventory in another region and it ships Monday. I'll confirm once it's on the truck. Going forward I'll give you a weekly update every Tuesday.\n\n{rep_name}"),
        ("Delivery appointment", "{contact_first} - the carrier attempted delivery after your dock closed. I've set an appointment for {date} before noon. Reference is on {order_number}."),
        ("Weekly update - {order_number}", "Hi {contact_first}, weekly update: no change. Still tracking to {date}. Component has shipped to our factory, which is a good sign. Next update Tuesday."),
    ],
    "emails_in": [
        ("where is our order", "{rep_first}, we were told {date}. It's now past that and the portal still says 'in production'. We have 40 new hires starting Monday. What is going on?"),
        ("RE: Order - updated ship date", "We'll take option 2. Please make sure the image still works with the different memory config."),
        ("wrong address", "The order went to HQ but it needs to be at {site_city}. I know the PO said HQ but that was a mistake on our side. Can you help?"),
        ("Re: Weekly update", "Appreciate the weekly updates even when there's no news. Thanks."),
        ("cancel?", "Can we cancel the backordered units and keep what we have? We sourced the rest elsewhere because we couldn't wait."),
    ],
    "chatter": [
        "{order_number} for {account} slipped again. {weeks} wks now. anyone in supply chain who can find stock?",
        "memory shortage is hitting {product} orders. swap to 32GB config is in stock and customers are happy to take it",
        "heads up {account} escalated the delay to my manager. deserved, we missed {date}",
        "@{rep_first} credit hold on {account}'s order - not supply. can you nudge finance?",
        "fyi carrier missed {account}'s dock window AGAIN. receiving closes at 3. appointments please",
        "proactively telling customers about delays before the portal does saves so much pain. {account} thanked me",
    ],
}

TOPICS["warranty_renewal"] = {
    "subjects": [
        "ProCare renewal - {account}",
        "Support contract expiring {date}",
        "Warranty extension options",
        "ProCare tier review",
        "Renewal quote - {quote_number}",
        "Co-term support contracts",
        "Post-warranty support options",
        "ProCare Mission Critical renewal",
    ],
    "summaries": [
        "ProCare on {servers} servers expires {date}. Called {contact_first} - they want to renew but cut cost. Proposed downgrading non-prod hosts to ProCare and keeping Mission Critical on prod.",
        "Renewal is messy: 14 separate contracts with different end dates. Proposed co-terming everything to {lease_end} so they get one renewal a year. {contact_first} loved that idea.",
        "Spoke w/ {contact_first}. They're debating whether to renew support on 6-yr-old servers or replace them. Year 6 support is priced at a premium. Showed the replacement math - new gear with 3-yr ProCare Plus is close to 2 years of renewal on the old.",
        "Renewal booked. ProCare Plus, 1 yr, {amount}.",
        "A third-party maintenance provider quoted them ~40% less. Pointed out they don't have firmware access, parts are refurbished, and there's no escalation to engineering. {contact_first} said they'll keep us on prod and consider third-party on the old lab gear.",
        "Asked about extended warranty on laptops - years 4 and 5. They're stretching the fleet. ProCare extension is possible on most models; quoted per device.",
        "Spoke w/ {contact2_name}. Finance wants to understand what they actually used. Pulled case history: 47 cases last year, 12 onsite dispatches, 3 Sev 1. That's real value.",
        "Lapsed contract. Support expired {days} days ago and they didn't notice until a drive failed. Reinstatement requires a hardware inspection and a fee. Not a great conversation.",
        "Accidental damage add-on came up for their field laptops. Breakage rate on the Bastion fleet is ~{pct}%/yr. ADP pays for itself at that rate.",
        "Renewal is tied to a broader conversation - they want to know what refresh would look like before committing. Sending both.",
        "ProCare Mission Critical renewal for the SAN. 4-hr parts and labor, 24x7, assigned technical account manager. They value the TAM more than anything else.",
        "Quick call. {contact_first} asked for a list of all assets with warranty end dates. Exported from the portal and sent.",
        "Customer asked why renewal went up {pct}%. Partly list increase, partly because they're now in year 5 on some units. Offered a 2-yr renewal at a locked rate.",
        "Keep-your-drive add-on: their security policy says no failed drives leave the building. Added KYD across all storage and servers.",
    ],
    "next_steps": [
        "Send renewal quote on {quote_number}",
        "Co-term all contracts to {lease_end}",
        "Pull case history for value conversation",
        "Quote replacement as alternative to year 6 renewal",
        "Export asset list w/ warranty end dates",
        "Add keep-your-drive to server and storage lines",
        "Quote accidental damage for Bastion fleet",
        "Process reinstatement for lapsed contract",
    ],
    "emails_out": [
        ("ProCare renewal - expiring {date}", "Hi {contact_first},\n\nYour ProCare coverage on {servers} servers expires {date}. Renewal quote attached on {quote_number}. I've split it into two options:\n- A: like-for-like\n- B: Mission Critical on production, ProCare Plus on non-prod (saves ~{pct}%)\n\n{rep_first}"),
        ("Co-terming your support", "{contact_first},\n\nRight now you have 14 contracts ending on 14 dates. I can co-term everything to {lease_end} so you get one renewal, one PO, one invoice. The first year is prorated. Want me to build it?"),
        ("Your support usage last year", "Hi {contact2_name} - quick summary of what your team used under ProCare last year: 47 cases, 12 onsite dispatches, 3 Severity 1 incidents (avg time to resolution 3.2 hours). Hopefully useful context for the renewal."),
        ("Renew vs. replace", "{contact_first},\n\nSide by side for the 6-yr-old hosts: renewing year 6 support vs. replacing with new {infra_product} and 3-yr ProCare Plus. Replacement costs more upfront but less over 3 years, and you lose the risk of parts availability. Attached."),
        ("Lapsed coverage", "Hi {contact_first}, I'm sorry about the timing on the drive failure. To reinstate coverage we need a quick remote health check on the affected systems and a reinstatement fee. I've asked if we can waive the fee given the circumstances - will let you know."),
    ],
    "emails_in": [
        ("support renewal", "{rep_first} - the support renewal came in higher than last year. What changed? Need an explanation for finance."),
        ("RE: Co-terming your support", "Yes please. This would make my life so much easier."),
        ("third party quote", "We got a quote from a third-party maintenance company for about 40% less. Can you match it? If not, help me understand what we lose."),
        ("warranty", "Can you send me a list of everything we own and when the warranty ends? Our asset system is a mess."),
        ("drive failed - no coverage?", "Drive failed on our file server and support says our contract expired. Nobody told us! We need this fixed today."),
    ],
    "chatter": [
        "{account} ProCare lapsed {days} days ago and a drive just failed. can we waive reinstatement fee? they're good customers",
        "co-terming {account}'s 14 contracts to {lease_end}. renewals team, can you help build it?",
        "third party maintenance is coming up on every renewal now. the firmware access argument works",
        "fyi {account} renewing Mission Critical on SAN - TAM is the reason. Shout out to their TAM",
        "@{rep_first} {account} asking why renewal went up {pct}%. do we have the list increase letter?",
        "renew vs replace analysis on year 6 hardware turned a renewal into a refresh at {account}",
    ],
}

TOPICS["support_escalation"] = {
    "subjects": [
        "Escalation - case {case_number}",
        "Sev 1: {account} production down",
        "Customer escalation - repeat failures",
        "Exec escalation from {contact_name}",
        "Support escalation follow-up",
        "Case {case_number} - no resolution after {days} days",
        "Escalation review w/ support mgmt",
        "Root cause analysis request",
    ],
    "summaries": [
        "{contact_first} called me directly - case {case_number} has been open {days} days with no resolution. Storage controller keeps rebooting. Support has replaced the controller twice. Escalated to duty manager.",
        "Sev 1 last night: production cluster lost quorum after a node failure and a network blip at the same time. Support engaged within 15 min, cluster back in 2 hrs. RCA requested.",
        "Spoke w/ {contact_name}. Frustrated. Laptop motherboard failures on {pct}% of the {product} fleet in the last 90 days. Asked for a fleet-level investigation, not one case at a time.",
        "Escalation call w/ support management, {contact_first}, and {se_name}. Agreed: dedicated engineer, daily updates, and engineering engaged on the firmware angle. Customer calmer by the end.",
        "RCA delivered for {case_number}: firmware bug in the NIC under sustained high throughput with a specific driver version. Fix in {firmware}. Customer accepted the RCA but wants proactive notification next time.",
        "{contact2_name} (exec) called our regional VP. Not about one case - about the pattern. 5 escalations this quarter. VP wants an account review in 2 weeks.",
        "Quick update: case {case_number} resolved. Replaced backplane, not the drives. Customer confirmed stable for 72 hours.",
        "Customer is frustrated by being bounced between hardware and software support. The issue is the interaction between our BMC and their {hypervisor} host agent. Assigned a single owner.",
        "Escalated part availability for {case_number}. Replacement DIMM was out of stock locally; next-day from another depot. Customer has ProCare Mission Critical with 4-hr - we missed SLA. Requesting service credit.",
        "On-site engineer showed up without the right part. Second visit tomorrow. {contact_first} said this is the third time it's happened. Flagged to field service manager.",
        "Spoke w/ {contact_first}. Sev 1 resolved but they want a post-incident review with our engineering team, not just support. Arranged for {date}.",
        "Fleet issue confirmed: batch of batteries from a specific supplier is degrading early. Proactive replacement program for affected serials. Customer has {qty} affected units.",
        "Remote session with escalation engineer. Collected a BMC log bundle, found correctable memory errors on 3 DIMMs that never threw an alert because the threshold was set too high. Adjusted alerting.",
        "{contact_first}'s team doesn't trust the support process anymore. Proposed a monthly service review with their TAM until things stabilize.",
    ],
    "next_steps": [
        "Escalate {case_number} to duty manager",
        "Request formal RCA",
        "Set up daily update call until resolved",
        "Request service credit for missed SLA",
        "Schedule post-incident review w/ engineering {date}",
        "Pull fleet failure data for {product}",
        "Confirm proactive battery replacement for affected serials",
        "Book monthly service review w/ TAM",
    ],
    "emails_out": [
        ("Case {case_number} - escalated", "Hi {contact_first},\n\nI've escalated {case_number} to our support duty manager. You'll get a call within the hour from a senior engineer who owns it end to end. I'm on the thread and will check in tonight.\n\nI'm sorry it's taken this long.\n\n{rep_first}"),
        ("RCA - {case_number}", "{contact_first},\n\nAttached is the RCA. Summary: NIC firmware bug under sustained high throughput with the driver version you're running. Fixed in {firmware}. Recommend updating during your next maintenance window - {se_name} can help plan it."),
        ("Post-incident review", "Hi {contact_name},\n\nConfirming the post-incident review on {date} with our engineering team. Agenda: timeline, root cause, what we're changing, what we need from you. 60 min."),
        ("Battery replacement program", "{contact_first},\n\nWe've identified a battery batch degrading earlier than spec. {qty} of your units are affected (serial list attached). We'll ship replacements in advance, and your team or ours can swap them. No cost."),
        ("Escalation follow-up", "Hi {contact2_name} - following up on your call with our VP. We've scheduled an account review for {date} covering every escalation this quarter, what went wrong, and what's changing. I'll send an agenda tomorrow."),
    ],
    "emails_in": [
        ("URGENT case {case_number}", "This is the third controller failure in 2 weeks. I need someone senior on the phone today. Our production system is running on one controller and I can't sleep."),
        ("RE: RCA", "RCA is fine but why did we have to find this ourselves? If you knew about the firmware issue why wasn't there an advisory?"),
        ("tech didn't have the part", "Your tech showed up at 8am without the DIMM. Again. I have a 4 hour contract. What exactly am I paying for?"),
        ("Re: Case escalated", "Thank you. The engineer who called was excellent. Finally someone who listened."),
        ("fleet issue", "We've had 30 motherboard failures on the {product} in 90 days. I'm done opening individual cases. I want someone to look at this as a fleet problem."),
    ],
    "chatter": [
        "{account} case {case_number} open {days} days, 2 controller swaps, still failing. @{se_name} can you look at logs?",
        "missed 4hr SLA at {account} on a DIMM. requesting service credit, please support",
        "heads up {account} exec called the RVP. account review in 2 wks. need everyone's escalation history",
        "fyi battery batch issue confirmed, {account} has {qty} affected units. proactive program kicking off",
        "kudos to the escalation engineer on {account}. customer literally emailed to say thanks",
        "tech showed up without part at {account} for the 3rd time. who do I escalate to in field service?",
    ],
}

TOPICS["competitor_threat"] = {
    "subjects": [
        "{competitor} activity at {account}",
        "Competitive threat - {product_line}",
        "{competitor} pitching {account}",
        "Competitive bake-off",
        "Defending the install base",
        "{competitor} pricing intel",
        "Competitive review w/ {se_name}",
        "Head-to-head eval",
    ],
    "summaries": [
        "{contact_first} let slip that {competitor} was in last week pitching their HCI. They're offering free migration services and a big first-year discount. Customer is listening.",
        "Competitive intel: {competitor} quoted the {product_line} refresh at roughly {discount}% below our number. They're clearly buying the business. We won't match; we'll differentiate on deployment and support.",
        "Bake-off planned. {competitor} and us, same config, {weeks} weeks in their lab. Criteria: performance, management, support responsiveness. {se_name} is all over it.",
        "Spoke w/ {contact_name}. {competitor} went over IT's head to the CFO with a TCO slide. CFO is now asking IT why they aren't considering it. Need to get in front of the CFO.",
        "Not a real threat yet. {competitor} sent a quote as a price check. {contact_first} said they use it to keep us honest.",
        "Lost the storage piece to {competitor} - they bundled it with networking. We kept compute. Monitoring for expansion.",
        "{contact_first} said the {competitor} rep promised 4-week delivery on everything. We know their supply situation. Asked customer to get it in writing with penalties. They did - {competitor} wouldn't commit.",
        "Bake-off results: we won on management and support response time. {competitor} won on raw IOPS in one synthetic test. Customer weighted management higher. Good outcome.",
        "Their new {exec_title} came from a {competitor} shop and has a friend there. Uphill. Need to build a relationship fast.",
        "{competitor} is offering 0% financing for 36 months. Matched it through Orvane Financial Services. Neutralized.",
        "Spoke w/ {contact2_name}. They're happy with us but procurement policy requires competitive bids every 3 years. It's not a threat, it's a process. Make it easy for them to pick us.",
        "Install base risk: they have {servers} of our servers, but {competitor} has been working the storage team for months. If storage goes, compute follows.",
        "Quorra Networks is pitching the network refresh. Mesh is in good position but Quorra has their network team's loyalty.",
        "{competitor} lost their partner certification in this region. Customer's local partner can't support them anymore. Opportunity.",
    ],
    "next_steps": [
        "Build competitive comparison vs. {competitor}",
        "Request exec meeting w/ CFO",
        "Set up bake-off criteria + timeline",
        "Get {competitor} delivery commitment in writing",
        "Match financing via Orvane Financial Services",
        "Map relationships w/ new {exec_title}",
        "Run install base health check to show value",
        "Line up 2 reference customers who switched from {competitor}",
    ],
    "emails_out": [
        ("Comparison - Orvane vs. {competitor}", "Hi {contact_first},\n\nAs promised, an honest comparison. I've tried to keep it factual - spec, support model, deployment, financing. Where they're stronger, I say so. Happy to discuss any of it.\n\n{rep_first}"),
        ("Bake-off - proposed criteria", "{contact_first},\n\nProposed criteria and weighting for the eval:\n- Performance on your workload (30%)\n- Management / day-2 ops (25%)\n- Support response (20%)\n- Cost over 5 years (25%)\n\nWe'll ship gear by {date}."),
        ("Reference customers", "Hi {contact_first} - two customers who moved from {competitor} in the last year and are happy to talk candidly, including about what didn't go well. Let me know and I'll intro."),
        ("Meeting request - {contact2_name}", "Hi {contact2_name},\n\nI understand you've been looking at a TCO comparison. I'd value 30 minutes to share our view and make sure you have the full picture before a decision. Any time the week of {date}?\n\n{rep_name}"),
        ("Financing options", "{contact_first}, Orvane Financial Services can match 0% for 36 months on this deal. Terms attached. Just want to make sure financing isn't the deciding factor."),
    ],
    "emails_in": [
        ("FYI", "Heads up, {competitor} is in on Thursday to present to our CIO. Thought you should know."),
        ("RE: Comparison", "Thanks. Their number is still lower. Can you sharpen your pencil?"),
        ("bake-off", "We've decided to run a bake-off before deciding. Can you have gear here by {date}?"),
        ("Re: Bake-off - proposed criteria", "Looks fair. We'd weight support higher. Last vendor's support was a disaster."),
        ("decision", "Wanted you to hear it from me. We're going with you on compute but {competitor} on storage. Bundle pricing was too good. Hope we keep working together."),
    ],
    "chatter": [
        "{competitor} went around IT to the CFO at {account}. need exec sponsor asap",
        "@{se_name} bake-off at {account} vs {competitor}, gear needs to land {date}. are we good?",
        "fyi {competitor} quoting {discount}% below us on {product_line}. not matching, differentiating",
        "won the bake-off at {account}!! management + support won it",
        "heads up {competitor}'s partner in this region lost certification. check your accounts",
        "{competitor} promising 4-week delivery again. ask customers to get it in writing, they never commit",
    ],
}

TOPICS["budget_planning"] = {
    "subjects": [
        "{fy} budget planning - {account}",
        "Capital planning discussion",
        "Budget cycle timing",
        "Refresh roadmap for {fy}",
        "Budget review w/ {contact2_name}",
        "Opex vs. capex discussion",
        "Multi-year IT plan",
        "Budget submission support",
    ],
    "summaries": [
        "{contact_first} is building the {fy} budget now - submissions due {date}. Wants rough numbers for server refresh, Win 11 replacements, and backup. Not quotes, just planning figures.",
        "Budget cycle: IT submits in {quarter}, finance approves, money available start of {fy}. Anything not in the budget waits a full year. Getting the numbers right now matters.",
        "Spoke w/ {contact2_name}. Finance wants to move IT from capex to opex. Orvane Flex and Device-as-a-Service fit that exactly. Scheduled a deeper session.",
        "Multi-year plan: year 1 clients, year 2 servers + storage, year 3 network. Total ~{budget} over 3 yrs. They want a partner, not 3 separate vendors.",
        "Budget got cut {pct}%. {contact_first} has to prioritize. Storage is the must-do. Client refresh pushed to next {fy}.",
        "Sent planning numbers. {contact_first} used them almost verbatim in the budget submission. Good sign.",
        "Budget approved: {budget} for infrastructure in {fy}. Money becomes available {date}.",
        "Spoke w/ {contact_first}. No new budget this year, but they have money left in a maintenance line that can be reallocated if it's framed as replacing out-of-support gear. Creative.",
        "Grant funding available for {initiative} - they need quotes that align with the grant categories. Finance is particular about format.",
        "{contact2_name} asked for a 5-year forecast of what Orvane spend would look like. Built one including refresh cycles and support.",
        "Use-it-or-lose-it: {amount} left in this {fy} that has to be committed by {date}. They want ideas for what to pull forward.",
        "Discussed contingency. They want a 10% buffer in the budget for supply chain price increases. Reasonable given recent history.",
        "Budget is frozen until their new {exec_title} starts. Nothing moves until then.",
        "Quick call. Board approved the capital plan. {contact_first} is relieved.",
    ],
    "next_steps": [
        "Send planning-level pricing for {fy} budget",
        "Build 3-yr roadmap w/ costs",
        "Schedule Orvane Flex session w/ {contact2_name}",
        "Model capex vs. opex for refresh",
        "Format quotes to match grant categories",
        "Identify what can pull forward into this {fy}",
        "Check back after budget approval {date}",
        "Build 5-yr spend forecast",
    ],
    "emails_out": [
        ("{fy} planning numbers", "Hi {contact_first},\n\nPlanning figures for your {fy} submission (not quotes - budget-level with ~10% headroom):\n- Server refresh: {amount}\n- Win 11 replacements: ~{qty} devices\n- Backup/DR: separate line\n\nHappy to adjust as scope firms up.\n\n{rep_first}"),
        ("3-year roadmap", "{contact_first},\n\nDraft 3-yr roadmap attached: year 1 clients, year 2 compute + storage, year 3 network. Total ~{budget}. Spreading it this way keeps each year's spend roughly flat."),
        ("Opex options", "Hi {contact2_name} - two ways to move this to opex: Orvane Flex for infrastructure (pay for what you use above a committed baseline) and Device-as-a-Service for clients. Overview attached. Happy to walk through."),
        ("What could pull forward", "{contact_first}, if you have {amount} to commit by {date}, here's what could ship and invoice in time: the Win 11 replacements and the backup appliance. Both in stock."),
        ("Checking in post-budget", "Hi {contact_first} - how did the budget review go? Anything I can help with now that numbers are final?"),
    ],
    "emails_in": [
        ("budget numbers", "Need ballpark numbers for next year's budget by {date}. Don't need to be exact."),
        ("RE: {fy} planning numbers", "Thanks, these are great. Finance asked if we can spread the server piece over 2 years."),
        ("budget cut", "Bad news, IT budget got cut {pct}%. Need to rethink what we're doing. Can we talk next week?"),
        ("Re: Opex options", "CFO is interested. Can you send a sample contract?"),
        ("leftover money", "I have about {amount} that needs to be spent before {date} or it goes away. What can you ship fast?"),
    ],
    "chatter": [
        "{account} budget cut {pct}%, storage survives, clients pushed. adjusting forecast",
        "{account} used my planning numbers verbatim in their budget submission. that's how you get in early",
        "fyi {account} has {amount} use-it-or-lose-it by {date}. @{rep_first} what's in stock?",
        "budget frozen at {account} until new {exec_title} starts. pushing everything",
        "{account} CFO wants opex. Flex and DaaS conversation next week",
        "board approved {account} capital plan - {budget} for {fy}. let's go",
    ],
}

TOPICS["exec_change"] = {
    "subjects": [
        "New {exec_title} at {account} - {new_exec}",
        "Intro to {new_exec}",
        "Leadership change - impact on pipeline",
        "Exec alignment meeting",
        "{contact_name} leaving {account}",
        "Re-establishing exec sponsor",
        "First meeting w/ new {exec_title}",
        "Org change - IT reporting structure",
    ],
    "summaries": [
        "{contact_first} let me know {new_exec} starts as {exec_title} on {date}. Came from a much larger company. Expect a review of every vendor and every project in flight.",
        "Our champion {contact_name} is leaving {account} at end of month. Huge loss. Asked who's taking over - probably {contact2_name}, who we barely know.",
        "First meeting w/ {new_exec}. 30 min, all business. Priorities: cut costs, reduce vendor count, get off legacy systems. Wants a summary of everything we're doing with them and what it costs. Sending by Friday.",
        "{new_exec} has paused all projects over $100k pending review. Our server refresh is in that bucket. Need to make the case again, from scratch.",
        "Good news: {new_exec} knows Orvane from their last company and had a good experience. Mentioned our support specifically. Doors open.",
        "Bad news: {new_exec} brought a preferred vendor list from their last job and {competitor} is on it. Need to get in front of this fast.",
        "Spoke w/ {contact2_name}, who now reports to {new_exec}. Morale is shaky. Nobody knows what's going to happen to their projects. Advised to keep our heads down and be helpful.",
        "IT now reports to the CFO instead of the CEO. Changes the conversation - everything is about cost now.",
        "Exec alignment meeting w/ {new_exec}, our regional VP, and me. {new_exec} wants a single point of contact and quarterly business reviews. Agreed.",
        "{contact_first} got promoted to {exec_title}. Great for us - long relationship, and now with budget authority.",
        "New {exec_title} cancelled our standing meeting. Not personal, they cancelled all vendor meetings for 60 days. Will try again in {quarter}.",
        "Spoke w/ {old_rep}'s old contact who moved to another company. They want to bring us in there. Passing the lead to that territory's rep.",
        "{new_exec} asked a sharp question: 'what would you do if you were me?' Gave an honest answer - consolidate on fewer platforms, fix backup first, stop buying servers one at a time.",
        "Org restructure: infrastructure and end-user computing teams are merging under {contact2_name}. One decision maker for both now. Simpler for us.",
    ],
    "next_steps": [
        "Send account summary to {new_exec}",
        "Request intro meeting w/ {new_exec}",
        "Get our RVP to reach out to {new_exec}",
        "Build relationship w/ {contact2_name}",
        "Re-justify server refresh for review",
        "Find out who's replacing {contact_name}",
        "Set up quarterly business review cadence",
        "Send congrats note to {contact_first}",
    ],
    "emails_out": [
        ("Welcome, and a quick summary", "Hi {new_exec},\n\nWelcome to {account}. I'm {rep_name}, the account lead at Orvane. Attached is a one-page summary of what we support today, what's in flight, and what it costs annually. No pitch - just so you have the picture. Happy to meet whenever useful.\n\n{rep_name}"),
        ("Congrats!", "{contact_first} - congrats on the {exec_title} role. Well deserved. Let's grab coffee when you're settled in.\n\n{rep_first}"),
        ("Thank you", "{contact_first},\n\nSorry to hear you're leaving {account} but excited for you. Thank you for everything over the last few years - you made it easy to do good work. Stay in touch, and if you end up somewhere we can help, I'd love to hear from you.\n\n{rep_first}"),
        ("Intro - {rep_name} from Orvane", "Hi {contact2_name},\n\n{contact_name} mentioned you'd be taking over their responsibilities. I'd like to make sure you have everything you need from us. 20 minutes next week?"),
        ("Refresh business case - updated", "{new_exec},\n\nFollowing up on your project review. The server refresh business case is attached - focused on cost reduction and risk, which I understand are your priorities. The headline is a {pct}% reduction in power and licensing over 3 years."),
    ],
    "emails_in": [
        ("leaving", "{rep_first}, wanted to let you know personally - I've accepted a role elsewhere. Last day is {date}. {contact2_name} will be your contact going forward. It's been great working with you."),
        ("RE: Welcome", "Thanks. I'll be reviewing all vendor relationships over the next 60 days. Will reach out if I have questions."),
        ("Re: Congrats!", "Thanks {rep_first}! Coffee sounds great. Lots to figure out."),
        ("project freeze", "FYI new {exec_title} has frozen all projects over $100k until review. Our refresh is included. Sorry. I'll fight for it."),
        ("vendor review", "{new_exec} wants a summary of all Orvane spend for the last 3 years and current contracts. Can you send by end of week?"),
    ],
    "chatter": [
        "new {exec_title} at {account} - {new_exec}. anyone know them? came from a big shop",
        "{contact_name} leaving {account}. our champion. need to rebuild fast",
        "heads up {new_exec} froze all projects over 100k. our refresh is stuck",
        "@{rep_first} {new_exec} brought a preferred vendor list w/ {competitor} on it. need exec engagement",
        "good news - {new_exec} at {account} knows us from their last company. good experience",
        "{contact_first} promoted to {exec_title} at {account}!! long time champion now w/ budget",
    ],
}

TOPICS["partner_conflict"] = {
    "subjects": [
        "Channel conflict - {account}",
        "Deal reg dispute w/ {partner}",
        "Partner engagement on {account}",
        "Direct vs. partner - who owns it",
        "Partner pricing conflict",
        "{partner} co-sell planning",
        "Rules of engagement - {account}",
        "Partner escalation",
    ],
    "summaries": [
        "{partner} registered the {account} deal last week. I've been working it for 3 months directly. Customer prefers to buy direct. Raised with channel manager.",
        "Spoke w/ {partner}'s rep. They have a services relationship with {account} and want the hardware too. Agreed on a split: we sell, they deploy. Everyone happy-ish.",
        "Price conflict - customer got a quote from {partner} that's lower than mine because partner has a better rebate tier. Customer is confused why the same product has two prices.",
        "Deal reg approved for {partner}. I'm out as primary seller. Supporting them with {se_name} and pricing.",
        "Rules of engagement meeting w/ channel manager and {partner}. {account} is now partner-led for clients, direct for infra. Documented.",
        "Customer doesn't want {partner} involved - bad experience on the last deployment. Partner is pushing hard to stay. Awkward.",
        "{partner} brought us into {account} - they found the opp. Credit them. Working together.",
        "Spoke w/ channel manager. {partner} has been registering every deal they hear about, even ones they aren't working. Pattern across several accounts. Channel team investigating.",
        "Co-sell plan with {partner}: they lead the relationship, we bring {se_name} for technical, they fulfill. Target close {quarter}.",
        "{partner} and I quoted the same deal at different prices without realizing. Customer pointed it out. Embarrassing. Agreed to one quote going forward.",
        "Partner is adding a margin on the services that makes the total uncompetitive vs. {competitor}. Talking to them about it.",
        "Escalation from {partner} - they say I went around them on {account}. I didn't - customer called me directly. Shared the email thread. Resolved.",
        "Fulfillment question: customer wants to buy through {partner} because they have a cooperative contract we're not on. Fine. Partner fulfills, I stay engaged.",
        "{partner}'s account manager left and nobody's covering {account}. Customer is calling me. Working it direct until partner sorts it out.",
    ],
    "next_steps": [
        "Raise deal reg conflict w/ channel manager",
        "Document rules of engagement for {account}",
        "Align pricing w/ {partner} on single quote",
        "Support {partner} w/ {se_name} on technical",
        "Confirm {partner} fulfillment via co-op contract",
        "Share email thread w/ channel to resolve dispute",
        "Set up co-sell planning call w/ {partner}",
        "Check {partner}'s registration against our opp history",
    ],
    "emails_out": [
        ("{account} - coordination", "Hi team at {partner},\n\nWant to make sure we're aligned on {account}. My understanding: you lead on deployment services, we lead on the hardware sale. If that's not your understanding, let's talk before either of us goes back to the customer.\n\n{rep_first}"),
        ("Deal reg question", "Hi channel team,\n\n{partner} registered {account} on {date}. I've been working it directly since {quarter} with documented activity. Can we review before it's approved? Activity log attached.\n\n{rep_name}"),
        ("Single quote going forward", "{partner} team - customer noticed two quotes at two prices. Let's agree on one. I'm happy for you to quote if you're fulfilling; I'll make sure the pricing support is there."),
        ("Co-sell plan", "Hi - co-sell plan for {account} attached. Roles, timing, who talks to whom. Target close {quarter}. Let's review Thursday."),
        ("Re: escalation", "Hi channel team - attached is the email where {contact_first} reached out to me directly. I didn't initiate. Happy to involve {partner} going forward if the customer agrees."),
    ],
    "emails_in": [
        ("quote confusion", "{rep_first}, I have quotes from you and from {partner} for the same thing at different prices. Which one is real? This is confusing."),
        ("RE: {account} - coordination", "Agreed on the split. We'll handle imaging and deployment, you handle hardware. Send us the order details when it's booked."),
        ("partner", "We don't want {partner} on this project. Last time they were 2 months late. Can we work directly with you?"),
        ("deal reg", "Hi {rep_first}, this is the {partner} team. We've registered {account}. Please route all communication through us going forward."),
        ("Re: Deal reg question", "Reviewed. Activity log shows direct engagement prior to the registration date. Reg declined. Please coordinate with {partner} on services if customer wants them."),
    ],
    "chatter": [
        "{partner} registered {account} after I'd been working it 3 months. channel team please look",
        "fyi {account} doesn't want {partner} on the project. awkward but customer's call",
        "{partner} brought us {account}, give them credit. good partnership on this one",
        "@{rep_first} two quotes at two prices went to {account} from us and {partner}. need to align",
        "rules of engagement doc for {account} done. clients partner-led, infra direct",
        "heads up {partner} registering every deal they hear about. channel investigating",
    ],
}

TOPICS["lease_end"] = {
    "subjects": [
        "Lease ending {lease_end} - {account}",
        "End of lease options",
        "Lease return logistics",
        "Lease extension request",
        "Refresh at lease end",
        "Orvane Financial Services - lease review",
        "Buyout vs. return",
        "Lease renewal proposal",
    ],
    "summaries": [
        "Lease on {qty} laptops ends {lease_end}. Called {contact_first} - options are return, buyout, or extend month-to-month. They want to refresh with new hardware on a new lease.",
        "Buyout quote from Orvane Financial Services came in at fair market value. {contact_first} thinks it's high for 3-yr-old laptops. Explained the FMV basis. They're thinking about it.",
        "Return logistics are the hard part. {qty} devices across 12 sites and remote workers. Proposed a return kit service - box and label shipped to each user, tracked back.",
        "Lease extension for 90 days approved - new hardware won't arrive before {lease_end}. Month-to-month at the same rate.",
        "Spoke w/ {contact2_name}. Finance wants to understand total cost of leasing vs. buying for the next cycle. Built a comparison.",
        "Lease end on the server equipment in {quarter}. They want to keep the servers but renew support. Buyout is the cleanest path.",
        "Concern about data on returned devices. Lease return includes NIST 800-88 wipe with certificates per serial. {contact_first} relieved.",
        "Missing devices: {pct}% of the leased fleet can't be located. They'll owe for those at FMV. {contact_first} is trying to track them down.",
        "Refresh + new lease signed. New devices ship before {lease_end}, swap and return in one motion.",
        "Spoke w/ {contact_first}. Leasing worked well, they'll do it again. Want shorter 3-yr terms to align with Windows lifecycles.",
        "Damage charges on returned laptops - cracked screens, missing keys. Customer disputing. Reviewing photos with OFS.",
        "Early termination question - they want to end the lease 6 months early as part of an upgrade. OFS can roll the remaining balance into the new lease.",
        "Quick call. Return complete. All {qty} devices accounted for. Final invoice to follow.",
        "Server lease ending but the gear is running production. Can't just return it. Proposed rolling refresh - new hardware, migrate, then return old.",
    ],
    "next_steps": [
        "Get buyout quote from Orvane Financial Services",
        "Arrange return kits for {qty} devices",
        "Process 90-day lease extension",
        "Build lease vs. buy comparison",
        "Locate missing leased devices",
        "Review damage charge photos w/ OFS",
        "Roll remaining balance into new lease",
        "Schedule rolling server swap before {lease_end}",
    ],
    "emails_out": [
        ("Your lease ends {lease_end}", "Hi {contact_first},\n\nThe lease on {qty} laptops ends {lease_end}. Your options:\n1. Return and refresh on a new lease\n2. Buy out at fair market value\n3. Extend month-to-month\n\nI'd suggest we start planning 1 now so new devices arrive before the end date.\n\n{rep_first}"),
        ("Return logistics", "{contact_first},\n\nFor remote users we'll ship a return kit (box, packing, prepaid label) to each address. Every device is tracked back to the serial. Wiped per NIST 800-88 with a certificate per device."),
        ("Lease extension approved", "Hi {contact_first} - 90-day extension approved at the same monthly rate. New end date is 90 days after {lease_end}. No paperwork beyond the signature on the attached."),
        ("Lease vs. buy", "{contact2_name},\n\nComparison attached for the next cycle: lease (36 months) vs. buy with 3-yr ProCare Plus. Lease has higher total cost but no capital outlay and handles end-of-life logistics. Depends on what you're optimizing for."),
        ("Missing devices", "Hi {contact_first} - we're showing {pct}% of the leased devices not returned. List attached by serial and last-known user. Anything you can find before {date} avoids the FMV charge."),
    ],
    "emails_in": [
        ("lease", "Our lease ends {lease_end} and nobody told me until today. What are our options?"),
        ("RE: Lease ends", "We want option 1. Can we get the same devices as last time? Users liked them."),
        ("damage charges", "We received a bill for damage on returned laptops. Normal wear and tear is not damage. Please review."),
        ("buyout", "The buyout price seems high for 3-year-old laptops. Is it negotiable?"),
        ("missing laptops", "We've found about half of the missing laptops. Rest are probably with former employees. What happens now?"),
    ],
    "chatter": [
        "{account} lease ends {lease_end}, {qty} devices. refresh + new lease is the play",
        "@{rep_first} {account} disputing damage charges on lease returns. OFS reviewing photos",
        "fyi {pct}% of {account}'s leased fleet is missing. FMV charges coming, customer won't like it",
        "lease extension for {account} approved - 90 days. new gear won't land in time",
        "return kits for remote workers make lease returns so much easier. {account} loved it",
        "{account} rolled remaining lease balance into new lease. early upgrade done",
    ],
}

TOPICS["consumption_billing"] = {
    "subjects": [
        "Orvane Flex usage review - {account}",
        "Flex overage - {quarter}",
        "Consumption billing question",
        "Flex committed capacity discussion",
        "Usage report review",
        "Flex invoice dispute - {invoice_number}",
        "Flex capacity expansion",
        "Metering data review",
    ],
    "summaries": [
        "Monthly Flex review w/ {contact_first}. Usage at {util}% of committed capacity. Above the buffer threshold, so overage billing kicked in. They weren't expecting it.",
        "Flex invoice {invoice_number} came in higher than expected - {amount} vs. usual. Pulled metering data: storage usage jumped {tb}TB in one week. Customer investigating - probably a misconfigured backup job writing to primary.",
        "Committed capacity conversation. They're consistently at {util}% of commit, so they're paying for headroom they don't use. Recommended lowering commit at next adjustment window.",
        "Spoke w/ {contact2_name}. Finance doesn't understand the Flex invoice format. Walked through committed vs. on-demand vs. overage. They want a simpler summary page.",
        "Flex expansion - they need more capacity. Buffer capacity is on site and ready; just needs to be activated. Activated same day.",
        "Customer disputing overage charges - says metering is wrong. Pulled raw data from Orvane Insight and the metering collector. Numbers match. Showing them.",
        "Quarterly Flex review: usage growing {growth}% per quarter. At this rate they'll exceed buffer in {quarter}. Need to add capacity before then.",
        "Spoke w/ {contact_first}. They want to move from Flex back to owned. Contract term doesn't allow it until year 3. Discussed what happens at end of term.",
        "Metering collector lost connectivity for 4 days. Billing estimated usage for that period. Customer wants actuals. Requesting a correction.",
        "Flex compute: they spun up 12 VMs for a project and forgot about them. Overage for 2 months. Not our problem but they're asking for a credit. Will ask.",
        "Showed them the Flex usage dashboard. They didn't know it existed. Now they can see their own usage in real time. Should reduce surprises.",
        "Flex renewal coming up. They want a lower rate per TB. Usage profile has been stable so there's room.",
        "Quick call. Usage at {util}%, no overage this month. All good.",
        "Spoke w/ {contact2_name}. Finance loves the predictability of the committed amount; IT loves not having to plan capacity. Overage is the only friction.",
    ],
    "next_steps": [
        "Pull metering data for {invoice_number}",
        "Activate buffer capacity",
        "Recommend commit adjustment at next window",
        "Send simplified invoice summary to finance",
        "Request billing correction for collector outage",
        "Set up Flex dashboard access for {contact_first}",
        "Add capacity before buffer exceeded in {quarter}",
        "Ask for goodwill credit on forgotten VMs",
    ],
    "emails_out": [
        ("Flex usage - {quarter}", "Hi {contact_first},\n\nYour {quarter} Flex summary:\n- Committed: 100%\n- Average usage: {util}%\n- Overage: billed on {invoice_number}\n\nThe spike was mostly storage in week 3. If that was the backup job we discussed, the overage should drop next month.\n\n{rep_first}"),
        ("Metering data for {invoice_number}", "{contact_first},\n\nRaw metering data attached for the billing period. Daily usage per resource, timestamped. The jump on day 18 lines up with a {tb}TB write to the primary pool. Happy to walk through it."),
        ("Flex dashboard access", "Hi {contact_first} - set you up on the Flex usage dashboard. Shows usage vs. commit in near real time and alerts at 80% and 90% of buffer. Login instructions attached."),
        ("Commit adjustment", "{contact2_name},\n\nYou've averaged {util}% of committed capacity for 6 months. At the next adjustment window we can lower the commit, which lowers the fixed monthly. Want me to model it?"),
        ("Billing correction", "Hi {contact_first} - the metering collector was offline {date} for 4 days, so that period was estimated. I've requested a correction based on actuals once the data backfills."),
    ],
    "emails_in": [
        ("Flex invoice", "Why is this month's Flex invoice so much higher? Nobody approved any expansion."),
        ("RE: Metering data", "OK, the data shows what you say. We found the backup job. It's fixed. Can we get a credit for this one?"),
        ("invoice format", "Our AP team can't reconcile the Flex invoice to our PO. The line items don't match. Can someone help?"),
        ("Re: Flex usage", "Thanks. We'd like to lower our commit. What's the process?"),
        ("capacity", "We need more storage on Flex. Can we turn on the buffer today? Project starting Monday."),
    ],
    "chatter": [
        "{account} Flex overage was a misconfigured backup job writing to primary. customer asking for credit. thoughts?",
        "@{se_name} Flex metering collector at {account} offline 4 days. can we backfill actuals?",
        "fyi {account} at {util}% of Flex commit for 6 months. recommending lower commit, builds trust",
        "Flex dashboard is a game changer. {account} had no idea it existed",
        "buffer capacity activated at {account} same day. that's the Flex pitch right there",
        "heads up {account} finance can't reconcile Flex invoices to PO. billing ops can you help?",
    ],
}

TOPICS["security_advisory"] = {
    "subjects": [
        "Security advisory {advisory} - {account}",
        "BMC vulnerability remediation",
        "Firmware update {firmware} - planning",
        "Critical BIOS update",
        "Advisory follow-up w/ security team",
        "Patch status review",
        "Vulnerability scan findings",
        "Remediation timeline",
    ],
    "summaries": [
        "Advisory {advisory} published - critical BMC vulnerability, remote code execution if the BMC is reachable from the network. Called {contact_first} proactively. Their BMCs are on the production VLAN, not isolated. That's a problem.",
        "Remediation plan: update BMC firmware to {firmware} on {servers} servers. Can be done without host reboot. {se_name} walked their team through doing it in batches via Orvane Insight.",
        "Spoke w/ {contact_name} (security). Their vuln scanner flagged {advisory} on {servers} hosts. Wants confirmation of fixed version and timeline. Sent advisory details.",
        "BIOS update for a CPU microcode issue. Requires host reboot. They need to schedule maintenance windows across all clusters. {weeks} weeks to complete.",
        "Patch status: {pct}% of servers updated. Remaining are in a change freeze until {date}. Security team accepted the risk with compensating controls.",
        "Recommended isolating BMCs on a dedicated out-of-band management VLAN regardless of patching. Their network team agreed - long overdue.",
        "Customer asked why they found out about {advisory} from their scanner before hearing from us. Fair. Signed them up for proactive advisory notifications.",
        "Firmware update {firmware} bricked a BMC on one host. Support case opened, RMA'd the board. Customer nervous about continuing. Paused rollout until RCA.",
        "Spoke w/ {contact_first}. Their auditors want evidence of remediation. Exported firmware compliance report from Orvane Insight showing all hosts at {firmware}.",
        "Laptop BIOS vulnerability - {qty} {product} units need an update. Pushed via Orvane Manage. {pct}% done in 48 hrs; stragglers are offline devices.",
        "Advisory is critical but they're running an older model ({model}) that's past end of support. No fix coming for that model. Recommended replacement.",
        "Security team wants a call with our PSIRT. Arranged for {date}.",
        "Quick check-in: all {servers} hosts at {firmware}. Closed out.",
        "Discussed signed firmware and secure boot chain. Their new CISO wants to understand our supply chain security. Sent the hardware root of trust whitepaper.",
    ],
    "next_steps": [
        "Send {advisory} details + fixed version",
        "Plan BMC update to {firmware} in batches",
        "Isolate BMCs on OOB management VLAN",
        "Schedule maintenance windows for BIOS updates",
        "Export firmware compliance report for auditors",
        "Sign customer up for proactive advisory notifications",
        "Arrange PSIRT call {date}",
        "Quote replacement for end-of-support {model}",
    ],
    "emails_out": [
        ("Security advisory {advisory} - action required", "Hi {contact_first},\n\nWanted to flag {advisory}, published today. Critical BMC vulnerability affecting your {servers} servers. Fixed in {firmware}. The update doesn't require a host reboot. Separately, we strongly recommend isolating BMC interfaces on a dedicated management network.\n\n{se_name} can help plan the rollout.\n\n{rep_first}"),
        ("Firmware compliance report", "{contact_first},\n\nAttached is the firmware compliance report from Orvane Insight showing all {servers} hosts at {firmware}. Timestamped and exportable as PDF for your auditors."),
        ("Re: {advisory}", "Hi {contact_name} - confirming {advisory} is remediated in {firmware}. Advisory text and CVSS details attached. No workaround needed beyond the update, though network isolation reduces exposure."),
        ("Proactive notifications", "{contact_first}, I've signed you up for proactive security notifications for your assets. You'll get advisories as they publish, filtered to the models you own. Sorry you heard about this one from your scanner first."),
        ("End of support - {model}", "Hi {contact_first} - unfortunately {model} is past end of support and won't receive a fix for {advisory}. Options: isolate it heavily or replace. I've attached a replacement quote."),
    ],
    "emails_in": [
        ("vuln scan", "Our scanner flagged {advisory} on {servers} of your servers. When is the fix available? Security wants a timeline by EOD."),
        ("BMC update failed", "We pushed {firmware} to the first batch and one BMC is now unresponsive. Stopping rollout. Need help."),
        ("RE: Security advisory", "Thanks for the heads up. Our BMCs are on the prod VLAN. I know, I know. We'll fix that."),
        ("audit evidence", "Auditors want evidence all servers are patched for {advisory}. What can you give me?"),
        ("PSIRT", "Our CISO wants to talk to your security team directly about how you handle firmware vulnerabilities. Can you arrange?"),
    ],
    "chatter": [
        "{advisory} is out, critical BMC RCE. check your accounts with BMCs on prod VLANs. {account} is one",
        "@{se_name} {firmware} bricked a BMC at {account}. RMA in, rollout paused. anyone else seen this?",
        "fyi {account} found out about {advisory} from their scanner before we told them. signed them up for notifications",
        "{account} at 100% {firmware} across {servers} hosts. closed",
        "heads up {model} is EOS, no fix for {advisory}. replacement opp at {account}",
        "{account} CISO wants PSIRT call. who coordinates that?",
    ],
}

TOPICS["qbr_review"] = {
    "subjects": [
        "QBR - {account} {quarter}",
        "Quarterly business review prep",
        "{quarter} account review",
        "QBR follow-up items",
        "Executive QBR w/ {contact2_name}",
        "Service review + QBR",
        "QBR: spend, support, roadmap",
        "Semi-annual business review",
    ],
    "summaries": [
        "QBR w/ {contact_first} and {contact2_name}. Covered: {amount} spend this quarter, {pct}% of devices out of warranty, 3 open escalations (all resolved since). Roadmap: storage refresh in {quarter}, Win 11 completion. Good meeting.",
        "QBR highlights: support satisfaction up, order delivery on time {pct}%, one missed SLA. Customer asked for better visibility into order status. Showing them the portal.",
        "{contact2_name} pushed on cost. Asked for a breakdown of every dollar spent with Orvane this year. Will send detailed spend report.",
        "QBR agenda: 1) business update from customer 2) spend + support metrics 3) roadmap 4) asks. Their business is growing {growth}% - they need more capacity in {quarter}.",
        "Good QBR. They mentioned 3 projects I didn't know about: a new site in {site_city}, an {initiative}, and a datacenter consolidation. All potential opportunities.",
        "QBR was tense. Two escalations this quarter and a late order. {contact_first} said we're 'on notice.' Need to deliver a clean next quarter.",
        "Shared Orvane Insight data in the QBR: {servers} servers healthy, 4 with predictive drive failure warnings, firmware drift on 12. They didn't know any of it.",
        "QBR w/ new format - customer asked for less slides, more conversation. Worked much better.",
        "Spoke w/ {contact_first} on QBR follow-ups. 5 action items, 3 done. Remaining: pricing on storage and ITAD quote.",
        "Executive QBR: our RVP and their {exec_title}. High-level: they're happy with product, want better account coverage. Committed to a dedicated SE.",
        "QBR revealed they're buying monitors from a reseller at higher prices than our contract. They didn't know they could buy through us. Easy win.",
        "Mixed QBR. Product good, support good, sales coverage bad - they had 3 reps in 2 years. Acknowledged it.",
        "QBR prep with {se_name}: pull spend, cases, warranty status, Insight health data, roadmap items.",
        "Short QBR - customer had 30 min only. Covered roadmap and asks. Metrics sent separately.",
    ],
    "next_steps": [
        "Send detailed spend report to {contact2_name}",
        "Follow up on 5 QBR action items",
        "Quote storage refresh for {quarter}",
        "Show customer the order status portal",
        "Address firmware drift on 12 hosts",
        "Set up dedicated SE coverage",
        "Schedule next QBR for {date}",
        "Qualify new projects: {site_city}, {initiative}",
    ],
    "emails_out": [
        ("QBR recap - {quarter}", "Hi {contact_first},\n\nThanks for the time today. Recap:\n- Spend this quarter: {amount}\n- Support: 3 escalations, all resolved\n- Roadmap: storage refresh {quarter}, Win 11 completion\n- Action items: spend report, ITAD quote, storage pricing\n\nNext QBR {date}.\n\n{rep_first}"),
        ("QBR agenda", "{contact_first},\n\nProposed agenda for {date}:\n1. Your business update (15 min)\n2. Spend, support and health metrics (15 min)\n3. Roadmap (15 min)\n4. Asks both ways (15 min)\n\nAnything you'd like added?"),
        ("Spend report", "Hi {contact2_name} - detailed spend report attached: every order, every support contract, by category and month. Total this year {amount}."),
        ("Infrastructure health snapshot", "{contact_first},\n\nThe Insight snapshot we discussed: 4 drives with predictive failure warnings (we'll ship replacements proactively) and 12 hosts with firmware drift. {se_name} can help bring them to baseline."),
        ("QBR follow-ups - status", "Hi {contact_first} - 3 of 5 QBR items done. Storage pricing coming Friday, ITAD quote next week."),
    ],
    "emails_in": [
        ("RE: QBR recap", "Thanks. One thing missing - we asked about extending ProCare on the 2019 servers. Can you add?"),
        ("QBR", "Can we push the QBR a couple weeks? Quarter end is crazy."),
        ("spend", "Before the QBR can you send everything we've spent with you this year? Finance wants it."),
        ("Re: QBR agenda", "Looks good. Keep it under an hour. Less slides please."),
        ("monitors", "Wait, we can buy monitors through you at contract price? We've been buying from a reseller. Please send pricing."),
    ],
    "chatter": [
        "QBR at {account} uncovered 3 new projects. {site_city} site, {initiative}, DC consolidation",
        "{account} QBR was tense. 'on notice'. need clean quarter",
        "@{se_name} need Insight health data for {account} QBR {date}",
        "fyi {account} buying monitors from reseller at higher prices than contract. easy win",
        "exec QBR at {account} went well. committed dedicated SE",
        "QBR tip: less slides, more conversation. {account} loved the new format",
    ],
}

TOPICS["contract_pricing"] = {
    "subjects": [
        "Master agreement pricing - {account}",
        "Subsidiary access to parent contract",
        "MSA renewal negotiation",
        "Contract pricing tier review",
        "Adding affiliates to agreement",
        "Pricing exhibit update",
        "Contract compliance - off-contract buying",
        "Enterprise agreement - year 2 pricing",
    ],
    "summaries": [
        "Parent company's master agreement covers {account} as a subsidiary, but nobody at {account} knew. They've been paying list. Got them set up under the parent's pricing - immediate ~{discount}% savings.",
        "MSA renewal with corporate procurement. They want the same discount tier with lower volume commitments. Their spend is down {pct}% YoY because of the hiring freeze. Hard ask.",
        "Spoke w/ {contact2_name} in corporate procurement. Three new acquisitions need to be added as affiliates. Each needs a separate ship-to and bill-to but shares the parent's pricing.",
        "Contract pricing exhibit is out of date - half the SKUs are discontinued. Customer keeps ordering off-contract replacements at list. Updating the exhibit with current equivalents.",
        "Compliance issue: subsidiaries in {site_city} are buying from {partner} at worse prices than the parent agreement. Corporate wants all purchasing to go through the contract. Working with their procurement on it.",
        "Year 2 pricing on the enterprise agreement kicks in {date}. Price holds on clients, +{pct}% on infrastructure due to component costs. Customer is pushing back on the infrastructure increase.",
        "Legal review of the MSA redline. Sticking points: limitation of liability, data handling for returned drives, and termination for convenience. Our legal and theirs on a call {date}.",
        "Corporate wants a single global price list for North America including Canada in CAD. Working with pricing on currency handling.",
        "Discussed volume tiers: at current run rate they're $40k short of the next tier. Showed what they'd save by consolidating the subsidiary spend. Motivating.",
        "Subsidiary {account} wants out of the parent agreement - they think they can get better pricing on their own. Told them honestly they probably can't at their volume.",
        "Spoke w/ {contact_first}. Contract pricing is fine; the problem is the catalog in their procurement system is stale. Punchout catalog refresh scheduled.",
        "MSA signed. 3-yr term, pricing reviewed annually, all subsidiaries covered. Big milestone.",
        "Price protection clause triggered - our list price dropped on a model and they're entitled to the lower price on open orders. Processing.",
        "Rebate structure discussion. They want a back-end rebate tied to annual spend instead of front-end discount. Finance prefers it; procurement doesn't.",
    ],
    "next_steps": [
        "Set up {account} under parent agreement pricing",
        "Add 3 affiliates w/ separate ship-to/bill-to",
        "Refresh pricing exhibit w/ current SKUs",
        "Schedule legal call on MSA redlines {date}",
        "Refresh punchout catalog in their procurement system",
        "Model rebate vs. front-end discount",
        "Build CAD price list for Canadian entities",
        "Show subsidiary spend consolidation savings",
    ],
    "emails_out": [
        ("You're covered under the parent agreement", "Hi {contact_first},\n\nGood news: {account} is covered under your parent company's master agreement with Orvane, which means contract pricing - roughly {discount}% below what you've been paying. I've linked your account. Next order will reflect it.\n\n{rep_first}"),
        ("Adding affiliates", "{contact2_name},\n\nTo add the three new affiliates I need for each: legal entity name, tax ID, bill-to, ship-to(s), and AP contact. Template attached. They'll share the parent pricing from day one."),
        ("Updated pricing exhibit", "Hi {contact2_name} - updated exhibit attached. Discontinued SKUs are mapped to current equivalents at the same or better pricing. Effective {date} once you countersign."),
        ("Year 2 pricing", "{contact2_name},\n\nYear 2 pricing summary: client pricing holds; infrastructure is up {pct}% reflecting component costs (memory and NVMe primarily). Happy to discuss options, including locking current pricing on a committed volume."),
        ("Subsidiary purchasing", "Hi {contact2_name} - we're seeing subsidiaries in {site_city} buying outside the agreement at higher prices. Happy to set up their users in the portal with contract pricing so it's the easy path."),
    ],
    "emails_in": [
        ("pricing question", "We just found out our parent company has a contract with you. Are we eligible for that pricing? We've been paying full price this whole time apparently."),
        ("RE: Year 2 pricing", "A {pct}% increase on infrastructure is not acceptable. Our agreement says pricing is reviewed annually, not raised automatically. Please revisit."),
        ("MSA redline", "Attached is our redline. Our legal team has concerns about section 9 (liability) and section 14 (data). Please review with your legal."),
        ("affiliates", "We closed on the acquisition of 3 companies. They need to be added to our agreement. What do you need?"),
        ("catalog", "The pricing in our procurement catalog doesn't match the contract. Users are confused. Can you fix?"),
    ],
    "chatter": [
        "{account} has been paying list for 2 years. parent co has an MSA with us. nobody knew. fixed it",
        "MSA renewal at {account} parent - they want same tier w/ {pct}% lower volume. tough",
        "@{rep_first} subsidiaries in {site_city} buying through {partner} at worse prices. corporate wants compliance",
        "fyi {account} MSA signed - 3 yr, all subs covered",
        "price protection triggered on {account} open orders. pricing ops processing",
        "anyone done a CAD price list under a US MSA? {account} needs one",
    ],
}

TOPICS["credit_hold_collections"] = {
    "subjects": [
        "Credit hold - {account}",
        "Past due invoice {invoice_number}",
        "Order blocked by credit hold",
        "AR follow-up w/ {contact_name}",
        "Payment status - {invoice_number}",
        "Credit limit increase request",
        "Disputed invoice resolution",
        "Collections escalation",
    ],
    "summaries": [
        "Order {order_number} blocked by credit hold. Invoice {invoice_number} is {days} days past due. Called {contact_first} - they didn't know. AP is backed up. Promised payment by {date}.",
        "Credit hold on {account}. Total past due {amount}. Finance won't release orders until at least half is paid. Customer escalating because they need the hardware.",
        "Spoke w/ AP at {account}. Invoice {invoice_number} was rejected because it didn't reference the PO. Re-issued with {po_number}. Should process in next payment run.",
        "Credit limit increase requested - the new order would put them over. Their payment history is good. Submitted to credit.",
        "Disputed invoice: customer says they were charged for 10 more units than received. Checked shipping - 2 boxes delivered to wrong dock. Found them. Invoice correct.",
        "Customer short-paid {invoice_number} by the discount they thought they were getting. Discount was conditional on PO timing they missed. Explaining to {contact_first}.",
        "Payment received for {invoice_number}. Credit hold released. Order shipping tomorrow.",
        "Collections escalation - {days} days past due, no response from AP. Asked {contact_first} for help. They walked over to AP.",
        "Spoke w/ {contact2_name} (controller). Cash flow issues this quarter. Asked for a payment plan on {amount}. Routing to finance.",
        "Customer paid but to the wrong remit address - an old lockbox. Finance tracking it down.",
        "Credit hold released by finance as an exception - customer has strategic importance and a solid history. Order {order_number} can ship.",
        "Invoice {invoice_number} pending because the customer's AP requires a vendor portal invoice submission. We emailed it. Submitted through their portal.",
        "Customer in Chapter 11. All orders on hold pending legal review. Not much I can do.",
        "Quick call. {contact_first} confirmed check is in the mail for {invoice_number}.",
    ],
    "next_steps": [
        "Get payment commitment for {invoice_number} by {date}",
        "Re-issue invoice w/ PO {po_number}",
        "Submit credit limit increase",
        "Route payment plan request to finance",
        "Locate payment sent to old lockbox",
        "Submit invoice through customer's AP portal",
        "Request credit hold exception",
        "Confirm order {order_number} releases once paid",
    ],
    "emails_out": [
        ("Invoice {invoice_number} - past due", "Hi {contact_first},\n\nHeads up - invoice {invoice_number} for {amount} is {days} days past due and has put your account on credit hold, which is blocking order {order_number}. Can you check with AP? Happy to resend anything they need.\n\n{rep_first}"),
        ("Re-issued invoice", "{contact_first}, re-issued {invoice_number} with PO {po_number} referenced. AP should be able to match it now."),
        ("Order released", "Hi {contact_first} - payment received, hold released, {order_number} ships tomorrow. Thanks for chasing AP."),
        ("Remit address", "{contact_first},\n\nFinance tells me the payment for {invoice_number} went to a lockbox we closed last year. The bank should return it, but it can take weeks. Could AP re-send to the remit address on the invoice? I'll make sure we don't double-apply."),
        ("Payment plan request", "Hi {contact2_name} - I've passed the payment plan request on {amount} to our finance team with my support. They'll reach out directly."),
    ],
    "emails_in": [
        ("order on hold?", "Why is our order on hold? We need these laptops for new hires starting Monday."),
        ("RE: past due", "We never received that invoice. Please resend to ap@ our domain. Also needs the PO number on it."),
        ("payment", "Check was mailed {date}. Please release the hold."),
        ("disputed charge", "We were billed for more units than we received. Not paying until this is corrected."),
        ("Re: Invoice", "AP says this was paid. Please check your records. Attached remittance."),
    ],
    "chatter": [
        "{account} on credit hold, {days} days past due. order {order_number} blocked. @{rep_first} can you help?",
        "payment for {account} went to old lockbox. finance hunting it down",
        "credit hold exception approved for {account}. order shipping",
        "fyi {account} short-paid {invoice_number} by the discount. explaining conditions",
        "{account} invoice rejected - no PO reference. re-issued",
        "heads up {account} asked for a payment plan. cash flow issues",
    ],
}

TOPICS["rep_handoff"] = {
    "subjects": [
        "Introduction - your new Orvane account rep",
        "Account transition from {old_rep}",
        "Intro call w/ {contact_first} - new rep",
        "Handoff meeting w/ {old_rep}",
        "Transition plan - {account}",
        "New account team intro",
        "Getting up to speed on {account}",
        "Account review w/ previous rep",
    ],
    "summaries": [
        "Handoff call with {old_rep}. Key context: {contact_first} is the champion, {contact2_name} controls budget. Open opps: server refresh ({amount}), Win 11 tail. Watch-outs: an escalation last quarter still stings.",
        "Intro call with {contact_first}. Introduced myself as their new rep. They were polite but noted this is their 3rd rep in 2 years. Committed to being around.",
        "Spoke w/ {contact_first}. They liked {old_rep} and are sorry to see them go. Promised continuity - same SE ({se_name}), same pricing, no surprises.",
        "First meeting at {account}. Spent most of it listening. Learned more about their environment than the CRM had - {servers} servers, not the 20 in our notes. CRM is wrong in a lot of places.",
        "Handoff notes from {old_rep} were thin. Rebuilding from emails and quotes. Calling every contact this week.",
        "{contact_first} asked what happens to the deals {old_rep} was working. Confirmed: all pricing and commitments stand.",
        "Intro email got no response. Called - got VM. Will try {contact2_name}.",
        "Transition meeting with {old_rep}, {se_name} and {contact_first}. Clean handoff. {old_rep} stayed on for the first 10 min then dropped.",
        "New rep intro. {contact_first} was blunt: 'previous rep only called when they wanted something.' Noted.",
        "Getting up to speed: pulled all orders, cases and quotes for the last 2 years. Total spend {amount}. Biggest gap is storage - they buy it from {competitor}.",
        "{contact_first} took the chance to vent about a few open issues {old_rep} never closed: a credit memo, a missing dock, an RMA. Fixing all three this week.",
        "Quick intro with {contact2_name}. They didn't know who their rep was. Now they do.",
        "Territory realignment moved {account} to me. {old_rep} still owns the parent account. Need to coordinate.",
        "Intro went well. {contact_first} invited me to their quarterly IT planning meeting on {date}.",
    ],
    "next_steps": [
        "Send intro email to all contacts",
        "Review open opps w/ {old_rep}",
        "Clean up CRM contact and environment data",
        "Close out open items {old_rep} left",
        "Schedule intro w/ {contact2_name}",
        "Attend IT planning meeting {date}",
        "Coordinate w/ {old_rep} on parent account",
        "Pull 2-yr order + case history",
    ],
    "emails_out": [
        ("Introduction - your new Orvane rep", "Hi {contact_first},\n\nI'm {rep_name}, and I'm taking over as your account rep from {old_rep}. {se_name} stays on as your SE, and all existing quotes and pricing stand. I'd love 30 minutes to hear what's on your plate - any time next week?\n\n{rep_name}"),
        ("Following up - intro", "Hi {contact_first} - following up on my intro last week. No agenda, just want to put a face to the name. Coffee or a call, your pick."),
        ("Open items", "{contact_first},\n\nThanks for the candor today. On the three open items:\n1. Credit memo - processed, should hit by {date}\n2. Missing dock - shipping today\n3. RMA - case {case_number} reopened and escalated\n\n{rep_first}"),
        ("Intro - {rep_name}", "Hi {contact2_name},\n\nI'm your new Orvane account rep. Wanted to introduce myself and make sure you have my direct line. If anything comes up - orders, support, pricing - I'm the person to call."),
        ("Handoff - joint call", "Hi {contact_first} - {old_rep} and I would like to do a quick joint call to make the handoff clean. 20 min, {date}?"),
    ],
    "emails_in": [
        ("RE: Introduction", "Welcome. Third rep in two years, so forgive me if I don't memorize your name yet. Happy to meet."),
        ("Re: Following up", "Sorry, busy month. Next week works. Tuesday afternoon?"),
        ("open issues", "Glad you reached out. A few things {old_rep} was working on never got closed. Can we go through them?"),
        ("where's {old_rep}?", "Haven't heard from {old_rep} in a month. Is there a new contact? We have an order question."),
        ("Re: Intro", "Thanks {rep_first}. Good to know who to call. We're starting planning for {fy} soon, would like you involved."),
    ],
    "chatter": [
        "took over {account} from {old_rep}. 3rd rep in 2 yrs for them. need to earn trust",
        "@{old_rep} thanks for the handoff notes on {account}. super helpful",
        "CRM data on {account} is way off. {servers} servers, not 20. cleaning up",
        "{account} had 3 open items {old_rep} never closed. fixing this week",
        "fyi {account} invited me to their IT planning mtg {date}. good start",
        "anyone know {contact_name} at {account}? new rep here, trying to get context",
    ],
}

TOPICS["relationship_check_in"] = {
    "subjects": [
        "Check-in w/ {contact_first}",
        "Quarterly touch base",
        "Coffee w/ {contact_name}",
        "Catch up - {account}",
        "Relationship check-in",
        "Lunch w/ {contact_first}",
        "How's it going call",
        "Quick check-in",
    ],
    "summaries": [
        "Caught up w/ {contact_first}. Nothing urgent. Their team is heads down on a migration. Mentioned they'll need more storage next year. Noted.",
        "Coffee with {contact_name}. Mostly personal - kid starting college, they're training for a half marathon. Work-wise, IT team is down 2 heads and they're stretched.",
        "Quick call. All good. No open issues. They're happy.",
        "Lunch w/ {contact_first}. Good to talk outside the office. They opened up about frustrations with their leadership. Not much I can do but listen.",
        "Check-in. {contact_first} mentioned they're evaluating a move to {cloud} for some workloads. Not a threat to everything, but some on-prem spend will shift. Good to know early.",
        "Touch base w/ {contact2_name}. Business is good - growing {growth}%. They're hiring in {site_city}. Possible new site coming.",
        "Called just to check in. {contact_first} was surprised - 'you're not selling anything?' No, just checking in. Built goodwill.",
        "Check-in surfaced a support issue they hadn't escalated. Laptop docks dropping connections. Opened a case and looped in {se_name}.",
        "Caught {contact_first} at the end of a bad week - outage on Tuesday, not ours. Offered help. They appreciated it.",
        "Quarterly touch base. They've been quiet because the budget is tight. Nothing until {quarter}. Staying close.",
        "Spoke w/ {contact_first}. Happy with Orvane. Asked about the Orvane Tech Summit - want to attend. Sent registration info.",
        "Check-in w/ {contact_name}. They're getting promoted - moving to a broader role covering infrastructure and security. Good for us.",
        "Coffee. Learned their CEO is pushing for an AI strategy. {contact_first} doesn't know where to start. Offered a workshop.",
        "Quick catch-up via text. All good, talk next month.",
    ],
    "next_steps": [
        "Check in again in {weeks} wks",
        "Open case for dock connectivity issue",
        "Send Orvane Tech Summit registration",
        "Offer AI strategy workshop",
        "Follow up on {site_city} expansion",
        "Note {cloud} migration plans for account plan",
        "Send congrats on promotion",
        "Revisit storage need in {quarter}",
    ],
    "emails_out": [
        ("Checking in", "Hi {contact_first} - no agenda, just checking in. How are things going? Anything I can help with?\n\n{rep_first}"),
        ("Good catching up", "{contact_first}, good catching up today. Good luck with the half marathon! I'll check back in a few weeks on the storage question."),
        ("Tech Summit", "Hi {contact_first} - registration link for the Orvane Tech Summit attached. Let me know if you want help picking sessions; there's a good track on infrastructure modernization."),
        ("AI workshop offer", "{contact_first},\n\nFollowing up on our coffee. If it's useful, {se_name} can run a half-day AI strategy workshop with your team - no hardware pitch, just helping you figure out use cases and what you'd need. Open offer."),
        ("Re: outage", "Sorry to hear about Tuesday. If there's anything we can do - even if it's not our gear - just say the word."),
    ],
    "emails_in": [
        ("Re: Checking in", "All good here, thanks for checking in. Busy but nothing on fire. Talk soon."),
        ("hey", "{rep_first}, random q - do you know anyone good at {competitor} support? We have one of their boxes and it's giving us grief. lol"),
        ("Re: Good catching up", "Thanks! Will let you know how the race goes. Definitely talk storage in a few weeks."),
        ("Tech Summit?", "Is the Tech Summit worth it this year? Last year I spent most of it in sales sessions."),
        ("RE: AI workshop offer", "That would actually be really helpful. Let me check calendars and get back to you."),
    ],
    "chatter": [
        "coffee w/ {contact_first} at {account}. learned they're down 2 IT heads. stretched thin",
        "check-in at {account} surfaced a dock issue nobody escalated. opened case",
        "fyi {account} looking at {cloud} for some workloads. not all of it",
        "{contact_name} at {account} getting promoted to broader role. good for us",
        "just checking in call to {account} built more goodwill than any pitch. remember to do these",
        "{account} CEO wants AI strategy. offered workshop. @{se_name} you in?",
    ],
}

TOPICS["event_followup"] = {
    "subjects": [
        "Orvane Tech Summit follow-up",
        "Great to see you at Tech Summit",
        "Webinar follow-up - {initiative}",
        "Post-event: next steps",
        "Tech Summit session recap",
        "Event lead follow-up - {contact_name}",
        "Following up from the booth",
        "Executive dinner follow-up",
    ],
    "summaries": [
        "{contact_first} attended Tech Summit, went to the AI infrastructure track. Stopped by the booth asking about Atlas AI. Follow-up call booked.",
        "Met {contact_name} at the Tech Summit executive dinner. Sat next to them. They're a {contact_title} at {account}, {seats} employees. Interested in Converge after the keynote.",
        "Webinar lead - {contact_first} attended the {initiative} webinar and downloaded the reference architecture. Called. They're early-stage research.",
        "Post-Summit call. {contact_first} came back excited about Orvane Flex. Their CFO wants opex for everything. Scheduling a deeper session.",
        "Event lead - scanned at the booth. Called. {contact_first} said they were just picking up swag. Not a real lead.",
        "Follow-up from Summit hands-on lab. {contact_first} tried the Converge lab and wants a POC. Fast mover.",
        "{contact_first} attended the security session and asked about BMC isolation best practices. Sent the guide. Opened a conversation about their outdated firmware.",
        "Spoke w/ {contact_first}. Summit was their first exposure to Orvane beyond laptops. Didn't know we did servers. Booked a discovery.",
        "Webinar attendee from {account}. Already a customer for clients. Asked about Vault for M365 backup. Easy expansion.",
        "Executive dinner follow-up. {contact2_name} ({contact2_title}) wants an executive briefing for their leadership team.",
        "Tried to follow up with Summit lead. 3 attempts, no response. Moving to nurture.",
        "{contact_first} told me the Summit keynote demo of Orvane Insight was the best part. Wants it for their environment.",
        "Customer advisory board meeting at Summit. {contact_first} gave candid feedback on our support portal. Passing to product team.",
        "Summit attendee {contact_first} mentioned their {competitor} contract ends in {quarter}. Perfect timing.",
    ],
    "next_steps": [
        "Book discovery w/ {contact_first}",
        "Send reference architecture from session",
        "Schedule Converge POC",
        "Set up executive briefing w/ {contact2_name}",
        "Move lead to nurture",
        "Send BMC isolation best practice guide",
        "Demo Orvane Insight on their environment",
        "Track {competitor} contract end in {quarter}",
    ],
    "emails_out": [
        ("Great to meet you at Tech Summit", "Hi {contact_first},\n\nGreat chatting at the Orvane Tech Summit. As promised, the Atlas AI reference architecture from the session is attached. Would a 30-min call next week be useful to talk about your {initiative}?\n\n{rep_first}"),
        ("Following up - executive dinner", "{contact2_name},\n\nThanks for the great conversation at dinner. You mentioned an executive briefing for your leadership team - I'd be glad to arrange one at our briefing center or on site. A few dates attached."),
        ("Webinar follow-up", "Hi {contact_first} - thanks for joining the webinar. The recording and slides are here. If any of it sparked questions specific to {account}, happy to talk."),
        ("Converge lab - next step", "{contact_first},\n\nGlad you enjoyed the Converge hands-on lab. If you'd like to try it with your own workloads, we can ship a 3-node POC. {se_name} will help set up. Timing?"),
        ("Insight demo", "Hi {contact_first} - you mentioned the Insight demo at Summit. We can run the collector against your environment for 2 weeks free and show you what it finds. Interested?"),
    ],
    "emails_in": [
        ("RE: Great to meet you", "Thanks for following up. Yes, next week works. We're early but serious."),
        ("Summit", "Enjoyed the summit. The AI session was useful. Can you send the slides from the keynote?"),
        ("Re: Webinar follow-up", "Thanks but I was just curious. Not working on anything right now."),
        ("POC", "Want to do the Converge POC we talked about at Summit. How fast can you ship?"),
        ("unsubscribe", "Please remove me from your mailing list."),
    ],
    "chatter": [
        "Tech Summit lead from {account} wants Converge POC. hot",
        "met {contact_name} at exec dinner. {account} wants exec briefing",
        "@{se_name} Summit lead {account} wants Insight demo on their env",
        "fyi Summit leads: lots of AI interest, not much budget. qualify hard",
        "{account} {competitor} contract ends {quarter}. met at Summit, perfect timing",
        "customer advisory board feedback on support portal from {account}. passing to product",
    ],
}

TOPICS["m_and_a_integration"] = {
    "subjects": [
        "{account} acquisition - IT integration",
        "M&A impact on Orvane relationship",
        "Integrating acquired company infrastructure",
        "Post-merger IT standardization",
        "Acquisition announced - next steps",
        "Divestiture - separating IT",
        "M&A: contract consolidation",
        "Day 1 readiness for acquisition",
    ],
    "summaries": [
        "{account} announced acquisition of a smaller competitor. {contact_first} says the acquired company runs {competitor} servers and a mix of laptops. Integration plan wants everyone on one standard within 12 months. Big opportunity.",
        "{account} is being acquired. {contact_first} doesn't know what happens to IT. Acquirer has their own vendors. Pipeline at risk.",
        "Integration planning: {qty} new employees need laptops on the {account} standard. Day 1 is {date}. Need imaging and shipping lined up.",
        "Spoke w/ {contact_first}. Acquired company has a datacenter in {site_city} they want to shut down. Workloads move to {account}'s DC. Need capacity: ~{servers} additional hosts worth of workload.",
        "Divestiture: {account} is spinning off a division. The spun-off company needs its own infrastructure. Possibly a new customer.",
        "Contract consolidation: acquired company had its own agreement with us at different pricing. Merging into {account}'s agreement. They save money.",
        "Post-merger, the new combined IT team is evaluating vendors from scratch. Both sides had different preferences. Pitching to the combined team on {date}.",
        "Day 1 readiness: acquired employees need {account} email, VPN and laptops. Pre-imaged {product} units shipped to their offices. Swap on Day 1.",
        "{contact2_name} from the acquired company joined the call. They're used to {competitor}. Need to win them over.",
        "Integration slowed - legal close delayed by regulatory review. Hardware orders on hold until close.",
        "Acquirer's IT ({competitor} shop) is taking over. {contact_first} is fighting to keep Orvane but may lose. Worth an exec-to-exec call.",
        "Quick call. Acquisition closed. Integration starting. {contact_first} will send a project plan.",
        "M&A data migration: need to move {tb}TB from acquired company's storage. Proposing migration services.",
        "Spoke w/ {contact_first}. The acquisition doubled their size overnight. Everything needs to scale. Good problem for us.",
    ],
    "next_steps": [
        "Get integration timeline from {contact_first}",
        "Quote {qty} laptops for Day 1 on {date}",
        "Size capacity for DC consolidation",
        "Merge acquired company's contract",
        "Prep pitch for combined IT team {date}",
        "Request exec-to-exec call w/ acquirer",
        "Scope data migration for {tb}TB",
        "Meet {contact2_name} from acquired co",
    ],
    "emails_out": [
        ("Congrats on the acquisition", "Hi {contact_first},\n\nCongrats on the news. I imagine integration is going to keep you busy. A few ways we can help: Day 1 laptops pre-imaged to your standard, capacity for the DC consolidation, and data migration services. Let me know when you're ready to talk.\n\n{rep_first}"),
        ("Day 1 laptops", "{contact_first},\n\nPlan for Day 1: {qty} {product} units imaged to your standard, shipped to the acquired company's offices to arrive {date}. Users swap on Day 1 and return old devices in the same box. Quote attached."),
        ("Contract consolidation", "Hi {contact2_name} - the acquired company's agreement with us has worse pricing than {account}'s. We'll merge them under {account}'s agreement effective at close."),
        ("Meeting the combined IT team", "{contact_first}, confirming {date} for the combined IT team session. I'll keep it focused on how we support both sides today and what consolidation could look like."),
        ("Data migration scope", "Hi {contact_first} - for the {tb}TB migration from the acquired company's storage, our services team proposes a phased migration over {weeks} weeks. Scope attached."),
    ],
    "emails_in": [
        ("acquisition", "Big news coming tomorrow. Can't say more yet. Will call you."),
        ("RE: Congrats", "Thanks. It's going to be a crazy year. Day 1 is {date}. We'll need laptops for {qty} people."),
        ("acquired", "We're being acquired. I don't know what happens to our projects yet. Please hold all open quotes."),
        ("integration", "The acquirer's IT team is taking over infrastructure decisions. I'll try to keep you in but no promises."),
        ("Day 1", "Laptops arrived at all 4 offices. Users are happy. Thanks for pulling this off on short notice."),
    ],
    "chatter": [
        "{account} acquiring a {competitor} shop. integration = standardization = opportunity",
        "{account} being acquired. pipeline at risk. acquirer uses {competitor}",
        "Day 1 at {account} - {qty} laptops on {date}. ops can we do it?",
        "@{rep_first} {account} combined IT team evaluating from scratch. pitch {date}",
        "fyi {account} acquisition delayed by regulatory review. orders on hold",
        "Day 1 laptops delivered at {account}. smooth",
    ],
}

TOPICS["layoffs_cost_cutting"] = {
    "subjects": [
        "Cost reduction at {account}",
        "Layoffs - impact on IT spend",
        "Budget cuts + project freeze",
        "Right-sizing support contracts",
        "Reducing IT costs - options",
        "Headcount reduction - device recovery",
        "Cost-out initiative w/ {contact2_name}",
        "Spending freeze update",
    ],
    "summaries": [
        "{account} announced a {pct}% workforce reduction. {contact_first} survived but lost two people on the infra team. Every open project is under review. Our refresh is paused, not cancelled - their words.",
        "Cost-out conversation with {contact2_name}. They're not buying anything new this half; the ask is how to spend less on what they already have. Came prepared with three ideas: co-term and right-size ProCare, drop Mission Critical on non-prod, and recover/redeploy devices from departed employees instead of buying new.",
        "Layoffs left ~{qty} laptops sitting in a storage room, some still with user data. Pitched a recovery + re-image service: wipe, re-image, re-stock for new hires when hiring resumes. ITAD for anything over 4 yrs.",
        "Spending freeze through end of {fy}. Only break/fix and security-driven spend allowed. Worth noting {advisory} counts as security-driven.",
        "Spoke w/ {contact_first}. They've been told to cut IT spend {pct}% next year. Biggest line items are cloud ({cloud}) and software licensing, not hardware. Opportunity to repatriate some steady-state workloads if the math works.",
        "Honest conversation. {contact_first} asked me not to call for a couple of months - they're in survival mode and every vendor call is a reminder of what they can't do. Respecting it. Will send a short note in {weeks} wks.",
        "Their hypervisor bill is the single biggest cost lever. Fewer hosts = fewer cores to license. Consolidation saves money even with new hardware. {contact2_name} wants to see the numbers.",
        "Remote-site closures: {account} is closing 4 of 11 offices. Equipment comes back to HQ. Asked if we can handle pickup and ITAD at the closing sites. Yes - quoting.",
        "DaaS conversation got traction for the first time. With a smaller headcount they want to stop owning depreciating laptops. Per-seat monthly that flexes down if they shrink again is the hook.",
        "Short call. Freeze lifted for anything with a 12-month payback. Server consolidation qualifies. Re-submitting the business case.",
        "Cancelled the Clarity monitor order - {qty} units. Not worth fighting. Kept the relationship.",
        "{contact_first} is now covering three jobs. Simplicity matters more than price right now. Fewer consoles, fewer contracts, fewer vendors.",
        "Asked to reduce ProCare on {servers} servers from Mission Critical to ProCare Plus mid-term. Contract doesn't allow mid-term downgrade, but we can align it at renewal on {date}. Customer grumbled, understood.",
        "Spoke w/ {contact2_name}. Board wants every vendor to show a cost reduction. Offered extended payment terms through Orvane Financial Services and a price hold. They took the price hold.",
    ],
    "next_steps": [
        "Build cost-reduction options on existing spend",
        "Quote device recovery + re-image for {qty} laptops",
        "Model consolidation savings on {hypervisor} licensing",
        "Quote ITAD + pickup at closing sites",
        "Re-submit server business case w/ 12-mo payback",
        "Send short check-in note in {weeks} wks - nothing salesy",
        "Align ProCare downgrade at renewal {date}",
        "Price DaaS w/ flex-down terms",
    ],
    "emails_out": [
        ("Ways to lower your Orvane spend", "Hi {contact2_name},\n\nI know new spend is off the table, so here are three ways to reduce what you're already paying us:\n1. Co-term and right-size ProCare (non-prod to ProCare Plus at renewal)\n2. Recover and re-image laptops from departed employees instead of buying new\n3. Consolidate hosts to cut {hypervisor} core licensing\n\nRough savings for each attached.\n\n{rep_name}"),
        ("Laptops in storage", "{contact_first},\n\nWe can pick up the ~{qty} laptops from departed employees, wipe them to NIST 800-88, re-image to your standard and hold them in our depot until you're hiring again. Anything over 4 yrs goes to ITAD with value credited back. Quote attached."),
        ("No ask, just a note", "Hi {contact_first} - not selling anything. Know it's been a rough few months. If there's something we can take off your plate, shout. Otherwise I'll stay out of your way.\n\n{rep_first}"),
        ("Office closures - equipment", "{contact_first}, for the 4 closing offices we can do pickup, data wipe and ITAD on site, with a certificate per serial. One PO, one schedule. Pricing per site attached."),
        ("Server consolidation - 12-month payback", "Hi {contact2_name},\n\nUpdated business case attached. Payback lands at about 11 months, driven mostly by licensing and power. Happy to walk through the assumptions with whoever owns the freeze exceptions."),
    ],
    "emails_in": [
        ("hold", "{rep_first}, we've been told to hold all purchases until further notice. Please don't send anything new. I'll let you know when that changes."),
        ("RE: Ways to lower your Orvane spend", "Option 2 is interesting. We have a room full of laptops and no plan for them. What does it cost?"),
        ("cancel monitors", "Need to cancel the monitor order. Sorry. Not my call."),
        ("Re: No ask, just a note", "Appreciate that. It's been brutal. Talk in a couple months."),
        ("support downgrade", "Can we drop the Mission Critical to the cheaper tier now? We need savings this quarter not next year."),
    ],
    "chatter": [
        "{account} announced {pct}% RIF. refresh paused. pulling from commit, leaving in pipe",
        "{account} has ~{qty} laptops from layoffs sitting in a closet w/ data still on them. recovery + re-image quote going out. this is a good service, use it",
        "fyi {contact_first} at {account} asked for space. giving it. don't anyone else call them pls",
        "freeze at {account} lifted for anything w/ 12 mo payback. consolidation case going back in",
        "cost-out convos are the new normal. showing customers how to spend LESS with us is winning trust",
        "@{rep_first} {account} wants mid-term ProCare downgrade. contract says no. any flexibility?",
    ],
}

TOPICS["expansion_new_site"] = {
    "subjects": [
        "New site - {site_city}",
        "Site build-out: IT requirements",
        "{account} expansion to {site_city}",
        "New office kit list",
        "Greenfield site - network + compute",
        "Site opening timeline",
        "New facility - edge + endpoints",
        "Expansion BOM review",
    ],
    "summaries": [
        "{account} is opening a new facility in {site_city}, ~{seats} people at full ramp. Opening {date}. Needs everything: laptops, docks, monitors, switches, a small server footprint, and conference rooms.",
        "Site requirements walk w/ {contact_first}. IDF on each floor, MDF on 1. 2 x 48-port PoE+ per IDF, Mesh core in MDF. Two Outpost nodes for local file/print and the badge system. Rest goes to the HQ DC over SD-WAN.",
        "Timeline is tight: building turnover {date}, staff arrive 3 wks later. Proposed staging everything at our integration center and delivering a single coordinated shipment.",
        "Conference rooms: 12 rooms, they want a standard kit - Cadence mini PC, Clarity display, USB camera/speaker bar. Asked for a 'room in a box' SKU. Working with {se_name} on a BOM.",
        "Short call. Expansion confirmed. {qty} seats for wave 1, more in {quarter}.",
        "Spoke w/ {contact2_name}. New site is a manufacturing plant, not offices. Different gear: Bastion rugged laptops on the floor, Wisp thin clients in the break areas, ruggedized edge server near the line.",
        "Construction delays pushed the site opening from {date} by {weeks} weeks. Holding the order in our warehouse rather than shipping to an unsecured building.",
        "Discussed power and cooling for the new server room. It's a closet with a single 20A circuit. Two Outpost nodes and a switch fit; a rack of Atlas does not.",
        "{account} expanding into Canada - new office in {site_city}. Need bilingual keyboard SKUs and Canadian power cords. Checking stock.",
        "Their real estate team chose the site without asking IT. No fiber to the building yet. Carrier says {weeks} weeks. Proposed LTE failover as a bridge.",
        "Expansion BOM approved, {amount} total. PO coming from {contact2_name}.",
        "Site went live. Install team had it done over a weekend. {contact_first} sent a photo of the finished IDF - cleanest cabling they've ever had.",
        "Asked about receiving at a site with no staff yet. Arranged white-glove delivery: our team receives, unpacks, sets up, removes packaging.",
        "{contact_first} wants this new site to be the template for the next 3. Documenting the standard as we go.",
    ],
    "next_steps": [
        "Build full site BOM for {site_city}",
        "Stage at integration center, single shipment",
        "Spec 'room in a box' conference kit",
        "Check stock on Canadian keyboards + power cords",
        "Quote LTE failover as fiber bridge",
        "Arrange white-glove delivery + setup",
        "Hold order in warehouse until building ready",
        "Document site standard for future rollouts",
    ],
    "emails_out": [
        ("{site_city} site - draft BOM", "Hi {contact_first},\n\nDraft BOM for {site_city}:\n- {qty} x {product} + Tether dock + 2 x Clarity 24\n- 2 x Mesh 48-port PoE+ per IDF, core pair in MDF\n- 2 x Outpost for local services\n- 12 x conference room kits\n\nAll staged at our integration center and delivered together. Total on {quote_number}.\n\n{rep_first}"),
        ("Site opening - delivery plan", "{contact_first},\n\nGiven the construction delay, I suggest we hold the order in our warehouse and deliver the week before staff arrive. No sense leaving {amount} of gear in an unsecured building."),
        ("Conference room standard", "Hi {contact_first} - here's the 'room in a box' standard {se_name} put together: Cadence mini PC, Clarity 55in, camera/speaker bar, wall mount, cabling. One SKU per room. Pricing attached."),
        ("Fiber delay workaround", "{contact_first}, if fiber is {weeks} weeks out, an LTE gateway on the edge firewall can get you running on day one. Not ideal for heavy traffic, but enough for SaaS and Teams."),
        ("Site template", "Hi {contact_first} - attached is the {site_city} site standard as built: BOM, rack elevation, VLAN plan, config templates. Should make the next three a lot faster."),
    ],
    "emails_in": [
        ("new site", "We're opening a new office in {site_city}. Need everything. Can we get on a call this week?"),
        ("RE: draft BOM", "Looks right. Swap monitors to 27 for the engineering floor. And we need 6 more seats than I told you."),
        ("delay", "Construction is behind again. Building won't be ready until at least {date}. Please hold everything."),
        ("Re: Site opening", "Site is live. Thank you to your install team, they were great."),
        ("receiving", "There's nobody at the new site to receive deliveries yet. How do we handle that?"),
    ],
    "chatter": [
        "{account} opening {site_city}, {seats} seats at full ramp. full site build. @{se_name} let's do the BOM together",
        "construction delay at {account} {site_city} site, holding order in warehouse. ops pls don't ship",
        "{account} {site_city} site live! install team crushed it",
        "anyone know if we have bilingual keyboards in stock? {account} Canada office",
        "{account} wants {site_city} as template for 3 more sites. documenting the standard",
        "white glove delivery for a site with no staff yet - does ops still offer that?",
    ],
}

TOPICS["small_business_purchase"] = {
    "subjects": [
        "Laptop purchase - {account}",
        "Small business order - {qty} laptops",
        "Quote request - {contact_name}",
        "Order w/ credit card",
        "New business setup - {contact_first}",
        "Replacement laptop - urgent",
        "Small office setup",
        "Phone order - {account}",
    ],
    "summaries": [
        "{contact_first} owns {account}, 8 employees. Needs 3 laptops for new hires. Paying by card. Recommended {product}. Ordered on the phone.",
        "Small business owner called - laptop died, needs a replacement tomorrow. Checked stock, expedited shipping. Done.",
        "Quick quote for {contact_first}. {qty} laptops + docks. They're a small accounting firm, tax season is coming. Need delivered by {date}.",
        "{contact_first} wanted to know the difference between Aster and Nova. Explained: Aster has business warranty, TPM, manageability, longer availability. Went Aster.",
        "Card declined - billing address mismatch. {contact_first} called their bank. Re-ran, went through.",
        "Small biz owner asked if we do setup. Offered our basic setup service - unbox, Windows setup, Microsoft 365 sign-in, data transfer from old PC. They took it.",
        "{contact_first} runs a dental office. Needs a front-desk PC, 2 laptops for the hygienists, and a small server for the practice management software. Way more than they expected to spend. Phasing it.",
        "Spoke with {contact_first} - they bought one laptop last year, liked it, want 4 more. Same model if possible. Model was discontinued, offered the successor.",
        "Small business financing: {contact_first} asked about paying monthly. Orvane Financial Services has a small business program. Sent application link.",
        "{contact_first} is very price sensitive. Found them a refurbished option through the outlet and a business warranty upgrade. Happy.",
        "Called back about a quote from last week. They bought from a big box store. Lost on price, but they said they'd come to us for the next batch because the box store had no business warranty.",
        "Owner-operator, runs a landscaping company. Needs 2 rugged tablets for crews. Bastion fits. Card order.",
        "Asked about tax exemption - they're a nonprofit. Need their exemption certificate on file before we can remove tax. Sent instructions.",
        "{contact_first} wanted to add accidental damage protection after the fact. Possible within 30 days of purchase. Added.",
    ],
    "next_steps": [
        "Send order confirmation + tracking",
        "Expedite shipping for replacement",
        "Send quote for {qty} laptops + docks",
        "Re-run card after bank clears it",
        "Book setup service",
        "Send OFS small business application",
        "Get tax exemption certificate on file",
        "Add accidental damage within 30 days",
    ],
    "emails_out": [
        ("Your Orvane order", "Hi {contact_first},\n\nThanks for your order! {qty} x {product}, order {order_number}. Ships in 2-3 business days. I'll send tracking once it's out. Let me know if you need anything.\n\n{rep_first}"),
        ("Quote - {qty} laptops", "Hi {contact_first} - quote attached for {qty} {product} with docks. Delivered by {date} if ordered by Friday. Card or invoice, your pick."),
        ("Setup service", "{contact_first}, booked your setup service for {date}. Tech will call ahead. Have your Microsoft 365 admin login handy."),
        ("Monthly payment option", "Hi {contact_first} - here's the link for Orvane Financial Services' small business program. Takes about 10 minutes, decision usually same day."),
        ("Following up", "Hi {contact_first} - just checking that the laptops arrived OK and everyone's set up. Anything you need?"),
    ],
    "emails_in": [
        ("laptops", "Hi, I need 3 laptops for my office. Nothing fancy. What do you recommend? Budget is around $1,200 each."),
        ("order", "Got the laptops. They're great. Thanks!"),
        ("help", "My laptop won't turn on and I have a client meeting tomorrow. Can you get me a new one fast??"),
        ("card", "My card got declined but I have the money. What do I do?"),
        ("Re: Quote", "Thanks. Can you do any better on price? I'm a small business lol"),
    ],
    "chatter": [
        "small biz order from {account} - 3 laptops on card. easy one",
        "{account} owner needed a laptop by tomorrow. expedited. happy customer",
        "fyi lost {account} to big box store on price. they'll be back, no business warranty there",
        "dental office {account} needs way more than they budgeted. phasing it",
        "small biz financing program is underused. offer it",
        "{account} card declined, billing address mismatch. cleared up",
    ],
}

TOPICS["software_licensing"] = {
    "subjects": [
        "Software licensing - {account}",
        "Orvane Manage license renewal",
        "Vault Backup license true-up",
        "Licensing audit question",
        "Orvane Shield seat count",
        "Software subscription renewal",
        "License key issue",
        "OS licensing for new servers",
    ],
    "summaries": [
        "Orvane Manage renewal: they have {seats} licenses, using ~{pct}% of them. Right-sizing at renewal.",
        "Vault Backup true-up: protecting {tb}TB but licensed for less. True-up invoice coming. Customer expected it.",
        "{contact_first} asked about OS licensing on the new servers - Windows Server Datacenter vs. Standard. With {hypervisor} and many VMs per host, Datacenter makes more sense. Per-core again.",
        "Orvane Shield expansion - adding {seats} seats for the acquired company. Pro-rated to co-term.",
        "License key for Insight not working after upgrade. Opened case {case_number}. Fixed in 2 hrs - key needed re-activation.",
        "Customer got an audit letter from a software vendor (not us). Asked if we can help them pull hardware inventory for the audit. Exported from Orvane Manage.",
        "Discussed bundling Orvane Manage + Shield. Bundle price is lower than separate. They switched.",
        "Spoke w/ {contact_first}. They let Orvane Manage lapse 2 months ago. Re-subscribed. No penalty.",
        "SQL Server licensing came up on the database server refresh. Fewer, faster cores saves them real money on Enterprise licensing.",
        "Software subscription renewal {amount}. Approved.",
        "{contact2_name} asked for a single view of every Orvane software subscription and when each renews. Built a summary.",
        "Shield licensing: they had both us and {competitor} endpoint agents on some devices. Removing {competitor} saves them money.",
        "Customer asked if Vault Backup is licensed per socket, per VM or per TB. Per front-end TB. Simplest model.",
        "Licensing portal access issue - their admin left and nobody has the login. Reset ownership to {contact_first}.",
    ],
    "next_steps": [
        "Right-size Orvane Manage at renewal",
        "Send Vault true-up invoice",
        "Quote Windows Server Datacenter for new hosts",
        "Pro-rate Shield seats to co-term",
        "Export hardware inventory for audit",
        "Build software subscription summary",
        "Reset licensing portal owner to {contact_first}",
        "Quote Manage + Shield bundle",
    ],
    "emails_out": [
        ("Orvane Manage renewal", "Hi {contact_first},\n\nYour Orvane Manage renewal is coming up {date}. You're licensed for {seats} and using about {pct}%. I'd suggest we right-size at renewal. Quote attached at the lower count."),
        ("Vault true-up", "{contact_first} - heads up on the Vault Backup true-up. You're protecting {tb}TB vs. licensed capacity. True-up invoice to follow. Happy to walk through the math."),
        ("Software summary", "Hi {contact2_name} - attached is every Orvane software subscription you have, count, renewal date and annual cost. Want to co-term them?"),
        ("Bundle pricing", "{contact_first}, Manage + Shield bundle comes in at less than the two separately. Quote attached."),
        ("Portal access", "Hi {contact_first} - licensing portal ownership is now in your name. Password reset link sent separately."),
    ],
    "emails_in": [
        ("license key", "License key isn't working after the upgrade. Insight won't start. Help?"),
        ("audit", "We got an audit letter from our software vendor. Can you help us pull hardware inventory?"),
        ("RE: Vault true-up", "Expected. Send the invoice."),
        ("licensing", "Is Vault licensed per VM, per socket or per TB? Trying to budget."),
        ("lapsed", "We let Orvane Manage lapse. Can we reinstate without penalty?"),
    ],
    "chatter": [
        "{account} using {pct}% of Manage licenses. right-sizing at renewal, builds trust",
        "Vault true-up at {account}. customer expected it, no drama",
        "@{se_name} {account} license key won't activate after Insight upgrade. case {case_number}",
        "fyi {account} has both Shield and {competitor} agents on some devices. consolidation opp",
        "software audit at {account} (not ours). we helped w/ inventory export. goodwill",
        "{account} licensing portal admin left, nobody had login. fixed",
    ],
}

TOPICS["services_deployment"] = {
    "subjects": [
        "Deployment services - {account}",
        "Imaging + asset tagging",
        "Rack & stack - {order_number}",
        "Data migration services",
        "ITAD pickup scheduling",
        "Residency services - onsite engineer",
        "Deployment kickoff call",
        "Services SOW review",
    ],
    "summaries": [
        "Deployment kickoff for {qty} laptops. Factory imaging with their Intune profile, asset tags, BIOS settings locked. Drop-ship to users. {weeks}-week rollout.",
        "Rack & stack for {servers} servers. Our team racks, cables, powers on and hands off to their team for OS config. 2 days onsite.",
        "Data migration from {competitor} array to {storage_product}: {tb}TB, {weeks} weeks. Using host-based migration for VMs, array-based for file shares.",
        "ITAD pickup for {qty} old devices. NIST 800-88 wipe or physical destruction per their policy. Certificates per serial.",
        "Residency services: an onsite Orvane engineer for 6 months to help with the infrastructure refresh. They're short-staffed.",
        "SOW review: they want fixed price, not time and materials. Scope is clear enough. Converting.",
        "Imaging issue: the image they gave us had a driver that conflicted with the new model. Caught it in our QA. Fixed before shipping.",
        "Deployment progress: {pct}% complete. On track. Two users had issues with data transfer - resolved.",
        "Rack & stack done. Cabling labeled, rack elevation documented, everything powered on and handed off. Customer was happy.",
        "Data migration cutover weekend went smoothly. {tb}TB moved, validation passed. Old array decommissioned.",
        "Spoke w/ {contact_first}. They want deployment services for the next wave too. Same team please.",
        "ITAD value report: their old devices generated credit toward the new purchase.",
        "Residency engineer is effectively part of their team now. They want to extend 6 more months.",
        "Deployment delayed - customer's Intune environment had a misconfigured enrollment profile. Our team helped them fix it.",
    ],
    "next_steps": [
        "Schedule deployment kickoff",
        "Get Intune tenant ID + enrollment profile",
        "Book rack & stack team for {date}",
        "Finalize data migration runbook",
        "Schedule ITAD pickup",
        "Convert SOW to fixed price",
        "Extend residency services 6 months",
        "Send ITAD value report",
    ],
    "emails_out": [
        ("Deployment kickoff", "Hi {contact_first},\n\nKickoff for the {qty}-device deployment is {date}. Agenda: image validation, BIOS settings, asset tag format, shipping file, user communication. Please bring your Intune admin.\n\n{rep_first}"),
        ("Rack & stack - confirmed", "{contact_first}, rack & stack team confirmed for {date}. 2 engineers, 2 days. They'll need badge access and a loading dock slot."),
        ("ITAD certificates", "Hi {contact_first} - certificates of data destruction for all {qty} devices attached, by serial. Value credit applied to your account."),
        ("Migration plan", "{contact_first},\n\nAttached is the migration runbook for {tb}TB. Phased over {weeks} weeks, cutover weekends highlighted. Rollback plan included."),
        ("Residency extension", "Hi {contact2_name} - happy to extend the residency engagement 6 months. Same engineer. Quote attached."),
    ],
    "emails_in": [
        ("deployment", "Users are asking when they'll get their new laptops. Do we have a schedule?"),
        ("RE: Rack & stack", "Badge access is set up. Loading dock is free from 7am. Thanks."),
        ("image problem", "Some of the new laptops are blue-screening on first boot. Is this the image?"),
        ("Re: Migration plan", "Looks thorough. Our DBA wants to be on the call for the SQL cutover."),
        ("ITAD", "Need certificates of destruction for our auditors. Do you have them?"),
    ],
    "chatter": [
        "deployment at {account} {pct}% done, on track. imaging team caught a driver conflict in QA - nice",
        "rack & stack at {account} done. {servers} servers, clean cabling, happy customer",
        "@{se_name} migration cutover at {account} this weekend. {tb}TB. fingers crossed",
        "residency engineer at {account} is basically on their team now. extending",
        "ITAD credit at {account} paid for a chunk of the new order",
        "{account} Intune enrollment profile was broken, delayed deployment. we helped fix",
    ],
}


# =============================================================================
# 2. MEETING_NOTES  (Attendees block is prepended by the generator)
# =============================================================================

MEETING_NOTES = {
    "discovery": [
        (
            "Purpose: understand current environment and priorities ahead of {fy} planning.\n"
            "\n"
            "Environment\n"
            "- ~{seats} users, HQ in {hq_city} plus 2 regional offices\n"
            "- {servers} hosts on {hypervisor}, oldest are {model}, 6+ yrs\n"
            "- Storage: single {competitor} array, ~{util}% full, no replication\n"
            "- Backups nightly to disk, weekly copy to {cloud}\n"
            "\n"
            "Pain points (customer's words)\n"
            "- 'we find out a drive died when the user calls'\n"
            "- imaging takes a tech half a day per laptop\n"
            "- no one owns firmware, nothing has been updated in 2 yrs\n"
            "\n"
            "Action items\n"
            "- {rep_first}: send Orvane Insight trial + collector instructions\n"
            "- {contact_first}: export hardware inventory from RMM\n"
            "- {se_name}: draft high-level architecture options by {date}"
        ),
        (
            "Agenda: intros, business priorities, IT roadmap, next steps\n"
            "\n"
            "Business context\n"
            "- {account} growing ~{growth}% YoY, opening {site_city} in {quarter}\n"
            "- Board pushing an {initiative} - no defined scope yet\n"
            "- IT team is 7 people, 2 open reqs they can't fill\n"
            "\n"
            "Discussion\n"
            "- {contact_name} wants fewer vendors and fewer consoles\n"
            "- Decision process: IT recommends, {contact2_name} ({contact2_title}) approves, board over $250k\n"
            "- Budget for {fy} gets locked in {quarter}\n"
            "\n"
            "Next steps\n"
            "- Technical deep dive w/ {se_name} on compute + storage\n"
            "- Planning numbers to {contact_first} before budget lock"
        ),
        (
            "Discovery - end user computing\n"
            "\n"
            "- Fleet: ~{qty} laptops, ~400 desktops, mix of 4 models + whatever was in stock\n"
            "- {os} on ~60%, rest on older OS - readiness unknown\n"
            "- Intune for new devices, legacy GPOs for the rest (messy)\n"
            "- Refresh cycle: 'when it breaks'\n"
            "- Docks: 3 different types, users swap them and things stop working\n"
            "\n"
            "What good looks like for them\n"
            "- 2 standard configs, one dock, zero-touch\n"
            "- devices shipped direct to remote employees\n"
            "\n"
            "Risks\n"
            "- {partner} holds the imaging contract through {lease_end}\n"
            "\n"
            "Follow-ups: readiness scan via Orvane Manage; persona workshop {date}"
        ),
        (
            "Notes - discovery call (60 min)\n"
            "\n"
            "Datacenter: colo cage in {hq_city}, 4 racks, 2 x 30A per rack, ~70% of contracted power used.\n"
            "Network: 10GbE to hosts, core is 25G, flat VLAN for mgmt + BMC (flagged this).\n"
            "Apps that matter: ERP on SQL Server, Epic-adjacent scheduling, file shares, a Splunk instance that keeps growing.\n"
            "DR: secondary site in {site_city}, async replication, never fully tested.\n"
            "\n"
            "Key quote from {contact_first}: 'I don't need the fastest thing, I need the thing that doesn't page me at 2am.'\n"
            "\n"
            "Qualification: budget {budget} indicated, timing {quarter}, {contact2_name} is economic buyer, {competitor} is incumbent on storage.\n"
            "\n"
            "Next: {se_name} to pull perf data with the Insight collector for 14 days."
        ),
        (
            "Discovery - security + compliance angle\n"
            "\n"
            "- New CISO started {date}, first ask was a hardware/firmware inventory - nobody could produce it\n"
            "- Cyber insurance renewal requires immutable backups + MFA on admin planes\n"
            "- {advisory} hit them via scanner, took 3 weeks to patch because no tooling\n"
            "- BMCs reachable from user VLAN (!)\n"
            "\n"
            "Where we can help\n"
            "- Orvane Insight for firmware baseline + drift alerts\n"
            "- Vault w/ retention lock\n"
            "- OOB mgmt network design via Mesh\n"
            "\n"
            "Action: {rep_first} to set up CISO briefing; {se_name} to send BMC isolation guide."
        ),
        (
            "Quick discovery (30 min, {contact_first} only)\n"
            "\n"
            "- They're early - just know the {hypervisor} renewal is ugly and want options\n"
            "- {servers} hosts, ~350 VMs, about a dozen are 'pets' nobody wants to touch\n"
            "- Already got a quote from {competitor} for HCI, didn't love the partner-only support\n"
            "- Not ready to involve finance yet\n"
            "\n"
            "Agreed next step: RVTools-style export so we can size properly, then a 90-min workshop.\n"
            "Gut feel: real, but 2 quarters out."
        ),
    ],
    "product_demo": [
        (
            "Demo: Orvane Insight + Atlas BMC\n"
            "\n"
            "Shown\n"
            "- Fleet dashboard, health rollup across {servers} hosts\n"
            "- Firmware baseline + drift report (the 'aha' moment)\n"
            "- Remote BIOS update over BMC, no reboot on BMC itself\n"
            "- Alert routing into ServiceNow\n"
            "\n"
            "Questions\n"
            "- Redfish API support? Yes - {se_name} to send docs\n"
            "- Can it monitor {competitor} gear? Basic SNMP only, be honest about that\n"
            "- On-prem vs SaaS collector? Both\n"
            "\n"
            "Reaction: strong. {contact_first} asked for a 30-day trial on prod."
        ),
        (
            "Demo - Converge HCI\n"
            "\n"
            "- Built a 3-node cluster live from bare metal in ~40 min (pre-staged images)\n"
            "- Migrated a test VM from their {hypervisor} environment\n"
            "- Pulled a node mid-demo - VMs restarted on survivors in under 2 min\n"
            "- 1-click rolling upgrade (firmware + hypervisor) shown on recording to save time\n"
            "\n"
            "Pushback\n"
            "- {contact2_name}: 'what about our backup software?' - covered, plugin exists\n"
            "- Network team worried about east-west traffic on 25G - fair, sizing will address\n"
            "\n"
            "Next: POC scoping call {date}."
        ),
        (
            "Endpoint demo for persona workshop\n"
            "\n"
            "- {product} vs Aster 7 side by side, users handled both\n"
            "- Tether dock: single cable to 2 x Clarity 27, ethernet, charging - worked first time\n"
            "- Zero-touch: unboxed, signed into Intune, apps landing in ~18 min\n"
            "- Bastion drop test video, field team loved it\n"
            "\n"
            "Feedback\n"
            "- want backlit keyboard on standard config\n"
            "- webcam quality matters more than we thought (exec team)\n"
            "- 14in vs 16in split roughly 70/30\n"
            "\n"
            "Action: revise configs, pilot units for 25 users."
        ),
        (
            "Demo: Vault data protection\n"
            "\n"
            "- Instant VM recovery: booted a 400GB SQL VM from backup in 6 min\n"
            "- Retention lock: tried to delete a locked backup as domain admin, denied (they made us try twice)\n"
            "- M365 restore of a deleted OneDrive folder\n"
            "- Cloud tier to {cloud} w/ object lock\n"
            "\n"
            "Concerns\n"
            "- How does it handle 7-yr retention for finance? Long-term tier, separate policy\n"
            "- MFA on the Vault console - yes, separate identity from AD\n"
            "\n"
            "Next: sizing for {tb}TB front-end."
        ),
        (
            "Atlas AI demo (remote, our lab)\n"
            "\n"
            "- {gpu_count}-GPU node running a 70B model in inference, ~30 tokens/sec/user at 20 concurrent\n"
            "- Fine-tuning job on an 8B model, showed GPU utilization + NVMe throughput\n"
            "- Kubernetes w/ GPU operator, model serving, vector DB - the reference stack\n"
            "\n"
            "Their data scientist asked about multi-instance GPU partitioning - yes, shown briefly.\n"
            "Facilities person on the call went quiet when we hit the 10kW slide.\n"
            "\n"
            "Next: facilities walk-through + power assessment before any quote."
        ),
        (
            "Mesh switching demo\n"
            "\n"
            "- CLI walkthrough - network team said 'oh, this is basically what we already know'\n"
            "- Zero-touch provisioning of a branch switch from template\n"
            "- EVPN-VXLAN fabric in the lab, leaf failure, no dropped pings\n"
            "- Ansible playbook pushing VLAN changes across 6 switches\n"
            "\n"
            "Big point: perpetual licensing, no subscription to keep ports up.\n"
            "{competitor} subscription renewal is their pain - came up 3 times.\n"
            "\n"
            "Action: POC kit to lab by {date}."
        ),
    ],
    "technical_deep_dive": [
        (
            "Technical deep dive - compute + storage sizing\n"
            "\n"
            "Inputs (from 14-day Insight collection)\n"
            "- CPU avg {util}%, peak 78% month-end\n"
            "- RAM: 91% allocated, ballooning on 3 hosts\n"
            "- Storage: 85k IOPS peak, 70/30 read/write, 32K avg block\n"
            "- Latency spikes to 20ms+ during 1-3am backup window\n"
            "\n"
            "Proposed\n"
            "- {infra_product} x 6, 2 x 32-core, 1TB RAM (16 x 64GB, all channels populated)\n"
            "- {storage_product}, all-NVMe, {tb}TB usable at 3:1\n"
            "- 25GbE to hosts, 100G uplinks\n"
            "\n"
            "Open questions\n"
            "- growth assumption: customer says {growth}%, we modeled 20%\n"
            "- keep FC or move to iSCSI? leaning iSCSI\n"
            "\n"
            "Owner: {se_name}. BOM draft by {date}."
        ),
        (
            "Deep dive: backup + DR\n"
            "\n"
            "- Tier 1 apps: ERP, SQL, AD - RPO 15m / RTO 4h\n"
            "- Tier 2: file, print, intranet - RPO 24h / RTO 24h\n"
            "- Current: nightly fulls on weekends, incrementals weeknights, 10hr window\n"
            "- DR site in {site_city}, 3ms RTT, 1Gbps link (shared w/ user traffic, not great)\n"
            "\n"
            "Design decisions\n"
            "- Vault appliance at primary, replicated copy at DR, immutable copy in {cloud}\n"
            "- Retention: 30 daily / 12 monthly / 7 yearly (finance)\n"
            "- Orchestrated failover runbook for tier 1\n"
            "\n"
            "Risks: DR link bandwidth - may need QoS or a dedicated circuit."
        ),
        (
            "Network deep dive for HCI\n"
            "\n"
            "- 2 x 25GbE per node, LACP vs active/standby: going active/standby for storage, LACP for VM traffic\n"
            "- VLANs: mgmt 10, vMotion 20, storage 30 (MTU 9000), VM 100-199, OOB/BMC 900\n"
            "- Jumbo frames must be end to end - their core is set to 1500, needs change window\n"
            "- BMCs currently on VLAN 10 with hypervisor mgmt - moving to isolated OOB\n"
            "\n"
            "Action items\n"
            "- {contact_first}: change ticket for MTU on core\n"
            "- {se_name}: final IP plan + switch configs\n"
            "- verify with ping -s 8972 -M do before cutover"
        ),
        (
            "Deep dive - GPU infrastructure for {initiative}\n"
            "\n"
            "Workload: RAG over ~{tb}TB internal docs, ~500 users, latency target < 2s first token.\n"
            "Model: 8B fine-tuned now, maybe 70B later.\n"
            "\n"
            "Recommendation\n"
            "- 1 x Atlas AI, {gpu_count} GPUs, 80GB+ each, 2TB RAM, 8 x 7.68TB NVMe\n"
            "- 2 x 200Gb for future scale-out\n"
            "- {storage_product} fast file tier for the corpus\n"
            "\n"
            "Facilities\n"
            "- ~10kW peak, needs 2 x 30A 208V circuits minimum\n"
            "- rear-door heat exchanger worth considering\n"
            "\n"
            "Next: facilities sign-off, then quote."
        ),
        (
            "Deep dive: client imaging + zero touch\n"
            "\n"
            "- Intune tenant ready, Autopilot-style profiles exist for 1 of 3 personas\n"
            "- Hardware hash registration at factory - need tenant ID + group tag per persona\n"
            "- Driver packs: pin audio driver on older Aster 5 (known headset issue)\n"
            "- BIOS settings: secure boot on, TPM on, boot order locked, BIOS password via Orvane Manage\n"
            "- Apps: 14 required, 3 still MSI-only, 1 needs a license server reachable from VPN\n"
            "\n"
            "Decision: no golden image. Pure zero-touch, apps via Intune.\n"
            "Risk: the license server app - {contact_first} to test before pilot."
        ),
        (
            "Deep dive - storage migration plan\n"
            "\n"
            "- Source: {competitor} array, {tb}TB used, FC\n"
            "- Target: {storage_product}, iSCSI\n"
            "- VMs: storage vMotion over 2 weekends, ~200 VMs per weekend\n"
            "- File shares: robocopy /MIR /COPYALL w/ ACLs, final delta during cutover\n"
            "- SQL: log shipping, cutover in a 30-min window\n"
            "- Oracle: RMAN restore to new LUNs (DBA owns)\n"
            "\n"
            "Rollback: source array stays live 30 days post-cutover.\n"
            "Open: whether the old FC switches can be decommed at the same time."
        ),
    ],
    "architecture_workshop": [
        (
            "Architecture workshop (half day, whiteboard)\n"
            "\n"
            "Current state\n"
            "- 3-tier: {servers} hosts, FC SAN, separate backup appliance, 3 consoles\n"
            "\n"
            "Future state options\n"
            "A) refresh 3-tier like-for-like\n"
            "B) Converge HCI for general VMs, keep {storage_product} for big SQL\n"
            "C) Converge for everything\n"
            "\n"
            "Scoring (customer-weighted): operability 30, cost 30, risk 20, performance 20\n"
            "- A: 62  B: 81  C: 74\n"
            "\n"
            "Consensus: option B. SQL team didn't want their storage shared.\n"
            "Next: detailed BOM for B, TCO vs current renewal path."
        ),
        (
            "Workshop: hybrid cloud strategy\n"
            "\n"
            "- {account} has a 'cloud first' mandate from 3 yrs ago; {cloud} bill is now {budget}/yr and growing\n"
            "- Steady-state workloads (ERP, file, AD) cost 2-3x what they'd cost on-prem\n"
            "- Bursty / dev-test workloads genuinely belong in cloud\n"
            "\n"
            "Recommendation (theirs, we facilitated)\n"
            "- Repatriate ERP + file to on-prem Converge\n"
            "- Keep dev/test + analytics in {cloud}\n"
            "- Orvane Flex to keep opex model finance likes\n"
            "\n"
            "Concern: politics - the cloud-first exec is still there. Frame as 'cloud smart.'"
        ),
        (
            "Edge architecture workshop\n"
            "\n"
            "Sites: retail stores, ~{qty}, 3 tiers by size\n"
            "Requirements: POS backend, NVR, local file, survive WAN outage 72h\n"
            "\n"
            "Design\n"
            "- Tier A: 2 x Outpost + cloud witness\n"
            "- Tier B/C: 1 x Outpost, nightly backup to HQ\n"
            "- Mesh 24-port PoE per site, ZTP from template\n"
            "- OOB via LTE modem on BMC\n"
            "- Orvane Insight centrally\n"
            "\n"
            "Constraints: no rack at Tier C, closet temps up to 40C, store staff non-technical.\n"
            "Next: pilot store {site_city}."
        ),
        (
            "Workshop - DC network fabric\n"
            "\n"
            "Today: 3-tier, STP, 2 x core, ~30 access switches in the DC, constant loops/outages\n"
            "\n"
            "Target\n"
            "- Leaf-spine, Mesh 100G spines x 2, 25G leaves x 6 to start\n"
            "- EVPN-VXLAN, anycast gateway\n"
            "- Border leaf pair for WAN + firewall\n"
            "- OOB mgmt network physically separate\n"
            "\n"
            "Migration: build new fabric alongside, L2 extend, move racks one at a time.\n"
            "Timeline: {weeks} weeks after hardware lands.\n"
            "Risk: 2-person network team, will need residency engineer."
        ),
        (
            "VDI architecture session\n"
            "\n"
            "- Use case: {seats} task workers + 80 engineers needing 3D apps\n"
            "- Endpoints: Wisp thin clients for task workers, Forge for the heavy users (not VDI)\n"
            "- Hosts: {infra_product} w/ GPUs for the 3D pool if they want VDI for engineers later\n"
            "- Profile mgmt + storage IOPS: boot storm at 8am is the sizing driver\n"
            "\n"
            "Decision: phase 1 = task workers only.\n"
            "Action: {se_name} to size boot storm IOPS for {storage_product}."
        ),
        (
            "Workshop - device lifecycle\n"
            "\n"
            "Today: buy, deploy by hand, run until dead, pile in closet\n"
            "Target: 3-yr cycle, zero-touch deployment, ITAD at end, predictable cost\n"
            "\n"
            "Options compared\n"
            "- capex purchase + ProCare Plus\n"
            "- Orvane Financial Services 36-mo lease\n"
            "- Device-as-a-Service (per seat/month incl. services)\n"
            "\n"
            "Finance ({contact2_name}) favors DaaS; IT worried about losing control of config. Agreed config stays theirs.\n"
            "Next: DaaS proposal for {seats} seats."
        ),
    ],
    "executive_briefing": [
        (
            "Executive briefing - {account} leadership at Orvane briefing center\n"
            "\n"
            "Their priorities (from {exec_title})\n"
            "1. cost predictability\n"
            "2. resilience - last outage cost them a weekend of shipments\n"
            "3. AI - board pressure, no plan\n"
            "\n"
            "Our points\n"
            "- consolidation + licensing savings\n"
            "- Vault + immutable copies for the ransomware conversation\n"
            "- AI: start small, prove value, then scale\n"
            "\n"
            "Asks from them: single exec sponsor on our side, quarterly reviews.\n"
            "Commitment: our RVP as sponsor, first QBR {date}."
        ),
        (
            "Exec briefing (virtual, 45 min)\n"
            "\n"
            "- {new_exec} ({exec_title}) ran the meeting, very direct\n"
            "- Wants to cut vendor count by half in 18 months\n"
            "- Asked 'why should Orvane be one of the survivors?'\n"
            "- Our answer: breadth (client to DC to edge), one support org, financing flexibility\n"
            "- They pushed on support quality - referenced last quarter's escalation\n"
            "\n"
            "Outcome: invited to submit consolidation proposal by {date}.\n"
            "Risk: {competitor} is getting the same invitation."
        ),
        (
            "Executive briefing - AI readiness\n"
            "\n"
            "Attendees from customer: CEO, CFO, {contact_title}\n"
            "\n"
            "- CEO wants AI 'somewhere visible' by {quarter}\n"
            "- CFO wants to know cost and payback\n"
            "- IT worried about data leaving the building\n"
            "\n"
            "We proposed: 90-day proof of value, one use case (internal knowledge search), on-prem Atlas AI node, success metrics defined upfront.\n"
            "CFO liked the bounded cost. CEO wanted faster. Compromise: kickoff in {weeks} wks.\n"
            "\n"
            "Next: use-case workshop with business owners."
        ),
        (
            "Exec meeting - relationship reset\n"
            "\n"
            "Context: 3 escalations + late order this year. {contact2_name} requested meeting.\n"
            "\n"
            "- We opened by owning it. Timeline of each issue, what failed, what changed\n"
            "- They want: named TAM, monthly service review, proactive advisories\n"
            "- We agreed to all three\n"
            "- {contact2_name}: 'I don't need perfect, I need to hear about problems from you first'\n"
            "\n"
            "Mood at end: cautiously positive.\n"
            "Follow-up: written commitments by {date}."
        ),
        (
            "Executive briefing - sustainability + lifecycle\n"
            "\n"
            "- {account} has public emissions targets, IT is ~8% of their footprint\n"
            "- Interested in: power reduction via consolidation, ITAD w/ recycling reports, packaging take-back\n"
            "- Showed power savings from consolidating {servers} hosts (~{pct}%)\n"
            "- ITAD reports feed their ESG disclosures\n"
            "\n"
            "Ask: data for their annual sustainability report. We'll provide product carbon footprint sheets.\n"
            "Opp: refresh framed as sustainability, not just cost."
        ),
        (
            "Exec briefing - M&A integration\n"
            "\n"
            "- {account} closing acquisition {date}, doubles employee count\n"
            "- {exec_title} wants Day 1 = email + laptops + VPN, Day 90 = one network, Day 365 = one DC\n"
            "- Acquired company runs {competitor} for everything\n"
            "\n"
            "We positioned: Day 1 laptop program, DC consolidation capacity, residency engineers to supplement their team.\n"
            "\n"
            "Decision: they'll use us for Day 1. DC decision later.\n"
            "Next: Day 1 plan + BOM in 10 days."
        ),
    ],
    "qbr": [
        (
            "QBR - {quarter}\n"
            "\n"
            "Spend\n"
            "- {amount} this quarter, mostly client refresh wave 2\n"
            "- YTD tracking to plan\n"
            "\n"
            "Support\n"
            "- 23 cases, 2 Sev 2, 0 Sev 1\n"
            "- avg time to resolve 1.6 days\n"
            "- 1 missed onsite SLA ({case_number}) - service credit applied\n"
            "\n"
            "Health (Insight)\n"
            "- 4 predictive drive failures, replacements shipped\n"
            "- firmware drift on 12 hosts\n"
            "\n"
            "Roadmap: storage refresh {quarter}, Win 11 tail.\n"
            "Asks: they want order status visibility - portal walkthrough scheduled."
        ),
        (
            "Quarterly review - shorter format at customer's request\n"
            "\n"
            "What went well: deployment of {qty} devices, on time.\n"
            "What didn't: GPU node delivery slipped {weeks} weeks.\n"
            "What's next: {initiative} phase 2, network refresh in {fy}.\n"
            "\n"
            "{contact_first} raised a concern about our renewal pricing creeping up {pct}% YoY - asked for a multi-year lock.\n"
            "\n"
            "Action: multi-year renewal option by {date}."
        ),
        (
            "QBR\n"
            "\n"
            "Customer business update\n"
            "- revenue up, hiring in {site_city}, new {exec_title} starting\n"
            "- {cloud} costs are under scrutiny\n"
            "\n"
            "Orvane scorecard\n"
            "- On-time delivery {pct}%\n"
            "- Support CSAT 4.6/5\n"
            "- 1 escalation, resolved w/ RCA\n"
            "\n"
            "Opportunities raised\n"
            "- {site_city} build-out\n"
            "- repatriating 2 workloads from {cloud}\n"
            "- monitor purchases going to a reseller at worse pricing (easy fix)\n"
            "\n"
            "Next QBR {date}."
        ),
        (
            "QBR - tense\n"
            "\n"
            "- {contact2_name} opened with the late order and two escalations\n"
            "- We walked through RCA for each; they accepted but want proof it won't repeat\n"
            "- They're 'evaluating options' for the storage refresh - {competitor} in\n"
            "- On the positive side: client fleet is stable, deployment team praised\n"
            "\n"
            "Commitments made\n"
            "- weekly order status until backlog clears\n"
            "- TAM on all Sev 1/2\n"
            "\n"
            "Read: relationship damaged but recoverable. Next 90 days matter."
        ),
        (
            "Semi-annual business review\n"
            "\n"
            "- Total spend last 6 months: {amount}\n"
            "- Orvane Flex usage averaging {util}% of commit - recommending commit reduction at next window\n"
            "- ProCare: 14 contracts co-termed to {lease_end}\n"
            "- Shield deployed on {seats} endpoints, 3 incidents caught\n"
            "\n"
            "Their roadmap\n"
            "- AI pilot {quarter}\n"
            "- Office consolidation (2 sites closing)\n"
            "\n"
            "Asks: ITAD at closing sites, AI workshop."
        ),
        (
            "QBR - exec version\n"
            "\n"
            "Present: {exec_title}, {contact_name}, our RVP, {rep_name}, {se_name}\n"
            "(note: agenda items only - metrics sent ahead as pre-read)\n"
            "\n"
            "1. Strategic priorities next 12 months - cost, resilience, AI\n"
            "2. Where Orvane fits: consolidation, Vault, Atlas AI pilot\n"
            "3. Relationship health - they rated us 7/10, want 9\n"
            "4. What gets us to 9: fewer rep changes, proactive advisories, honest lead times\n"
            "\n"
            "Next steps owned by {rep_first}."
        ),
    ],
    "proposal_review": [
        (
            "Proposal review - {quote_number}\n"
            "\n"
            "Walked {contact_first} + {contact2_name} through the proposal\n"
            "- Option A: like-for-like refresh, {amount}\n"
            "- Option B: consolidated w/ Converge, ~{pct}% lower 5-yr TCO\n"
            "- Services: rack integration, migration, 6 months residency\n"
            "\n"
            "Feedback\n"
            "- like B, worried about migration risk\n"
            "- want services split out so they can compare to {partner}\n"
            "- {contact2_name} asked for financing option\n"
            "\n"
            "Revisions due {date}."
        ),
        (
            "Proposal review (procurement present)\n"
            "\n"
            "- Procurement wants: all-in unit pricing, quote validity date, maintenance as separate line\n"
            "- Technical team is aligned on the solution\n"
            "- Price is {discount}% off list, procurement opened at '{discount} is not enough'\n"
            "- Delivery: {weeks} weeks for GPU nodes is a concern\n"
            "\n"
            "No decision in room. Procurement will run their scoring.\n"
            "Expected decision {date}."
        ),
        (
            "Proposal walkthrough - client refresh / DaaS\n"
            "\n"
            "- {seats} seats, 36 months, 3 personas\n"
            "- Includes ProCare Plus, deployment, ITAD at end of term\n"
            "- Per-seat monthly compared to their current purchase + support + labor\n"
            "\n"
            "Questions\n"
            "- what if headcount drops 15%? flex-down terms in section 4\n"
            "- who owns the device at end? we do, returned via ITAD\n"
            "- can they buy out early? yes, schedule in appendix\n"
            "\n"
            "Generally positive. Legal review next."
        ),
        (
            "Proposal review - storage\n"
            "\n"
            "- {storage_product}, {tb}TB usable at 3:1, effective capacity guarantee included\n"
            "- worst case at 2:1 shown per their request - still fits through year 2\n"
            "- sync replication to {site_city}\n"
            "- migration services, 3 weekends\n"
            "\n"
            "{contact_first}: comfortable. {contact2_name}: wants to see {competitor}'s final number first.\n"
            "\n"
            "Risk: price. Next: deal desk approval on additional discount ahead of BAFO."
        ),
        (
            "Proposal review - network\n"
            "\n"
            "- Campus: 40 x Mesh 48-port PoE+, 2 x core\n"
            "- DC: leaf-spine, 2 spines, 6 leaves\n"
            "- Perpetual licenses, ProCare Plus 5 yrs\n"
            "- Migration: phased, 1 floor/week\n"
            "\n"
            "Pushback: they want to reuse existing optics. Need to check compatibility - {se_name}.\n"
            "Also asked for training credits for 2 network engineers.\n"
            "\n"
            "Revised proposal {date}."
        ),
        (
            "Proposal review - AI pilot\n"
            "\n"
            "- Atlas AI node ({gpu_count} GPUs), {storage_product} fast tier, Mesh 100G\n"
            "- Deployment + reference stack install, 2 weeks\n"
            "- 90-day proof of value w/ defined metrics\n"
            "- Total {amount}\n"
            "\n"
            "CFO asked: what if the pilot fails? Hardware is reusable for other workloads; no stranded cost.\n"
            "Facilities sign-off still pending.\n"
            "\n"
            "Target decision {date}."
        ),
    ],
    "negotiation": [
        (
            "Negotiation call - {quote_number}\n"
            "\n"
            "Their asks\n"
            "1. {discount}% off (we're at {pct}%)\n"
            "2. net 60\n"
            "3. 12-month price protection\n"
            "4. free shipping\n"
            "\n"
            "Our position\n"
            "- discount: deal desk max is 3 pts more, only w/ PO by {date}\n"
            "- net 45, not 60\n"
            "- price protection 6 months on same configs\n"
            "- free shipping - yes\n"
            "\n"
            "They'll take it to their CFO. Expect answer by Friday."
        ),
        (
            "Negotiation - procurement led\n"
            "\n"
            "- Opened with {competitor}'s price, claimed we're 12% higher\n"
            "- We showed line-by-line: their quote is basic warranty, no deployment\n"
            "- Normalized gap ~2%\n"
            "- Procurement acknowledged but 'needs to show savings'\n"
            "\n"
            "Give/get\n"
            "- we gave: 2 extra pts + free ITAD on old units\n"
            "- we got: 3-yr commitment on refresh waves\n"
            "\n"
            "Verbal agreement. Paperwork {date}."
        ),
        (
            "Negotiation - MSA renewal\n"
            "\n"
            "- Volume down {pct}% YoY, they want to keep the same tier\n"
            "- Our offer: keep tier for 12 months, true-up at month 12\n"
            "- Liability cap: they want 2x annual spend, we're at 1x - legal to legal\n"
            "- Data on returned drives: agreed keep-your-drive at no charge for storage\n"
            "\n"
            "Open: liability cap. Everything else agreed.\n"
            "Next call {date}."
        ),
        (
            "Negotiation call - short\n"
            "\n"
            "- {contact2_name} said they're out of time, needs final number today\n"
            "- Gave best and final at {discount}%, valid through {date}\n"
            "- Asked them directly: if we're at this number, do we have the deal? Answer: 'yes, assuming legal is fine'\n"
            "\n"
            "Next: send BAFO in writing within the hour."
        ),
        (
            "Negotiation - financing\n"
            "\n"
            "- Total {amount}, budget is {budget}\n"
            "- Options presented: 36-mo FMV lease, 36-mo $1 out, 90-day deferral\n"
            "- They chose deferral - keeps it in next {fy}'s budget\n"
            "- {competitor} offered 0% for 36 - OFS matched\n"
            "\n"
            "Done on terms. PO expected {date}."
        ),
        (
            "Negotiation - services scope\n"
            "\n"
            "- They want services fixed-price, not T&M\n"
            "- Scope locked: rack & stack {servers} servers, migrate ~400 VMs, 2 weekends\n"
            "- Change order process agreed for anything outside scope\n"
            "- They pushed residency from 6 to 3 months to save money - accepted\n"
            "\n"
            "Final services number {amount}. SOW to legal."
        ),
    ],
    "account_planning": [
        (
            "Internal account planning - {account}\n"
            "\n"
            "Where we are\n"
            "- {fy} spend {amount}, mostly clients\n"
            "- Weak in DC: {competitor} owns storage, compute split\n"
            "\n"
            "Plays\n"
            "1. storage refresh - array at {util}%, out of support {quarter}\n"
            "2. {hypervisor} renewal shock - Converge\n"
            "3. Vault - insurance requirements\n"
            "\n"
            "Relationships: strong w/ {contact_first}, none w/ {contact2_name} - fix that\n"
            "Owners: {rep_first} (exec), {se_name} (technical)."
        ),
        (
            "Account planning session w/ {se_name} and partner {partner}\n"
            "\n"
            "- Whitespace: networking, edge, AI\n"
            "- Partner owns services relationship, we own product\n"
            "- Agreed to co-sell on network refresh, partner deploys\n"
            "- Risk: partner's margin on services may price us out vs {competitor}\n"
            "\n"
            "Targets this {fy}: {budget} total, 40% DC."
        ),
        (
            "Account plan review (manager 1:1)\n"
            "\n"
            "- Pipeline {amount}, 60% in one deal - too concentrated\n"
            "- Need more contacts beyond IT - finance and the new {exec_title}\n"
            "- Competitive risk: {competitor} has an exec relationship we don't\n"
            "\n"
            "Actions\n"
            "- exec briefing within 60 days\n"
            "- 3 new contacts in finance/security\n"
            "- break the big deal into phases to de-risk"
        ),
        (
            "Account planning - install base renewal\n"
            "\n"
            "- {servers} servers coming off warranty next 12 months\n"
            "- ProCare renewal value vs refresh value - refresh is bigger and better for customer\n"
            "- Firmware drift across fleet = good conversation starter\n"
            "\n"
            "Plan: renew vs replace analysis per cluster, present at QBR {date}."
        ),
        (
            "Territory account planning - {account}\n"
            "\n"
            "Business: {growth}% growth, expanding to {site_city}, new {exec_title}.\n"
            "IT: cloud-heavy ({cloud}), costs rising, open to repatriation.\n"
            "\n"
            "Our plays\n"
            "- {site_city} site build (near-term)\n"
            "- Flex for repatriated workloads (mid-term)\n"
            "- AI pilot (long shot)\n"
            "\n"
            "Biggest risk: new {exec_title} unknown. Get meeting."
        ),
        (
            "Account planning - recovery plan\n"
            "\n"
            "- Lost storage to {competitor} last {quarter}\n"
            "- Customer blamed price, but real reason was escalation history\n"
            "- Compute still ours, renewal in {quarter}\n"
            "\n"
            "Recovery\n"
            "- fix support experience: TAM + monthly reviews\n"
            "- win compute renewal cleanly\n"
            "- re-engage on storage at {competitor}'s first hiccup (and there will be one)"
        ),
    ],
}


# =============================================================================
# 3. CASE  (support case subjects + comments)
# =============================================================================

CASE = {
    "hardware_failure": {
        "subjects": [
            "{model} - system board failure, host down",
            "PSU 2 failed on {infra_product} at {site_city}",
            "Amber fault light on {model}, PSOD on reboot",
            "Memory errors - DIMM B3 uncorrectable",
            "Fan module failure - thermal shutdown",
            "{product} won't power on after BIOS update",
            "RAID controller battery failed - write cache disabled",
            "Intermittent reboots on {model} - suspected CPU",
        ],
        "comments": [
            "Customer reports host rebooted twice overnight. Requested support log bundle export via BMC.",
            "Reviewed log bundle. SEL shows: 'Uncorrectable memory error detected on DIMM B3. Configuration: ... Event 0x0C'. Dispatching DIMM PN 7X4K2 (64GB RDIMM) w/ onsite tech under ProCare Mission Critical, 4-hr.",
            "Tech onsite 10:42 local. Replaced DIMM B3, ran Orvane onboard diagnostics (extended memory test), all pass. Host back in cluster.",
            "Customer confirms 48 hrs stable, no new SEL entries. Closing case.",
            "PSU 2 showing 'Power supply input lost' in BMC log but the PDU outlet tests fine. Swapping PSU, PN 2R8MH, 1400W Titanium.",
            "Spoke with {contact_first}. Fan 4 reporting 0 RPM, ambient at 31C, system throttled. Fan module PN 9KD31 shipped next business day. Advised keeping the front bezel off temporarily for airflow.",
            "Collected logs. Machine Check Exception on CPU 1, bank 4, three occurrences in 24 hrs. Engineering recommends CPU + system board replacement. Scheduling for customer's maintenance window {date}.",
            "Onsite: system board PN 6WJ0N replaced. Service tag re-applied, BIOS updated to {firmware}, BMC license re-imported. Customer validated VMs.",
            "Customer is asking why the replacement board shipped with an older BIOS. Explained boards ship with base firmware and are updated onsite. Agreed it should have been done before handoff - noted for field team.",
            "RAID controller battery reporting 'Failed - learn cycle did not complete'. Write-back cache disabled, write latency up 5x. Battery PN 70K80 dispatched.",
            "BIOS update on {product} failed at 63% after battery died mid-flash. Unit no longer POSTs. BIOS recovery via USB attempted, no luck. Advanced exchange approved.",
            "Customer called back - host showing same errors after DIMM swap. Moving DIMM to a different slot to rule out the slot. If error follows slot, board is next.",
        ],
    },
    "drive_failure": {
        "subjects": [
            "Predictive failure - disk 4 on {storage_product}",
            "Drive failed in RAID 5 - array degraded",
            "NVMe SSD offline on {infra_product}",
            "Multiple drive failures - same batch?",
            "Keep-your-drive replacement request",
            "Drive rebuild slow, array still degraded after 30 hrs",
        ],
        "comments": [
            "Insight alert: predictive failure on enclosure 1 bay 4, SMART 'reallocated sector count' threshold exceeded. Proactive replacement shipped, PN 3X8F4 (1.92TB SAS SSD).",
            "Customer reports virtual disk degraded. Controller log: 'Physical disk 0:1:2 failed. Error: 0x0B'. Hot spare kicked in, rebuild at 14%.",
            "Drive shipped NBD. Customer has keep-your-drive, so no return required. Please retain failed drive per your policy.",
            "Third drive failure on this array in 60 days. All from the same manufacturing lot. Escalating to engineering for lot analysis.",
            "Engineering confirmed: firmware issue on this drive model causing early wear. Firmware update for drives available, applies non-disruptively one drive at a time. Sending procedure.",
            "Rebuild slow - 30 hrs and still at 62%. Array under heavy write load. Recommended lowering rebuild priority is the wrong direction - increased rebuild rate to 60% and moved backup jobs out of the window.",
            "NVMe drive in bay 3 dropped offline. 'NVMe drive not responding' in BMC log. Reseat performed by customer, drive came back but logged critical warning. Replacing anyway. PN 0J7KC.",
            "Customer asked if the replacement drive can be a larger capacity. Not under warranty - like-for-like only. Referred to account rep for upgrade quote.",
            "Drive installed, rebuild complete in 4h12m. Virtual disk optimal. Closing.",
            "Customer requested certificate of destruction for failed drive. KYD applies, so drive stays onsite - they destroy it. We can provide on-site shredding via ITAD services if needed.",
            "Wrong drive shipped - SAS vs NVMe. Apologized. Correct PN 5HT9W shipping priority overnight.",
        ],
    },
    "firmware_bug": {
        "subjects": [
            "BMC unresponsive after update to {firmware}",
            "NIC link flaps after firmware upgrade",
            "Known issue? BIOS {firmware} breaks PXE boot",
            "Firmware {firmware} - vMotion failures",
            "Dock firmware - external displays not detected",
            "RAID controller firmware causing latency spikes",
        ],
        "comments": [
            "Customer updated BMC to {firmware} via Insight. One of 12 hosts now unresponsive on BMC IP, host OS fine. Asked customer to try a BMC reset via host OS tool.",
            "BMC reset did not help. Engineering aware of an issue with {firmware} on {model} with a specific NIC config. Workaround: AC power cycle (full drain). If no recovery, board replacement.",
            "AC power cycle recovered the BMC. Customer advised to hold remaining hosts until {firmware} hotfix next week.",
            "NIC link flapping every ~20 min after firmware update. Logs: 'Link down on port 1, Link up on port 1' repeating. Matches known issue with auto-negotiation on 25G with certain switch models. Workaround: force speed to 25G on both ends.",
            "Workaround confirmed by customer. Permanent fix in next NIC firmware. Leaving case open until then.",
            "PXE boot failing after BIOS update. Default boot mode changed from legacy to UEFI in this release. Customer's PXE server only serves legacy. Recommended updating PXE server, or set boot mode back via Orvane Manage.",
            "Customer reports Tether dock no longer driving second display after dock firmware update. Rolled back to previous dock firmware, resolved. Bug filed against dock firmware.",
            "RAID controller firmware causing 200ms+ latency spikes under sustained random write. Confirmed in engineering lab. Fixed version available, release notes attached.",
            "Customer frustrated that the advisory wasn't sent proactively. Signed them up for proactive firmware notifications.",
            "Hotfix released. Customer applied to remaining 11 hosts, no issues. Closing.",
            "Firmware rollback procedure sent: Insight > Firmware > Host > Rollback, or via BMC web UI under Maintenance > Firmware > Rollback. Only the previous version is retained.",
        ],
    },
    "performance": {
        "subjects": [
            "Slow VM performance on Converge cluster",
            "High latency on {storage_product}",
            "{product} laptops slow after update",
            "Database performance degraded after migration",
            "GPU utilization lower than expected on Atlas AI",
            "Backup throughput dropped 50%",
        ],
        "comments": [
            "Customer reports VMs slow since Monday. Pulled cluster metrics: storage latency avg 18ms vs 2ms baseline. One node's NVMe showing high queue depth.",
            "Root cause: one disk group is running in degraded mode after a drive replacement didn't fully rebuild. Triggered manual resync. Latency back to 2ms after 3 hrs.",
            "{storage_product} latency spikes to 40ms between 1-3am. Correlates with backup and a SQL maintenance job. Not a hardware issue. Recommend schedule changes.",
            "Laptop slow after update - High CPU from a management agent stuck in a loop. Known issue with agent version. Updated agent via Orvane Manage, resolved.",
            "DB performance after migration: VM was migrated with default storage policy, not the performance tier. Changed policy, latency improved 4x.",
            "GPU utilization only 30% in training job. Profiling shows data loader bottleneck - training data on NFS share over 10GbE. Recommended moving dataset to local NVMe or the fast file tier.",
            "Customer moved data to local NVMe, GPU utilization now 92%. Closing.",
            "Backup throughput dropped after network change - jumbo frames disabled on backup VLAN during switch replacement. Re-enabled MTU 9000, throughput restored.",
            "Requested perf data: esxtop / perfmon captures for 15 min during the issue, plus storage array performance export. Will review with engineering.",
            "No hardware fault found. All components healthy. Performance issue appears workload-related. Offered a paid performance assessment via services.",
        ],
    },
    "config_help": {
        "subjects": [
            "How to configure BMC on isolated VLAN",
            "Help w/ RAID config on new {infra_product}",
            "Setting up Orvane Manage BIOS policies",
            "VLAN config on Mesh switch",
            "Converge cluster expansion - adding a node",
            "Tether dock MAC address passthrough setup",
        ],
        "comments": [
            "Customer asking how to move BMC to dedicated NIC on VLAN 900. Steps: BMC web UI > Network > NIC selection: Dedicated, enable VLAN tagging, ID 900. Or via the Orvane BMC CLI. Sent doc.",
            "RAID recommendation for 8 x 3.84TB SSD in a SQL server: RAID 10 for logs/tempdb, RAID 5 for data if capacity matters. Customer chose RAID 10 across all.",
            "Orvane Manage BIOS policy walkthrough: Policies > BIOS > New. Enable secure boot, TPM, set admin password from vault. Assign to device group. Takes effect on next check-in + reboot.",
            "Mesh VLAN config sent: 'vlan 30 name storage', 'interface ethernet 1/1-1/8 switchport trunk allowed vlan add 30', 'mtu 9216' on storage ports.",
            "Adding node to Converge: node must match firmware baseline. Run pre-check from console first. Customer's new node has older BIOS - updating before join.",
            "MAC passthrough on Tether: enable in BIOS under 'Integrated Devices > MAC Address Pass-Through > System Unique MAC'. Customer's NAC needs this for 802.1X.",
            "Customer asked for a remote session to walk through. Scheduled for {date} 2pm ET.",
            "Session complete. Customer configured 2 hosts, will do the rest themselves. Closing.",
            "Not a defect - config question. Provided KB article link. Customer confirmed resolved.",
            "Customer needed help with Redfish API auth for their automation. Sent example: session-based auth via POST to /redfish/v1/SessionService/Sessions, token in X-Auth-Token header.",
        ],
    },
    "shipping_damage": {
        "subjects": [
            "Damaged on arrival - order {order_number}",
            "Crushed box, server rails bent",
            "Laptop screens cracked in shipment",
            "Pallet tipped - multiple units damaged",
            "Missing items from shipment",
            "Monitor arrived with shattered panel",
        ],
        "comments": [
            "Customer received {order_number} with visible damage to 3 boxes. Photos attached. Requesting replacement.",
            "Photos reviewed. Outer box crushed on one corner, rails bent. Opening carrier claim. Replacement rails PN 1M4XV shipped NBD.",
            "Laptops: 4 of 50 with cracked screens. Customer refused delivery on those 4 per instructions. Replacements shipping from regional depot.",
            "Pallet arrived tipped - shock indicator triggered. Customer did not sign as 'damaged'. Need them to note damage on BOL for carrier claim. Explained process.",
            "Customer says 2 docks missing from shipment. Packing list shows them in box 7 of 9. Customer found box 7 in another dock. Resolved.",
            "Monitor panel shattered. Replacement shipped, return label for damaged unit sent.",
            "Carrier claim filed, reference attached. Customer not responsible for return shipping.",
            "Replacement units delivered and confirmed undamaged. Closing.",
            "Second shipment to same site also damaged. Requested different carrier for this route.",
            "Customer asked for white-glove for future orders to avoid damage. Referred to account rep.",
        ],
    },
    "doa": {
        "subjects": [
            "DOA - new {product}",
            "New server won't POST",
            "Dead on arrival - {qty} units affected",
            "New switch no power",
            "DOA dock - no video out",
            "New laptop boot loop out of the box",
        ],
        "comments": [
            "New {product} won't power on. Customer tried different charger and outlet. Battery LED blinks amber 3 times, white once - indicates system board fault.",
            "DOA confirmed. Advanced exchange approved. New unit ships today, return label in the box.",
            "New server: POST stops at memory initialization. BMC shows 'No memory detected'. Likely DIMMs unseated in shipping. Asked customer to reseat. Resolved.",
            "Switch has no power - customer tried both PSUs. Confirmed DOA, replacement from depot.",
            "Customer reports 5 of 200 laptops DOA - 2.5%. Higher than normal. Pulling serials to check for a common batch.",
            "Laptop in boot loop out of box - factory image corrupted. Re-imaging via recovery USB fixes it, but customer wants replacement. Approved.",
            "Dock: no video on any port. Firmware recovery attempted, failed. DOA replacement shipped.",
            "Customer wants a credit for time spent troubleshooting DOA units. Referred to account manager.",
            "Replacement received and working. Closing.",
            "All 5 DOA serials from same build lot. Quality team notified.",
        ],
    },
    "warranty_question": {
        "subjects": [
            "Warranty status for service tag",
            "Is accidental damage covered?",
            "Transfer warranty to new owner",
            "Warranty expired - options?",
            "Upgrade ProCare to Mission Critical mid-term",
            "Warranty coverage for international travel",
        ],
        "comments": [
            "Customer asked about warranty status. ProCare Plus, NBD onsite, expires {lease_end}.",
            "Accidental damage not covered under current contract. Can be added within 30 days of purchase only. Purchase was 6 months ago. Not eligible.",
            "Warranty transfer to acquiring company: need ownership transfer form + proof of acquisition. Sent form.",
            "Warranty expired {days} days ago. Options: post-warranty support (per incident or annual), or reinstatement with inspection. Referred to renewals team.",
            "Mid-term upgrade to Mission Critical: possible, prorated. Referred to account rep for quote.",
            "International coverage: ProCare Plus covers travel in supported countries. Customer traveling to a supported country, covered.",
            "Customer asked why the warranty in the portal shows a different end date than invoice. Ship date vs invoice date - warranty starts at ship.",
            "Customer satisfied with explanation. Closing.",
            "Battery is covered for 1 year only, even with 3-yr ProCare. Customer unhappy. Explained it's a consumable. Offered extended battery coverage add-on.",
            "Bulk warranty lookup: sent customer the portal export instructions for all service tags.",
        ],
    },
    "billing_issue": {
        "subjects": [
            "Invoice {invoice_number} doesn't match quote",
            "Charged twice for same order",
            "Tax charged on tax-exempt order",
            "Credit memo not received",
            "Wrong PO on invoice",
            "Shipping charged despite free shipping agreement",
        ],
        "comments": [
            "Customer reports invoice {invoice_number} total {amount} vs quote total lower. Investigating. Quote included discount that wasn't applied at order entry.",
            "Confirmed order entry error. Corrected invoice issued. Original voided.",
            "Duplicate charge on card - one is a pre-auth, will drop off in 3-5 days. Explained to customer.",
            "Tax charged on exempt order - exemption certificate on file expired last month. Customer to send updated cert, then credit memo issued.",
            "Credit memo for returned units: processed, but went to old AP email. Re-sent.",
            "PO on invoice wrong - order entry used old PO. Re-issued with {po_number}.",
            "Shipping charged on order that should've been free per agreement. Refund processed.",
            "Customer requested invoice copy in a different format for their AP system. Sent.",
            "Routing to billing team, out of scope for technical support.",
            "Billing confirmed corrected. Closing.",
        ],
    },
    "software_licensing": {
        "subjects": [
            "License key not activating - Orvane Insight",
            "Orvane Manage seat count exceeded",
            "Vault Backup license expired - jobs failing",
            "Can't access licensing portal",
            "Shield license not applying to new devices",
            "Transfer license to new server",
        ],
        "comments": [
            "Insight license key returns 'invalid' after upgrade. Keys are version-specific; issued new key for current version.",
            "Orvane Manage seat count exceeded - new devices not enrolling. Customer needs to purchase additional seats or retire old devices. Referred to rep.",
            "Vault backup jobs failing: 'License expired'. Renewal processed but key not applied. Applied new key, jobs running.",
            "Licensing portal access - admin left company. Verified {contact_first} as new admin via account rep. Access granted.",
            "Shield not applying to new devices - license pool full. Reassigned licenses from decommissioned devices.",
            "License transfer to new server: deactivate on old, activate on new. Sent procedure.",
            "Customer wants a grace period on expired license while PO processes. 30-day grace granted.",
            "Resolved. Closing.",
            "Error: 'License server unreachable' - firewall blocking outbound 443 to licensing endpoint. Customer opened port.",
            "Offline activation for air-gapped environment: generate request file, upload from connected machine, apply response file. Sent steps.",
        ],
    },
    "network_connectivity": {
        "subjects": [
            "Host losing network connectivity intermittently",
            "Mesh switch port down",
            "Can't reach BMC over network",
            "Dock ethernet not working",
            "Packet loss on storage network",
            "LACP bond not forming",
        ],
        "comments": [
            "Host losing connectivity every few hours. NIC logs show link down/up. Checked cable and SFP - SFP showing high temp. Replaced SFP PN 4KJ9P, stable.",
            "Mesh port down: 'err-disabled' due to BPDU guard. Customer plugged in an unmanaged switch. Removed, re-enabled port.",
            "BMC unreachable - customer changed BMC VLAN but didn't update switch port. Fixed switch config.",
            "Dock ethernet not working: dock firmware outdated, update fixed it.",
            "Packet loss on storage network: MTU mismatch, host at 9000, switch at 1500. Fixed switch.",
            "LACP bond not forming: switch port-channel configured as static, host expects LACP. Changed switch to 'mode active'.",
            "Requested: switch config, host NIC config, and output of 'show interface' and 'show lacp neighbor'.",
            "Customer confirms resolved after config change. Closing.",
            "Not a hardware issue - config. Provided guidance.",
            "Intermittent issue, can't reproduce. Asked customer to collect logs next time it happens.",
        ],
    },
    "data_recovery": {
        "subjects": [
            "Data recovery - failed RAID array",
            "Accidentally deleted VM - restore help",
            "Laptop drive failed, need data",
            "Vault restore failing",
            "Ransomware recovery assistance",
            "Recover from corrupted backup",
        ],
        "comments": [
            "Two drives failed in RAID 5 - array offline. Not recoverable via controller. Referred to data recovery partner. Customer's backup was 3 days old.",
            "Deleted VM: restored from Vault, last night's backup. VM up in 15 min via instant recovery.",
            "Laptop SSD failed. Data recovery not covered under warranty. Referred to third-party recovery service.",
            "Vault restore failing with 'checksum mismatch'. Escalated to engineering. Using previous restore point succeeded.",
            "Ransomware: customer's primary systems encrypted. Vault immutable copies intact. Working through restore priority with their incident response team.",
            "Restore progress: tier 1 apps restored in 6 hrs. Tier 2 in progress.",
            "Corrupted backup: one restore point affected, earlier points fine. Root cause: storage issue on backup target during write.",
            "Customer extremely grateful. Immutable backups saved the business.",
            "Recommended running regular restore tests going forward.",
            "Closing. RCA to follow.",
        ],
    },
    "battery_swelling": {
        "subjects": [
            "Battery swelling - {product}",
            "Laptop case bulging",
            "Trackpad pushed up - swollen battery",
            "Multiple laptops with swollen batteries",
            "Swollen battery - safety concern",
            "Battery replacement request - swelling",
        ],
        "comments": [
            "Customer reports trackpad raised and case not sitting flat. Classic swollen battery. Advised: stop using, do not charge, store in a cool place away from flammable material.",
            "Replacement battery PN 9JRV1 shipped. Onsite tech will replace under warranty - swelling is covered regardless of battery coverage period.",
            "Swollen battery shipped as hazmat - customer needs to use the provided return packaging. Do not ship via regular mail.",
            "Customer has 12 laptops with swelling. All on docks 24/7. Recommended enabling 'Primarily AC use' battery mode in BIOS via Orvane Manage to limit charge to ~80%.",
            "Pulled serials - all from same battery batch. Part of proactive replacement program.",
            "Tech replaced battery onsite. Old battery taken for disposal.",
            "Customer asked if it's dangerous. Yes, can be - advised immediate action.",
            "Closing. Advised customer on battery charge settings to prevent recurrence.",
            "Customer pushed back on 'Primarily AC' mode - users complained battery doesn't fully charge. Explained trade-off.",
            "Battery replacement program active - customer has {qty} eligible units.",
        ],
    },
    "display_issue": {
        "subjects": [
            "Flickering display on {product}",
            "Dead pixels on Clarity monitor",
            "No display after waking from sleep",
            "Lines on laptop screen",
            "External monitor not detected via dock",
            "Display brightness stuck at max",
        ],
        "comments": [
            "Flickering at low brightness - known issue with panel PWM on this model. BIOS update {firmware} fixes it.",
            "Dead pixels: 4 on Clarity monitor. Policy is replace at 3+ bright pixels. Approved.",
            "No display after sleep: graphics driver issue. Updated to latest, resolved.",
            "Vertical lines on laptop screen: LCD cable or panel. Tech onsite to replace panel PN 2XK7M.",
            "External monitor not detected via dock: dock firmware + graphics driver mismatch. Updated both.",
            "Brightness stuck: ambient light sensor driver. Reinstalled, resolved.",
            "Customer sent photo - screen damage is physical (crack). Not covered under standard warranty. Accidental damage not on contract.",
            "Panel replacement complete. Closing.",
            "Can't reproduce. Asked customer to record video when issue occurs.",
            "Issue reproduces only with a specific HDMI cable. Customer swapped cable, resolved.",
        ],
    },
}


# =============================================================================
# 4. COLLECTIONS_NOTES
# =============================================================================

COLLECTIONS_NOTES = [
    "Called AP at {account} re: {invoice_number} ({amount}), {days} days past due. Spoke w/ AP clerk - invoice is approved, scheduled for next Thursday check run. PTP {date}.",
    "Customer short-paid {invoice_number} by {discount}%. Says they were promised the early-pay discount. Discount on quote was contingent on PO by quote expiry; PO came 2 wks late. Sent quote terms to {contact_name}. Disputed amount moved to dispute queue, remainder applied.",
    "Remittance received but payment went to the old lockbox (closed last {fy}). Bank is forwarding but could be 2-3 wks. Asked customer to update remit-to in their vendor master. Sent updated remit letter on letterhead.",
    "P-card declined on order {order_number} - over single-transaction limit. {contact_first} is asking their card admin for a temp limit increase. Alt: split into 2 transactions? Not allowed per our policy. Holding order.",
    "Invoice rejected by customer's AP portal - missing PO line number. Re-submitted {invoice_number} via portal with PO {po_number} line 1. Portal status 'Received - pending match'.",
    "Customer requires vendor registration in their supplier portal before any payment can be released. Started registration. Needs W-9, COI and banking letter. Sent request to our treasury for banking letter.",
    "W-9 requested again - customer says the one on file is from 2019 and their policy requires within 3 yrs. Sent current W-9.",
    "Tax-exempt certificate on file for {account} expired {date}. Invoices since then were taxed. Customer disputing tax on {invoice_number}. Requested renewed cert; credit memo for tax once received.",
    "Spoke w/ {contact_name}, AP Manager. Check #40917 mailed {date} for {amount}. Will watch for it at the lockbox. Follow up in 7 days if not received.",
    "Check received, applied to {invoice_number}. Account current. Credit hold released, order {order_number} released to ship.",
    "Left VM for AP at {account}. 3rd attempt. Escalating to {rep_name} for help reaching someone.",
    "{account} AP says invoice was never received. Our records show emailed to their AP inbox on invoice date. Re-sent with read receipt. They also want invoices sent to a new inbox going forward - updated bill-to contact.",
    "Customer on payment plan for {amount}: 3 installments. Installment 1 received on time. Next due {date}.",
    "Installment 2 missed. Called {contact_first} - cash flow issue, expects payment in 10 days. Noted. Account remains on hold for new orders.",
    "Partial payment of {amount} received against {invoice_number}. Remittance didn't specify which invoices. Called AP - applied to oldest first per their instruction.",
    "ACH returned - 'account closed'. Customer changed banks and didn't update. Asked them to resend via new account. Flagged account.",
    "Customer disputes freight charges on {invoice_number}. Agreement includes free shipping on orders over $5k; this one qualifies. Credit memo for freight approved.",
    "Customer in Chapter 11 as of {date}. All collection activity stopped per legal. Filed proof of claim for pre-petition balance of {amount}.",
    "Customer requesting net 60 on future invoices. Current terms net 30, history shows avg 48 days to pay. Referred to credit for decision.",
    "Duplicate payment received - customer paid {invoice_number} twice. Refund request submitted, or apply as credit to next invoice? Customer chose credit.",
    "Customer says {invoice_number} was paid {date} via wire. No record on our side. Requested wire confirmation / Fed reference number from their bank.",
    "Wire found - posted to wrong customer account due to similar name. Reversed and reapplied. Apologized to customer.",
    "Credit limit at {account} is $250k, current exposure $310k with pending order. Credit review: strong payment history, approved temp increase for 60 days.",
    "Dunning letter 2 sent for {invoice_number}, {days} days past due. No response to letter 1.",
    "Account referred to third-party collections at 120+ days, {amount}. Notified {rep_name}.",
    "Customer requires all invoices to reference their internal cost center code. Updated customer master with cost center. Re-issued last 3 invoices.",
    "Vendor setup form from {account} asks for diversity certification and insurance limits. Sent to our compliance team to complete.",
    "Customer short-paid by the amount of a credit memo they believe is owed for returned units. RMA shows units received {date}; credit memo processed but not yet sent. Sent credit memo, balanced.",
    "Spoke w/ controller {contact2_name}. Year-end close, payments held until {date}. Committed full payment then. Will hold off on escalation.",
    "Payment received. Account clear. Closing collections activity.",
]


# =============================================================================
# 5. SURVEY_VERBATIMS
# =============================================================================

SURVEY_VERBATIMS = {
    "promoter": [
        "fast shipping",
        "Support was excellent. Engineer called back within 20 min on a Sunday and stayed on the line until the host was back in the cluster.",
        "Easy to order, everything arrived on time.",
        "{rep_first} actually listens. First rep in years who didn't try to sell us something we didn't need.",
        "The laptops are solid. Users stopped complaining, which is the highest praise in IT.",
        "Zero-touch deployment worked exactly as promised. We rolled out {qty} devices with 2 people.",
        "Great product, great support.",
        "Orvane Insight caught a failing drive before it failed. That alone paid for it.",
        "Deployment team was professional, on time, and cleaned up after themselves. Rare.",
        "The Tether dock just works. Single cable, two monitors, no drama.",
        "Vault instant recovery saved us during an incident. Restored a critical VM in minutes.",
        "Pricing was fair and the quote was easy to understand. No surprises on the invoice.",
        "Love the Aster 7. Light, fast, battery lasts all day.",
        "Rack integration service is worth every penny. Plugged in power and it was up.",
        "{se_name} is a rock star. Knew our environment better than we did by the end.",
        "Reliable hardware. We've had very few failures over 5 years.",
        "Converge migration went smoother than expected. Zero downtime on the VMs that mattered.",
        "Proactive about issues. They called us about the battery recall before we noticed anything.",
        "Good value",
        "Account team is responsive and knowledgeable. Always get a straight answer.",
        "The edge rollout was the smoothest project we've done this year.",
        "Would recommend to any IT shop our size.",
    ],
    "passive": [
        "Products are fine. Support can be slow on lower priority cases.",
        "OK",
        "Shipping took longer than quoted.",
        "Good hardware but the support portal is confusing. Took me 15 minutes to find where to upload logs.",
        "Pricing could be better. {competitor} came in lower.",
        "We've had 3 different reps in 2 years. Hard to build a relationship.",
        "Product does what it should. Nothing exceptional.",
        "Lead times on GPUs are a problem.",
        "Laptop is good but the webcam is mediocre for the price.",
        "Generally positive, but the onsite tech didn't have the right part on the first visit.",
        "Invoicing is confusing - three separate invoices for one order.",
        "Support resolved the issue but it took 4 days and a lot of back and forth.",
        "Satisfied overall.",
        "Fine. Would be better if the BIOS updates didn't keep resetting our settings.",
        "Decent experience. The firmware update process could be smoother.",
        "Hardware is good, software tools need work.",
        "Communication about the order delay was poor. Found out from the portal.",
        "It works.",
        "Product quality good, sales process a bit pushy.",
        "Average. Neither better nor worse than {competitor}.",
        "The Flex billing is hard to understand. Finance keeps asking me questions I can't answer.",
    ],
    "detractor": [
        "Order was 6 weeks late with no communication.",
        "Support is terrible. Bounced between 4 people before anyone understood the problem.",
        "Too expensive",
        "Third motherboard failure on the same model. Quality has gone downhill.",
        "Tech showed up without the part. Twice. We pay for 4-hour response.",
        "Rep disappeared after the sale. Haven't heard from anyone in 6 months.",
        "The BIOS update bricked 3 machines. No warning, no advisory.",
        "We were charged for items we never received and it took 3 months to get a credit.",
        "Firmware update broke our BMC and we had to find out from a forum that it was a known issue.",
        "Never again.",
        "Credit hold blocked our order over a $400 invoice that was already paid. Ridiculous.",
        "Support asked me to reseat a drive 3 times before escalating. I've been doing this for 20 years.",
        "Lead time quoted at 2 weeks, delivered in 9.",
        "{competitor} is cheaper and their support is just as good. Considering switching.",
        "Battery swelling on multiple units. Had to fight to get replacements.",
        "Docks drop monitors constantly. Users hate them.",
        "Price went up 15% on renewal with no explanation.",
        "Partner experience was awful. Not sure if that's on you or them, but it reflects on you.",
        "Survey is too long",
        "Your phone tree is a nightmare. Couldn't get to a human for 40 minutes.",
        "We lost a day of production because of a firmware bug you knew about. Unacceptable.",
    ],
}


# =============================================================================
# 6. WIN_NOTES / LOSS_NOTES
# =============================================================================

WIN_NOTES = [
    "Won. {competitor} was cheaper by ~8% but couldn't commit to a delivery date before {quarter}. We had stock. Timing beat price.",
    "Win on {account} server refresh, {amount}. Licensing model sold it - consolidating from {servers} hosts cut their {hypervisor} bill enough to fund half the hardware. {se_name} built the model; customer's finance team checked it themselves and agreed.",
    "Won the bake-off vs {competitor}. They beat us on one synthetic IOPS test; we won on management, support response, and the effective capacity guarantee. Customer weighted day-2 ops heavily.",
    "Closed {amount}. Deployment services were the differentiator - customer did their last refresh with {competitor} and it took 9 months. Our plan was 10 weeks and we had references to prove it.",
    "Won. Relationship deal. {contact_first} has bought from us at 3 companies. Never really competitive.",
    "Vault win. Insurance renewal required immutable backups by {date}. We were the only vendor who could deliver, install and run a documented restore test in time.",
    "Won Converge after a 4-week POC. Node pull test and rolling upgrade sealed it. {competitor}'s POC took 2 weeks just to get installed.",
    "Won edge rollout, {qty} sites. Remote BMC/OOB was the difference - {competitor}'s box had no out-of-band management, and the customer had been driving 3 hours to power-cycle servers.",
    "Win at {discount}% off. Not proud of the margin but it opens the DC door - previously clients-only account.",
    "Won networking deal. Perpetual licensing on Mesh vs {competitor}'s subscription model. Customer's CFO did the 7-yr math and it wasn't close.",
    "Won AI pilot. Delivered GPUs in {weeks} weeks vs {competitor}'s 16. Customer's board deadline was the driver.",
    "DaaS win, {seats} seats, 36 months. Finance wanted opex, IT wanted control of configs. We gave both.",
    "Won back {account} after losing them to {competitor} 3 years ago. Their support experience with {competitor} was bad and they remembered ours was good.",
    "Won. Single vendor for client + DC + edge. Customer's new {exec_title} mandated vendor consolidation and we were the only one with the full stack.",
    "Small win, {amount}, but strategic: first storage deal at {account}. Foot in the door.",
    "Won via {partner}. They had the services relationship and brought us in. Clean co-sell.",
    "Won the renewal plus a refresh. Renew-vs-replace analysis showed replacement was cheaper over 3 years. Customer appreciated the honesty.",
    "Win. Orvane Financial Services matched {competitor}'s 0% financing. Took financing off the table, and then it came down to product.",
    "Closed {amount} on the last day of {quarter}. Customer had use-it-or-lose-it budget and we had stock that could ship and invoice in time.",
    "Won M&A Day 1 laptop deal, {qty} units. {competitor} couldn't image and ship in 3 weeks. We did it in 2.",
    "Won. Their CISO cared about firmware supply chain security and hardware root of trust. Our story there was stronger.",
    "Win on {account} Flex deal. Repatriated 2 workloads from {cloud}. Opex model kept finance happy, cost dropped {pct}%.",
]

LOSS_NOTES = [
    "Lost to {competitor} on price. They came in ~{pct}% below our best number. Customer acknowledged our solution was better but the budget was fixed at {budget}.",
    "Lost - no decision. Project shelved after their budget was frozen. Might come back in {fy}.",
    "Lost to {competitor}. They bundled storage with networking at a price we couldn't touch on storage alone.",
    "Lost. Customer moved the workload to {cloud} instead. Cloud-first mandate from the CEO overrode the TCO analysis.",
    "Lost to {competitor} - the new {exec_title} came from a {competitor} shop and brought them in. Relationship we didn't have.",
    "Lost on timing. Our lead time on the GPU config was {weeks} weeks; {competitor} had stock. Board deadline couldn't move.",
    "Lost - {partner} was fulfilling and their services margin made the total uncompetitive. Product was priced right; the bundle wasn't.",
    "Lost. Support escalations this year were cited directly in the decision. We earned this one.",
    "No decision. Champion {contact_name} left the company mid-cycle and nobody picked it up.",
    "Lost the {hypervisor} replacement deal - they renewed after all. Migration risk was too scary for a 2-person team. Fair.",
    "Lost to {competitor}. Procurement ran a reverse auction and price was 70% of the scoring.",
    "Lost. Customer was acquired; acquirer standardized on {competitor}.",
    "Lost - budget redirected to a cybersecurity incident response. Hardware refresh deferred indefinitely.",
    "Lost to {competitor} on storage. They offered a 5:1 data reduction guarantee; we offered 3:1. Ours is realistic, theirs probably won't hold, but customer believed the bigger number.",
    "Lost. Customer went with refurbished gear from a reseller - 40% cheaper, no warranty. Price was the only thing that mattered.",
    "No decision - project kept slipping quarter to quarter and eventually closed out. Never had a real compelling event.",
    "Lost to {competitor}. They gave away a year of support. We couldn't justify matching.",
    "Lost. Layoffs at {account} - IT team cut by a third and all projects cancelled.",
    "Lost the AI deal - customer decided to use {cloud} GPU instances for the pilot. Might come back if usage grows.",
    "Lost - they chose {competitor}'s HCI because their MSP only supports that platform.",
    "Lost on relationship. {competitor}'s rep has been there 8 years; we've had 3 reps in 2 years.",
    "Lost - customer delayed to next {fy} and then didn't respond. Closing.",
]


# =============================================================================
# 7. ACCOUNT_PLAN
# =============================================================================

ACCOUNT_PLAN = {
    "executive_summary": [
        "{account} is a {seats}-employee company headquartered in {hq_city}, growing ~{growth}% annually. Orvane is the incumbent on client devices; {competitor} owns most of the datacenter. Our goal this {fy} is to win the storage refresh and establish Orvane as a strategic DC vendor.",
        "Long-standing customer with strong relationships in IT. Total Orvane spend {amount} last year. Biggest opportunity is the {hypervisor} renewal - the licensing change opens the door to Converge.",
        "{account} is in a cost-reduction phase following layoffs. Near-term opportunities are limited to cost-saving initiatives; the strategy is to be the vendor that helps them spend less, positioning for a refresh when budgets recover.",
        "New logo pursuit. {account} has no current Orvane relationship. Entry point is the Win 11 migration ({qty} devices incompatible). If successful, expand into DC.",
        "Strategic account with a new {exec_title} ({new_exec}) driving vendor consolidation. We must be one of the survivors. Plan focuses on exec engagement and full-stack positioning.",
        "{account} is expanding rapidly (new site in {site_city}) and launching an {initiative}. Plan targets the site build and AI pilot as growth vectors.",
        "At-risk account. Three escalations and a late order this year. Priority is relationship recovery before any new pursuits.",
        "{account} recently acquired a {competitor} shop, roughly doubling IT footprint. Integration creates a 12-18 month standardization opportunity.",
        "Mid-market account, purchasing through {partner}. Plan focuses on co-selling with {partner} and increasing share of wallet in infrastructure.",
    ],
    "business_priorities": [
        "Cost reduction - board mandate to cut IT spend {pct}% by end of {fy}.",
        "Growth - expanding into {site_city} and hiring ~{seats} people over 2 years.",
        "Resilience - recent outage cost a weekend of operations; board wants better DR.",
        "AI - CEO wants an {initiative} visible by {quarter}.",
        "Security and compliance - cyber insurance requirements, new CISO, audit findings.",
        "M&A integration - Day 1 by {date}, full integration in 12 months.",
        "Sustainability - public emissions targets; IT is ~8% of footprint.",
        "Workforce enablement - hybrid work is permanent; employee experience is a stated priority.",
        "Modernization - moving off legacy systems and reducing technical debt.",
    ],
    "it_environment": [
        "~{seats} endpoints, mostly Orvane Aster on {os}, Intune-managed. Mixed dock types causing tickets.",
        "{servers} hosts on {hypervisor}, mix of {model} (Orvane) and {competitor}. Oldest gear 6+ yrs. FC SAN, 10/25GbE.",
        "Storage: {competitor} array, ~{tb}TB, {util}% full, out of support {quarter}. No replication to DR.",
        "Backup: {competitor} dedupe appliance + tape. Not immutable. Insurance flagged it.",
        "Network: {competitor} core, EOL {quarter}. Flat management network with BMCs exposed.",
        "Cloud: {cloud} for dev/test and some SaaS. ~{budget}/yr and growing.",
        "Edge: {qty} remote sites each with 1-2 aging tower servers.",
        "Apps: ERP on SQL Server, ServiceNow for ITSM, Splunk for logs, M365 for productivity.",
        "IT team: 12 people, 2 open reqs. Thin on network and storage expertise.",
    ],
    "whitespace": [
        "Storage - {competitor} array out of support {quarter}. {storage_product} opportunity, est. {amount}.",
        "Data protection - no immutable backups. Vault + M365 backup.",
        "HCI - {hypervisor} renewal shock. Converge for general VMs.",
        "Networking - core switches EOL. Mesh campus + DC fabric.",
        "Edge - {qty} sites with aging servers. Outpost standard.",
        "AI - {initiative} in planning. Atlas AI pilot.",
        "Services - no deployment, ITAD or residency services today. All whitespace.",
        "Monitors and docks - buying from a reseller at worse prices than contract.",
        "Orvane Manage / Shield - not deployed. Win 11 migration is the hook.",
    ],
    "relationship_map": [
        "{contact_name} ({contact_title}) - champion. Long relationship, technical, trusts us.",
        "{contact2_name} ({contact2_title}) - economic buyer. Limited relationship. Priority to build.",
        "{new_exec} ({exec_title}) - new, unknown. Came from a {competitor} shop. Need a meeting.",
        "Procurement - process-driven, measured on savings. Open every quote with room.",
        "Security team - new CISO, focused on firmware and supply chain. Opportunity to engage on Insight + Shield.",
        "Network team - 2 people, {competitor}-loyal. Need technical credibility via {se_name}.",
        "Finance - wants opex. Receptive to Flex and DaaS.",
        "{partner} - services partner with long relationship. Co-sell, don't compete.",
        "Former champion {old_rep} relationship - left. Rebuilding with successor.",
    ],
    "competitive_landscape": [
        "{competitor} - incumbent on storage and networking. Strong exec relationship. Aggressive on price.",
        "Corsalis - pitching HCI with free migration offer. Partner-only support is a weakness.",
        "Varenta - occasional price checks on clients. Not a real threat.",
        "Lumora - has storage foothold at the acquired company.",
        "Quorra Networks - network team loyal to their CLI. Mesh POC is the counter.",
        "Helixon - pitching GPU servers with aggressive delivery claims. Unproven.",
        "Cloud ({cloud}) - the real competitor for some workloads. Position hybrid, not either/or.",
        "Third-party maintenance - offered ~40% lower support pricing. Counter with firmware access + engineering escalation.",
        "Refurb resellers - compete on price for the cost-conscious buyer.",
    ],
    "risks": [
        "Champion {contact_name} may leave - rumor of job search. Need multi-threading.",
        "Budget freeze could push all projects to next {fy}.",
        "Support escalations damaged trust; another bad experience could lose the account.",
        "New {exec_title} may bring {competitor}.",
        "GPU lead times ({weeks} weeks) may miss board deadline.",
        "Partner conflict with {partner} could derail deals.",
        "Pricing - procurement pushing {discount}% and {competitor} is lower.",
        "Acquisition - if {account} is acquired, decisions move to acquirer.",
        "Cloud-first mandate could move workloads off-prem permanently.",
    ],
    "action_plan": [
        "Exec briefing with {new_exec} by {date}. Owner: {rep_first} + RVP.",
        "Storage proposal + effective capacity guarantee by {date}. Owner: {se_name}.",
        "Build relationship with {contact2_name} - monthly touch. Owner: {rep_first}.",
        "Run Insight collector to show firmware drift + predictive failures. Owner: {se_name}.",
        "Co-sell plan with {partner} for network refresh. Owner: {rep_first}.",
        "Quarterly business reviews starting {quarter}. Owner: {rep_first}.",
        "Win 11 readiness report via Orvane Manage. Owner: {se_name}.",
        "Fix monitor/dock purchasing - move to contract. Owner: {rep_first}.",
        "Vault POC to address insurance requirements. Owner: {se_name}.",
    ],
}


# =============================================================================
# 8. NEWS  (trade-press / press-release snippets about the customer)
# =============================================================================

NEWS = {
    "funding": [
        ("{account} raises {budget} Series C to accelerate expansion", "{account} announced a {budget} Series C round led by a growth equity firm. The company plans to use the funds to expand operations in {site_city} and invest in technology infrastructure."),
        ("{account} secures {budget} growth investment", "The {hq_city}-based company said the investment will fund product development and roughly double headcount over the next 18 months."),
        ("{account} closes {budget} credit facility", "{account} has closed a {budget} revolving credit facility to support working capital and strategic acquisitions, according to a company statement."),
        ("{account} lands {budget} from private equity", "A private equity firm has taken a significant minority stake in {account}. Terms were not disclosed beyond the {budget} headline figure."),
        ("{account} raises {budget} to scale {initiative}", "{account} said the new funding will primarily support its {initiative} and related data infrastructure."),
        ("{account} announces {budget} strategic investment", "{account} received a {budget} strategic investment from an industry partner, which will also take a board seat."),
    ],
    "earnings_beat": [
        ("{account} beats {quarter} estimates, raises full-year guidance", "{account} reported {quarter} revenue up {growth}% year over year, ahead of analyst expectations. Management raised {fy} guidance, citing strong demand and operational efficiency."),
        ("{account} posts record quarter", "{account} delivered its strongest quarter on record, with revenue growth of {growth}% and margin expansion of {pct} basis points."),
        ("{account} shares jump on strong {quarter} results", "Shares of {account} rose after the company reported results well above consensus and announced a buyback program."),
        ("{account} tops forecasts as {initiative} gains traction", "{account} attributed its {quarter} beat partly to early returns from its {initiative}."),
        ("{account} raises outlook after solid {quarter}", "{account} raised its outlook for {fy} after a quarter in which revenue rose {growth}% and operating costs fell."),
        ("{account} reports {growth}% revenue growth", "{account} said growth was broad-based across segments, with particular strength in {site_city}."),
    ],
    "earnings_miss": [
        ("{account} misses {quarter} estimates, cuts guidance", "{account} reported {quarter} revenue below analyst expectations and lowered its {fy} outlook, citing softer demand and higher costs."),
        ("{account} shares fall on weak results", "Shares of {account} declined after the company reported a {pct}% drop in operating income and announced a cost review."),
        ("{account} warns on full-year profit", "{account} said full-year profit will come in below previous guidance and that it would 'reduce discretionary spending across the business.'"),
        ("{account} {quarter} revenue declines {pct}%", "{account} reported a year-over-year revenue decline and said it is evaluating its cost structure."),
        ("{account} lowers {fy} forecast", "{account} cut its {fy} forecast, pointing to macroeconomic headwinds and delayed customer orders."),
        ("{account} misses on margin pressure", "Revenue was in line but margins disappointed as {account} absorbed higher input costs."),
    ],
    "layoffs": [
        ("{account} to cut {pct}% of workforce", "{account} announced plans to reduce its workforce by approximately {pct}%, affecting multiple departments. The company said the move is part of a broader effort to streamline operations."),
        ("{account} announces restructuring, layoffs", "{account} is restructuring its operations and eliminating roles, primarily in corporate functions, according to an internal memo seen by local media."),
        ("{account} closes {site_city} office in cost-cutting move", "{account} will close its {site_city} office and consolidate staff in {hq_city}."),
        ("{account} trims headcount as demand softens", "{account} confirmed layoffs but declined to say how many employees were affected."),
        ("{account} reduces staff, freezes hiring", "In addition to layoffs, {account} has frozen hiring and paused several capital projects."),
        ("{account} cuts jobs amid restructuring", "{account} said the reduction would save roughly {amount} annually."),
    ],
    "acquisition": [
        ("{account} acquires Northbridge Data Systems", "{account} has agreed to acquire Northbridge Data Systems, a regional provider of managed IT services. The deal is expected to close in {quarter}."),
        ("{account} to buy Pinecrest Analytics for {budget}", "{account} will acquire Pinecrest Analytics in a deal valued at {budget}, adding data and analytics capabilities."),
        ("{account} snaps up Redwater Logistics", "{account} announced the acquisition of Redwater Logistics, expanding its footprint into {site_city}."),
        ("{account} completes acquisition of Halberd Manufacturing", "{account} has closed its acquisition of Halberd Manufacturing. Integration is expected to take 12 to 18 months."),
        ("{account} acquires Cobalt Health Partners", "{account} acquired Cobalt Health Partners, a network of outpatient clinics, for an undisclosed sum."),
        ("{account} announces deal for Sable Ridge Software", "{account} will acquire Sable Ridge Software to accelerate its {initiative}."),
    ],
    "acquired": [
        ("{account} to be acquired in {budget} deal", "{account} has agreed to be acquired by a larger industry player in a transaction valued at {budget}. The deal is expected to close in {quarter}, pending regulatory approval."),
        ("{account} agrees to sale to private equity firm", "{account} will be taken private by a private equity firm. Management is expected to remain in place."),
        ("{account} acquired by larger rival", "{account} has been acquired by a larger competitor. The combined company will be headquartered in {hq_city}."),
        ("{account} sale completed", "The acquisition of {account} has closed. {account} will operate as a subsidiary of its new parent."),
        ("{account} explores sale", "{account} has hired advisers to explore strategic alternatives, including a potential sale."),
        ("{account} merger approved by regulators", "Regulators approved the merger involving {account}, clearing the way for the deal to close."),
    ],
    "exec_hire": [
        ("{account} names {new_exec} as {exec_title}", "{account} has appointed {new_exec} as {exec_title}, effective {date}. {new_exec} joins from a larger enterprise where they led technology modernization."),
        ("{new_exec} joins {account} as {exec_title}", "{new_exec} will lead {account}'s technology strategy and report to the CEO."),
        ("{account} appoints new {exec_title}", "{account} announced the appointment of {new_exec} as its new {exec_title}, succeeding a long-time executive who is retiring."),
        ("{account} hires {new_exec} to lead IT", "{new_exec} joins {account} with a mandate to modernize infrastructure and reduce costs."),
        ("{account} taps {new_exec} for {exec_title} role", "{account} said {new_exec} brings experience in digital transformation and cloud strategy."),
        ("Leadership change at {account}: {new_exec} named {exec_title}", "{account} has named {new_exec} as {exec_title}. The appointment is part of a broader leadership refresh."),
    ],
    "hq_move": [
        ("{account} relocates headquarters to {hq_city}", "{account} announced it will move its corporate headquarters to {hq_city}, citing access to talent and lower operating costs."),
        ("{account} to open new HQ in {hq_city}", "{account} will open a new headquarters campus in {hq_city} in {quarter}."),
        ("{account} moves HQ, consolidates offices", "{account} is relocating its headquarters to {hq_city} and consolidating several regional offices."),
        ("{account} signs lease for new {hq_city} headquarters", "{account} has signed a long-term lease for a new headquarters in {hq_city}."),
        ("{account} headquarters move complete", "{account} has completed its move to {hq_city}."),
        ("{account} chooses {hq_city} for new headquarters", "After a lengthy search, {account} selected {hq_city} for its new headquarters."),
    ],
    "expansion": [
        ("{account} opens new facility in {site_city}", "{account} has opened a new facility in {site_city}, creating approximately {seats} jobs."),
        ("{account} expands into {site_city}", "{account} announced plans to expand operations into {site_city}, with a new office opening in {quarter}."),
        ("{account} breaks ground on {site_city} site", "{account} broke ground on a new site in {site_city}, expected to open next year."),
        ("{account} to add {seats} jobs in {site_city}", "{account} will add {seats} jobs as part of its expansion into {site_city}."),
        ("{account} invests {budget} in {site_city} expansion", "{account} will invest {budget} in a new facility in {site_city}."),
        ("{account} opens {site_city} distribution center", "{account} has opened a new distribution center in {site_city} to serve growing demand."),
    ],
    "bankruptcy": [
        ("{account} files for Chapter 11 protection", "{account} has filed for Chapter 11 bankruptcy protection. The company said operations will continue during the restructuring."),
        ("{account} enters bankruptcy", "{account} filed for bankruptcy, citing debt burden and declining revenue."),
        ("{account} seeks creditor protection", "{account} has sought creditor protection while it restructures its debt."),
        ("{account} files Chapter 11, plans sale", "{account} filed for Chapter 11 and plans to sell its assets through a court-supervised process."),
        ("{account} restructuring: Chapter 11 filing", "{account} said it expects to emerge from Chapter 11 within 6 months."),
        ("{account} bankruptcy filing affects {seats} employees", "{account}'s bankruptcy filing puts approximately {seats} jobs at risk."),
    ],
    "rebrand": [
        ("{account} unveils new brand identity", "{account} has rebranded, introducing a new logo and visual identity to reflect its evolving business."),
        ("{account} rebrands to reflect growth", "{account} announced a rebrand as it expands beyond its original market."),
        ("{account} launches new brand", "{account} unveiled a new brand identity, part of a broader transformation."),
        ("{account} refreshes brand", "{account} refreshed its brand to better communicate its value proposition."),
        ("{account} new name, same mission", "{account} announced a name change as part of a corporate rebrand."),
        ("{account} rebrand marks new chapter", "{account} said the rebrand signals a new chapter after a period of transformation."),
    ],
    "award": [
        ("{account} named a Top Workplace", "{account} has been named a Top Workplace in {hq_city} for the third consecutive year."),
        ("{account} wins industry innovation award", "{account} received an industry award for its {initiative}."),
        ("{account} recognized for sustainability", "{account} was recognized for its sustainability efforts, including reducing its carbon footprint by {pct}%."),
        ("{account} wins customer service award", "{account} won a customer service excellence award."),
        ("{account} named to fastest-growing companies list", "{account} was named one of the fastest-growing companies in the region, with {growth}% growth."),
        ("{account} CIO honored", "{account}'s CIO was named among the top technology leaders in the region."),
    ],
    "partnership": [
        ("{account} partners with {cloud} on digital transformation", "{account} announced a strategic partnership with {cloud} to accelerate its {initiative}."),
        ("{account} forms strategic alliance", "{account} has formed a strategic alliance with a technology firm to expand its capabilities."),
        ("{account} and partner launch joint offering", "{account} and a partner launched a joint offering targeting mid-market customers."),
        ("{account} signs multi-year partnership", "{account} signed a multi-year partnership agreement worth {budget}."),
        ("{account} partners to expand in {site_city}", "{account} partnered with a local firm to expand into {site_city}."),
        ("{account} announces technology partnership", "{account} announced a technology partnership focused on AI and data."),
    ],
    "cyber_incident": [
        ("{account} discloses cybersecurity incident", "{account} disclosed a cybersecurity incident that disrupted some operations. The company said it is working with external experts to investigate."),
        ("{account} hit by ransomware attack", "{account} was the target of a ransomware attack that affected some systems. Operations are being restored."),
        ("{account} investigating data breach", "{account} is investigating a potential data breach and has notified law enforcement."),
        ("{account} restores systems after cyberattack", "{account} said it has restored most systems following a cyberattack last week."),
        ("{account} cyber incident disrupts operations", "A cyber incident at {account} disrupted operations for several days."),
        ("{account} reports network intrusion", "{account} disclosed a network intrusion in a regulatory filing."),
    ],
    "ipo": [
        ("{account} files for IPO", "{account} has filed for an initial public offering, seeking to raise {budget}."),
        ("{account} prices IPO", "{account} priced its IPO, raising {budget}."),
        ("{account} shares debut", "{account} shares began trading, rising {pct}% on the first day."),
        ("{account} plans IPO in {quarter}", "{account} is planning an IPO for {quarter}, according to people familiar with the matter."),
        ("{account} confidentially files for IPO", "{account} has confidentially filed for an IPO."),
        ("{account} IPO raises {budget}", "{account}'s IPO raised {budget}, valuing the company at several times that."),
    ],
    "contract_win": [
        ("{account} wins {budget} contract", "{account} has been awarded a {budget} multi-year contract."),
        ("{account} lands major government contract", "{account} won a government contract worth {budget}."),
        ("{account} selected for {budget} project", "{account} was selected for a {budget} project in {site_city}."),
        ("{account} signs contract with major customer", "{account} signed a significant contract with a major customer."),
        ("{account} awarded multi-year deal", "{account} was awarded a multi-year deal worth {budget}."),
        ("{account} wins contract to expand services", "{account} won a contract to expand its services into {site_city}."),
    ],
}


# =============================================================================
# 9. PARTNER_NOTES
# =============================================================================

PARTNER_NOTES = [
    "{partner} submitted deal reg for {account}, {amount}, {product_line}. Approved - no conflicting direct activity in last 90 days.",
    "Deal reg from {partner} on {account} rejected - {rep_name} has documented direct engagement since {quarter}. Notified partner with activity log.",
    "{partner} requesting MDF for a joint event targeting healthcare accounts in {site_city}. Budget ask {amount}. Pending channel marketing approval.",
    "Quarterly rebate for {partner} calculated: {amount} on {quarter} sell-through. Paid via credit memo.",
    "{partner} brought in {account} as a net-new logo. Partner-sourced. Partner leads, {se_name} supports technical.",
    "Conflict: {partner} and direct rep both quoted {account}. Customer confused by different prices. Rules of engagement: partner fulfills, direct supports.",
    "{partner} hit Gold tier this {fy}. Unlocks additional {discount}% discount on infrastructure deal reg.",
    "{partner} asking for pricing support on {account} to beat {competitor}. Submitted to deal desk at {discount}%.",
    "QBR with {partner}: {amount} sell-through YTD, 14 deal regs approved, 3 rejected. Focus next quarter: Converge and Vault.",
    "{partner} SE certified on Converge. Can now run POCs without Orvane SE.",
    "{partner} complaint: direct rep went around them on {account}. Investigated - customer initiated contact. Shared emails with partner.",
    "MDF claim from {partner} for webinar: {amount}. Proof of execution received (attendee list, recording). Approved.",
    "{partner} registered 6 deals in one week, several in accounts they haven't worked before. Channel manager reviewing.",
    "{partner} deployment team handled rack & stack at {account}. Customer happy. Good co-delivery model.",
    "Partner-sourced pipeline from {partner}: {amount} across 8 opps. Strongest in mid-market.",
    "{partner} losing deals to {competitor}'s partner on services margin. Discussed competitive services pricing.",
    "{partner} asking for extension on deal reg for {account} - customer delayed to {quarter}. Extended 90 days.",
    "New partner {partner} onboarded. Kickoff call: product training, deal reg process, portal access.",
    "{partner} wants to resell Orvane Flex. Requires additional certification. Sending requirements.",
    "{partner} rebate dispute: they say sell-through was higher. Reconciling against distributor reports.",
    "Joint account planning with {partner} on {account}: they own services, we own product. Target {budget} this {fy}.",
    "{partner} account manager left. New contact assigned. Re-introducing to {account}.",
]


# =============================================================================
# 10. SHORTHAND
# =============================================================================

SHORTHAND = {
    "follow up": "f/u",
    "with": "w/",
    "without": "w/o",
    "next week": "nxt wk",
    "customer": "cust",
    "quarter": "qtr",
    "approximately": "~",
    "meeting": "mtg",
    "voicemail": "VM",
    "because": "b/c",
    "information": "info",
    "regarding": "re:",
    "please": "pls",
    "thanks": "thx",
    "message": "msg",
    "management": "mgmt",
    "department": "dept",
    "number": "#",
    "between": "btwn",
    "before": "b4",
    "account": "acct",
    "business": "biz",
    "decision maker": "DM",
    "end of day": "EOD",
    "end of week": "EOW",
    "end of month": "EOM",
    "end of quarter": "EOQ",
    "as soon as possible": "ASAP",
    "for your information": "FYI",
    "out of office": "OOO",
    "purchase order": "PO",
    "statement of work": "SOW",
    "request for proposal": "RFP",
    "request for quote": "RFQ",
    "proof of concept": "POC",
    "total cost of ownership": "TCO",
    "return on investment": "ROI",
    "year over year": "YoY",
    "month over month": "MoM",
    "year to date": "YTD",
    "quarterly business review": "QBR",
    "sales engineer": "SE",
    "account manager": "AM",
    "technical account manager": "TAM",
    "vice president": "VP",
    "director": "dir",
    "manager": "mgr",
    "requirements": "reqs",
    "environment": "env",
    "configuration": "config",
    "infrastructure": "infra",
    "production": "prod",
    "development": "dev",
    "approved": "appvd",
    "scheduled": "sched",
    "discussed": "disc'd",
    "confirmed": "conf'd",
    "pending": "pndg",
    "tomorrow": "tmrw",
    "today": "tdy",
    "week": "wk",
    "month": "mo",
    "year": "yr",
    "hours": "hrs",
    "minutes": "min",
    "something": "smth",
    "people": "ppl",
    "probably": "prob",
    "question": "q",
    "conversation": "convo",
    "opportunity": "opp",
    "competitor": "comp",
    "budget": "bdgt",
    "quote": "qt",
    "laptop": "lt",
    "server": "svr",
    "storage": "stg",
    "support": "supp",
    "renewal": "rnwl",
    "maintenance": "maint",
    "deployment": "deploy",
    "migration": "migr",
}


# =============================================================================
# 11. SIGNATURES
# =============================================================================

SIGNATURES = [
    "Sent from my iPhone",
    "Sent from my Android",
    "Get Outlook for iOS",
    "{contact_name}\n{contact_title}\n{account}\n",
    "--\n{contact_name} | {contact_title}\n{account}\nOffice: 555-0100 | Mobile: 555-0199",
    "Thanks,\n{contact_first}\n\nCONFIDENTIALITY NOTICE: This email and any attachments are for the sole use of the intended recipient(s) and may contain confidential information. If you are not the intended recipient, please notify the sender and delete this message.",
    "{contact_name}\n{contact_title} | {account}\n\nPlease consider the environment before printing this email.",
    "Best regards,\n\n{contact_name}\n{contact_title}\n{account} | {hq_city}",
    "Regards,\n{contact_first}\n\n[This message originated outside your organization. Use caution with links and attachments.]",
    "-{contact_first}\n\nSent from mobile, please excuse typos",
    "{contact_name}\n{contact_title}\n{account}\nI'm working flexible hours. Please don't feel obligated to reply outside your normal working hours.",
    "Thank you,\n{contact_name}\n\n*** EXTERNAL EMAIL ***",
    "{contact_first}\n{contact_title}\nPronouns: they/them\n{account}",
]


# =============================================================================
# 12. CALL_DISPOSITIONS_TEXT
# =============================================================================

CALL_DISPOSITIONS_TEXT = {
    "connected": [
        "Connected w/ {contact_first}. Brief convo, they're busy - asked to call back {date}.",
        "Spoke w/ {contact_name}. Discussed {initiative}. Sending info.",
        "Connected. {contact_first} confirmed PO is in approval.",
        "Talked to {contact_first} ~10 min. Good convo, f/u nxt wk.",
        "Reached {contact_name}. Not a good time, will call back.",
        "Connected w/ {contact_first} re: {quote_number}. Questions on config, sending revised.",
        "Spoke to {contact_first}. All good, no open issues.",
    ],
    "left_voicemail": [
        "Left VM for {contact_first}.",
        "LVM re: {quote_number}.",
        "Left VM, asked for callback re: {initiative}.",
        "VM left for {contact_name}. 2nd attempt.",
        "Left detailed VM about {advisory}.",
        "Left VM - following up on email from {date}.",
        "LVM. Will try again Thurs.",
    ],
    "no_answer": [
        "No answer.",
        "NA, no VM option.",
        "Rang out.",
        "No answer, mailbox full.",
        "Tried {contact_first}, NA.",
        "No answer, will email instead.",
    ],
    "wrong_number": [
        "Wrong number - not {contact_name}.",
        "Number belongs to someone else now. Need updated contact info.",
        "Wrong #. Updated record.",
        "Reached a different dept. Transferred, dropped.",
        "Wrong number - {contact_name} no longer at this extension.",
        "Number in CRM is a fax line.",
    ],
    "gatekeeper": [
        "Gatekeeper - {contact_first} in meetings all day. Left msg.",
        "Admin said {contact_name} doesn't take vendor calls. Asked for email.",
        "Receptionist took a message.",
        "Got EA, asked to send meeting request via email.",
        "Gatekeeper wouldn't transfer. Will try direct line.",
        "Front desk said {contact_first} is OOO until {date}.",
    ],
    "meeting_booked": [
        "Booked mtg w/ {contact_first} for {date}.",
        "Meeting booked - discovery w/ {se_name}, {date}.",
        "Booked 30 min w/ {contact_name} re: {initiative}.",
        "Mtg set for {date}. Invite sent.",
        "Booked demo for {date}.",
        "Meeting scheduled w/ {contact_first} + {contact2_name} on {date}.",
    ],
    "callback_requested": [
        "{contact_first} asked for callback {date}.",
        "Callback requested - after their board mtg.",
        "Asked to call back nxt wk.",
        "Call back in {weeks} wks.",
        "Callback requested after budget cycle.",
        "Call back after {quarter} - not before.",
    ],
    "not_interested": [
        "Not interested - happy w/ {competitor}.",
        "Not interested at this time.",
        "No budget. Not interested this yr.",
        "Asked not to be contacted again. Marked DNC.",
        "Not interested, just signed w/ {competitor}.",
        "Not a fit - too small.",
    ],
    "bad_number": [
        "Bad number - disconnected.",
        "Number not in service.",
        "Bad #. Need new contact info.",
        "Disconnected. Contact may have left company.",
        "Invalid number.",
        "Fast busy. Bad number.",
    ],
}


# =============================================================================
# Self-test
# =============================================================================

if __name__ == "__main__":
    import string

    SLOTS = list(SLOT_NAMES)
    formatter = string.Formatter()
    dummy = {name: "<" + name + ">" for name in SLOTS}
    errors = []

    def walk(obj, path):
        """Yield (path, string) for every string in a nested structure."""
        if isinstance(obj, str):
            yield path, obj
        elif isinstance(obj, dict):
            for key, value in obj.items():
                yield from walk(value, path + "[" + repr(key) + "]")
        elif isinstance(obj, (list, tuple)):
            for i, value in enumerate(obj):
                yield from walk(value, path + "[" + str(i) + "]")
        else:
            errors.append(path + ": unexpected type " + type(obj).__name__)

    def check(name, obj):
        count = 0
        for path, text in walk(obj, name):
            count += 1
            try:
                for _, field, spec, conv in formatter.parse(text):
                    if field is None:
                        continue
                    if field not in SLOTS:
                        errors.append(path + ": unknown slot " + repr(field))
                    if spec or conv:
                        errors.append(path + ": format spec/conversion not allowed")
                text.format_map(dummy)
            except (ValueError, KeyError, IndexError) as exc:
                errors.append(path + ": " + repr(exc))
        return count

    def require(cond, msg):
        if not cond:
            errors.append(msg)

    # --- shape / minimum-count checks ---------------------------------------
    TOPIC_KEYS = [
        "intro_discovery", "client_refresh", "win11_migration", "server_refresh",
        "storage_capacity", "data_protection", "hci_virtualization", "ai_gpu_initiative",
        "networking_upgrade", "edge_deployment", "pricing_negotiation", "po_followup",
        "order_status_delay", "warranty_renewal", "support_escalation", "competitor_threat",
        "budget_planning", "exec_change", "partner_conflict", "lease_end",
        "consumption_billing", "security_advisory", "qbr_review", "contract_pricing",
        "credit_hold_collections", "rep_handoff", "relationship_check_in", "event_followup",
        "m_and_a_integration", "layoffs_cost_cutting", "expansion_new_site",
        "small_business_purchase", "software_licensing", "services_deployment",
    ]
    TOPIC_MIN = {"subjects": 8, "summaries": 14, "next_steps": 8,
                 "emails_out": 5, "emails_in": 5, "chatter": 6}
    for key in TOPIC_KEYS:
        require(key in TOPICS, "TOPICS missing " + key)
        for field, minimum in TOPIC_MIN.items():
            items = TOPICS.get(key, {}).get(field, [])
            require(len(items) >= minimum,
                    "TOPICS[%s][%s] has %d < %d" % (key, field, len(items), minimum))
            if field.startswith("emails"):
                for i, item in enumerate(items):
                    require(isinstance(item, tuple) and len(item) == 2,
                            "TOPICS[%s][%s][%d] not a (subject, body) tuple" % (key, field, i))
    require(set(TOPICS) == set(TOPIC_KEYS), "TOPICS has unexpected keys")

    for mtype in ["discovery", "product_demo", "technical_deep_dive", "architecture_workshop",
                  "executive_briefing", "qbr", "proposal_review", "negotiation",
                  "account_planning"]:
        require(len(MEETING_NOTES.get(mtype, [])) >= 6, "MEETING_NOTES[%s] < 6" % mtype)

    for cat in ["hardware_failure", "drive_failure", "firmware_bug", "performance",
                "config_help", "shipping_damage", "doa", "warranty_question", "billing_issue",
                "software_licensing", "network_connectivity", "data_recovery",
                "battery_swelling", "display_issue"]:
        require(len(CASE.get(cat, {}).get("subjects", [])) >= 6, "CASE[%s] subjects < 6" % cat)
        require(len(CASE.get(cat, {}).get("comments", [])) >= 10, "CASE[%s] comments < 10" % cat)

    require(len(COLLECTIONS_NOTES) >= 25, "COLLECTIONS_NOTES < 25")
    for k in ("promoter", "passive", "detractor"):
        require(len(SURVEY_VERBATIMS.get(k, [])) >= 20, "SURVEY_VERBATIMS[%s] < 20" % k)
    require(len(WIN_NOTES) >= 20, "WIN_NOTES < 20")
    require(len(LOSS_NOTES) >= 20, "LOSS_NOTES < 20")
    for sec in ["executive_summary", "business_priorities", "it_environment", "whitespace",
                "relationship_map", "competitive_landscape", "risks", "action_plan"]:
        require(len(ACCOUNT_PLAN.get(sec, [])) >= 8, "ACCOUNT_PLAN[%s] < 8" % sec)
    for ntype in ["funding", "earnings_beat", "earnings_miss", "layoffs", "acquisition",
                  "acquired", "exec_hire", "hq_move", "expansion", "bankruptcy", "rebrand",
                  "award", "partnership", "cyber_incident", "ipo", "contract_win"]:
        items = NEWS.get(ntype, [])
        require(len(items) >= 6, "NEWS[%s] < 6" % ntype)
        for i, item in enumerate(items):
            require(isinstance(item, tuple) and len(item) == 2,
                    "NEWS[%s][%d] not a (headline, summary) tuple" % (ntype, i))
    require(len(PARTNER_NOTES) >= 20, "PARTNER_NOTES < 20")
    require(len(SHORTHAND) >= 60, "SHORTHAND < 60")
    require(all(k == k.lower() for k in SHORTHAND), "SHORTHAND keys must be lowercase")
    require(len(SIGNATURES) >= 10, "SIGNATURES < 10")
    for disp in ["connected", "left_voicemail", "no_answer", "wrong_number", "gatekeeper",
                 "meeting_booked", "callback_requested", "not_interested", "bad_number"]:
        require(len(CALL_DISPOSITIONS_TEXT.get(disp, [])) >= 6,
                "CALL_DISPOSITIONS_TEXT[%s] < 6" % disp)

    # --- slot / render checks -----------------------------------------------
    structures = [
        ("TOPICS", TOPICS), ("MEETING_NOTES", MEETING_NOTES), ("CASE", CASE),
        ("COLLECTIONS_NOTES", COLLECTIONS_NOTES), ("SURVEY_VERBATIMS", SURVEY_VERBATIMS),
        ("WIN_NOTES", WIN_NOTES), ("LOSS_NOTES", LOSS_NOTES), ("ACCOUNT_PLAN", ACCOUNT_PLAN),
        ("NEWS", NEWS), ("PARTNER_NOTES", PARTNER_NOTES), ("SHORTHAND", SHORTHAND),
        ("SIGNATURES", SIGNATURES), ("CALL_DISPOSITIONS_TEXT", CALL_DISPOSITIONS_TEXT),
    ]
    total = 0
    for name, obj in structures:
        n = check(name, obj)
        total += n
        print("%-24s %6d strings" % (name, n))
    print("%-24s %6d strings" % ("TOTAL", total))

    # --- banned real-vendor names -------------------------------------------
    import re
    banned = re.compile(r"\b(dell|hpe?|hewlett|lenovo|cisco|netapp|pure storage|apple|"
                        r"supermicro|ibm|nutanix|idrac|ilo|xclarity)\b", re.IGNORECASE)
    for name, obj in structures:
        for path, text in walk(obj, name):
            m = banned.search(text)
            if m:
                errors.append(path + ": banned vendor term " + repr(m.group(0)))

    if errors:
        print("\n%d ERROR(S):" % len(errors))
        for e in errors:
            print("  " + e)
        raise SystemExit(1)
    print("\nOK - all templates use only known slots and render cleanly.")
