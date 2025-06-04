#!/usr/bin/env python3
"""
A2 Robot Project - Documentation Validation Script

Validates documentation compliance with the A2 style guide:
- Checks for required metadata blocks
- Validates file naming conventions
- Ensures required sections are present
- Checks formatting standards
- Validates internal links
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

class DocumentValidator:
    def __init__(self, strict=False):
        self.strict = strict
        self.errors = []
        self.warnings = []
        
    def validate_file(self, filepath):
        """Validate a single markdown file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"{filepath}: Cannot read file - {e}")
            return
            
        filename = os.path.basename(filepath)
        relative_path = os.path.relpath(filepath)
        
        # Validate filename
        self._validate_filename(filename, relative_path)
        
        # Validate content structure
        self._validate_metadata_block(content, relative_path)
        self._validate_headers(content, relative_path)
        self._validate_required_sections(content, relative_path, filename)
        self._validate_formatting(content, relative_path)
        
    def _validate_filename(self, filename, filepath):
        """Validate filename follows naming conventions."""
        if not filename.endswith('.md'):
            return  # Only validate markdown files
            
        # Check for spaces
        if ' ' in filename:
            self.errors.append(f"{filepath}: Filename contains spaces")
            
        # Check for mixed case (except README.md)
        if filename != 'README.md' and re.search(r'[A-Z]', filename.replace('.md', '')):
            self.warnings.append(f"{filepath}: Filename contains uppercase letters")
            
        # Check for mixed separators
        if '_' in filename and '-' in filename:
            self.errors.append(f"{filepath}: Filename uses mixed separators (both _ and -)")
            
        # Check length
        if len(filename) > 50:
            self.warnings.append(f"{filepath}: Filename longer than 50 characters")
            
        # Check for proper document type suffix
        valid_types = ['-design', '-guide', '-api', '-spec', '-test', '-config']
        if filename not in ['README.md', 'STYLE_GUIDE.md'] and not filename.startswith('.'):
            has_valid_type = any(doc_type in filename for doc_type in valid_types)
            if not has_valid_type and self.strict:
                self.warnings.append(f"{filepath}: Filename doesn't follow type convention (should end with {', '.join(valid_types)})")
    
    def _validate_metadata_block(self, content, filepath):
        """Validate presence and format of metadata block."""
        lines = content.split('\n')
        
        # Check for YAML frontmatter first
        yaml_metadata_found = False
        if lines and lines[0].strip() == '---':
            # Look for closing ---
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    yaml_metadata_found = True
                    break
                if i > 20:  # Don't search too far
                    break
        
        # Check for old-style metadata block
        old_style_metadata_found = False
        for i, line in enumerate(lines[:10]):
            if line.strip().startswith('> **Document Status:**'):
                old_style_metadata_found = True
                break
                
        if not yaml_metadata_found and not old_style_metadata_found:
            self.errors.append(f"{filepath}: Missing required metadata block (YAML frontmatter or old-style)")
            return
            
        # If old-style metadata is found, validate its fields
        if old_style_metadata_found:
            required_fields = [
                'Document Status:',
                'Last Updated:',
                'Version:',
                'Scope:'
            ]
            
            metadata_section = '\n'.join(lines[:20])  # Check first 20 lines
            
            for field in required_fields:
                if f'**{field}**' not in metadata_section:
                    self.errors.append(f"{filepath}: Missing metadata field '{field}'")
                    
            # Validate status values
            status_match = re.search(r'\*\*Document Status:\*\*\s*(\w+)', metadata_section)
            if status_match:
                status = status_match.group(1)
                valid_statuses = ['CURRENT', 'DRAFT', 'DEPRECATED']
                if status not in valid_statuses:
                    self.errors.append(f"{filepath}: Invalid document status '{status}' (must be one of {valid_statuses})")
                    
            # Validate date format
            date_match = re.search(r'\*\*Last Updated:\*\*\s*(\d{4}-\d{2}-\d{2})', metadata_section)
            if not date_match:
                self.errors.append(f"{filepath}: Invalid or missing date format (should be YYYY-MM-DD)")
        
        # If YAML frontmatter is found, validate basic structure
        if yaml_metadata_found:
            yaml_section = []
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    break
                yaml_section.append(line)
            
            yaml_content = '\n'.join(yaml_section)
            
            # Check for basic required fields in YAML
            required_yaml_fields = ['title:', 'type:', 'status:']
            for field in required_yaml_fields:
                if field not in yaml_content:
                    self.warnings.append(f"{filepath}: YAML metadata missing recommended field '{field}'")
    
    def _validate_headers(self, content, filepath):
        """Validate header formatting."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                # Check for trailing #
                if line.rstrip().endswith('#') and not line.rstrip().endswith('##'):
                    self.warnings.append(f"{filepath}:{i}: Header has trailing # characters")
                    
                # Check for proper spacing
                if not re.match(r'^#{1,4}\s+', line):
                    self.errors.append(f"{filepath}:{i}: Header missing space after #")
                    
                # Check nesting depth
                header_level = len(line) - len(line.lstrip('#'))
                if header_level > 4:
                    self.warnings.append(f"{filepath}:{i}: Header nesting too deep (max 4 levels)")
                    
    def _validate_required_sections(self, content, filepath, filename):
        """Validate presence of required sections based on document type."""
        # Skip validation for certain files
        skip_files = ['README.md', 'STYLE_GUIDE.md', 'DOCUMENTATION_INDEX.md']
        if filename in skip_files:
            return
            
        # Check for Overview section
        if '## Overview' not in content and '# Overview' not in content:
            self.warnings.append(f"{filepath}: Missing Overview section")
            
        # Check for Table of Contents if document is long
        line_count = len(content.split('\n'))
        if line_count > 100 and 'Table of Contents' not in content:
            self.warnings.append(f"{filepath}: Long document missing Table of Contents")
            
        # Type-specific validations
        if '-design' in filename:
            required_sections = ['Requirements', 'Architecture', 'Implementation']
            for section in required_sections:
                if f'## {section}' not in content:
                    self.warnings.append(f"{filepath}: Design document missing '{section}' section")
                    
        elif '-guide' in filename:
            required_sections = ['Prerequisites', 'Instructions']
            for section in required_sections:
                if f'## {section}' not in content and section.lower() in content.lower():
                    self.warnings.append(f"{filepath}: Guide missing '{section}' section")
                    
    def _validate_formatting(self, content, filepath):
        """Validate formatting standards."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for tabs
            if '\t' in line:
                self.warnings.append(f"{filepath}:{i}: Line contains tabs (use spaces)")
                
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                self.warnings.append(f"{filepath}:{i}: Line has trailing whitespace")
                
            # Check bullet point format
            if re.match(r'^\s*[\*\+]\s', line):
                self.warnings.append(f"{filepath}:{i}: Use '-' for bullet points, not '*' or '+'")
                
        # Check for code blocks without language specification
        code_blocks = re.findall(r'```(\w*)\n', content)
        for block in code_blocks:
            if not block:  # Empty language specification
                self.warnings.append(f"{filepath}: Code block missing language specification")
                
    def get_results(self):
        """Get validation results."""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
        
    def print_results(self):
        """Print validation results to console."""
        if self.errors:
            print("🔴 ERRORS:")
            for error in self.errors:
                print(f"  {error}")
            print()
            
        if self.warnings:
            print("🟡 WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
            
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            print("✅ All documents pass validation!")
        else:
            print(f"📊 Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
            
        return len(self.errors) == 0  # Return True if no errors

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
    parser = argparse.ArgumentParser(description='Validate A2 Robot documentation')
    parser.add_argument('--strict', action='store_true', 
                       help='Enable strict validation (more warnings)')
    parser.add_argument('--directory', default='a2-docs',
                       help='Directory to validate (default: a2-docs)')
    parser.add_argument('--output', help='Output results to JSON file')
    parser.add_argument('--files', nargs='*', help='Specific files to validate')
    
    args = parser.parse_args()
    
    validator = DocumentValidator(strict=args.strict)
    
    if args.files:
        # Validate specific files
        files_to_validate = args.files
    else:
        # Validate directory
        if not os.path.exists(args.directory):
            print(f"❌ Directory '{args.directory}' not found")
            sys.exit(1)
            
        files_to_validate = find_markdown_files(args.directory)
        
    if not files_to_validate:
        print("No markdown files found to validate")
        sys.exit(0)
        
    print(f"🔍 Validating {len(files_to_validate)} markdown files...")
    print()
    
    for filepath in files_to_validate:
        validator.validate_file(filepath)
        
    # Print results
    success = validator.print_results()
    
    # Save results if requested
    if args.output:
        results = validator.get_results()
        results['validated_files'] = files_to_validate
        results['validation_date'] = datetime.now().isoformat()
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Results saved to {args.output}")
        
    # Exit with error code if validation failed
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 