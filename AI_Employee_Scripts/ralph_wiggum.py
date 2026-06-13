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
MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '10'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_pending_items() -> list:
    needs_action = VAULT_PATH / 'Needs_Action'
    return list(needs_action.glob('*.md'))

def move_to_done(file_path: Path):
    done_path = VAULT_PATH / 'Done' / file_path.name
    
    # If file already exists in Done, add timestamp to name
    if done_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        done_path = VAULT_PATH / 'Done' / new_name
    
    file_path.rename(done_path)
    logger.info(f'Moved to Done: {file_path.name}')

def process_item(file_path: Path) -> bool:
    """Process a single Needs_Action item"""
    try:
        content = file_path.read_text(encoding='utf-8')
        logger.info(f'Processing: {file_path.name}')

        if DRY_RUN:
            logger.info(f'[DRY RUN] Would process: {file_path.name}')
            # In dry run — simulate processing
            time.sleep(1)
            return True

        # Check file type from frontmatter
        if 'type: email' in content:
            logger.info(f'Email item — creating plan')
            from reasoning_engine import create_plan
            create_plan([{
                'filename': file_path.name,
                'content': content[:500]
            }])
            return True

        elif 'type: file_drop' in content:
            logger.info(f'File drop item — logging')
            return True

        return True

    except Exception as e:
        logger.error(f'Error processing {file_path.name}: {e}')
        return False

def ralph_wiggum_loop(
    task_description: str,
    max_iterations: int = MAX_ITERATIONS
):
    """
    Ralph Wiggum Loop — keeps working until all tasks complete.
    Named after the Stop hook pattern that prevents Claude from
    exiting until work is done.
    """
    logger.info('='*50)
    logger.info('🔄 Ralph Wiggum Loop Starting')
    logger.info(f'Task: {task_description}')
    logger.info(f'Max iterations: {max_iterations}')
    logger.info('='*50)

    iteration = 0
    total_processed = 0

    while iteration < max_iterations:
        iteration += 1
        logger.info(f'\n--- Iteration {iteration}/{max_iterations} ---')

        # Check for pending items
        pending_items = get_pending_items()
        logger.info(f'Pending items: {len(pending_items)}')

        if not pending_items:
            logger.info('✅ All tasks complete! Stopping loop.')
            break

        # Process each item
        processed_this_round = 0
        for item in pending_items:
            success = process_item(item)
            if success:
                move_to_done(item)
                processed_this_round += 1
                total_processed += 1

        logger.info(
            f'Processed {processed_this_round} items this round'
        )

        # Log state
        log_state(iteration, total_processed, len(pending_items))

        # Check if more items appeared
        remaining = get_pending_items()
        if not remaining:
            logger.info('✅ TASK_COMPLETE — No more items!')
            break

        logger.info(f'{len(remaining)} items remaining...')
        time.sleep(30)

    logger.info('='*50)
    logger.info(f'Loop finished after {iteration} iterations')
    logger.info(f'Total items processed: {total_processed}')
    logger.info('='*50)

    return total_processed

def log_state(iteration: int, processed: int, pending: int):
    state_file = VAULT_PATH / 'Plans' / 'ralph_wiggum_state.md'
    content = f'''---
updated: {datetime.now().isoformat()}
iteration: {iteration}
total_processed: {processed}
pending: {pending}
---

# 🔄 Ralph Wiggum Loop State

- **Iteration:** {iteration}
- **Total Processed:** {processed}
- **Still Pending:** {pending}
- **Last Update:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Status
{"✅ Running smoothly" if pending > 0 else "🏁 Complete!"}
'''
    state_file.write_text(content, encoding='utf-8')

if __name__ == '__main__':
    total = ralph_wiggum_loop(
        "Process all files in /Needs_Action, move to /Done when complete",
        max_iterations=10
    )
    print(f'\n✅ Ralph Wiggum loop complete!')
    print(f'📊 Total items processed: {total}')