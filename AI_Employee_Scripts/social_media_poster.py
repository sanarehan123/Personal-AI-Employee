import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH',
    'E:\\Python Projects\\Personal AI Employee Hackathon 0\\AI_Employee_Vault'))
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_social_approval(
    post_content: str,
    platform: str,
    image_path: str = None
):
    """Create approval file for social media post"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    approval_path = VAULT_PATH / 'Pending_Approval' / \
        f'SOCIAL_{platform.upper()}_{timestamp}.md'

    content = f'''---
type: social_media_post
platform: {platform}
action: post
status: pending
created: {datetime.now().isoformat()}
image_path: {image_path or "none"}
dry_run: {DRY_RUN}
---

# {platform.title()} Post Approval Required

## Post Content
{post_content}

## Platform Details
- Platform: {platform.title()}
- Image: {image_path or "No image"}
- Character count: {len(post_content)}
- Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Instructions
- ✅ Move this file to /Approved to post
- ❌ Move this file to /Rejected to cancel

---
*Waiting for human approval*
'''
    approval_path.write_text(content, encoding='utf-8')
    logger.info(f'{platform} approval file created: {approval_path.name}')
    return approval_path

def post_to_facebook(post_content: str, image_path: str = None):
    """Post to Facebook Page using Graph API"""
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post to Facebook:\n{post_content}')
        return True

    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        logger.error('Facebook credentials not configured in .env')
        return False

    try:
        import requests
        url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed'
        data = {
            'message': post_content,
            'access_token': FACEBOOK_ACCESS_TOKEN
        }
        response = requests.post(url, data=data)
        result = response.json()

        if 'id' in result:
            logger.info(f'Posted to Facebook! Post ID: {result["id"]}')
            return True
        else:
            logger.error(f'Facebook post failed: {result}')
            return False

    except Exception as e:
        logger.error(f'Facebook posting error: {e}')
        return False

def post_to_instagram(post_content: str, image_path: str = None):
    """Post to Instagram using Instagrapi"""
    if DRY_RUN:
        logger.info(f'[DRY RUN] Would post to Instagram:\n{post_content}')
        return True

    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        logger.error('Instagram credentials not configured in .env')
        return False

    try:
        from instagrapi import Client
        cl = Client()
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

        if image_path and Path(image_path).exists():
            # Post with image
            media = cl.photo_upload(
                path=image_path,
                caption=post_content
            )
            logger.info(f'Posted to Instagram with image! ID: {media.id}')
        else:
            logger.warning('Instagram requires an image — skipping')
            return False

        return True

    except Exception as e:
        logger.error(f'Instagram posting error: {e}')
        return False

def watch_approved_social():
    """Watch /Approved folder for social media posts"""
    approved_path = VAULT_PATH / 'Approved'
    done_path = VAULT_PATH / 'Done'
    approved_path.mkdir(exist_ok=True)
    done_path.mkdir(exist_ok=True)

    logger.info('Watching for approved social media posts...')

    while True:
        try:
            for file in approved_path.glob('SOCIAL_*.md'):
                logger.info(f'Found approved social post: {file.name}')
                content = file.read_text(encoding='utf-8')

                # Detect platform
                platform = 'facebook'
                if 'INSTAGRAM' in file.name:
                    platform = 'instagram'

                # Extract post content
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

                # Post to platform
                if platform == 'facebook':
                    success = post_to_facebook(post_content)
                else:
                    success = post_to_instagram(post_content)

                if success:
                    done_file = done_path / file.name
                    file.rename(done_file)
                    logger.info(f'Social post completed: {file.name}')
                    log_action(
                        f'{platform}_post',
                        post_content[:100],
                        'success'
                    )
                else:
                    logger.error(f'Social post failed: {file.name}')

        except Exception as e:
            logger.error(f'Error watching approved posts: {e}')

        time.sleep(30)

def log_action(action_type: str, details: str, result: str):
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
    log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

if __name__ == '__main__':
    print("\n🤖 Social Media Poster")
    print("=" * 40)
    print("1. Create Facebook post")
    print("2. Create Instagram post")
    print("3. Watch for approved posts")
    print("4. Exit")

    choice = input("\nChoose option: ").strip()

    if choice in ["1", "2"]:
        platform = "facebook" if choice == "1" else "instagram"
        print(f"\nEnter your {platform.title()} post content:")
        print("(Press Enter twice when done)")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        post_content = '\n'.join(lines[:-1]).strip()

        if post_content:
            approval_file = create_social_approval(
                post_content, platform
            )
            print(f"\n✅ Approval file created!")
            print(f"📁 Check: Pending_Approval/{approval_file.name}")
            print(f"👉 Move to /Approved folder to post")
        else:
            print("❌ No content entered")

    elif choice == "3":
        watch_approved_social()