"""
tcode_lookup.py
===============
SAP T-Code lookup tool for the P2P process.

Usage:
    python scripts/tcode_lookup.py           # interactive
    python scripts/tcode_lookup.py ME21N     # direct lookup
    python scripts/tcode_lookup.py --list    # show all
"""

import sys

TCODES = {
    "ME51N": {"name": "Create Purchase Requisition", "module": "MM", "step": "Step 1 — PR Creation",
              "desc": "Raise a formal internal request for goods or services."},
    "ME52N": {"name": "Change Purchase Requisition", "module": "MM", "step": "Step 1 — PR Modification",
              "desc": "Edit an existing purchase requisition before PO creation."},
    "ME53N": {"name": "Display Purchase Requisition", "module": "MM", "step": "Step 1 — PR View",
              "desc": "View details of an existing purchase requisition."},
    "ME54N": {"name": "Release Purchase Requisition", "module": "MM", "step": "Step 1 — PR Approval",
              "desc": "Approve (release) a PR via the release strategy workflow."},
    "ME55":  {"name": "Collective Release of PRs", "module": "MM", "step": "Step 1 — Bulk Approval",
              "desc": "Approve multiple PRs in a single transaction."},
    "ME21N": {"name": "Create Purchase Order", "module": "MM", "step": "Step 2 — PO Creation",
              "desc": "Convert approved PR into a binding purchase order for the vendor."},
    "ME22N": {"name": "Change Purchase Order", "module": "MM", "step": "Step 2 — PO Modification",
              "desc": "Amend an existing purchase order (qty, price, dates)."},
    "ME23N": {"name": "Display Purchase Order", "module": "MM", "step": "Step 2 — PO View",
              "desc": "View all details of a purchase order document."},
    "ME9F":  {"name": "Print / Send Purchase Order", "module": "MM", "step": "Step 2 — Dispatch PO",
              "desc": "Print or electronically transmit the PO to the vendor."},
    "MIGO":  {"name": "Goods Receipt", "module": "MM", "step": "Step 3 — Goods Receipt",
              "desc": "Record delivery of goods from vendor. Updates stock and triggers FI GL posting."},
    "MB03":  {"name": "Display Material Document", "module": "MM", "step": "Step 3 — GR Verification",
              "desc": "View the material document created by a goods movement."},
    "MIRO":  {"name": "Enter Incoming Invoice", "module": "MM-IV", "step": "Step 4 — Invoice Verification",
              "desc": "Post vendor invoice. Performs 3-way match: PO + GR + Invoice."},
    "MRBR":  {"name": "Release Blocked Invoices", "module": "MM-IV", "step": "Step 4 — Invoice Unblocking",
              "desc": "Review and release invoices blocked due to price/qty discrepancies."},
    "FB60":  {"name": "Enter Vendor Invoice (FI)", "module": "FI-AP", "step": "Step 4 — Direct AP Invoice",
              "desc": "Post a vendor invoice directly in FI without MM reference."},
    "F110":  {"name": "Automatic Payment Run", "module": "FI-AP", "step": "Step 5 — Payment Processing",
              "desc": "Execute the automatic payment program to settle AP open items."},
    "F-53":  {"name": "Post Outgoing Payment", "module": "FI-AP", "step": "Step 5 — Manual Payment",
              "desc": "Manually post a single vendor payment and clear AP line item."},
    "FBL1N": {"name": "Vendor Line Items", "module": "FI-AP", "step": "Step 5 — AP Reconciliation",
              "desc": "Display open and cleared AP items for a vendor account."},
    "QA32":  {"name": "Change Inspection Lot", "module": "QM", "step": "Supporting — Quality Inspection",
              "desc": "Record quality inspection results for goods received from vendors."},
}


def show(code):
    code = code.upper()
    if code not in TCODES:
        print(f"\n  ❌ '{code}' not found. Try: {', '.join(sorted(TCODES))}")
        return
    t = TCODES[code]
    print(f"\n  {'─'*52}")
    print(f"  T-Code   : {code}")
    print(f"  Name     : {t['name']}")
    print(f"  Module   : {t['module']}")
    print(f"  P2P Step : {t['step']}")
    print(f"  {'─'*52}")
    print(f"  {t['desc']}")
    print(f"  {'─'*52}\n")


def list_all():
    print(f"\n  {'─'*60}")
    print(f"  {'T-CODE':<10} {'NAME':<38} {'MODULE'}")
    print(f"  {'─'*60}")
    for code, t in sorted(TCODES.items()):
        print(f"  {code:<10} {t['name']:<38} {t['module']}")
    print(f"  {'─'*60}\n")


def interactive():
    print("\n" + "="*52)
    print("  SAP P2P T-Code Lookup")
    print("="*52)
    print("  Type a T-Code, 'list', or 'quit'\n")
    while True:
        inp = input("  T-Code: ").strip().lower()
        if inp in ("quit", "exit", "q"):
            break
        elif inp == "list":
            list_all()
        elif inp:
            show(inp)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_all()
        else:
            show(sys.argv[1])
    else:
        interactive()
