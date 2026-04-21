# Procure-to-Pay (P2P) — SAP MM Project

## 📌 Project Overview

This project demonstrates the complete implementation of the **Procure-to-Pay (P2P)** process using SAP Materials Management (MM). It covers the full procurement lifecycle from purchase requisition to vendor payment, integrating both logistics and financial operations.

The system ensures automation, accuracy, and real-time data processing across procurement activities.

---

## ❓ Problem Statement

In many organizations, procurement is handled manually or through disconnected systems, leading to:

* Delays in purchase approvals
* Poor vendor coordination
* Lack of real-time inventory visibility
* Errors in invoices and purchase orders
* Inefficient communication between departments
* Increased operational costs

This project solves these issues by implementing a centralized SAP-based procurement system.

---

## ⚙️ Implementation Steps & SAP T-Codes

| Step | Activity             | T-Code |
| ---- | -------------------- | ------ |
| 1    | Purchase Requisition | ME51N  |
| 2    | Purchase Order       | ME21N  |
| 3    | Goods Receipt        | MIGO   |
| 4    | Invoice Verification | MIRO   |
| 5    | Payment Processing   | F110   |

---

## 🔄 P2P Process Flow

Purchase Requisition → Purchase Order → Goods Receipt → Invoice Verification → Payment

---

## 🧠 Detailed Process

### 1. Purchase Requisition

Internal request created for required materials.

### 2. Purchase Order

Official order sent to vendor with pricing and delivery details.

### 3. Goods Receipt

Material received and inventory updated in SAP.

### 4. Invoice Verification

Three-way matching between PO, GR, and invoice.

### 5. Payment

Processed through SAP FI module.

---

## 🧰 Tech Stack

* SAP S/4HANA / SAP ECC
* SAP MM (Materials Management)
* SAP FI (Financial Accounting)
* SAP GUI
* SAP Database

---

## 📸 Screenshots

### Purchase Order (ME21N)

![ME21N Screenshot](screenshots/me21n.png)

### Goods Receipt (MIGO)

![MIGO Screenshot](screenshots/migo.png)

### Invoice Verification (MIRO)

![MIRO Screenshot](screenshots/miro.png)

### SAP Dashboard

![SAP Dashboard](screenshots/dashboard.png)

---

## ⭐ Unique Points

* End-to-end procurement lifecycle
* Real-time inventory updates
* Integration with SAP FI
* Automated invoice verification
* Reduced manual errors

---

## 🔮 Future Improvements

* AI-based vendor selection
* Mobile approval system
* Analytics dashboard
* Supplier portal integration

---

## 📊 Project Outcome

This project demonstrates how SAP MM automates procurement and integrates with finance to ensure efficiency, transparency, and accuracy.

---

## 👤 Author

**Name:** Pravin Kumar 
**Roll No:** 23051688 
**Branch:** B.Tech CSE 
**Submission Date:** 21 April 2026

---
