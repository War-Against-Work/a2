#!/usr/bin/env python3
"""Generate living documentation index for A2 project."""

import os
from pathlib import Path
from datetime import datetime
import re

def generate_index():
    """Generate DOCUMENTATION_INDEX.md"""
    doc_dir = Path("/home/waragainstwork/A2/a2-docs")
    
    categories = {
        "Architecture": ["-overview", "-architecture", "-design"],
        "Hardware": ["-spec", "-guide", "bill_of_materials"],
        "Software": ["-api", "-interface", "-implementation"],
        "Integration": ["-integration", "-plan"],
        "Testing": ["-test", "-validation"]
    }
    
    # Scan and categorize documents
    docs_by_category = {cat: [] for cat in categories}
    docs_by_category["Other"] = []
    
    for md_file in sorted(doc_dir.glob("*.md")):
        if md_file.name in ["README.md", "DOCUMENTATION_INDEX.md"]:
            continue
            
        categorized = False
        for category, patterns in categories.items():
            if any(pattern in md_file.name for pattern in patterns):
                docs_by_category[category].append(md_file)
                categorized = True
                break
                
        if not categorized:
            docs_by_category["Other"].append(md_file)
    
    # Generate index content
    content = f"""# A2 Robot Documentation Index

> **Auto-Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
> **Total Documents:** {sum(len(docs) for docs in docs_by_category.values())}

## Quick Links
- [Master Document](master-document.md) - Central hub
- [Implementation Guide](a2-implementation-guide.md) - Development roadmap
- [STT Integration Plan](stt-ros-integration-plan.md) - Speech system integration
- [GPU Strategy](gpu_compute_strategy.md) - Resource allocation

"""
    
    # Add categorized documents
    for category, docs in docs_by_category.items():
        if not docs:
            continue
            
        content += f"\n## {category}\n\n"
        content += "| Document | Status | Last Updated | Description |\n"
        content += "|----------|--------|--------------|-------------|\n"
        
        for doc in docs:
            # Extract metadata
            doc_content = doc.read_text()
            status = "Unknown"
            last_updated = "Unknown"
            
            status_match = re.search(r'Document Status:\*\* (\w+)', doc_content)
            if status_match:
                status = status_match.group(1)
                
            date_match = re.search(r'Last Updated:\*\* ([\d-]+)', doc_content)
            if date_match:
                last_updated = date_match.group(1)
                
            # Get first line as description
            for line in doc_content.split('\n'):
                if line.startswith('# ') and not line.startswith('# A2'):
                    first_line = line.strip('# ')
                    break
            else:
                first_line = doc.stem.replace('-', ' ').title()
            
            # Status emoji
            status_emoji = {
                "CURRENT": "✅",
                "DRAFT": "📝",
                "DEPRECATED": "⚠️"
            }.get(status, "❓")
            
            content += f"| [{doc.name}]({doc.name}) | {status_emoji} {status} | {last_updated} | {first_line[:50]}... |\n"
    
    # Add statistics section
    content += f"\n## Documentation Statistics\n\n"
    content += f"- **Total Documents**: {sum(len(docs) for docs in docs_by_category.values())}\n"
    content += f"- **Current**: {sum(1 for cat in docs_by_category.values() for doc in cat if 'CURRENT' in doc.read_text())}\n"
    content += f"- **Draft**: {sum(1 for cat in docs_by_category.values() for doc in cat if 'DRAFT' in doc.read_text())}\n"
    content += f"- **Deprecated**: {sum(1 for cat in docs_by_category.values() for doc in cat if 'DEPRECATED' in doc.read_text())}\n"
    
    content += "\n## Maintenance Notes\n\n"
    content += "This index is auto-generated. To update:\n"
    content += "```bash\n"
    content += "python3 scripts/utils/generate_doc_index.py\n"
    content += "```\n"
    
    # Save index
    index_path = doc_dir / "DOCUMENTATION_INDEX.md"
    index_path.write_text(content)
    print(f"✅ Generated: {index_path}")

if __name__ == "__main__":
    generate_index()