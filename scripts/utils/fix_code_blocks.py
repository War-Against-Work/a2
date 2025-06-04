#!/usr/bin/env python3
"""
Fix code blocks missing language specifications.
"""

import os
import re
from typing import List, Tuple

def detect_language_from_content(code_content: str) -> str:
    """Detect programming language from code content."""
    content = code_content.strip().lower()
    
    # Python indicators
    if any(keyword in content for keyword in [
        'def ', 'import ', 'from ', 'class ', 'if __name__', 'print(', 
        'python', '#!/usr/bin/env python', '#!/usr/bin/python'
    ]):
        return 'python'
    
    # Bash/shell indicators
    if any(indicator in content for indicator in [
        '#!/bin/bash', '#!/bin/sh', 'sudo ', 'apt-get', 'apt ', 'pip install',
        'npm ', 'cd ', 'ls ', 'mkdir', 'chmod', 'export ', 'echo $', '${', 'curl '
    ]):
        return 'bash'
    
    # YAML indicators
    if any(indicator in content for indicator in [
        'version:', 'services:', 'volumes:', 'environment:', 'ports:', 'image:',
        'depends_on:', 'networks:', 'build:', 'command:'
    ]) or re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*:\s*$', content, re.MULTILINE):
        return 'yaml'
    
    # JSON indicators
    if (content.strip().startswith('{') and content.strip().endswith('}')) or \
       (content.strip().startswith('[') and content.strip().endswith(']')) or \
       re.search(r'"[^"]*":\s*["\d\[\{]', content):
        return 'json'
    
    # C++/Arduino indicators
    if any(keyword in content for keyword in [
        '#include', 'void setup()', 'void loop()', 'digitalwrite', 'digitalread',
        'analogread', 'arduino', 'int main(', 'std::', 'cout <<'
    ]):
        return 'cpp'
    
    # HTML indicators
    if any(indicator in content for indicator in [
        '<!doctype', '<html', '<head>', '<body>', '<div', '<span', '<p>', '<a href'
    ]):
        return 'html'
    
    # XML indicators
    if content.startswith('<?xml') or re.search(r'<[a-zA-Z][^>]*>', content):
        return 'xml'
    
    # SQL indicators
    if any(keyword in content for keyword in [
        'select ', 'insert ', 'update ', 'delete ', 'create table', 'alter table',
        'drop table', 'from ', 'where ', 'join ', 'group by', 'order by'
    ]):
        return 'sql'
    
    # Markdown indicators
    if any(indicator in content for indicator in [
        '# ', '## ', '### ', '[', '](', '**', '*', '- ', '1. '
    ]):
        return 'markdown'
    
    # CSS indicators
    if any(indicator in content for indicator in [
        '{', '}', ':', ';', 'color:', 'background:', 'margin:', 'padding:'
    ]) and not content.startswith('{'):
        return 'css'
    
    # If we can't detect, return empty string
    return ''

def fix_code_blocks_in_content(content: str) -> Tuple[str, List[str]]:
    """Fix code blocks missing language specifications."""
    changes = []
    
    # Find all code blocks
    pattern = r'```(\w*)\n(.*?)\n```'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    # Process matches in reverse order to avoid offset issues
    for match in reversed(matches):
        current_lang = match.group(1)
        code_content = match.group(2)
        
        # Only process if no language is specified
        if not current_lang:
            detected_lang = detect_language_from_content(code_content)
            
            if detected_lang:
                # Replace the code block
                start, end = match.span()
                new_block = f'```{detected_lang}\n{code_content}\n```'
                content = content[:start] + new_block + content[end:]
                changes.append(f"Added '{detected_lang}' language to code block")
    
    return content, changes

def process_file(filepath: str, dry_run: bool = False) -> dict:
    """Process a single file to fix code blocks."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return {
            'file': filepath,
            'changes': [],
            'success': False,
            'error': str(e)
        }
    
    content, changes = fix_code_blocks_in_content(original_content)
    
    # Write back if changes were made and not dry run
    if changes and not dry_run:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            return {
                'file': filepath,
                'changes': changes,
                'success': False,
                'error': str(e)
            }
    
    return {
        'file': filepath,
        'changes': changes,
        'success': True
    }

def main():
    """Fix code blocks missing language specifications."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix code blocks missing language specifications')
    parser.add_argument('--directory', default='a2-docs', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--files', nargs='*', help='Specific files to process')
    
    args = parser.parse_args()
    
    # Collect files to process
    files_to_process = []
    
    if args.files:
        files_to_process = [f for f in args.files if f.endswith('.md')]
    else:
        for root, dirs, files in os.walk(args.directory):
            for file in files:
                if file.endswith('.md'):
                    files_to_process.append(os.path.join(root, file))
    
    if not files_to_process:
        print("No markdown files found to process.")
        return
    
    print(f"🔧 {'Analyzing' if args.dry_run else 'Processing'} {len(files_to_process)} markdown files...")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    total_changes = 0
    modified_files = 0
    
    for filepath in files_to_process:
        result = process_file(filepath, args.dry_run)
        
        if result['success']:
            if result['changes']:
                modified_files += 1
                total_changes += len(result['changes'])
                status = "Would fix" if args.dry_run else "Fixed"
                print(f"✅ {status} {result['file']}")
                for change in result['changes']:
                    print(f"   - {change}")
        else:
            print(f"❌ Error processing {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Summary
    action = "would be modified" if args.dry_run else "modified"
    print(f"\n📊 Summary: {modified_files} files {action} with {total_changes} total changes.")

if __name__ == '__main__':
    main() 