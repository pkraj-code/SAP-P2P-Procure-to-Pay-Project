"""
p2p_checklist.py
================
Interactive CLI checklist for the SAP Procure-to-Pay (P2P) closing cycle.
Guides the user through each procurement step and generates a summary report.

Usage:
    python scripts/p2p_checklist.py
"""

import datetime

CHECKLIST = [
    {
        "step": 1,
        "title": "Create Purchase Requisition",
        "tcode": "ME51N",
        "description": "Department raises a formal request for goods/services.",
        "checks": [
            "Material description and quantity specified",
            "Required delivery date set",
            "Cost centre / GL account assigned",
            "PR approved by department head",
        ],
    },
    {
        "step": 2,
        "title": "Create Purchase Order",
        "tcode": "ME21N",
        "description": "Approved PR converted to binding PO and sent to vendor.",
        "checks": [
            "Vendor selected and verified",
            "Unit price and payment terms agreed",
            "PO dispatched to vendor (ME9F)",
            "Delivery date confirmed",
        ],
    },
    {
        "step": 3,
        "title": "Post Goods Receipt",
        "tcode": "MIGO",
        "description": "Warehouse records delivery and updates stock levels.",
        "checks": [
            "Physical goods inspected and matched to PO",
            "GR posted in MIGO — material document created",
            "Stock balance updated in system",
            "GR/IR clearing account posted (GL entry)",
        ],
    },
    {
        "step": 4,
        "title": "Invoice Verification",
        "tcode": "MIRO",
        "description": "Supplier invoice validated via 3-way match (PO + GR + Invoice).",
        "checks": [
            "Invoice amount matches PO value (within tolerance)",
            "Invoice quantity matches GR quantity",
            "3-way match passed — no discrepancies",
            "AP document posted — vendor liability recorded",
        ],
    },
    {
        "step": 5,
        "title": "Process Vendor Payment",
        "tcode": "F110",
        "description": "FI module executes payment and clears AP open item.",
        "checks": [
            "Payment run configured with correct parameters",
            "Vendor payment executed via bank transfer",
            "AP open item cleared",
            "Reconciliation confirmed in FBL1N",
        ],
    },
]


def print_banner():
    print("\n" + "=" * 58)
    print("   SAP P2P — Procurement Checklist")
    print(f"   Date: {datetime.date.today().strftime('%d %B %Y')}")
    print("=" * 58 + "\n")
    print("  For each check: c = complete | s = skip | i = issue\n")


def prompt_check(text):
    while True:
        resp = input(f"  [ ] {text}\n      (c/s/i): ").strip().lower()
        if resp in ("c", "complete"):
            return "✅ Complete"
        elif resp in ("s", "skip"):
            return "⏭  Skipped"
        elif resp in ("i", "issue"):
            note = input("      Describe issue: ").strip()
            return f"⚠️  Issue — {note}"
        print("      Enter c, s, or i.")


def run_step(step_data):
    print(f"\n{'─'*58}")
    print(f"  STEP {step_data['step']}: {step_data['title']}")
    print(f"  T-Code : {step_data['tcode']}")
    print(f"  Info   : {step_data['description']}")
    print(f"{'─'*58}")
    results = {}
    for check in step_data["checks"]:
        results[check] = prompt_check(check)
    return results


def print_summary(all_results):
    print("\n\n" + "=" * 58)
    print("   P2P CHECKLIST SUMMARY")
    print(f"   {datetime.datetime.now().strftime('%d %B %Y %H:%M')}")
    print("=" * 58)
    issues = False
    for step in CHECKLIST:
        res = all_results.get(step["step"], {})
        print(f"\nStep {step['step']}: {step['title']} ({step['tcode']})")
        for check, status in res.items():
            print(f"  {status} — {check}")
            if "Issue" in status:
                issues = True
    print("\n" + "=" * 58)
    if issues:
        print("  ⚠️  STATUS: Procurement cycle complete with issues.")
    else:
        print("  ✅  STATUS: All steps complete. P2P cycle successful.")
    print("=" * 58 + "\n")


def main():
    print_banner()
    all_results = {}
    for step_data in CHECKLIST:
        results = run_step(step_data)
        all_results[step_data["step"]] = results
        cont = input("\n  Proceed to next step? (y/n): ").strip().lower()
        if cont != "y":
            print("\n  Checklist paused.")
            break
    print_summary(all_results)


if __name__ == "__main__":
    main()
