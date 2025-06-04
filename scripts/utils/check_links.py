#!/usr/bin/env python3
"""
A2 Robot Project - Link Checker Script

Validates all internal links in markdown documentation:
- Checks relative path links
- Validates section anchors
- Reports broken links
- Suggests fixes for common issues
"""

import os
import re
import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class LinkChecker:
    def __init__(self, base_directory):
        self.base_directory = Path(base_directory).resolve()
        self.broken_links = []
        self.warnings = []
        self.checked_files = set()
        
    def check_file(self, filepath):
        """Check all links in a single markdown file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.broken_links.append({
                'file': str(filepath),
                'error': f"Cannot read file: {e}",
                'line': 0
            })
            return
            
        self.checked_files.add(str(filepath))
        relative_path = os.path.relpath(filepath, self.base_directory)
        
        # Find all markdown links
        links = self._extract_links(content)
        
        for link_info in links:
            self._validate_link(filepath, relative_path, link_info)
            
    def _extract_links(self, content):
        """Extract all markdown links from content."""
        links = []
        lines = content.split('\n')
        
        # Pattern for markdown links: [text](url) or [text](url#anchor)
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(link_pattern, line)
            for match in matches:
                link_text = match.group(1)
                link_url = match.group(2)
                
                # Skip external links (http/https)
                if link_url.startswith(('http://', 'https://', 'mailto:')):
                    continue
                    
                links.append({
                    'text': link_text,
                    'url': link_url,
                    'line': line_num,
                    'full_line': line.strip()
                })
                
        return links
        
    def _validate_link(self, source_file, source_relative, link_info):
        """Validate a single link."""
        url = link_info['url']
        line_num = link_info['line']
        
        # Parse URL to separate path and anchor
        if '#' in url:
            file_path, anchor = url.split('#', 1)
        else:
            file_path = url
            anchor = None
            
        # Handle empty file path (same-file anchor)
        if not file_path:
            target_file = source_file
            target_relative = source_relative
        else:
            # Resolve relative path
            source_dir = os.path.dirname(source_file)
            target_file = os.path.normpath(os.path.join(source_dir, file_path))
            target_relative = os.path.relpath(target_file, self.base_directory)
            
        # Check if target file exists
        if not os.path.exists(target_file):
            self.broken_links.append({
                'file': source_relative,
                'line': line_num,
                'link': url,
                'error': f"Target file not found: {target_relative}",
                'suggestion': self._suggest_file_fix(file_path)
            })
            return
            
        # Check if target is a file (not directory)
        if os.path.isdir(target_file):
            self.warnings.append({
                'file': source_relative,
                'line': line_num,
                'link': url,
                'warning': f"Link points to directory, not file: {target_relative}"
            })
            return
            
        # Validate anchor if present
        if anchor:
            self._validate_anchor(source_relative, line_num, target_file, target_relative, anchor, url)
            
    def _validate_anchor(self, source_relative, line_num, target_file, target_relative, anchor, full_url):
        """Validate that an anchor exists in the target file."""
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.broken_links.append({
                'file': source_relative,
                'line': line_num,
                'link': full_url,
                'error': f"Cannot read target file {target_relative}: {e}"
            })
            return
            
        # Find all headers in target file
        headers = self._extract_headers(content)
        
        # Convert anchor to expected format (lowercase, hyphens)
        expected_anchor = self._normalize_anchor(anchor)
        
        # Check if anchor exists
        found = False
        for header in headers:
            if header['anchor'] == expected_anchor:
                found = True
                break
                
        if not found:
            # Try to find similar headers for suggestions
            suggestions = self._suggest_anchor_fix(expected_anchor, headers)
            
            self.broken_links.append({
                'file': source_relative,
                'line': line_num,
                'link': full_url,
                'error': f"Anchor '#{anchor}' not found in {target_relative}",
                'suggestion': f"Available anchors: {', '.join(['#' + h['anchor'] for h in headers[:5]])}" if headers else "No headers found",
                'similar': suggestions
            })
            
    def _extract_headers(self, content):
        """Extract all headers from markdown content."""
        headers = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                # Extract header text
                header_match = re.match(r'^(#{1,6})\s+(.+)', line.strip())
                if header_match:
                    level = len(header_match.group(1))
                    text = header_match.group(2).strip()
                    anchor = self._normalize_anchor(text)
                    
                    headers.append({
                        'level': level,
                        'text': text,
                        'anchor': anchor,
                        'line': line_num
                    })
                    
        return headers
        
    def _normalize_anchor(self, text):
        """Convert header text to anchor format."""
        # Remove markdown formatting
        text = re.sub(r'[*_`]', '', text)
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and special chars with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        # Remove leading/trailing hyphens
        text = text.strip('-')
        return text
        
    def _suggest_file_fix(self, broken_path):
        """Suggest fixes for broken file paths."""
        if not broken_path:
            return None
            
        # Look for similar files
        filename = os.path.basename(broken_path)
        directory = os.path.dirname(broken_path)
        
        # Search for files with similar names
        suggestions = []
        search_dir = os.path.join(self.base_directory, directory) if directory else self.base_directory
        
        if os.path.exists(search_dir):
            for file in os.listdir(search_dir):
                if file.endswith('.md') and self._similarity(filename, file) > 0.6:
                    suggestions.append(os.path.join(directory, file) if directory else file)
                    
        return suggestions[:3] if suggestions else None
        
    def _suggest_anchor_fix(self, broken_anchor, headers):
        """Suggest fixes for broken anchors."""
        suggestions = []
        for header in headers:
            if self._similarity(broken_anchor, header['anchor']) > 0.6:
                suggestions.append(header['anchor'])
                
        return suggestions[:3]
        
    def _similarity(self, a, b):
        """Calculate simple similarity between two strings."""
        if not a or not b:
            return 0
            
        # Simple Jaccard similarity
        set_a = set(a.lower())
        set_b = set(b.lower())
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0
        
    def get_results(self):
        """Get link checking results."""
        return {
            'broken_links': self.broken_links,
            'warnings': self.warnings,
            'checked_files': list(self.checked_files),
            'broken_count': len(self.broken_links),
            'warning_count': len(self.warnings),
            'files_checked': len(self.checked_files)
        }
        
    def print_results(self):
        """Print link checking results to console."""
        if self.broken_links:
            print("🔴 BROKEN LINKS:")
            for link in self.broken_links:
                print(f"  📄 {link['file']}:{link['line']}")
                print(f"     Link: {link['link']}")
                print(f"     Error: {link['error']}")
                if 'suggestion' in link and link['suggestion']:
                    if isinstance(link['suggestion'], list):
                        print(f"     Suggestions: {', '.join(link['suggestion'])}")
                    else:
                        print(f"     Suggestion: {link['suggestion']}")
                if 'similar' in link and link['similar']:
                    print(f"     Similar: {', '.join(['#' + s for s in link['similar']])}")
                print()
                
        if self.warnings:
            print("🟡 WARNINGS:")
            for warning in self.warnings:
                print(f"  📄 {warning['file']}:{warning['line']}")
                print(f"     Link: {warning['link']}")
                print(f"     Warning: {warning['warning']}")
                print()
                
        total_issues = len(self.broken_links) + len(self.warnings)
        if total_issues == 0:
            print(f"✅ All links valid! Checked {len(self.checked_files)} files.")
        else:
            print(f"📊 Summary: {len(self.broken_links)} broken links, {len(self.warnings)} warnings in {len(self.checked_files)} files")
            
        return len(self.broken_links) == 0  # Return True if no broken links

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
    parser = argparse.ArgumentParser(description='Check links in A2 Robot documentation')
    parser.add_argument('directory', nargs='?', default='a2-docs',
                       help='Directory to check (default: a2-docs)')
    parser.add_argument('--output', help='Output results to JSON file')
    parser.add_argument('--files', nargs='*', help='Specific files to check')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ Directory '{args.directory}' not found")
        sys.exit(1)
        
    checker = LinkChecker(args.directory)
    
    if args.files:
        # Check specific files
        files_to_check = args.files
    else:
        # Check all markdown files in directory
        files_to_check = find_markdown_files(args.directory)
        
    if not files_to_check:
        print("No markdown files found to check")
        sys.exit(0)
        
    print(f"🔍 Checking links in {len(files_to_check)} markdown files...")
    print()
    
    for filepath in files_to_check:
        checker.check_file(filepath)
        
    # Print results
    success = checker.print_results()
    
    # Save results if requested
    if args.output:
        results = checker.get_results()
        results['check_date'] = datetime.now().isoformat()
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Results saved to {args.output}")
        
    # Exit with error code if links are broken
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 