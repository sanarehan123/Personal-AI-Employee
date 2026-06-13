import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH',
    'E:\\Python Projects\\Personal AI Employee Hackathon 0\\AI_Employee_Vault'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_vault_file(filename: str) -> str:
    filepath = VAULT_PATH / filename
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    return "File not found"

def get_done_items_this_week() -> list:
    done_path = VAULT_PATH / 'Done'
    items = []
    week_ago = datetime.now() - timedelta(days=7)

    for file in done_path.glob('*.md'):
        if file.stat().st_mtime > week_ago.timestamp():
            content = file.read_text(encoding='utf-8')
            items.append({
                'filename': file.name,
                'content': content[:300]
            })
    return items

def get_weekly_logs() -> list:
    logs_path = VAULT_PATH / 'Logs'
    all_logs = []
    week_ago = datetime.now() - timedelta(days=7)

    for log_file in logs_path.glob('*.json'):
        if log_file.stat().st_mtime > week_ago.timestamp():
            try:
                logs = json.loads(
                    log_file.read_text(encoding='utf-8')
                )
                all_logs.extend(logs)
            except:
                pass
    return all_logs

def call_groq_for_briefing(context: str) -> str:
    if not GROQ_API_KEY:
        return "Mock CEO briefing — add GROQ_API_KEY to .env"

    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {
                        'role': 'system',
                        'content': (
                            'You are a Chief of Staff preparing a '
                            'Monday Morning CEO Briefing. '
                            'Be concise, actionable, and highlight '
                            'key wins, bottlenecks, and suggestions. '
                            'Format as a professional markdown report.'
                        )
                    },
                    {
                        'role': 'user',
                        'content': context
                    }
                ],
                'max_tokens': 1500
            }
        )
        data = response.json()
        return data['choices'][0]['message']['content']

    except Exception as e:
        logger.error(f'Groq API error: {e}')
        return f"Error generating briefing: {e}"

def generate_ceo_briefing():
    logger.info('Generating CEO Briefing...')

    # Gather context
    business_goals = read_vault_file('Business_Goals.md')
    company_handbook = read_vault_file('Company_Handbook.md')
    done_items = get_done_items_this_week()
    weekly_logs = get_weekly_logs()

    # Count actions by type
    action_counts = {}
    for log in weekly_logs:
        action_type = log.get('action_type', 'unknown')
        action_counts[action_type] = \
            action_counts.get(action_type, 0) + 1

    # Build context for AI
    context = f"""
## Business Goals
{business_goals[:500]}

## Completed This Week ({len(done_items)} items)
{chr(10).join([f"- {item['filename']}" for item in done_items])}

## Actions Taken This Week
{json.dumps(action_counts, indent=2)}

## Total Actions: {len(weekly_logs)}

Please generate a Monday Morning CEO Briefing with:
1. Executive Summary
2. Key Wins this week
3. Completed Tasks
4. Bottlenecks identified
5. Proactive Suggestions
6. Upcoming priorities
"""

    if DRY_RUN:
        logger.info('[DRY RUN] Would call Groq for CEO briefing')
        briefing_content = f"""## Executive Summary (DRY RUN)
This is a dry run briefing.

## Key Wins
- {len(done_items)} items completed this week
- {len(weekly_logs)} total actions taken

## Actions Summary
{json.dumps(action_counts, indent=2)}

## Suggestions
- Review pending items in /Needs_Action
- Check /Pending_Approval for items awaiting review
"""
    else:
        briefing_content = call_groq_for_briefing(context)

    # Create briefing file
    today = datetime.now().strftime("%Y-%m-%d")
    briefings_path = VAULT_PATH / 'Briefings'
    briefings_path.mkdir(exist_ok=True)

    briefing_path = briefings_path / \
        f'{today}_Monday_Briefing.md'

    content = f'''---
generated: {datetime.now().isoformat()}
period: {(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")} to {today}
dry_run: {DRY_RUN}
---

# 📊 Monday Morning CEO Briefing
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

{briefing_content}

---

## 📈 Raw Stats This Week
- Items completed: {len(done_items)}
- Total actions: {len(weekly_logs)}
- Actions by type: {json.dumps(action_counts)}

---
*Generated by AI Employee v3.0 — Gold Tier*
'''

    briefing_path.write_text(content, encoding='utf-8')
    logger.info(f'CEO Briefing created: {briefing_path.name}')

    # Update dashboard
    dashboard_path = VAULT_PATH / 'Dashboard.md'
    if dashboard_path.exists():
        dashboard = dashboard_path.read_text(encoding='utf-8')
        dashboard += f'\n\n## 📊 Latest Briefing\nSee: Briefings/{briefing_path.name}'
        dashboard_path.write_text(dashboard, encoding='utf-8')

    return briefing_path

if __name__ == '__main__':
    path = generate_ceo_briefing()
    print(f'\n✅ CEO Briefing generated!')
    print(f'📁 Check Obsidian: Briefings/{path.name}')