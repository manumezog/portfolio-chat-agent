# Manuel Mezo — Professional Experience Stories (STAR Format)

This document contains detailed accounts of professional projects from Manuel Mezo's career at Amazon and McKinsey, written in STAR (Situation, Task, Action, Result) format. Each story is a real example from his experience, describing the business context, his specific contribution, and the measurable outcome.

---

## Keeping a Critical Capacity Planning Process Alive During Team Attrition Crisis

**Company:** Amazon | **Role:** Senior Manager, Transportation Capacity Planning | **Year:** ~2023 | **Skills:** crisis management, KTLO, leadership alignment, knowledge management, prioritization under pressure

**Situation:** A deep organisational restructuring triggered a wave of team departures concentrated in a small team responsible for Amazon's weekly Labor and Transportation capacity planning process — a function covering 45,000 trucks per week, over 30,000 Amazon Associates, and weekly cost exposure of $45M in transport and $30M in labor. Scope splits, handovers to other orgs, and delayed backfills left the team critically under-staffed. Key metrics logic was breaking down at the same time as a new feature was being deployed, and reporting gaps surfaced in senior business reviews.

**Task:** Ensure the weekly capacity plan continued to be published without failure ("KTLO — Keep The Lights On") while managing the knowledge loss from departing members, keeping remaining team members focused, and aligning leadership on what had to pause.

**Action:** Manuel immediately flagged the headcount departure timeline to leadership and formally requested backfills. He worked with leadership to align on a strict priority hierarchy: publishing the weekly plan was P0 for every remaining team member; all development work, monthly business reviews, and non-critical stakeholder requests were paused. He restructured each team member's focus accordingly and instituted structured knowledge-transfer sessions and documentation sprints with departing colleagues to capture process logic before they left. For the long term, he drove alignment on a tech scope handover to a partner technology organisation to reduce the team's operational dependency on fragile manual processes.

**Result:** The weekly capacity plan was published without interruption throughout the entire attrition crisis. The planned deployment of a key improvement feature proceeded on schedule. A long-term mitigation plan was aligned with leadership, formally handing the technical ownership to a partner org and making the process resilient to future headcount fluctuations.

---

## Earning the Trust of a Sceptical Client to Recover Delay on a Train Manufacturing Project

**Company:** McKinsey & Company | **Client:** a major European train manufacturer | **Year:** ~2022–2023 | **Skills:** stakeholder management, consulting, structured problem-solving, cross-functional engagement, delay recovery

**Situation:** Manuel was deployed on a McKinsey engagement for a major train manufacturer whose flagship project was 5.5 months behind on client delivery dates, with €17 million in contractual penalties already accumulating. The client's operations leadership was actively hostile toward the consulting team: previous consulting experiences had left a negative impression, and senior client managers were reluctant to allow the McKinsey team to scrutinise their internal project timelines. Without access to key departments, delay-recovery opportunities were invisible.

**Task:** Manuel was tasked with diagnosing and surfacing opportunities to recover delay across the project plan, working with departments across planning, procurement, manufacturing, assembly, logistics, testing, and regulatory compliance — all while navigating political resistance without formal authority.

**Action:** He began by independently building foundational knowledge of the program: typical project milestone structures, lead times by department, and which phases sat on the critical path. Rather than confronting resistant stakeholders directly, he used a differentiated engagement strategy for each department: offering to help a planning manager with a parallel workstream to earn goodwill, identifying and approaching the most motivated individuals in procurement, giving visibility to a testing expert's work in front of their own leadership, and packaging business-impact arguments for top-level executives. To manage uncertainty around regulatory approval timelines (a key risk), he mapped public-entity dependency milestones explicitly. He consolidated all identified recovery opportunities into a structured view and facilitated a workshop with the full client leadership team, inviting key contributors to give them visibility and build shared ownership of the output.

**Result:** The engagement surfaced credible opportunities to recover 4 weeks of delay — reducing the total schedule overrun from 16 to 12 weeks — with a potential €2–4.5 million reduction in penalty cost. Client leadership acknowledged the feasibility of the proposed timeline reductions and publicly congratulated the McKinsey team for the quality of findings, marking a complete turnaround from the initial scepticism.

---

## Unblocking a €6M Commercial Dispute with a 3PL Through Data Analysis

**Company:** Amazon | **Role:** BI Manager and Inventory Quality SME, EU External Fulfillment | **Year:** ~2021 | **Skills:** data analysis, commercial influence, stakeholder management, root cause analysis, legal escalation

**Situation:** A commercial negotiation with a third-party logistics provider (3PL) was blocked over a €6 million inventory loss claim that Amazon's account manager intended to raise against the provider for FY2021. The 3PL rejected approximately 50% of the disputed amount. Manuel was brought in as BI Manager and inventory quality SME and quickly formed the view that the largest portion of the claim was based on "virtual" losses — not genuine physical inventory losses — caused by a systems integration gap that Amazon itself had introduced when migrating the 3PL to its own externally deployed environment.

**Task:** Use BI expertise to reach a data-driven resolution that was fair to both parties, protect a commercial relationship worth over €20 million per year, and ensure Amazon was not claiming compensation for losses it had itself caused.

**Action:** Manuel required the 3PL to submit upfront, for every disputed transaction, their explanation for why they did not acknowledge the loss. He organised and led a joint deep-dive workshop with the provider, grouping the most recurrent justification types to identify the single cluster that accounted for approximately 50% of the disputed value. In that deep dive, he and the 3PL team established that these "losses" were a direct consequence of Amazon's own migration to a new WMS environment: the new system blocked warehouse staff from "unreceiving" inventory when quantities were entered in excess, forcing the system to mark the excess as "lost" — when no physical inventory had actually disappeared. Manuel concluded this use case was unfair to claim. After the workshop he organised an internal alignment call with the account manager and her management chain, escalated to regional ops, procurement, and finance leaders, and requested a formal legal assessment. Legal confirmed the claim was not supported under current contract terms. He also proposed a future mitigation plan: a new "receive-accuracy" KPI to be included in future contracts, and a process to claim refunds from inventory vendors — not from the 3PL — for overpayments caused by the system gap.

**Result:** The commercial renewal was unblocked. The claim amount was reduced from €6 million to €3 million by dropping the unfair use case. The business relationship of €20+ million per year was preserved. A legal backing statement was obtained and new contract KPIs and processes were established to prevent similar disputes.

---

## Building a Long-Term Transportation Loads Forecast When the Tech Team Said It Was Too Hard

**Company:** Amazon | **Role:** Senior Analytics Manager, Transportation Capacity Planning | **Year:** ~2024 | **Skills:** forecasting, entrepreneurial drive, prototyping, stakeholder influence, ML/statistical modelling

**Situation:** The Supply Chain Transportation planning team needed a rolling 52-week forecast of truck loads — covering all flows (outbound, sortable, wholesale, relocation, air freight, third-party) — to support an approximately $80 million trailer CAPEX procurement decision and an $18 million per year savings opportunity. A request had been filed with the science and technology organisation, but they assessed the effort as too large and declined. Manuel believed a simpler manual model could deliver sufficient accuracy and had already developed a conceptual approach in anticipation of this outcome.

**Task:** Deliver a 52-week loads forecast with week-flow-domicile granularity in approximately 1.5 months, in time for the CAPEX allocation decision. The model needed to cover ~130 domiciles, SET Y/N granularity, and 7 transportation flows.

**Action:** With an analyst assigned to support him, Manuel defined the conceptual approach: model each transportation flow individually, using long-term fulfillment-centre ship plans as the starting point rather than short-term marketplace demand signals (which would degrade rapidly at long horizons). The largest flows (wholesale, relocation) were parametrised against outbound forecast volumes, with peak-week timing shifts applied. Smaller flows were modelled using observed historical shares and enriched with insights from the respective business teams. He designed a method to split week-country-flow forecasts into individual domiciles using historical distribution shares, corrected for capacity constraints in past actuals. He performed a full backtest on 2024 actuals and benchmarked the manual model's accuracy against a recently built in-house machine learning model (using Prophet) run by the planning team.

**Result:** The forecast was delivered on time: 50,000 entries, 3.5 million truckloads projected, 38-week outlook across 7 flows. The customer team chose to rely on Manuel's manual model over the ML model — not because it was more accurate on average, but because its logic was transparent and errors could be understood and corrected. The project had an entitlement of $13 million per year in savings from rightsizing Amazon-managed trailer capacity and reducing premium costs for last-minute rentals, plus approximately $50 million in CAPEX investment guidance.

---

## Launching Multi-Item Shipping at Live 3PL Warehouses for the First Time

**Company:** Amazon | **Role:** Program Manager, EU External Fulfillment | **Year:** ~2021–2022 | **Skills:** program management, cross-functional coordination, change management, scalability design, entrepreneurial ownership

**Situation:** Amazon's EU External Fulfillment network relied on third-party logistics (3PL) providers that could only ship orders containing a single item per package. When a customer order contained multiple units of the same product, each unit was shipped separately, creating embarrassing multi-parcel deliveries that appeared in social media and national press, generated poor customer experience, cost significantly more in packaging and transportation, and created unnecessary environmental waste. Amazon's own fulfillment centres already had this "multi-item shipping" (multis) capability. No one had ever enabled it at a live 3PL warehouse.

**Task:** Manuel proactively requested the project from his manager, understanding the large financial and CX entitlement. He was responsible for the full programme: building the business case, getting approval, designing the implementation, managing the pilot, and creating a rollout model that could scale without him personally attending every site.

**Action:** He built a comprehensive financial model covering transportation cost savings, process productivity impact, and packaging (shipping supplies) savings to calculate the net end-to-end benefit per site. He identified and resolved all cross-functional dependencies — finance, procurement, technical programme management, and the 3PL IT teams — to reach financial and implementation approval. For the pilot he selected a single provider with fast, flexible IT systems and a high site count (IDL). He personally drove the end-to-end pilot implementation at the XDEQ site in Germany: internal system configuration (FOS, TRB), WMS integration validation, rebin-wall area definition, operational process design and testing, equipment quantification, associate training, volume ramp-up plan, quality monitoring, and contingency handling for issues like pick-short handling on multi-item orders. He ran the pilot at zero capital expenditure by borrowing rebin equipment from Amazon's own fulfillment centres, eliminating procurement lead time. After learning everything from the first go-live, he documented it all into a playbook covering methodology, milestones, and the specific failure modes to watch for, then structured a scalable rollout model where he served as remote SME and each site manager owned their own deployment, rather than Manuel attending every site.

**Result:** The programme was a first-ever success. It was rolled out to 6 sites rapidly and became the default for new 3PL contracts. In 2022 alone, 3 million units were shipped in multi-item packages, saving approximately 1.5 million boxes in packaging and $10 million in transportation cost. Operations at existing sites were never disrupted during deployment.

---

## Rebuilding the BI Infrastructure for a 400-Person EU Operations Organisation

**Company:** Amazon | **Role:** BI Manager, EU External Fulfillment | **Year:** ~2020–2021 | **Skills:** BI engineering, data architecture, process improvement, change management, metrics design

**Situation:** Amazon's EU External Fulfillment organisation had grown to approximately 400 staff across 185 active nodes (3PL warehouses, pickup points, van fleets). The data infrastructure supporting this organisation was fragmented: reports used different metrics definitions, ran on multiple platforms (Excel, SharePoint, Tableau, PDF, QuickSight), had individual query pipelines per report creating constant misalignment, and were supported by an ad hoc email- and Slack-based helpdesk system. The BI team spent 80% of its time on maintenance and troubleshooting, leaving only 20% for new development.

**Task:** Redesign the BI infrastructure to achieve: a single source of truth for all operational reporting, a scalable architecture that could absorb the organisation's rapid growth, and a dramatically reduced maintenance burden — freeing the team to develop new metrics rather than fight fires.

**Action:** Manuel migrated the entire reporting stack from SharePoint to Amazon QuickSight, replacing individual-per-node query jobs with two aligned centralised pipelines (KPI overview and deep-dive). He modified the pipeline logic so new nodes were marked "active" by default and appeared in reports automatically, eliminating manual intervention for network changes. He integrated the SSP compliance deck into the weekly business review, incorporated DEA root-cause buckets aligned with company-wide definitions (Perfect Mile, Operations Intelligence), and aligned the late-slam metric calculation with the company standard across all relevant reporting surfaces. He built a structured ticketing-based support system with defined tenets, FAQ documentation, and a self-service library of available metrics and data field definitions. He automated MBR data preparation for concessions, DEA, and IRDR metrics, saving approximately 6 hours per month. He also drove full integration of the EF organisation into Amazon's Stay Clean and Minerva operational analysis tools, including cross-functional development coordination, change management, and training for hundreds of users.

**Result:** The team's time ratio flipped from 20% development / 80% maintenance to 80% development / 20% maintenance. This unlocked the bandwidth to develop new key operational metrics that drove significant improvements: DEA-EF improved from 300 to 90 basis points, scan compliance (SSP) improved from 75% to over 95%, and concessions fell from 12,000 to 9,000 DPMO. The data infrastructure was rebuilt to scale with the organisation's growth and remained robust throughout Amazon's EU External Fulfillment network expansion.

---

## Recovering Quality at a Persistently Underperforming 3PL Warehouse

**Company:** Amazon | **Role:** Inventory Quality and BI Manager, EU External Fulfillment | **Year:** ~2021 | **Skills:** operational leadership, diagnostics, recovery planning, stakeholder positioning, influence without authority

**Situation:** A 3PL site (XDEQ) had been underperforming on quality metrics for six months since its launch: pick-short rate (PS) at 30,000 DPMO and IRDR at 10,000 DPMO against EU benchmarks of 1,500 and 5,000 respectively. Repeated escalations from Amazon's side produced no improvement. Then the PS rate spiked to 120,000 DPMO, creating a critical situation. Manuel was sent onsite alone to secure a recovery plan, representing Amazon to a 3PL site in crisis: the 3PL had just replaced its stock manager following the prior manager's dismissal, its site leader was an interim, and Amazon's own account manager for that site was newly hired.

**Task:** Develop and drive a credible quality recovery plan while establishing authority and credibility quickly in a first-ever interaction with that provider, under high pressure from Amazon's leadership and during peak preparations.

**Action:** Manuel's first step was positioning: he met the interim site leader directly, shared that this site ranked as the worst in the EU benchmark, and made clear that the situation was being tracked at Amazon VP level — establishing the seriousness without being adversarial. He simultaneously built trust with the new stock manager by framing the engagement as a common-goal partnership rather than an audit. He then led a full operational diagnostic: physical inspection of all inventory areas, audit of the pick-short process revealing systematic deviations from the Amazon operations manual, identification of root causes including disorganised floor pallet locations, absence of amnesty and damage container routines, and lack of permission controls on pick-short logging. He ordered an immediate full operations stop (inbound and outbound — a first-ever at that site) to conduct a full wall-to-wall inventory count, with pictures of conditions shared internally to justify the decision. He redesigned the PS operational process end-to-end, introduced IT-enforced permission controls for pick-short events, mandated exhaustion of alternative pick locations before logging a short, and set up research routines and a worst-offender reporting dashboard. He established a joint progress tracking mechanism shared with senior management from both Amazon and the 3PL, reviewing updates with the 3PL stock lead before each circulation.

**Result:** Pick-short rate recovered from 120,000 DPMO to pre-spike levels within 4 weeks. Within 8 weeks it reached 10,000 DPMO — the best result the site had ever recorded. By October 2021 it stabilised at or below 3,000 DPMO, including through the Q4 peak. The new inventory management standards (amnesty/damage processes, physical separation of pallet locations) and the redesigned pick-short process were subsequently adopted at three other new sites launched by the same 3PL provider, none of which experienced inventory quality issues post-launch.

---

## Proving There Was No Real Problem: ISR Flow-Mix Analysis

**Company:** Amazon | **Role:** Inventory Quality Manager, EU External Fulfillment | **Year:** ~2021 | **Skills:** data analysis, intellectual courage, influencing senior management, forensic root-cause analysis

**Situation:** Amazon launched a EU working group to address vendor experience pain points, and Amazon's EU External Fulfillment organisation appeared as the worst offender on the Invalid Shortages Rate (ISR) metric: 5.5% vs. 3.3% for the comparable fulfilment-centre benchmark, on $700 million in quarterly invoice value — implying a $15 million gap in ambition. Manuel's director was called out and tasked Manuel with researching the root cause and designing an improvement plan, with regular reporting up to EU VP level. Manuel had no prior knowledge of the ISR metric and no existing data access.

**Task:** Diagnose the cause of EF's apparent ISR underperformance and produce an improvement plan in time for the next senior business review cycle.

**Action:** Manuel was transparent with his management chain and the EU working group that he was starting from zero and needed time for proper diagnosis before proposing actions, buying himself space for rigorous analysis. He engaged with the BI Finance team to understand the metric's calculation logic and data sources, ultimately building his own self-sufficient reporting capability. Through deep analysis of the data, he established that the performance gap was entirely explained by three structural differences in EF's inbound flow mix compared to fulfillment centres: a higher proportion of direct-import (DI) flows, a higher rate of inbound volume redirections, and a higher proportion of each-level (vs. pallet-level) receiving processes. These were inherent characteristics of the 3PL network's inventory profile, not operational failures. He documented this "flow-mix" hypothesis carefully and brought it to his management chain with clear data.

**Result:** Initial pushback from senior management who expected "improvement initiatives" rather than a finding of "no real problem." Manuel maintained his data-backed position and over time the EU working group stopped targeting EF's ISR, shifted their attention to the OCEAN fulfilment flow which was the true driver, and stopped requesting EF's inputs to the improvement plan. Manuel successfully navigated genuine ambiguity, resisted pressure to fabricate improvement initiatives for a problem that did not exist, and protected the organisation's credibility through rigorous data-driven analysis.

---

## Designing the EU 3PL IRDR Audit Programme (MIGA)

**Company:** Amazon | **Role:** Inventory Quality Manager, EU External Fulfillment | **Year:** ~2021 | **Skills:** programme management, process design, influencing across organisations, SOP development, EU-scale stakeholder engagement

**Situation:** IRDR (Inventory Record Discrepancy Rate) data reported by Amazon's 3PL partners in Europe showed suspicious patterns: suspiciously stable performance over time, weak correlation with pick-short rates, significantly lower rates than equivalent Amazon-owned fulfilment centres, and near-constant values hovering just below contractual targets. Manuel's hypothesis was that 3PL sites were not conducting the IRDR audit count process as specified in Amazon's Operations Manual, and that the reported numbers were therefore unreliable.

**Task:** Develop and implement a programme to bring EU 3PL operators into compliance with Amazon's IRDR count methodology, and build the organisational infrastructure to sustain it.

**Action:** Manuel designed and personally conducted thorough onsite IRDR process audits at multiple 3PL sites, which confirmed his hypothesis: strong deviations from the Operations Manual specification were standard, and there was no consistent understanding among 3PL teams of what counted as an IRDR defect. Using these findings, he developed a comprehensive Standard Operating Procedure (SOP) for 3PL managers to conduct their own regular IRDR audits. He secured approval from EF regional leaders and alignment from the senior ICQA Operations Manager, then autonomously engaged all EU 3PL managers individually to present the programme and recruit partners to test and refine the SOP before broader rollout. He also identified the opportunity to embed IRDR reporting requirements into the 3PL Operations Manual (a contractual document), ensuring minimum levels of dive-deep research and historical defect documentation became a contractual obligation. He convinced EF leadership to keep the programme under 3PL managers (rather than Amazon's ICQA audit team) due to the different WMS tooling at 3PL sites and the scalability limitations of a centralised audit approach.

**Result:** 25 different 3PL sites were audited using the new SOP, conducted by 15 different 3PL managers. IRDR defects reported increased by 50% in H1 2021 vs. the prior six months (from 2,800 to 4,200 DPMO), reflecting more accurate measurement rather than a deterioration in operations. A minimum-cadence routine of two audits per year was established. Six proposed changes to the IRDR count process description were incorporated into the next Operations Manual release.

---

## Integrating the New Concessions Metric Logic Across EU External Fulfillment

**Company:** Amazon | **Role:** BI Manager, EU External Fulfillment | **Year:** ~2020–2021 | **Skills:** ownership, metrics design, analytics, change management, training delivery

**Situation:** Amazon's operations analytics function was releasing a fundamentally redesigned concessions logic (the measure of delivery defect attribution and classification). Manuel became aware of this upcoming change through quality circles and immediately recognised that it represented a significant opportunity for EU External Fulfillment: the new logic would produce more granular, actionable root-cause buckets, but would require a complete migration of all EF reporting and a recalibration of all performance targets.

**Task:** Own the full migration of EF's concessions reporting to the new logic — including data pipeline changes, metric recalibration, target-setting, change communication, and training for all of EF — before the change was adopted by the wider Amazon fulfillment network.

**Action:** Manuel managed every step independently: incorporating new data tables into the EF cluster, reverse-engineering the new logic to understand its meaning and impact, migrating all five concessions reports (WBR QuickSight, CF WBR PDF, external automated email, and dive-deep Excel files), and communicating the change across the organisation. He studied the quantitative impact of the logic change on existing metric values and proposed new, adjusted targets for each business unit and building group, calibrated to account for the definitional shift. He aligned these new targets with all 3PL and van-fleet leaders before publishing them. He then delivered three training sessions for the full EF organisation covering the new root-cause taxonomy, the target-setting methodology, and the Minerva tool for operational analysis.

**Result:** All five concessions reports were seamlessly migrated in February 2021 — before Amazon's own fulfillment-centre organisation had completed its own migration. Adjusted targets were aligned with all EF leaders and, for the first time, each site was measured against a target specific to its building type. The enhanced visibility contributed to a -32% DPMO improvement in EF concessions in H1 2021 and a partial closure of the historical performance gap with Amazon fulfillment centres (-1,014 DPMO for network-sortable 3PL vs. network-sortable FC in H1 2021).

---

## Building Scalable BI Data Infrastructure for a 185-Node Operations Network

**Company:** Amazon | **Role:** BI Manager, EU External Fulfillment | **Year:** ~2020–2021 | **Skills:** data architecture, BI engineering, systems thinking, cross-functional collaboration, scalability design

**Situation:** Amazon's EU External Fulfillment organisation had grown from ~125 to ~185 active nodes in one year and employed approximately 400 staff across L1–L7. All of these nodes and operations teams depended on centrally managed data resources for their weekly, monthly, and quarterly business reviews. The existing data infrastructure was fragile: individual query jobs per report, misaligned metric definitions across reports, a SharePoint-based distribution system prone to publishing failures, and a reactive support model based on ad hoc email and Slack requests.

**Task:** Redesign the data infrastructure to serve the full EF organisation reliably, scale automatically with network growth, reduce metric misalignment, minimise manual intervention, and free the BI team from reactive maintenance to focus on new metric development.

**Action:** Manuel migrated all node-level operational data delivery from SharePoint to Amazon QuickSight, replacing many individual node-specific query jobs with two centralised pipelines (KPI and deep-dive), ensuring all reports drew from the same source of truth as the official WBR. He modified the pipeline logic so all newly created nodes appeared in reports as "active" by default, eliminating the recurring manual work of adding new sites. He built a structured SIM (ticket) queue with defined tenets, supported use cases, and a self-service FAQ, replacing the Slack/email support model. He automated data preparation for the monthly business review (concessions, DEA, IRDR), reducing monthly preparation time by approximately 6 hours. He coordinated with Amazon's centralised development teams to integrate EF into Stay Clean and Minerva (internal operational analysis platforms), managing the full request lifecycle, cross-team testing, and user rollout and training. He incorporated and aligned new metrics including DEA root causes, SSP scan compliance, and PSR (package scan rate), along with adjustments to align EF's late-slam methodology with the company standard.

**Result:** The data infrastructure became resilient, scalable, and self-maintaining for routine network changes. The BI team's time allocation shifted from 80% maintenance to 80% new development. The new metrics unlocked major operational improvements: DEA-EF (300 to 90bps), scan compliance / SSP (75% to 95%+), and concessions (12,000 to 9,000 DPMO). The redesigned infrastructure supported the EF organisation's continued growth without requiring proportional growth in the BI team.

---

## Delivering a Capacity Planning Tool for Six Pharma Plants in Five Weeks

**Company:** McKinsey & Company | **Client:** a global pharmaceutical manufacturer | **Year:** February 2023 | **Skills:** consulting, tool design, capacity modelling, client management, rapid delivery

**Situation:** Manuel was placed on a short McKinsey engagement to help a global pharmaceutical manufacturer that was behind on its annual production target by approximately 80 million units (out of a ~1 billion unit goal). The client needed a standardised capacity planning methodology across all six of its manufacturing plants and 13 production lines to support data-driven decisions in business reviews — covering both production and release capacity, and including quality-signal constraints. There was no consistent methodology across plants, and existing tools were complex and not designed for scenario simulation. Manuel was working as a team of two: his manager handled quality-signal governance and meeting facilitation; Manuel owned everything related to methodology design, tool build, documentation, training, and handover.

**Task:** Design, build, document, and hand over a capacity planning tool in five weeks — covering six plants, thirteen lines, scenario simulation capability, and integration with quality-constraint signals.

**Action:** Manuel started by interviewing all six plant capacity planners to understand the current state, existing tools, and real pain points. He inherited a sophisticated but unwieldy existing model: he invested time to fully understand it, then significantly simplified it — removing redundant parameters, adding product-mix indexation, feeding historical actuals automatically, and building a simulation layer with buttons that dynamically showed end-of-year gap scenarios (OEE assumptions, line speed, downtime, release lead times). He raised data requirements with the client's BI team for upstream actuals feeds. He maintained weekly check-ins with each capacity planner — using these as both progress updates and as a mechanism to keep stakeholders engaged and validate his methodology as he built it.

**Result:** The tool was completed in six weeks (one week over the initial target), iterated twice with the client, and produced in both Excel and Tableau interfaces. The client's BI team described it as the best-ever consulting handover they had received. All six plants operated with a consistent methodology. Quality signals blocking capacity were integrated into the planning model. The tool delivered dynamic, real-time simulation of end-of-year production gap scenarios. By the engagement close, the client had already used the tool to clear 15 million units of capacity through deprioritisation of compliance projects.

---

## Discovering a Systematic Scheduling Bug Causing Chronic Truck Shortages

**Company:** Amazon | **Role:** Analytics Manager, Transportation Capacity Planning (WHT flows) | **Year:** ~2023 | **Skills:** forensic root-cause analysis, scheduling logic, quantification, cross-functional problem-solving

**Situation:** A chronic escalation pattern had developed in Amazon's Inbound Cross-Dock (IXD) scheduling: week after week, outbound truck schedules were coming up short, causing yard congestion at IXD sites and requiring expensive emergency "mini-tour" trucks to resolve the backlog. The situation was escalating internally but no one understood the root cause. Manuel was in a newly created role responsible for WHT forecasting and scheduling, and this was his first time owning this process.

**Task:** Identify what was causing the rolling truck shortages in the outbound IXD schedules and find a path to fix it.

**Action:** Manuel began a systematic audit of the scheduling process at route and truck-ID level, independently tracking forecast accuracy at the package level and truck-quantity accuracy across the scheduling refresh cycle. He partnered with the most-affected site (in the UK) and set up weekly scheduling reviews to compare his own pre-publication schedule audit with the site's experience. He noticed an immediate gap: schedules he had validated as correct were still causing dissatisfaction at the site. Digging into specific examples, he traced the discrepancy to the timing of consumption: by the end of week W-1, sites had already loaded trucks scheduled for the following week's departures, filling a significant portion of scheduled capacity with the current week's volume — leaving insufficient capacity for the next week's forecast volume. The root cause was a logic error in the scheduling refresh process: the Thursday-Friday refresh that updated schedules for the following week did not account for trucks already consumed (loaded) earlier in the current week. It therefore consistently underestimated the net new trucks required, creating a structurally short schedule every single week.

**Result:** By identifying and correcting for the bug manually, approximately 150–200 additional trucks per week were added to the standard W-1 scheduling process, stopping the chronic shortages. Across a full year this represented ~10,000 additional correctly scheduled trucks. Accounting for the premium cost of emergency mini-tours that had been substituting for these shortfalls, the fix was worth approximately $1 million per year. A stop-gap manual correction was implemented immediately; a permanent tech fix was filed with the product owner team.

---

## Cutting WHT Truck Fill-Rate Planning Error in Half

**Company:** Amazon | **Role:** Analytics Manager, Transportation Capacity Planning (WHT flows) | **Year:** ~2023 | **Skills:** forecasting accuracy, iterative improvement, process automation, S&OP engagement

**Situation:** Amazon's Wholesale Trunk (WHT) transportation flow had an add/cancel rate on truck schedules of approximately 30% — significantly higher than the outbound benchmark of ~20% — driven largely by poor truck fill-rate (TFR) planning accuracy. The TFR WAPE (Weighted Absolute Percentage Error) stood at 35%. There was almost no existing infrastructure for WHT analytics: no dashboards, no systematic tracking, no established methodology. The WHT forecasting and scheduling function was historically a low-investment area that the company was only beginning to build out.

**Task:** Understand the root causes of poor TFR accuracy and reduce it meaningfully.

**Action:** Manuel started by building his own analytical infrastructure from scratch — writing SQL queries, building Excel analyses, and creating QuickSight/Tableau dashboards to measure forecast accuracy and TFR accuracy independently. He initiated improvement efforts on two parallel workstreams: improving the upstream package forecast signal (engaging with S&OP planning), and improving the TFR calculation itself through iterative experimentation on fill-rate assumptions. On the S&OP side, he identified systemic biases (Sunday forecasts for specific site subsets, inconsistent node-day-of-week treatment). On the TFR methodology, he joined a weekly cross-site forum where operations teams shared their planned lane configurations for the following week (full-load vs. palletised lanes), using this as a real-time calibration signal. He experimented iteratively with assumptions: varying the lookback window on historical actuals for fill-rate estimation, and applying reduction factors to full-load lanes to account for periods where palletisation was required even on nominally full-load lanes. He ultimately discovered that incorporating the weekly site feedback added less incremental accuracy than maintaining the prior-week actuals as a stable base, allowing the process to be fully automated.

**Result:** TFR WAPE improved from 35% to 17% — a 50% reduction in planning error. The add/cancel rate fell by approximately 500 basis points (from 30% to 25%), closing half the gap to the outbound benchmark. The financial value of the 5% reduction in truck schedule variability, at ~7,000 WHT trucks per week, equated to approximately $1.8 million per year in avoided add/cancel premium and cancellation fees. The process was fully automated, requiring no ongoing manual supervision beyond execution.

---

## Surfacing an Undisclosed S&OP Practice Costing Amazon $7M/Year in Transport

**Company:** Amazon | **Role:** Analytics Manager, Transportation Capacity Planning (IXD flows) | **Year:** ~2023 | **Skills:** data discovery, business case development, cross-functional leadership, escalation, IBET engagement

**Situation:** Amazon's IXD (Inbound Cross-Dock) transportation scheduling was running a 30% add/cancel rate — significantly above the outbound benchmark of 20%. Forecast accuracy was poor, but Manuel believed there were structural causes beyond pure forecast error. In exploring the data, he discovered that Amazon's S&OP network planning team (IBET — Inbound Balancing & Execution Team) was regularly making intraweek changes to the destination plan — redirecting inbound volume from one site to another mid-week — without any awareness of or accounting for the transport execution disruption this caused. These changes affected approximately 10% of total weekly IXD volume.

**Task:** Quantify the impact of these undisclosed intraweek volume changes on transport operations, build a business case to request a reduction in this planning lever, and drive cross-functional action.

**Action:** Manuel obtained access to IBET data systems, built a new report from scratch to measure the magnitude and frequency of intraweek volume changes, and quantified the resulting transportation disruption (additional truck add/cancel requests and mini-tours). He prepared a structured business case demonstrating €7 million in annual transportation entitlement from reducing IXD intraweek changes. He created and coordinated a cross-functional working group with Amazon's Expert ACES team and presented the business case directly to IBET EU leadership. To avoid simply redirecting blame, he also engaged IBET to understand the legitimate business motivations for intraweek changes (managing overtime/idle time, inbound balancing), and structured his proposal to accommodate their operational constraints while minimising transport impact.

**Result:** The business case was accepted by IBET EU leadership. In the UK (the pilot geography), intraweek volume changes were reduced by 50% relative to the baseline — from approximately 10% to 5% of weekly volume — reaching the lowest weekly IWC percentage on record. This reduction in the UK alone translated to approximately 300 basis points less transport add/cancellations (from ~30%), saving approximately 7,800 truck schedule changes per year. Adoption by the wider EU network was pending at the time of writing.

---

## Extending the Transportation Forecast Horizon to 12 Weeks for Labor Planning

**Company:** Amazon | **Role:** Analytics Manager, Transportation Capacity Planning | **Year:** ~2024 | **Skills:** forecasting, data engineering, stakeholder alignment, process integration

**Situation:** Amazon's labor planning teams needed a full 12-week demand outlook across all transportation flows to allocate staffing capacity. Three flows were significantly under-served: WHT had only a 3-week horizon, BLP only 6 weeks (and its existing model was so inaccurate that manual overrides were routinely beating it), and LTL was entirely absent from the official forecast — managed offline in Excel by individuals. The remaining flows (SWA, AFN, CRET) were already at 12 weeks.

**Task:** Achieve full 12-week coverage for all flows and integrate LTL formally into the published forecast, delivering improved accuracy and operational consolidation.

**Action:** For BLP, Manuel evaluated the existing model, judged it too inaccurate to extend, and built a simplified manual modelling approach by independently consulting finance partners and his forecast manager. For LTL, he located and understood the existing offline Excel process, its cadence, and its owners, then coordinated with the data engineering team to feed LTL actuals into the main reporting infrastructure as a prerequisite for integration. He established a weekly routine to incorporate LTL into the official forecast publication and secured internal alignment that this interim manual approach would remain in place until a backend automation became available (with no committed ETA from the tech team). For WHT, he identified that the horizon limitation was driven by a constraint on lane topology visibility: the forecast model had been treating topology as dynamic when in fact major updates only occurred quarterly. Assuming topology constant (with quarterly correction) unblocked the 12-week extension.

**Result:** Full 12-week coverage was achieved across all M3 forecast flows. The labour planning function for 800,000 planned labor hours per week in France alone gained visibility into a demand signal worth approximately $28 million per week. A conservative 5–10% accuracy improvement from the extended horizon would translate to $1.5–3 million per year in reduced overtime, voluntary time off, and over/under-capacity costs. The change also delivered qualitative benefits: consolidated forecast signals and standardisation of the LTL and BLP flows against the methodology already used for outbound and air freight.

---
