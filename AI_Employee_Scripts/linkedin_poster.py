import os
import logging
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH',
    'E:\\Python Projects\\Personal AI Employee Hackathon 0\\AI_Employee_Vault'))
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_linkedin_approval(post_content: str, post_type: str = "update"):
    """Create approval file for LinkedIn post"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    approval_path = VAULT_PATH / 'Pending_Approval' / f'LINKEDIN_{timestamp}.md'
    
    content = f'''---
type: linkedin_post
action: post
status: pending
created: {datetime.now().isoformat()}
expires: {datetime.now().isoformat()}
post_type: {post_type}
dry_run: {DRY_RUN}
---

# LinkedIn Post Approval Required

## Post Content
{post_content}

## Instructions
- ✅ Move this file to /Approved to post
- ❌ Move this file to /Rejected to cancel

## Post Details
- Type: {post_type}
- Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Character count: {len(post_content)}

---
*Waiting for human approval before posting*
'''
    
    approval_path.write_text(content, encoding='utf-8')
    logger.info(f'LinkedIn approval file created: {approval_path.name}')
    return approval_path

def post_to_linkedin(post_content: str):
    """Post to LinkedIn using Playwright"""
    
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post to LinkedIn:\n{post_content}')
        return True
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to LinkedIn
            logger.info('Opening LinkedIn...')
            page.goto('https://www.linkedin.com/feed/')
            page.wait_for_load_state('networkidle')
            
            # Check if logged in
            if 'login' in page.url or 'signin' in page.url:
                logger.info('Please log in to LinkedIn manually...')
                page.wait_for_url('**/feed/**', timeout=60000)
            
            # Click Start a post button
            logger.info('Creating post...')
            page.click('[aria-label="Start a post"]')
            page.wait_for_timeout(2000)
            
            # Type the post content
            page.keyboard.type(post_content)
            page.wait_for_timeout(1000)
            
            # Click Post button
            page.click('[aria-label="Post"]')
            page.wait_for_timeout(3000)
            
            logger.info('Posted to LinkedIn successfully!')
            browser.close()
            return True
            
    except Exception as e:
        logger.error(f'LinkedIn posting failed: {e}')
        return False

def watch_approved_linkedin():
    """Watch /Approved folder for LinkedIn posts"""
    import time
    
    approved_path = VAULT_PATH / 'Approved'
    done_path = VAULT_PATH / 'Done'
    approved_path.mkdir(exist_ok=True)
    done_path.mkdir(exist_ok=True)
    
    logger.info('Watching for approved LinkedIn posts...')
    
    while True:
        try:
            # Check for approved LinkedIn files
            for file in approved_path.glob('LINKEDIN_*.md'):
                logger.info(f'Found approved LinkedIn post: {file.name}')
                
                # Read the post content
                content = file.read_text(encoding='utf-8')
                
                # Extract post content from file
                lines = content.split('\n')
                post_start = False
                post_lines = []
                
                for line in lines:
                    if line.strip() == '## Post Content':
                        post_start = True
                        continue
                    if post_start and line.strip().startswith('##'):
                        break
                    if post_start:
                        post_lines.append(line)
                
                post_content = '\n'.join(post_lines).strip()
                
                # Post to LinkedIn
                success = post_to_linkedin(post_content)
                
                if success:
                    # Move to Done
                    done_file = done_path / file.name
                    file.rename(done_file)
                    logger.info(f'LinkedIn post completed: {file.name}')
                    
                    # Log the action
                    log_action('linkedin_post', post_content[:100], 'success')
                else:
                    logger.error(f'LinkedIn post failed: {file.name}')
                    
        except Exception as e:
            logger.error(f'Error watching approved posts: {e}')
        
        time.sleep(30)

def log_action(action_type: str, details: str, result: str):
    """Log action to daily log"""
    log_file = VAULT_PATH / 'Logs' / \
        f'{datetime.now().strftime("%Y-%m-%d")}.json'
    
    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        except:
            logs = []
    
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": "ai_employee",
        "details": details,
        "dry_run": DRY_RUN,
        "result": result
    })
    
    log_file.write_text(
        json.dumps(logs, indent=2),
        encoding='utf-8'
    )

if __name__ == '__main__':
    print("\n🤖 LinkedIn Auto-Poster")
    print("=" * 40)
    print("1. Create a new post")
    print("2. Watch for approved posts")
    print("3. Exit")
    
    choice = input("\nChoose option: ").strip()
    
    if choice == "1":
        print("\nEnter your LinkedIn post content:")
        print("(Press Enter twice when done)")
        lines = []
        while True:
            line = input()
            if line == "":
                if lines and lines[-1] == "":
                    break
            lines.append(line)
        
        post_content = '\n'.join(lines[:-1])
        
        if post_content.strip():
            approval_file = create_linkedin_approval(post_content)
            print(f"\n✅ Approval file created!")
            print(f"📁 Check Obsidian: Pending_Approval/{approval_file.name}")
            print(f"👉 Move to /Approved folder to post")
        else:
            print("❌ No content entered")
            
    elif choice == "2":
        watch_approved_linkedin()
    
    elif choice == "3":
        print("Goodbye!")