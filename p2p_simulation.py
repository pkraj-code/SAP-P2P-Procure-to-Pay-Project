"""
p2p_simulation.py
=================
SAP Procure-to-Pay (P2P) Workflow Simulation Engine
----------------------------------------------------
Capstone Project — Pravin Kumar | Roll No: 23051688 | B.Tech CSE

This module simulates the complete end-to-end Procure-to-Pay cycle as
implemented in SAP MM/FI. It models all five core steps:

    Step 1 — Purchase Requisition  (ME51N)
    Step 2 — Purchase Order        (ME21N)
    Step 3 — Goods Receipt         (MIGO)
    Step 4 — Invoice Verification  (MIRO)
    Step 5 — Payment Processing    (F110)

Each transaction generates documents, updates stock, posts to ledgers,
and logs a full audit trail — mirroring SAP behaviour.

Usage:
    python src/p2p_simulation.py               # run a demo cycle
    python src/p2p_simulation.py --interactive  # guided mode
"""

import uuid
import datetime
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PurchaseRequisition:
    """Represents a SAP Purchase Requisition (PR) — T-Code ME51N."""
    pr_number: str
    material: str
    quantity: float
    unit: str
    required_date: str
    department: str
    created_by: str
    status: str = "OPEN"
    created_at: str = field(default_factory=lambda: _now())

    def display(self):
        print(f"\n  {'─'*50}")
        print(f"  📋 PURCHASE REQUISITION — {self.pr_number}")
        print(f"  {'─'*50}")
        print(f"  Material     : {self.material}")
        print(f"  Quantity     : {self.quantity} {self.unit}")
        print(f"  Required By  : {self.required_date}")
        print(f"  Department   : {self.department}")
        print(f"  Created By   : {self.created_by}")
        print(f"  Status       : {self.status}")
        print(f"  Created At   : {self.created_at}")
        print(f"  {'─'*50}")


@dataclass
class PurchaseOrder:
    """Represents a SAP Purchase Order (PO) — T-Code ME21N."""
    po_number: str
    pr_number: str
    vendor_id: str
    vendor_name: str
    material: str
    quantity: float
    unit: str
    unit_price: float
    currency: str
    delivery_date: str
    payment_terms: str
    status: str = "SENT_TO_VENDOR"
    created_at: str = field(default_factory=lambda: _now())

    @property
    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def display(self):
        print(f"\n  {'─'*50}")
        print(f"  🛒 PURCHASE ORDER — {self.po_number}")
        print(f"  {'─'*50}")
        print(f"  PR Reference : {self.pr_number}")
        print(f"  Vendor       : {self.vendor_name} ({self.vendor_id})")
        print(f"  Material     : {self.material}")
        print(f"  Quantity     : {self.quantity} {self.unit}")
        print(f"  Unit Price   : {self.currency} {self.unit_price:,.2f}")
        print(f"  Total Value  : {self.currency} {self.total_value:,.2f}")
        print(f"  Delivery     : {self.delivery_date}")
        print(f"  Payment Terms: {self.payment_terms}")
        print(f"  Status       : {self.status}")
        print(f"  {'─'*50}")


@dataclass
class GoodsReceipt:
    """Represents a SAP Goods Receipt document — T-Code MIGO."""
    gr_number: str
    po_number: str
    material_doc: str
    material: str
    quantity_received: float
    unit: str
    storage_location: str
    received_by: str
    gl_postings: list = field(default_factory=list)
    stock_updated: bool = False
    created_at: str = field(default_factory=lambda: _now())

    def display(self):
        print(f"\n  {'─'*50}")
        print(f"  📦 GOODS RECEIPT — {self.gr_number}")
        print(f"  {'─'*50}")
        print(f"  PO Reference : {self.po_number}")
        print(f"  Material Doc : {self.material_doc}")
        print(f"  Material     : {self.material}")
        print(f"  Qty Received : {self.quantity_received} {self.unit}")
        print(f"  Storage Loc  : {self.storage_location}")
        print(f"  Received By  : {self.received_by}")
        print(f"  Stock Updated: {'Yes ✅' if self.stock_updated else 'No ❌'}")
        if self.gl_postings:
            print(f"  GL Postings  :")
            for p in self.gl_postings:
                print(f"    {p}")
        print(f"  {'─'*50}")


@dataclass
class InvoiceVerification:
    """Represents a SAP Invoice Verification — T-Code MIRO."""
    invoice_number: str
    po_number: str
    gr_number: str
    vendor_id: str
    invoice_amount: float
    currency: str
    invoice_date: str
    three_way_match: bool = False
    match_result: str = "PENDING"
    ap_document: Optional[str] = None
    created_at: str = field(default_factory=lambda: _now())

    def display(self):
        match_icon = "✅" if self.three_way_match else "❌"
        print(f"\n  {'─'*50}")
        print(f"  🧾 INVOICE VERIFICATION — {self.invoice_number}")
        print(f"  {'─'*50}")
        print(f"  PO Reference : {self.po_number}")
        print(f"  GR Reference : {self.gr_number}")
        print(f"  Vendor       : {self.vendor_id}")
        print(f"  Invoice Amt  : {self.currency} {self.invoice_amount:,.2f}")
        print(f"  Invoice Date : {self.invoice_date}")
        print(f"  3-Way Match  : {match_icon} {self.match_result}")
        if self.ap_document:
            print(f"  AP Document  : {self.ap_document}")
        print(f"  {'─'*50}")


@dataclass
class PaymentRun:
    """Represents a SAP Automatic Payment Run — T-Code F110."""
    payment_doc: str
    invoice_number: str
    vendor_id: str
    vendor_name: str
    payment_amount: float
    currency: str
    bank_account: str
    payment_method: str
    value_date: str
    cleared: bool = False
    created_at: str = field(default_factory=lambda: _now())

    def display(self):
        print(f"\n  {'─'*50}")
        print(f"  💰 PAYMENT — {self.payment_doc}")
        print(f"  {'─'*50}")
        print(f"  Invoice Ref  : {self.invoice_number}")
        print(f"  Vendor       : {self.vendor_name} ({self.vendor_id})")
        print(f"  Amount Paid  : {self.currency} {self.payment_amount:,.2f}")
        print(f"  Bank Account : {self.bank_account}")
        print(f"  Method       : {self.payment_method}")
        print(f"  Value Date   : {self.value_date}")
        print(f"  AP Cleared   : {'Yes ✅' if self.cleared else 'No ❌'}")
        print(f"  {'─'*50}")


@dataclass
class AuditLog:
    """Full audit trail for a P2P transaction cycle."""
    cycle_id: str
    entries: list = field(default_factory=list)

    def log(self, step: int, tcode: str, action: str, doc_number: str):
        entry = {
            "timestamp": _now(),
            "step": step,
            "tcode": tcode,
            "action": action,
            "document": doc_number,
        }
        self.entries.append(entry)

    def display(self):
        print(f"\n  {'═'*55}")
        print(f"  📋 AUDIT TRAIL — Cycle {self.cycle_id}")
        print(f"  {'═'*55}")
        print(f"  {'Step':<6} {'T-Code':<10} {'Document':<20} {'Action'}")
        print(f"  {'─'*55}")
        for e in self.entries:
            print(f"  {e['step']:<6} {e['tcode']:<10} {e['document']:<20} {e['action']}")
        print(f"  {'═'*55}")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _doc_id(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def _section(title: str):
    width = 55
    print(f"\n{'═' * width}")
    print(f"  STEP {title}")
    print(f"{'═' * width}")


# ─────────────────────────────────────────────────────────────────────────────
# P2P WORKFLOW ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class P2PWorkflow:
    """
    Simulates the complete SAP Procure-to-Pay (P2P) cycle.

    Mirrors the 5-step workflow:
        ME51N → ME21N → MIGO → MIRO → F110

    Each step validates preconditions, creates documents, updates
    stock/ledger state, and records an audit entry.
    """

    def __init__(self, company_code: str = "1000", currency: str = "INR"):
        self.company_code = company_code
        self.currency = currency
        self.cycle_id = _doc_id("CYCLE-")
        self.audit = AuditLog(cycle_id=self.cycle_id)

        # State
        self.pr: Optional[PurchaseRequisition] = None
        self.po: Optional[PurchaseOrder] = None
        self.gr: Optional[GoodsReceipt] = None
        self.iv: Optional[InvoiceVerification] = None
        self.payment: Optional[PaymentRun] = None
        self.stock_balance: float = 0.0

    # ── Step 1: Purchase Requisition ─────────────────────────────────────────

    def create_purchase_requisition(
        self,
        material: str,
        quantity: float,
        unit: str,
        required_date: str,
        department: str,
        created_by: str,
    ) -> PurchaseRequisition:
        _section("1 — Purchase Requisition  [T-Code: ME51N]")

        pr_number = _doc_id("PR-")
        self.pr = PurchaseRequisition(
            pr_number=pr_number,
            material=material,
            quantity=quantity,
            unit=unit,
            required_date=required_date,
            department=department,
            created_by=created_by,
            status="APPROVED",
        )
        self.audit.log(1, "ME51N", "Purchase Requisition Created & Approved", pr_number)
        self.pr.display()
        print(f"  ✅ PR {pr_number} created and approved successfully.")
        return self.pr

    # ── Step 2: Purchase Order ───────────────────────────────────────────────

    def create_purchase_order(
        self,
        vendor_id: str,
        vendor_name: str,
        unit_price: float,
        delivery_date: str,
        payment_terms: str = "Net 30",
    ) -> PurchaseOrder:
        _section("2 — Purchase Order  [T-Code: ME21N]")

        if not self.pr or self.pr.status != "APPROVED":
            raise ValueError("❌ Cannot create PO: No approved Purchase Requisition found.")

        po_number = _doc_id("PO-")
        self.po = PurchaseOrder(
            po_number=po_number,
            pr_number=self.pr.pr_number,
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            material=self.pr.material,
            quantity=self.pr.quantity,
            unit=self.pr.unit,
            unit_price=unit_price,
            currency=self.currency,
            delivery_date=delivery_date,
            payment_terms=payment_terms,
            status="SENT_TO_VENDOR",
        )
        self.pr.status = "PO_CREATED"
        self.audit.log(2, "ME21N", "Purchase Order Created & Sent to Vendor", po_number)
        self.po.display()
        print(f"  ✅ PO {po_number} created and dispatched to vendor {vendor_name}.")
        return self.po

    # ── Step 3: Goods Receipt ────────────────────────────────────────────────

    def post_goods_receipt(
        self,
        quantity_received: float,
        storage_location: str,
        received_by: str,
    ) -> GoodsReceipt:
        _section("3 — Goods Receipt  [T-Code: MIGO]")

        if not self.po or self.po.status != "SENT_TO_VENDOR":
            raise ValueError("❌ Cannot post GR: No active Purchase Order found.")

        if quantity_received > self.po.quantity:
            raise ValueError(
                f"❌ Quantity received ({quantity_received}) exceeds PO quantity ({self.po.quantity})."
            )

        gr_number = _doc_id("GR-")
        material_doc = _doc_id("MATDOC-")
        gr_value = round(quantity_received * self.po.unit_price, 2)

        gl_postings = [
            f"Dr  Stock Account          {self.currency} {gr_value:>12,.2f}",
            f"Cr  GR/IR Clearing Account {self.currency} {gr_value:>12,.2f}",
        ]

        self.gr = GoodsReceipt(
            gr_number=gr_number,
            po_number=self.po.po_number,
            material_doc=material_doc,
            material=self.po.material,
            quantity_received=quantity_received,
            unit=self.po.unit,
            storage_location=storage_location,
            received_by=received_by,
            gl_postings=gl_postings,
            stock_updated=True,
        )

        # Update stock
        self.stock_balance += quantity_received
        self.po.status = "GOODS_RECEIVED"

        self.audit.log(3, "MIGO", f"Goods Receipt Posted — Stock +{quantity_received} {self.po.unit}", gr_number)
        self.gr.display()
        print(f"  ✅ GR {gr_number} posted. Stock balance updated to {self.stock_balance} {self.po.unit}.")
        return self.gr

    # ── Step 4: Invoice Verification ────────────────────────────────────────

    def verify_invoice(
        self,
        invoice_number: str,
        invoice_amount: float,
        invoice_date: str,
    ) -> InvoiceVerification:
        _section("4 — Invoice Verification  [T-Code: MIRO]")

        if not self.gr or not self.po:
            raise ValueError("❌ Cannot verify invoice: GR or PO not found.")

        expected_amount = self.gr.quantity_received * self.po.unit_price
        tolerance = 0.02  # 2% tolerance

        amount_diff = abs(invoice_amount - expected_amount)
        within_tolerance = amount_diff <= (expected_amount * tolerance)

        ap_document = _doc_id("AP-")
        match_result = "MATCHED ✅" if within_tolerance else f"DISCREPANCY ❌ (diff: {self.currency} {amount_diff:,.2f})"

        self.iv = InvoiceVerification(
            invoice_number=invoice_number,
            po_number=self.po.po_number,
            gr_number=self.gr.gr_number,
            vendor_id=self.po.vendor_id,
            invoice_amount=invoice_amount,
            currency=self.currency,
            invoice_date=invoice_date,
            three_way_match=within_tolerance,
            match_result=match_result,
            ap_document=ap_document if within_tolerance else None,
        )

        print(f"\n  3-Way Match Verification:")
        print(f"    PO Value (expected)  : {self.currency} {expected_amount:>12,.2f}")
        print(f"    GR Value (received)  : {self.currency} {expected_amount:>12,.2f}")
        print(f"    Invoice Amount       : {self.currency} {invoice_amount:>12,.2f}")
        print(f"    Difference           : {self.currency} {amount_diff:>12,.2f}")
        print(f"    Result               : {match_result}")

        self.iv.display()

        if within_tolerance:
            self.audit.log(4, "MIRO", "Invoice Verified — 3-Way Match Passed", invoice_number)
            print(f"  ✅ AP Document {ap_document} posted. Invoice approved for payment.")
        else:
            self.audit.log(4, "MIRO", "Invoice BLOCKED — 3-Way Match Failed", invoice_number)
            print(f"  ⚠️  Invoice {invoice_number} BLOCKED. Manual review required (T-Code: MRBR).")

        return self.iv

    # ── Step 5: Payment Processing ───────────────────────────────────────────

    def process_payment(self, bank_account: str = "HDFC-0001", payment_method: str = "Bank Transfer") -> PaymentRun:
        _section("5 — Payment Processing  [T-Code: F110]")

        if not self.iv:
            raise ValueError("❌ Cannot process payment: Invoice verification not completed.")

        if not self.iv.three_way_match:
            raise ValueError("❌ Cannot process payment: Invoice did not pass 3-way match. Resolve via MRBR.")

        payment_doc = _doc_id("PAY-")
        value_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")

        self.payment = PaymentRun(
            payment_doc=payment_doc,
            invoice_number=self.iv.invoice_number,
            vendor_id=self.po.vendor_id,
            vendor_name=self.po.vendor_name,
            payment_amount=self.iv.invoice_amount,
            currency=self.currency,
            bank_account=bank_account,
            payment_method=payment_method,
            value_date=value_date,
            cleared=True,
        )

        self.audit.log(5, "F110", "Payment Executed — AP Cleared", payment_doc)
        self.payment.display()
        print(f"  ✅ Payment {payment_doc} executed. AP open item cleared.")
        return self.payment

    # ── Summary ──────────────────────────────────────────────────────────────

    def print_summary(self):
        print(f"\n\n{'═'*55}")
        print(f"  P2P CYCLE COMPLETE — {self.cycle_id}")
        print(f"{'═'*55}")
        docs = [
            ("Purchase Requisition", self.pr.pr_number if self.pr else "N/A"),
            ("Purchase Order",       self.po.po_number if self.po else "N/A"),
            ("Goods Receipt",        self.gr.gr_number if self.gr else "N/A"),
            ("Invoice",              self.iv.invoice_number if self.iv else "N/A"),
            ("Payment",              self.payment.payment_doc if self.payment else "N/A"),
        ]
        for label, doc in docs:
            print(f"  {label:<25}: {doc}")
        print(f"\n  Final Stock Balance  : {self.stock_balance} {self.po.unit if self.po else ''}")
        if self.payment:
            print(f"  Total Amount Paid    : {self.currency} {self.payment.payment_amount:,.2f}")
        print(f"{'═'*55}")
        self.audit.display()

    def export_audit(self, filepath: str = "p2p_audit_log.json"):
        """Export the audit log and all documents to a JSON file."""
        data = {
            "cycle_id": self.cycle_id,
            "company_code": self.company_code,
            "currency": self.currency,
            "exported_at": _now(),
            "audit_trail": self.audit.entries,
            "documents": {
                "purchase_requisition": asdict(self.pr) if self.pr else None,
                "purchase_order": asdict(self.po) if self.po else None,
                "goods_receipt": asdict(self.gr) if self.gr else None,
                "invoice_verification": asdict(self.iv) if self.iv else None,
                "payment": asdict(self.payment) if self.payment else None,
            },
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n  📄 Audit log exported to: {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO RUN
# ─────────────────────────────────────────────────────────────────────────────

def run_demo():
    """Run a complete demo P2P cycle with sample data."""
    print("\n" + "=" * 55)
    print("  SAP P2P Simulation Engine — Demo Run")
    print(f"  Company Code: 1000  |  Currency: INR")
    print("=" * 55)

    workflow = P2PWorkflow(company_code="1000", currency="INR")

    # Step 1: Create Purchase Requisition
    workflow.create_purchase_requisition(
        material="Testing Material (PC)",
        quantity=10,
        unit="EA",
        required_date="2026-05-15",
        department="IT Department",
        created_by="Pravin Kumar",
    )

    # Step 2: Create Purchase Order
    workflow.create_purchase_order(
        vendor_id="V000050006",
        vendor_name="A & C Electricals",
        unit_price=11.00,
        delivery_date="2026-05-10",
        payment_terms="Net 30",
    )

    # Step 3: Post Goods Receipt
    workflow.post_goods_receipt(
        quantity_received=10,
        storage_location="SL01",
        received_by="Warehouse Team",
    )

    # Step 4: Invoice Verification (matching invoice)
    workflow.verify_invoice(
        invoice_number=_doc_id("INV-"),
        invoice_amount=110.00,
        invoice_date="2026-05-12",
    )

    # Step 5: Payment
    workflow.process_payment(
        bank_account="HDFC-0001",
        payment_method="Bank Transfer",
    )

    # Print summary and export
    workflow.print_summary()
    workflow.export_audit("p2p_audit_log.json")


# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE MODE
# ─────────────────────────────────────────────────────────────────────────────

def run_interactive():
    """Guided interactive P2P cycle entry."""
    print("\n" + "=" * 55)
    print("  SAP P2P Simulation — Interactive Mode")
    print("=" * 55)

    currency = input("\n  Currency (default INR): ").strip() or "INR"
    company = input("  Company Code (default 1000): ").strip() or "1000"
    workflow = P2PWorkflow(company_code=company, currency=currency)

    print("\n  --- Step 1: Purchase Requisition ---")
    material = input("  Material description: ").strip()
    qty = float(input("  Quantity: ").strip())
    unit = input("  Unit (e.g. EA, KG, PC): ").strip()
    req_date = input("  Required date (YYYY-MM-DD): ").strip()
    dept = input("  Department: ").strip()
    user = input("  Created by: ").strip()
    workflow.create_purchase_requisition(material, qty, unit, req_date, dept, user)

    print("\n  --- Step 2: Purchase Order ---")
    vendor_id = input("  Vendor ID: ").strip()
    vendor_name = input("  Vendor Name: ").strip()
    price = float(input("  Unit Price: ").strip())
    del_date = input("  Delivery date (YYYY-MM-DD): ").strip()
    terms = input("  Payment Terms (default Net 30): ").strip() or "Net 30"
    workflow.create_purchase_order(vendor_id, vendor_name, price, del_date, terms)

    print("\n  --- Step 3: Goods Receipt ---")
    recv_qty = float(input(f"  Quantity received (ordered: {qty}): ").strip())
    storage = input("  Storage location (e.g. SL01): ").strip()
    recv_by = input("  Received by: ").strip()
    workflow.post_goods_receipt(recv_qty, storage, recv_by)

    print("\n  --- Step 4: Invoice Verification ---")
    inv_num = input("  Invoice number: ").strip()
    inv_amt = float(input("  Invoice amount: ").strip())
    inv_date = input("  Invoice date (YYYY-MM-DD): ").strip()
    workflow.verify_invoice(inv_num, inv_amt, inv_date)

    if workflow.iv and workflow.iv.three_way_match:
        print("\n  --- Step 5: Payment ---")
        bank = input("  Bank account (default HDFC-0001): ").strip() or "HDFC-0001"
        method = input("  Payment method (default Bank Transfer): ").strip() or "Bank Transfer"
        workflow.process_payment(bank, method)

    workflow.print_summary()
    export = input("\n  Export audit log to JSON? (y/n): ").strip().lower()
    if export == "y":
        workflow.export_audit("p2p_audit_log.json")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAP P2P Simulation Engine")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (guided data entry)",
    )
    args = parser.parse_args()

    if args.interactive:
        run_interactive()
    else:
        run_demo()
