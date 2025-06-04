#!/usr/bin/env python3
"""
Add metadata blocks to files that are missing them.
"""

import os
from datetime import datetime

def add_metadata_to_file(filepath, metadata_type="yaml"):
    """Add appropriate metadata block to a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Cannot read {filepath}: {e}")
        return False
    
    # Check if already has metadata
    if content.strip().startswith('---') or '> **Document Status:**' in content:
        print(f"✅ {filepath} already has metadata")
        return True
    
    filename = os.path.basename(filepath)
    
    # Generate appropriate metadata based on file type
    if filename == "README.md":
        if "archive" in filepath:
            metadata = """---
title: "Archive README"
type: guide
status: archived
created: "2024-01-01"
updated: "2024-01-01"
---

"""
        elif "experiments" in filepath:
            metadata = """---
title: "Experiments README"
type: guide
status: active
created: "2024-01-01"
updated: "2024-01-01"
---

"""
        elif "scripts" in filepath:
            metadata = """---
title: "Scripts README"
type: guide
status: active
created: "2024-01-01"
updated: "2024-01-01"
---

"""
        else:
            metadata = """---
title: "README"
type: guide
status: active
created: "2024-01-01"
updated: "2024-01-01"
---

"""
    elif "DOCUMENTATION_INDEX" in filename:
        metadata = """---
title: "Documentation Index"
type: guide
status: active
created: "2024-01-01"
updated: "2024-01-01"
---

"""
    elif "HANDOFF" in filename or "handoff" in filename.lower():
        metadata = """---
title: "Assistant Handoff"
type: guide
status: archived
created: "2024-01-01"
updated: "2024-01-01"
---

"""
    elif "cleanup" in filename.lower():
        metadata = """---
title: "Cleanup Documentation"
type: guide
status: archived
created: "2024-01-01"
updated: "2024-01-01"
---

"""
    else:
        # Generic metadata
        title = filename.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
        metadata = f"""---
title: "{title}"
type: guide
status: active
created: "2024-01-01"
updated: "2024-01-01"
---

"""
    
    # Add metadata to beginning of file
    new_content = metadata + content
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Added metadata to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Cannot write {filepath}: {e}")
        return False

def main():
    """Add metadata to files that need it."""
    files_needing_metadata = [
        "a2-docs/DOCUMENTATION_INDEX.md",
        "a2-docs/archive/2025-05-deprecated/process-documents/NEXT_ASSISTANT_HANDOFF.md",
        "a2-docs/archive/2025-05-deprecated/process-documents/cleanup.md",
        "a2-docs/archive/2025-05-deprecated/redundant-documents/README.md",
        "a2-docs/archive/2025-05-deprecated/redundant-documents/a2-bom-update.md",
        "a2-docs/archive/README.md",
        "a2-docs/experiments/README.md",
        "a2-docs/scripts/README.md"
    ]
    
    print("🔧 Adding metadata blocks to files...")
    
    success_count = 0
    for filepath in files_needing_metadata:
        if os.path.exists(filepath):
            if add_metadata_to_file(filepath):
                success_count += 1
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print(f"\n📊 Summary: {success_count}/{len(files_needing_metadata)} files updated")

if __name__ == "__main__":
    main() 