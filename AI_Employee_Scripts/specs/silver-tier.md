# Silver Tier: Functional Assistant

## Overview
Extends Bronze tier with LinkedIn automation, Claude reasoning
loop, email MCP server, and human-in-the-loop approval workflow.

## Features

### 1. LinkedIn Auto-Poster
- Automatically posts business updates to LinkedIn
- Uses Playwright browser automation
- Requires human approval before posting
- Creates approval file in /Pending_Approval

### 2. Claude Reasoning Loop
- Reads /Needs_Action folder
- Creates Plan.md files with action steps
- Uses Groq LLaMA as reasoning engine
- Updates Dashboard after each reasoning cycle

### 3. Email MCP Server
- Sends emails via Gmail API
- Only sends after human approval
- Logs every sent email to /Logs
- Supports reply, forward, new email

### 4. Human-in-the-Loop Workflow
- Sensitive actions create approval files
- Human moves file to /Approved or /Rejected
- Orchestrator watches /Approved folder
- Executes approved actions automatically

### 5. Scheduling
- Gmail check: every 2 minutes
- LinkedIn post: manually triggered
- Dashboard update: every 60 seconds
- Reasoning loop: every 5 minutes