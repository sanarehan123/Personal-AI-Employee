# 🤖 Personal AI Employee
**Hackathon 0: Building Autonomous FTEs in 2026**

> Your life and business on autopilot.
> Local-first, agent-driven, human-in-the-loop.

---

## 🏆 Tier Achieved
**Bronze Tier** — Foundation

---

## 📋 What This Does
A Personal AI Employee that autonomously monitors your Gmail
and file system, creates action items in your Obsidian vault,
and keeps your Dashboard updated — all while requiring your
approval for sensitive actions.

---

## 🏗️ Architecture
External Sources          Perception Layer
─────────────────         ────────────────
Gmail          ──────▶   gmail_watcher.py
File System    ──────▶   filesystem_watcher.py
│
▼
Obsidian Vault
─────────────
/Needs_Action  ← New items
/Done          ← Completed
/Inbox         ← File drops
/Logs          ← Audit trail
Dashboard.md   ← Live status
│
▼
orchestrator.py
───────────────
Manages all watchers
Updates dashboard
Logs all actions

---

## 📁 Project Structure
Personal AI Employee Hackathon 0/
├── AI_Employee_Vault/              ← Obsidian Vault
│   ├── Dashboard.md                ← Live status dashboard
│   ├── Company_Handbook.md         ← AI rules of engagement
│   ├── Business_Goals.md           ← Goals and metrics
│   ├── Needs_Action/               ← Items requiring attention
│   ├── Done/                       ← Completed items
│   ├── Inbox/                      ← File drop zone
│   ├── Logs/                       ← Audit logs
│   ├── Plans/                      ← AI generated plans
│   ├── Pending_Approval/           ← Awaiting human approval
│   ├── Approved/                   ← Human approved actions
│   └── Rejected/                   ← Human rejected actions
│
└── AI_Employee_Scripts/            ← Python Scripts
├── base_watcher.py             ← Base watcher template
├── gmail_watcher.py            ← Gmail monitoring
├── filesystem_watcher.py       ← File system monitoring
├── orchestrator.py             ← Master controller
├── .env                        ← Environment variables (not committed)
├── .gitignore
└── README.md

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.13+
- Obsidian v1.10.6+
- Google Cloud account (free)

### 2. Clone the repo
```bash
git clone https://github.com/sanarehan123/Personal-AI-Employee.git
cd Personal-AI-Employee
```

### 3. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file:
```env
VAULT_PATH=your_vault_path_here
GMAIL_CREDENTIALS_PATH=path_to_credentials.json
CHECK_INTERVAL=120
DRY_RUN=true
```

### 5. Set up Gmail API
- Go to console.cloud.google.com
- Create a new project
- Enable Gmail API
- Create OAuth credentials
- Download as `credentials.json`
- Add your email as test user

### 6. Run the AI Employee
```bash
# Run Gmail watcher
python gmail_watcher.py

# Run filesystem watcher
python filesystem_watcher.py

# Run everything together
python orchestrator.py
```

---

## 🔒 Security

- ✅ DRY_RUN mode enabled by default
- ✅ Credentials never committed to GitHub
- ✅ Human approval required for all sensitive actions
- ✅ Full audit logging in /Logs folder
- ✅ Rate limiting (max 10 emails per hour)

---

## ✅ Bronze Tier Checklist

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md with rules
- [x] Basic folder structure
- [x] Gmail Watcher working
- [x] Filesystem Watcher working (bonus!)
- [x] Orchestrator managing all watchers
- [x] Audit logging
- [x] Human-in-the-loop pattern
- [x] DRY_RUN safety mode

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Knowledge Base | Obsidian (Local Markdown) |
| Perception | Python Watcher Scripts |
| Email Monitoring | Gmail API (Google OAuth) |
| File Monitoring | Python Watchdog |
| Orchestration | Python Threading |
| Security | DRY_RUN + HITL pattern |

---

## 📝 How It Works

1. **Gmail Watcher** checks for important unread emails every 2 minutes
2. Creates a `.md` file in `/Needs_Action` for each email
3. **Filesystem Watcher** monitors `/Inbox` for new files
4. Creates metadata `.md` files for each dropped file
5. **Orchestrator** runs both watchers in background threads
6. **Dashboard.md** updates every 60 seconds with current status
7. All actions logged to `/Logs/YYYY-MM-DD.json`

---

## 🚀 Future Improvements (Silver Tier)
- WhatsApp watcher
- LinkedIn auto-posting
- MCP server for sending emails
- Human approval workflow
- Scheduled CEO briefings

---

*Built for Personal AI Employee Hackathon 0*
*Tier: Bronze | Local-first | Human-in-the-loop*

## 🏆 Tier Achieved
**Silver Tier** — Functional Assistant

## ✅ Silver Tier Checklist
- [x] All Bronze requirements
- [x] LinkedIn Auto-Poster with approval workflow
- [x] Claude Reasoning Loop (Groq LLaMA)
- [x] Plan.md file generation
- [x] Human-in-the-loop for LinkedIn posts
- [x] Updated Orchestrator managing all services
- [x] Full audit logging