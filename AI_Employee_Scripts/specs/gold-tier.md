# Gold Tier: Autonomous Employee

## Overview
Extends Silver tier with social media automation,
weekly CEO briefing, Ralph Wiggum loop, and Odoo
accounting integration.

## Features

### 1. Facebook + Instagram Auto-Poster
- Posts business updates automatically
- Requires human approval before posting
- Uses Meta Graph API for Facebook
- Uses Instagrapi for Instagram
- Creates approval files in /Pending_Approval

### 2. Weekly CEO Briefing
- Runs every Sunday night automatically
- Reads Business_Goals.md
- Analyzes completed tasks from /Done
- Generates Monday Morning Briefing
- Highlights revenue, bottlenecks, suggestions

### 3. Ralph Wiggum Autonomous Loop
- Keeps AI working until task is complete
- Checks /Needs_Action every 2 minutes
- Creates plans, executes approved actions
- Moves completed items to /Done
- Stops only when all items are processed

### 4. Odoo Accounting Integration
- Self-hosted Odoo Community via Docker
- Reads transactions from Obsidian vault
- Creates draft invoices in Odoo
- Requires human approval before posting
- Syncs completed invoices back to vault

### 5. Error Recovery
- Exponential backoff retry logic
- Watchdog monitors all processes
- Auto-restarts failed watchers
- Alerts logged to Dashboard

## Security
- All social media posts require approval
- Odoo actions require approval
- Never auto-approve payments
- Full audit trail in /Logs