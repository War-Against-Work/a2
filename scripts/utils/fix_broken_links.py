#!/usr/bin/env python3
"""
Fix common broken link issues in markdown files.
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

def normalize_anchor(text: str) -> str:
    """Convert text to proper markdown anchor format."""
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\-]', '-', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text

def extract_headers(content: str) -> Dict[str, str]:
    """Extract all headers and their normalized anchors."""
    headers = {}
    
    # Find all headers
    header_pattern = r'^(#{1,6})\s+(.+)$'
    for match in re.finditer(header_pattern, content, re.MULTILINE):
        level = len(match.group(1))
        header_text = match.group(2).strip()
        
        # Remove markdown formatting from header text
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', header_text)  # Bold
        clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)       # Italic
        clean_text = re.sub(r'`([^`]+)`', r'\1', clean_text)         # Code
        clean_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_text)  # Links
        
        # Generate anchor
        anchor = normalize_anchor(clean_text)
        headers[header_text] = anchor
        
        # Also map the anchor to itself for exact matches
        headers[anchor] = anchor
    
    return headers

def find_similar_anchor(target: str, available: List[str]) -> str:
    """Find the most similar anchor from available options."""
    target_clean = normalize_anchor(target)
    
    # First try exact match
    for anchor in available:
        if normalize_anchor(anchor) == target_clean:
            return anchor
    
    # Try partial matches
    target_words = target_clean.split('-')
    best_match = ""
    best_score = 0
    
    for anchor in available:
        anchor_words = anchor.split('-')
        
        # Count matching words
        matches = sum(1 for word in target_words if word in anchor_words)
        score = matches / max(len(target_words), len(anchor_words))
        
        if score > best_score and score > 0.3:  # At least 30% similarity
            best_score = score
            best_match = anchor
    
    return best_match

def fix_links_in_file(filepath: str, dry_run: bool = False) -> int:
    """Fix broken links in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Extract headers from this file
        headers = extract_headers(content)
        available_anchors = list(headers.values())
        
        # Find all internal links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def fix_link(match):
            nonlocal changes_made
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links
            if link_url.startswith(('http://', 'https://', 'mailto:')):
                return match.group(0)
            
            # Skip file links (for now)
            if '/' in link_url and not link_url.startswith('#'):
                return match.group(0)
            
            # Handle anchor links
            if link_url.startswith('#'):
                anchor = link_url[1:]  # Remove #
                
                # Common fixes for anchor formatting
                fixes = [
                    # Remove special characters that don't belong in anchors
                    (r'[&]', '-'),
                    (r'[/]', '-'),
                    (r'[:]', ''),
                    (r'[+]', ''),
                    (r'[@]', ''),
                    (r'[()]', ''),
                    (r'["]', ''),
                    (r"[']", ''),
                    (r'[!]', ''),
                    (r'[?]', ''),
                    (r'[*]', ''),
                    (r'[✅]', ''),
                    (r'[⬅️]', ''),
                    (r'[🎉]', ''),
                    # Fix multiple hyphens
                    (r'-+', '-'),
                    # Remove leading/trailing hyphens
                    (r'^-+|-+$', ''),
                ]
                
                fixed_anchor = anchor
                for pattern, replacement in fixes:
                    fixed_anchor = re.sub(pattern, replacement, fixed_anchor)
                
                # Convert to lowercase
                fixed_anchor = fixed_anchor.lower()
                
                # If the fixed anchor is different and exists, use it
                if fixed_anchor != anchor and fixed_anchor in available_anchors:
                    changes_made += 1
                    return f'[{link_text}](#{fixed_anchor})'
                
                # Try to find a similar anchor
                if anchor not in available_anchors and fixed_anchor not in available_anchors:
                    similar = find_similar_anchor(anchor, available_anchors)
                    if similar:
                        changes_made += 1
                        return f'[{link_text}](#{similar})'
            
            return match.group(0)
        
        # Apply fixes
        content = re.sub(link_pattern, fix_link, content)
        
        # Write back if changes were made
        if changes_made > 0 and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed {changes_made} links in {filepath}")
        elif changes_made > 0 and dry_run:
            print(f"🔍 Would fix {changes_made} links in {filepath}")
        
        return changes_made
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description='Fix broken internal links in markdown files')
    parser.add_argument('--directory', default='a2-docs', help='Directory to process')
    parser.add_argument('--files', nargs='+', help='Specific files to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    
    files_to_process = []
    
    if args.files:
        files_to_process = args.files
    else:
        # Find all markdown files in directory
        for root, dirs, files in os.walk(args.directory):
            for file in files:
                if file.endswith('.md'):
                    files_to_process.append(os.path.join(root, file))
    
    total_changes = 0
    files_changed = 0
    
    print(f"🔧 {'Analyzing' if args.dry_run else 'Fixing'} broken links in {len(files_to_process)} files...")
    
    for filepath in files_to_process:
        changes = fix_links_in_file(filepath, args.dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1
    
    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(files_to_process)}")
    print(f"   Files with changes: {files_changed}")
    print(f"   Total link fixes: {total_changes}")
    
    if args.dry_run and total_changes > 0:
        print(f"\n💡 Run without --dry-run to apply these fixes")

if __name__ == '__main__':
    main() 