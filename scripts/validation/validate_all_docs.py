#!/usr/bin/env python3
"""
Comprehensive documentation validation for A2 project.
Checks consistency, dates, cross-references, and required content.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class A2DocValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.doc_dir = project_root / "a2-docs"
        self.errors = []
        self.warnings = []
        self.info = []
        
    def validate_all(self):
        """Run all validation checks."""
        print("🔍 A2 Documentation Validation")
        print("=" * 50)
        
        self.check_document_headers()
        self.check_outdated_content()
        self.check_cross_references()
        self.check_naming_conventions()
        self.generate_report()
        
    def check_document_headers(self):
        """Ensure all docs have proper headers."""
        required_pattern = r'> \*\*Document Status:\*\* (CURRENT|DRAFT|DEPRECATED)\s*\n> \*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}'
        
        for md_file in self.doc_dir.glob("*.md"):
            if md_file.name == "README.md":
                continue
                
            content = md_file.read_text()
            if not re.search(required_pattern, content):
                self.errors.append(f"{md_file.name}: Missing standard header")
                
            # Check if updated recently
            date_match = re.search(r'Last Updated:\*\* (\d{4}-\d{2}-\d{2})', content)
            if date_match:
                last_update = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                days_old = (datetime.now() - last_update).days
                if days_old > 30:
                    self.warnings.append(f"{md_file.name}: Not updated in {days_old} days")
                    
    def check_outdated_content(self):
        """Check for outdated technical content."""
        outdated_terms = {
            "single.*Arducam": "References single camera approach",
            "CSI.*cable.*gimbal": "References problematic CSI cable",
            "camera-only": "Mentions camera-only perception",
            "RTX 4080.*production.*LLM": "Suggests RTX 4080 for production LLM"
        }
        
        for md_file in self.doc_dir.glob("*.md"):
            content = md_file.read_text().lower()
            for pattern, description in outdated_terms.items():
                if re.search(pattern.lower(), content):
                    self.errors.append(f"{md_file.name}: {description}")
                    
    def check_cross_references(self):
        """Validate all markdown links."""
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for md_file in self.doc_dir.glob("*.md"):
            content = md_file.read_text()
            for match in re.finditer(link_pattern, content):
                link_text, link_path = match.groups()
                
                if link_path.startswith("http"):
                    continue
                    
                if link_path.startswith("#"):
                    continue
                    
                # Check relative path
                full_path = (md_file.parent / link_path.split("#")[0]).resolve()
                if not full_path.exists():
                    self.errors.append(f"{md_file.name}: Broken link to {link_path}")
                    
    def check_naming_conventions(self):
        """Ensure consistent file naming."""
        for md_file in self.doc_dir.glob("*.md"):
            name = md_file.stem
            
            # Check for underscores (should be hyphens)
            if "_" in name:
                self.warnings.append(f"{md_file.name}: Use hyphens not underscores")
                
            # Check for consistent suffixes
            expected_suffixes = ["-guide", "-design", "-spec", "-api", "-overview"]
            has_suffix = any(name.endswith(suffix) for suffix in expected_suffixes)
            
            if not has_suffix and name not in ["README", "master-document"]:
                self.info.append(f"{md_file.name}: Consider adding type suffix")
                
    def generate_report(self):
        """Generate validation report."""
        total_issues = len(self.errors) + len(self.warnings)
        
        if self.errors:
            print("\n❌ ERRORS (must fix):")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.warnings:
            print("\n⚠️  WARNINGS (should fix):")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        if self.info:
            print("\n💡 SUGGESTIONS:")
            for info in self.info:
                print(f"  - {info}")
                
        if total_issues == 0:
            print("\n✅ All documentation checks passed!")
        else:
            print(f"\n📊 Total issues: {total_issues}")
            
        # Generate health score
        doc_count = len(list(self.doc_dir.glob("*.md")))
        if doc_count > 0:
            health = max(0, 100 - (total_issues * 5))
            print(f"📈 Documentation Health Score: {health}%")

if __name__ == "__main__":
    validator = A2DocValidator(Path("/home/waragainstwork/A2"))
    validator.validate_all()