#!/usr/bin/env python3
"""
A2 Robot Project - Automated Formatting Fix Script

Automatically fixes common formatting issues:
- Removes trailing whitespace
- Converts bullet points from * to -
- Adds missing metadata blocks
- Fixes code block language specifications (basic cases)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

class DocumentFormatter:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.changes_made = []
        
    def fix_file(self, filepath):
        """Fix formatting issues in a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            print(f"❌ Cannot read {filepath}: {e}")
            return False
            
        content = original_content
        changes = []
        
        # Fix trailing whitespace
        lines = content.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            original_line = line
            line = line.rstrip()
            if original_line != line:
                changes.append(f"Line {i+1}: Removed trailing whitespace")
            fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        # Fix bullet points (* to -)
        bullet_pattern = r'^(\s*)\*(\s+)'
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.match(bullet_pattern, line):
                new_line = re.sub(bullet_pattern, r'\1-\2', line)
                if new_line != line:
                    lines[i] = new_line
                    changes.append(f"Line {i+1}: Changed * to - for bullet point")
        content = '\n'.join(lines)
        
        # Add metadata block if missing (for main docs, not prompts/archives)
        if self._should_add_metadata(filepath):
            if not self._has_metadata_block(content):
                metadata = self._generate_metadata_block(filepath)
                # Insert after title
                lines = content.split('\n')
                title_line = -1
                for i, line in enumerate(lines):
                    if line.startswith('# '):
                        title_line = i
                        break
                        
                if title_line >= 0:
                    lines.insert(title_line + 1, '')
                    lines.insert(title_line + 2, metadata)
                    content = '\n'.join(lines)
                    changes.append("Added missing metadata block")
        
        # Fix common code block language issues
        content = self._fix_code_blocks(content, changes)
        
        # Save changes if any were made
        if content != original_content:
            if not self.dry_run:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed {filepath}")
                    for change in changes:
                        print(f"   - {change}")
                except Exception as e:
                    print(f"❌ Cannot write {filepath}: {e}")
                    return False
            else:
                print(f"🔍 Would fix {filepath}:")
                for change in changes:
                    print(f"   - {change}")
                    
            self.changes_made.extend([(filepath, change) for change in changes])
            return True
        else:
            print(f"✅ No changes needed for {filepath}")
            return True
            
    def _should_add_metadata(self, filepath):
        """Determine if file should have metadata block."""
        # Skip certain file types
        skip_patterns = [
            'prompt', 'archive', 'README.md', 'STYLE_GUIDE.md', 
            'DOCUMENTATION_INDEX.md', 'cleanup.md'
        ]
        
        filepath_str = str(filepath).lower()
        return not any(pattern.lower() in filepath_str for pattern in skip_patterns)
        
    def _has_metadata_block(self, content):
        """Check if content already has metadata block."""
        return '> **Document Status:**' in content
        
    def _generate_metadata_block(self, filepath):
        """Generate appropriate metadata block."""
        filename = os.path.basename(filepath)
        
        # Determine document type and status
        if '-design' in filename:
            doc_type = 'Design Document'
        elif '-guide' in filename:
            doc_type = 'Implementation Guide'
        elif '-spec' in filename:
            doc_type = 'Technical Specification'
        elif '-api' in filename:
            doc_type = 'API Documentation'
        else:
            doc_type = 'Documentation'
            
        return f"""> **Document Status:** CURRENT  
> **Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
> **Version:** 1.0.0  
> **Scope:** Phase 1"""

    def _fix_code_blocks(self, content, changes):
        """Fix common code block language specification issues."""
        # Pattern for code blocks without language
        pattern = r'```\n'
        
        # Common patterns to detect language
        replacements = [
            (r'```\n(#!/usr/bin/env python|#!/usr/bin/python|import |from |def |class )', r'```python\n\1'),
            (r'```\n(#!/bin/bash|#!/bin/sh|\$ |sudo |apt |pip |npm )', r'```bash\n\1'),
            (r'```\n(\{|\[|"[^"]*":\s*)', r'```json\n\1'),
            (r'```\n([a-zA-Z_][a-zA-Z0-9_]*:\s*\n|\s*-\s+[a-zA-Z])', r'```yaml\n\1'),
            (r'```\n(<[^>]+>|<!DOCTYPE)', r'```html\n\1'),
            (r'```\n(SELECT |INSERT |UPDATE |DELETE |CREATE )', r'```sql\n\1'),
        ]
        
        original_content = content
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.MULTILINE)
            if new_content != content:
                changes.append("Fixed code block language specification")
                content = new_content
                break  # Only apply first match to avoid conflicts
                
        return content
        
    def get_summary(self):
        """Get summary of changes made."""
        if not self.changes_made:
            return "No changes made."
            
        files_changed = len(set(change[0] for change in self.changes_made))
        total_changes = len(self.changes_made)
        
        return f"Modified {files_changed} files with {total_changes} total changes."

def find_markdown_files(directory):
    """Find all markdown files in directory."""
    markdown_files = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common ignore patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
        
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
                
    return sorted(markdown_files)

def main():
    parser = argparse.ArgumentParser(description='Fix formatting issues in A2 Robot documentation')
    parser.add_argument('--directory', default='a2-docs',
                       help='Directory to fix (default: a2-docs)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--files', nargs='*', help='Specific files to fix')
    
    args = parser.parse_args()
    
    formatter = DocumentFormatter(dry_run=args.dry_run)
    
    if args.files:
        # Fix specific files
        files_to_fix = args.files
    else:
        # Fix all markdown files in directory
        if not os.path.exists(args.directory):
            print(f"❌ Directory '{args.directory}' not found")
            sys.exit(1)
            
        files_to_fix = find_markdown_files(args.directory)
        
    if not files_to_fix:
        print("No markdown files found to fix")
        sys.exit(0)
        
    action = "Checking" if args.dry_run else "Fixing"
    print(f"🔧 {action} {len(files_to_fix)} markdown files...")
    print()
    
    success_count = 0
    for filepath in files_to_fix:
        if formatter.fix_file(filepath):
            success_count += 1
            
    print()
    print(f"📊 Summary: {success_count}/{len(files_to_fix)} files processed successfully")
    print(formatter.get_summary())
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to apply these changes")

if __name__ == "__main__":
    main() 