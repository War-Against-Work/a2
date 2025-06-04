#!/usr/bin/env python3
"""
A2 Robot Project - Documentation Inventory Generator

Scan all repositories and create a complete inventory of:
- All .md files with their last modified dates
- All scripts (*.py, *.sh) and their purposes
- All configuration files (*.yaml, *.json)
- Identify temporary/test files
- Flag inconsistencies in naming
"""

import os
import glob
import json
from datetime import datetime
from pathlib import Path
import re

def get_file_info(filepath):
    """Get file information including size, modification time, and basic content analysis."""
    try:
        stat = os.stat(filepath)
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # Try to read first few lines for content analysis
        content_preview = ""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:5]
                content_preview = ''.join(lines).strip()
        except:
            content_preview = "Binary or unreadable file"
            
        return {
            'size': size,
            'modified': mtime.strftime('%Y-%m-%d %H:%M:%S'),
            'preview': content_preview[:200] + "..." if len(content_preview) > 200 else content_preview
        }
    except Exception as e:
        return {
            'size': 0,
            'modified': 'Unknown',
            'preview': f'Error reading file: {e}'
        }

def is_temporary_file(filepath):
    """Identify if a file appears to be temporary or test-related."""
    temp_patterns = [
        r'test[_-]',
        r'tmp[_-]',
        r'temp[_-]',
        r'backup[_-]',
        r'old[_-]',
        r'_test\.',
        r'_tmp\.',
        r'_temp\.',
        r'_backup\.',
        r'_old\.',
        r'\.bak$',
        r'\.backup$',
        r'\.tmp$',
        r'\.temp$'
    ]
    
    filename = os.path.basename(filepath).lower()
    return any(re.search(pattern, filename) for pattern in temp_patterns)

def analyze_naming_consistency(filepaths):
    """Analyze naming patterns and flag inconsistencies."""
    issues = []
    
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        
        # Check for mixed case in markdown files
        if filepath.endswith('.md'):
            if re.search(r'[A-Z]', filename.replace('.md', '')):
                issues.append(f"Mixed case in markdown: {filepath}")
        
        # Check for spaces in filenames
        if ' ' in filename:
            issues.append(f"Spaces in filename: {filepath}")
            
        # Check for inconsistent separators
        if '_' in filename and '-' in filename:
            issues.append(f"Mixed separators: {filepath}")
    
    return issues

def scan_directory(base_path):
    """Scan directory for all relevant files."""
    inventory = {
        'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'base_path': str(base_path),
        'markdown_files': [],
        'scripts': [],
        'config_files': [],
        'temporary_files': [],
        'naming_issues': [],
        'summary': {}
    }
    
    # File patterns to scan
    patterns = {
        'markdown': '**/*.md',
        'python': '**/*.py',
        'shell': '**/*.sh',
        'yaml': '**/*.yaml',
        'yml': '**/*.yml',
        'json': '**/*.json'
    }
    
    all_files = []
    
    for pattern_name, pattern in patterns.items():
        files = list(Path(base_path).glob(pattern))
        all_files.extend([str(f) for f in files])
        
        for filepath in files:
            filepath_str = str(filepath)
            file_info = get_file_info(filepath_str)
            
            file_data = {
                'path': filepath_str,
                'relative_path': os.path.relpath(filepath_str, base_path),
                'name': filepath.name,
                'size': file_info['size'],
                'modified': file_info['modified'],
                'preview': file_info['preview'],
                'is_temporary': is_temporary_file(filepath_str)
            }
            
            if pattern_name == 'markdown':
                inventory['markdown_files'].append(file_data)
            elif pattern_name in ['python', 'shell']:
                inventory['scripts'].append(file_data)
            elif pattern_name in ['yaml', 'yml', 'json']:
                inventory['config_files'].append(file_data)
            
            if file_data['is_temporary']:
                inventory['temporary_files'].append(file_data)
    
    # Analyze naming consistency
    inventory['naming_issues'] = analyze_naming_consistency(all_files)
    
    # Generate summary
    inventory['summary'] = {
        'total_markdown': len(inventory['markdown_files']),
        'total_scripts': len(inventory['scripts']),
        'total_configs': len(inventory['config_files']),
        'total_temporary': len(inventory['temporary_files']),
        'naming_issues_count': len(inventory['naming_issues']),
        'repositories_scanned': len([d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d.startswith('a2-')])
    }
    
    return inventory

def generate_report(inventory, output_file):
    """Generate a human-readable report."""
    with open(output_file, 'w') as f:
        f.write("# A2 Robot Project - Documentation Inventory Report\n\n")
        f.write(f"**Generated:** {inventory['scan_date']}  \n")
        f.write(f"**Base Path:** {inventory['base_path']}  \n\n")
        
        # Summary
        f.write("## Summary\n\n")
        summary = inventory['summary']
        f.write(f"- **Markdown Files:** {summary['total_markdown']}\n")
        f.write(f"- **Scripts:** {summary['total_scripts']}\n")
        f.write(f"- **Config Files:** {summary['total_configs']}\n")
        f.write(f"- **Temporary Files:** {summary['total_temporary']}\n")
        f.write(f"- **Naming Issues:** {summary['naming_issues_count']}\n")
        f.write(f"- **Repositories Scanned:** {summary['repositories_scanned']}\n\n")
        
        # Markdown Files
        f.write("## Markdown Documentation Files\n\n")
        f.write("| File | Size | Last Modified | Status |\n")
        f.write("|------|------|---------------|--------|\n")
        
        for doc in sorted(inventory['markdown_files'], key=lambda x: x['relative_path']):
            status = "🔴 TEMP" if doc['is_temporary'] else "✅ OK"
            f.write(f"| `{doc['relative_path']}` | {doc['size']} bytes | {doc['modified']} | {status} |\n")
        
        # Scripts
        f.write("\n## Scripts\n\n")
        f.write("| Script | Size | Last Modified | Purpose | Status |\n")
        f.write("|--------|------|---------------|---------|--------|\n")
        
        for script in sorted(inventory['scripts'], key=lambda x: x['relative_path']):
            # Try to extract purpose from first line or filename
            purpose = "Unknown"
            if script['preview']:
                lines = script['preview'].split('\n')
                for line in lines:
                    if line.strip().startswith('#') and len(line.strip()) > 1:
                        purpose = line.strip()[1:].strip()[:50]
                        break
            
            status = "🔴 TEMP" if script['is_temporary'] else "✅ OK"
            f.write(f"| `{script['relative_path']}` | {script['size']} bytes | {script['modified']} | {purpose} | {status} |\n")
        
        # Config Files
        f.write("\n## Configuration Files\n\n")
        f.write("| Config | Size | Last Modified | Status |\n")
        f.write("|--------|------|---------------|--------|\n")
        
        for config in sorted(inventory['config_files'], key=lambda x: x['relative_path']):
            status = "🔴 TEMP" if config['is_temporary'] else "✅ OK"
            f.write(f"| `{config['relative_path']}` | {config['size']} bytes | {config['modified']} | {status} |\n")
        
        # Temporary Files
        if inventory['temporary_files']:
            f.write("\n## 🔴 Temporary Files (Need Review)\n\n")
            for temp_file in sorted(inventory['temporary_files'], key=lambda x: x['relative_path']):
                f.write(f"- `{temp_file['relative_path']}` ({temp_file['size']} bytes, modified {temp_file['modified']})\n")
        
        # Naming Issues
        if inventory['naming_issues']:
            f.write("\n## 🔴 Naming Consistency Issues\n\n")
            for issue in inventory['naming_issues']:
                f.write(f"- {issue}\n")
        
        f.write("\n---\n")
        f.write("*This report was generated automatically by the A2 documentation cleanup process.*\n")

def main():
    """Main execution function."""
    base_path = os.getcwd()
    
    print("🔍 Scanning A2 Robot Project for documentation inventory...")
    inventory = scan_directory(base_path)
    
    # Save JSON data
    json_output = os.path.join(base_path, 'scripts', 'doc_inventory.json')
    with open(json_output, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    # Generate human-readable report
    report_output = os.path.join(base_path, 'scripts', 'DOC_INVENTORY_REPORT.md')
    generate_report(inventory, report_output)
    
    print(f"✅ Inventory complete!")
    print(f"📊 JSON data: {json_output}")
    print(f"📋 Report: {report_output}")
    print(f"\n📈 Summary:")
    print(f"   - {inventory['summary']['total_markdown']} markdown files")
    print(f"   - {inventory['summary']['total_scripts']} scripts")
    print(f"   - {inventory['summary']['total_configs']} config files")
    print(f"   - {inventory['summary']['total_temporary']} temporary files")
    print(f"   - {inventory['summary']['naming_issues_count']} naming issues")

if __name__ == "__main__":
    main() 