import shutil
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
import os

load_dotenv()

VAULT_PATH = os.getenv('VAULT_PATH', 'E:\\AI_Employee_Vault')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip hidden files and temp files
        if source.name.startswith('.') or source.name.startswith('~'):
            return

        logger.info(f'New file detected: {source.name}')
        
        if DRY_RUN:
            logger.info(f'[DRY RUN] Would process file: {source.name}')
        
        # Copy file to Needs_Action
        dest = self.needs_action / f'FILE_{source.name}'
        shutil.copy2(source, dest)
        
        # Create metadata file
        self.create_metadata(source)
        logger.info(f'Created action file for: {source.name}')

    def create_metadata(self, source: Path):
        meta_path = Path(VAULT_PATH) / 'Needs_Action' / f'FILE_{source.stem}.md'
        content = f'''---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size} bytes
received: {datetime.now().isoformat()}
status: pending
dry_run: {DRY_RUN}
---

## New File Received
A new file was dropped into the Inbox folder.

**File:** {source.name}
**Size:** {source.stat().st_size} bytes
**Received:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Suggested Actions
- [ ] Review file contents
- [ ] Determine required action
- [ ] Move to /Done when complete
'''
        meta_path.write_text(content, encoding='utf-8')

def start_filesystem_watcher():
    inbox_path = Path(VAULT_PATH) / 'Inbox'
    inbox_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f'Watching folder: {inbox_path}')
    logger.info(f'DRY_RUN mode: {DRY_RUN}')
    
    handler = DropFolderHandler(VAULT_PATH)
    observer = Observer()
    observer.schedule(handler, str(inbox_path), recursive=False)
    observer.start()
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info('File watcher stopped')
    observer.join()

if __name__ == '__main__':
    start_filesystem_watcher()