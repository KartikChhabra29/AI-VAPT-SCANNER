# scanner_core.py

import nvdlib
import nmap
import json
import sys
from ai_fix import get_fix_recommendations


# -------------------------------------------------
# Detect if scanner is being run by FastAPI backend
# -------------------------------------------------
API_MODE = len(sys.argv) > 1


# -------------------------------------------------
# 1. Run Nmap Scan
# -------------------------------------------------
def scan_target(target_ip: str):
    if not API_MODE:
        print(f"[+] Scanning {target_ip} ...")   # visible only in CLI mode

    scanner = nmap.PortScanner()
    scanner.scan(target_ip, arguments='-sV')
    return scanner


# -------------------------------------------------
# 2. Extract Services
# -------------------------------------------------
def extract_services(nm_scan):
    results = []

    for host in nm_scan.all_hosts():
        for proto in nm_scan[host].all_protocols():
            for port in nm_scan[host][proto]:
                svc = nm_scan[host][proto][port]

                product = svc.get("product")
                version = svc.get("version")

                full_version = f"{product} {version}".strip() if product else None

                results.append({
                    "host": host,
                    "port": port,
                    "service": svc.get("name"),
                    "version": full_version
                })
    return results


# -------------------------------------------------
# 3. Safe CVE Lookup
# -------------------------------------------------
def lookup_cves(query):
    try:
        return list(nvdlib.searchCVE(keywordSearch=query))
    except:
        return []


# -------------------------------------------------
# 4. Convert CVE to clean JSON
# -------------------------------------------------
def clean_cve(c):
    cid = getattr(c, "id", "N/A")

    # Summary
    summary = "No summary"
    try:
        if hasattr(c, "descriptions") and isinstance(c.descriptions, list):
            summary = c.descriptions[0].get("value", "No summary")
    except:
        pass

    # Convert metrics to string
    try:
        cvss = str(c.metrics)
    except:
        cvss = "N/A"

    return {"id": cid, "summary": summary, "cvss": cvss}


# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
if __name__ == "__main__":

    # Use CLI input if no args, else API mode
    target = sys.argv[1] if API_MODE else input("Enter target IP: ")

    nm = scan_target(target)
    services = extract_services(nm)

    report = {"target": target, "services": []}

    # Process CVEs
    for s in services:
        query = s["version"] if s["version"] else s["service"]
        found_cves = lookup_cves(query)

        s["cves"] = [clean_cve(cv) for cv in found_cves]
        report["services"].append(s)

    # AI Fixes
    report["ai_recommendations"] = get_fix_recommendations(report)

    # -------------------------------------------------
    # API MODE: Output ONLY JSON → NO PRINTS, NO PDF
    # -------------------------------------------------
    if API_MODE:
        print(json.dumps(report))
        sys.exit(0)

    # -------------------------------------------------
    # CLI MODE: Human readable + PDF
    # -------------------------------------------------
    print(json.dumps(report, indent=2))

    from pdf_report import make_pdf
    make_pdf(report)

    print("\n[+] Scan complete + PDF generated.\n")
