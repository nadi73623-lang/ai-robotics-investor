"""Emerging Markets Discovery radar.

This module is deliberately a discovery/watchlist layer, not a BUY signal engine.
It combines structural market hypotheses with a seed universe of listed issuers.
All company rows are candidates requiring current listing, liquidity, filings and
business-exposure verification before fundamental or technical scoring.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import re

VERSION = "0.1.0"

MARKETS = [
    {
        "id": "quantum",
        "name": "Quantum technologies",
        "priority": "high",
        "horizon": "long",
        "submarkets": ["quantum computing", "quantum sensing", "quantum communication", "post-quantum security", "cryogenics and control systems"],
        "structural_theses": [
            "error correction and logical-qubit progress",
            "paid cloud access and repeat enterprise workloads",
            "government procurement and national quantum programmes",
            "quantum-safe cryptography migration",
            "commercial sensing/navigation deployments",
        ],
        "commercial_evidence": ["paid production workload", "repeat customer contract", "independently benchmarked system", "regulatory or government procurement"],
        "risks": ["technical scaling", "cash burn and dilution", "uncertain useful advantage", "long commercialization cycle"],
    },
    {
        "id": "silicon_photonics",
        "name": "Silicon photonics and optical interconnect",
        "priority": "very_high",
        "horizon": "near_to_medium",
        "submarkets": ["co-packaged optics", "optical I/O", "laser sources", "transceivers", "photonics packaging and test"],
        "structural_theses": ["AI cluster bandwidth and power bottlenecks", "copper reach and energy limits", "hyperscaler optical deployment", "manufacturing yield and packaging capacity"],
        "commercial_evidence": ["volume qualification", "production design win", "repeat shipments", "customer capex translated into supplier revenue"],
        "risks": ["design-win to revenue delay", "customer concentration", "yield and capex intensity", "technology substitution"],
    },
    {
        "id": "advanced_nuclear",
        "name": "Advanced nuclear and SMR",
        "priority": "high",
        "horizon": "medium_to_long",
        "submarkets": ["SMR", "microreactors", "fuel enrichment and conversion", "reactor components", "nuclear services"],
        "structural_theses": ["data-centre baseload demand", "grid reliability and decarbonisation", "licensing milestones", "fuel-cycle capacity constraints"],
        "commercial_evidence": ["final investment decision", "construction or fuel contract", "regulatory licence", "binding power purchase agreement"],
        "risks": ["licensing and construction delays", "project finance", "fuel availability", "cost overruns"],
    },
    {
        "id": "next_gen_batteries",
        "name": "Next-generation batteries and storage",
        "priority": "high",
        "horizon": "medium",
        "submarkets": ["solid-state", "sodium-ion", "silicon anodes", "lithium-metal", "long-duration storage", "battery recycling"],
        "structural_theses": ["cell cost and energy-density improvements", "grid storage procurement", "OEM qualification", "manufacturing yield and scale-up"],
        "commercial_evidence": ["validated cell performance", "customer qualification", "commercial production yield", "repeat orders and gross margin"],
        "risks": ["pilot-to-factory execution", "capital intensity", "commodity cycles", "warranty and degradation"],
    },
    {
        "id": "physical_ai",
        "name": "Physical AI and humanoid robotics",
        "priority": "very_high",
        "horizon": "near_to_long",
        "submarkets": ["humanoids", "robot actuators and reducers", "machine vision", "robotics software", "warehouse and industrial automation"],
        "structural_theses": ["labour scarcity and wage inflation", "falling inference and sensor costs", "real-world deployment hours", "robot fleet utilization"],
        "commercial_evidence": ["paid deployment", "utilization and uptime", "repeat fleet expansion", "service and consumables revenue"],
        "risks": ["pilot theatre", "unit economics", "safety and reliability", "customer concentration"],
    },
    {
        "id": "advanced_materials",
        "name": "Advanced materials and semiconductor manufacturing",
        "priority": "high",
        "horizon": "near_to_medium",
        "submarkets": ["advanced packaging", "chiplets", "SiC and GaN", "rare-earth processing", "high-purity materials", "semiconductor process control"],
        "structural_theses": ["leading-edge packaging constraints", "power efficiency requirements", "reshoring and supply-chain security", "materials qualification cycles"],
        "commercial_evidence": ["qualified supplier status", "capacity utilization", "multi-year supply agreement", "volume shipments"],
        "risks": ["cyclicality", "customer concentration", "capex and yield", "geopolitical restrictions"],
    },
    {
        "id": "space_infrastructure",
        "name": "Space infrastructure",
        "priority": "medium_high",
        "horizon": "medium",
        "submarkets": ["launch and reusable systems", "satellite buses", "direct-to-device", "Earth observation", "space components and services"],
        "structural_theses": ["lower launch costs", "defence and sovereign demand", "recurring satellite connectivity", "commercial geospatial analytics"],
        "commercial_evidence": ["operational constellation", "recurring service revenue", "launch cadence", "funded backlog conversion"],
        "risks": ["capital intensity", "launch failure", "financing and dilution", "backlog cancellation"],
    },
    {
        "id": "neurotechnology",
        "name": "Brain-computer interfaces and neurotechnology",
        "priority": "medium",
        "horizon": "long",
        "submarkets": ["implantable BCI", "neural recording and stimulation", "surgical navigation", "non-invasive neurotechnology"],
        "structural_theses": ["clinical trial milestones", "regulatory approvals", "reimbursement pathways", "clinical workflow adoption"],
        "commercial_evidence": ["regulatory clearance", "peer-reviewed human data", "hospital adoption", "reimbursement and recurring consumables"],
        "risks": ["clinical and regulatory failure", "reimbursement", "small addressable patient cohorts", "cash burn"],
    },
]

# Listing identifiers are seeds, not verified live security master records.
# Exchange suffixes are explicit where needed; never silently treat these as US ADRs.
COMPANIES = [
    # Quantum computing, sensing and security
    ("IONQ", "IonQ", "quantum", "US", "trapped-ion quantum computing"),
    ("RGTI", "Rigetti Computing", "quantum", "US", "superconducting quantum computing"),
    ("QBTS", "D-Wave Quantum", "quantum", "US", "quantum annealing"),
    ("QUBT", "Quantum Computing Inc", "quantum", "US", "photonic quantum systems"),
    ("INFQ", "Infleqtion", "quantum", "US", "neutral-atom quantum and sensing"),
    ("XNDU", "Xanadu", "quantum", "CA/US", "photonic quantum computing"),
    ("ARQQ", "Arqit Quantum", "quantum", "UK/US", "post-quantum security"),
    ("LAES", "SEALSQ", "quantum", "CH/US", "quantum-resistant semiconductor security"),
    # Silicon photonics / optical interconnect
    ("COHR", "Coherent", "silicon_photonics", "US", "lasers and optical components"),
    ("LITE", "Lumentum", "silicon_photonics", "US", "optical components"),
    ("AAOI", "Applied Optoelectronics", "silicon_photonics", "US", "optical transceivers"),
    ("POET", "POET Technologies", "silicon_photonics", "CA/US", "photonic integration"),
    ("GLW", "Corning", "silicon_photonics", "US", "optical fibre and connectivity"),
    ("FN", "Fabrinet", "silicon_photonics", "US", "optical manufacturing"),
    ("CRDO", "Credo Technology", "silicon_photonics", "US", "high-speed connectivity"),
    # Advanced nuclear and fuel chain
    ("OKLO", "Oklo", "advanced_nuclear", "US", "advanced fission"),
    ("SMR", "NuScale Power", "advanced_nuclear", "US", "small modular reactors"),
    ("NNE", "Nano Nuclear Energy", "advanced_nuclear", "US", "microreactors"),
    ("LEU", "Centrus Energy", "advanced_nuclear", "US", "uranium enrichment"),
    ("BWXT", "BWX Technologies", "advanced_nuclear", "US", "nuclear components and services"),
    ("CCJ", "Cameco", "advanced_nuclear", "CA/US", "uranium and fuel services"),
    ("GEV", "GE Vernova", "advanced_nuclear", "US", "grid and power systems"),
    # Batteries and storage
    ("QS", "QuantumScape", "next_gen_batteries", "US", "solid-state battery"),
    ("SLDP", "Solid Power", "next_gen_batteries", "US", "solid electrolyte"),
    ("ENVX", "Enovix", "next_gen_batteries", "US", "silicon-anode batteries"),
    ("AMPX", "Amprius Technologies", "next_gen_batteries", "US", "silicon-anode batteries"),
    ("SES", "SES AI", "next_gen_batteries", "US", "lithium-metal battery technology"),
    ("EOSE", "Eos Energy Enterprises", "next_gen_batteries", "US", "zinc-based long-duration storage"),
    ("ALB", "Albemarle", "next_gen_batteries", "US", "lithium materials"),
    # Physical AI / components / deployment
    ("OUST", "Ouster", "physical_ai", "US", "lidar and perception"),
    ("PDYN", "Palladyne AI", "physical_ai", "US", "robotics autonomy software"),
    ("SYM", "Symbotic", "physical_ai", "US", "warehouse robotics"),
    ("TER", "Teradyne", "physical_ai", "US", "industrial and collaborative robotics"),
    ("CGNX", "Cognex", "physical_ai", "US", "machine vision"),
    ("NOVT", "Novanta", "physical_ai", "US", "precision motion and photonics"),
    ("ROK", "Rockwell Automation", "physical_ai", "US", "industrial automation"),
    ("FANUY", "FANUC", "physical_ai", "JP/US OTC", "industrial robotics"),
    # Advanced materials / semiconductor manufacturing
    ("ONTO", "Onto Innovation", "advanced_materials", "US", "advanced packaging metrology"),
    ("AMAT", "Applied Materials", "advanced_materials", "US", "semiconductor equipment"),
    ("LRCX", "Lam Research", "advanced_materials", "US", "semiconductor equipment"),
    ("MP", "MP Materials", "advanced_materials", "US", "rare-earth materials"),
    ("UUUU", "Energy Fuels", "advanced_materials", "US", "rare earths and uranium"),
    ("MPWR", "Monolithic Power Systems", "advanced_materials", "US", "power semiconductors"),
    ("WOLF", "Wolfspeed", "advanced_materials", "US", "silicon carbide"),
    # Space
    ("RKLB", "Rocket Lab", "space_infrastructure", "US", "launch and space systems"),
    ("ASTS", "AST SpaceMobile", "space_infrastructure", "US", "direct-to-device satellites"),
    ("PL", "Planet Labs", "space_infrastructure", "US", "Earth observation"),
    ("RDW", "Redwire", "space_infrastructure", "US", "space infrastructure"),
    ("LUNR", "Intuitive Machines", "space_infrastructure", "US", "lunar and space services"),
    ("BKSY", "BlackSky", "space_infrastructure", "US", "geospatial intelligence"),
    ("IRDM", "Iridium Communications", "space_infrastructure", "US", "satellite communications"),
    # Neurotechnology / BCI listed exposure; diversified issuers are not pure-play BCI
    ("NPCE", "NeuroPace", "neurotechnology", "US", "responsive neurostimulation"),
    ("CLPT", "ClearPoint Neuro", "neurotechnology", "US", "neurosurgical navigation"),
    ("ABT", "Abbott Laboratories", "neurotechnology", "US", "neuromodulation and medical devices"),
    ("MDT", "Medtronic", "neurotechnology", "US", "neuromodulation and medical devices"),
]

def _headline_matches(headline: str, ticker: str, name: str) -> bool:
    text = (headline or "").lower()
    if len(ticker) >= 4 and re.search(r"(?<![a-z0-9])" + re.escape(ticker.lower()) + r"(?![a-z0-9])", text):
        return True
    return name.lower() in text

def build_emerging_markets_radar(articles: list[dict] | None = None) -> dict:
    """Build an honest radar snapshot; absence of news is not evidence of no progress."""
    articles = articles or []
    market_by_id = {m["id"]: dict(m) for m in MARKETS}
    by_market: dict[str, list[dict]] = {m["id"]: [] for m in MARKETS}
    for ticker, name, market_id, exchange, exposure in COMPANIES:
        matched = [a for a in articles if _headline_matches(a.get("title", ""), ticker, name)]
        by_market[market_id].append({
            "ticker": ticker, "name": name, "market_id": market_id,
            "listing_region": exchange, "exposure": exposure,
            "news_mentions": len(matched),
            "news_evidence": matched[:3],
            "listing_status": "seed_requires_security_master_verification",
            "business_exposure_status": "unverified",
            "commercial_stage": "unassessed",
            "fundamental_score": None, "valuation_score": None, "entry_score": None,
            "investment_signal": "WATCHLIST_ONLY",
            "data_gaps": ["current listing and instrument", "latest filings and revenue exposure",
                          "cash runway and dilution", "current valuation", "technical entry"],
        })
    for market_id, rows in by_market.items():
        market = market_by_id[market_id]
        market["candidate_count"] = len(rows)
        market["news_matched_candidates"] = sum(r["news_mentions"] > 0 for r in rows)
        market["companies"] = rows
        market["market_stage"] = "unassessed"
        market["stage_reason"] = "News mentions alone cannot establish market maturity or commercial adoption."
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "structural_theses_plus_seed_universe_and_optional_news_cross_reference",
        "markets": list(market_by_id.values()),
        "coverage_limitations": [
            "Seed list is not a complete global equity universe.",
            "Listing identifiers and business exposure must be checked against current exchange and issuer sources.",
            "News mention counts are attention indicators only, not demand, valuation or investment scores.",
            "No market maturity stage or BUY signal is inferred without independently verified commercial evidence.",
            "Private companies are not included as investable equities; they may be tracked separately as ecosystem signals.",
        ],
        "investment_ranking_available": False,
        "buy_signals_enabled": False,
    }
