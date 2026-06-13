import os
import json
import logging
import xmlrpc.client
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH',
    'E:\\Python Projects\\Personal AI Employee Hackathon 0\\AI_Employee_Vault'))
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'odoo')
ODOO_USER = os.getenv('ODOO_USER', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_odoo():
    """Connect to Odoo via XML-RPC"""
    try:
        common = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/common'
        )
        uid = common.authenticate(
            ODOO_DB, ODOO_USER, ODOO_PASSWORD, {}
        )
        models = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/object'
        )
        logger.info(f'Connected to Odoo! User ID: {uid}')
        return uid, models
    except Exception as e:
        logger.error(f'Odoo connection failed: {e}')
        return None, None

def create_draft_invoice(
    customer_name: str,
    amount: float,
    description: str
):
    """Create a draft invoice in Odoo"""
    if DRY_RUN:
        logger.info(
            f'[DRY RUN] Would create invoice: '
            f'{customer_name} - ${amount}'
        )
        create_odoo_approval(customer_name, amount, description)
        return True

    uid, models = connect_odoo()
    if not uid:
        logger.error('Cannot create invoice — Odoo not connected')
        return False

    try:
        # Find or create partner
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['name', '=', customer_name]]]
        )

        if not partner_ids:
            partner_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'create',
                [{'name': customer_name}]
            )
        else:
            partner_id = partner_ids[0]

        # Create draft invoice
        invoice_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'create',
            [{
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }]
        )

        logger.info(f'Draft invoice created in Odoo! ID: {invoice_id}')
        create_odoo_approval(customer_name, amount, description)
        return True

    except Exception as e:
        logger.error(f'Error creating invoice: {e}')
        return False

def create_odoo_approval(
    customer_name: str,
    amount: float,
    description: str
):
    """Create approval file for Odoo invoice"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    approval_path = VAULT_PATH / 'Pending_Approval' / \
        f'ODOO_INVOICE_{timestamp}.md'

    content = f'''---
type: odoo_invoice
action: post_invoice
status: pending
customer: {customer_name}
amount: {amount}
created: {datetime.now().isoformat()}
dry_run: {DRY_RUN}
---

# Odoo Invoice Approval Required

## Invoice Details
- **Customer:** {customer_name}
- **Amount:** ${amount}
- **Description:** {description}
- **Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Instructions
- ✅ Move to /Approved to post invoice in Odoo
- ❌ Move to /Rejected to cancel

## Warning
⚠️ Posting this invoice will make it official in Odoo.
This action cannot be easily undone.

---
*Waiting for human approval*
'''
    approval_path.write_text(content, encoding='utf-8')
    logger.info(f'Odoo approval file created: {approval_path.name}')
    return approval_path

def get_odoo_invoices():
    """Get all invoices from Odoo"""
    if DRY_RUN:
        logger.info('[DRY RUN] Would fetch invoices from Odoo')
        return []

    uid, models = connect_odoo()
    if not uid:
        return []

    try:
        invoices = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'search_read',
            [[['move_type', '=', 'out_invoice']]],
            {'fields': ['name', 'partner_id',
                       'amount_total', 'state'],
             'limit': 10}
        )
        return invoices
    except Exception as e:
        logger.error(f'Error fetching invoices: {e}')
        return []

def sync_odoo_to_vault():
    """Sync Odoo invoices to Obsidian vault"""
    invoices = get_odoo_invoices()

    if not invoices:
        logger.info('No invoices to sync')
        return

    accounting_path = VAULT_PATH / 'Accounting'
    accounting_path.mkdir(exist_ok=True)

    content = f'''# Odoo Invoices
*Last synced: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

| Invoice | Customer | Amount | Status |
|---------|----------|--------|--------|
'''
    for inv in invoices:
        customer = inv['partner_id'][1] \
            if inv['partner_id'] else 'Unknown'
        content += f"| {inv['name']} | {customer} | "
        content += f"${inv['amount_total']} | {inv['state']} |\n"

    sync_file = accounting_path / 'odoo_invoices.md'
    sync_file.write_text(content, encoding='utf-8')
    logger.info(f'Synced {len(invoices)} invoices to vault')

if __name__ == '__main__':
    print("\n💼 Odoo Integration")
    print("=" * 40)
    print("1. Test Odoo connection")
    print("2. Create draft invoice")
    print("3. Sync invoices to vault")
    print("4. Exit")

    choice = input("\nChoose option: ").strip()

    if choice == "1":
        uid, models = connect_odoo()
        if uid:
            print(f"✅ Connected! User ID: {uid}")
        else:
            print("❌ Connection failed — is Odoo running?")

    elif choice == "2":
        customer = input("Customer name: ")
        amount = float(input("Amount ($): "))
        desc = input("Description: ")
        create_draft_invoice(customer, amount, desc)
        print("✅ Check Pending_Approval folder in Obsidian!")

    elif choice == "3":
        sync_odoo_to_vault()
        print("✅ Synced to vault!")