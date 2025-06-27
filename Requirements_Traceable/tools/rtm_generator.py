#!/usr/bin/env python3
"""
RTM Generator Tool for FY.WB.Midway Logistics Platform
Automated Requirements Traceability Matrix generation and analysis

This tool implements the traceability methodology specified in:
Development_Prompts/10_traceability_control.md

Features:
- Automated RTM generation from requirement documents
- Bidirectional traceability analysis
- Impact assessment for requirement changes
- Compliance mapping and verification
- Dependency graph generation
- Gap analysis and coverage reports
"""

import os
import csv
import yaml
import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Requirement:
    """Requirement data structure matching RTM schema"""
    id: str
    parent_id: str
    title: str
    description: str
    source_doc: str
    verification_method: str
    status: str
    created_date: str
    modified_date: str
    system_scope: str
    business_value: str
    risk_level: str
    owner: str
    dependencies: str
    test_id: str
    implementation_status: str

class RTMGenerator:
    """Requirements Traceability Matrix Generator"""
    
    def __init__(self, requirements_dir: str, output_dir: str):
        self.requirements_dir = Path(requirements_dir)
        self.output_dir = Path(output_dir)
        self.requirements: Dict[str, Requirement] = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_requirements_from_csv(self, csv_file: str) -> None:
        """Load requirements from existing RTM CSV file"""
        csv_path = Path(csv_file)
        if not csv_path.exists():
            logger.warning(f"CSV file not found: {csv_file}")
            return
            
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['ID']:  # Skip empty rows
                    req = Requirement(
                        id=row['ID'],
                        parent_id=row.get('Parent_ID', ''),
                        title=row.get('Title', ''),
                        description=row.get('Description', ''),
                        source_doc=row.get('Source_Doc', ''),
                        verification_method=row.get('Verification_Method', ''),
                        status=row.get('Status', ''),
                        created_date=row.get('Created_Date', ''),
                        modified_date=row.get('Modified_Date', ''),
                        system_scope=row.get('System_Scope', ''),
                        business_value=row.get('Business_Value', ''),
                        risk_level=row.get('Risk_Level', ''),
                        owner=row.get('Owner', ''),
                        dependencies=row.get('Dependencies', ''),
                        test_id=row.get('Test_ID', ''),
                        implementation_status=row.get('Implementation_Status', '')
                    )
                    self.requirements[req.id] = req
                    
        logger.info(f"Loaded {len(self.requirements)} requirements from {csv_file}")
    
    def analyze_impact(self, requirement_id: str) -> Dict[str, List[str]]:
        """Analyze impact of changes to a specific requirement"""
        if requirement_id not in self.requirements:
            return {'error': [f'Requirement {requirement_id} not found']}
        
        impact = {
            'direct_children': [],
            'dependent_requirements': [],
            'affected_systems': set(),
            'affected_tests': [],
            'compliance_impact': []
        }
        
        req = self.requirements[requirement_id]
        
        # Find direct children
        for other_id, other_req in self.requirements.items():
            if other_req.parent_id == requirement_id:
                impact['direct_children'].append(other_id)
        
        # Find dependent requirements
        for other_id, other_req in self.requirements.items():
            if other_req.dependencies and requirement_id in other_req.dependencies:
                impact['dependent_requirements'].append(other_id)
        
        # Analyze affected systems and tests
        all_affected = impact['direct_children'] + impact['dependent_requirements']
        for affected_id in all_affected:
            if affected_id in self.requirements:
                affected_req = self.requirements[affected_id]
                impact['affected_systems'].add(affected_req.system_scope)
                if affected_req.test_id:
                    impact['affected_tests'].append(affected_req.test_id)
        
        # Check compliance impact
        if any(comp in req.description.lower() for comp in ['pci', 'sox', 'gdpr', 'dot', 'fmcsa']):
            impact['compliance_impact'].append(f'Compliance requirement: {requirement_id}')
        
        # Convert set to list for JSON serialization
        impact['affected_systems'] = list(impact['affected_systems'])
        
        return impact
    
    def generate_coverage_report(self) -> Dict[str, any]:
        """Generate requirements coverage and gap analysis report"""
        report = {
            'total_requirements': len(self.requirements),
            'by_status': {},
            'by_system': {},
            'by_risk_level': {},
            'by_business_value': {},
            'verification_coverage': {},
            'test_coverage': {},
            'orphaned_requirements': [],
            'missing_dependencies': [],
            'compliance_coverage': {}
        }
        
        # Analyze by various dimensions
        for req in self.requirements.values():
            # Status distribution
            report['by_status'][req.status] = report['by_status'].get(req.status, 0) + 1
            
            # System distribution
            report['by_system'][req.system_scope] = report['by_system'].get(req.system_scope, 0) + 1
            
            # Risk level distribution
            report['by_risk_level'][req.risk_level] = report['by_risk_level'].get(req.risk_level, 0) + 1
            
            # Business value distribution
            report['by_business_value'][req.business_value] = report['by_business_value'].get(req.business_value, 0) + 1
            
            # Verification method coverage
            report['verification_coverage'][req.verification_method] = report['verification_coverage'].get(req.verification_method, 0) + 1
            
            # Test coverage
            if req.test_id:
                report['test_coverage']['with_tests'] = report['test_coverage'].get('with_tests', 0) + 1
            else:
                report['test_coverage']['without_tests'] = report['test_coverage'].get('without_tests', 0) + 1
            
            # Find orphaned requirements (no parent and no children)
            if not req.parent_id and req.id not in [r.parent_id for r in self.requirements.values() if r.parent_id]:
                report['orphaned_requirements'].append(req.id)
            
            # Check for missing dependencies
            if req.dependencies:
                deps = [dep.strip() for dep in req.dependencies.split(',') if dep.strip()]
                for dep in deps:
                    if dep not in self.requirements:
                        report['missing_dependencies'].append(f'{req.id} -> {dep}')
        
        # Compliance coverage analysis
        compliance_keywords = {
            'PCI DSS': ['pci', 'payment card', 'credit card'],
            'SOX': ['sox', 'sarbanes', 'financial reporting'],
            'GDPR': ['gdpr', 'data protection', 'privacy'],
            'DOT': ['dot', 'department of transportation'],
            'FMCSA': ['fmcsa', 'motor carrier', 'safety']
        }
        
        for compliance, keywords in compliance_keywords.items():
            count = 0
            for req in self.requirements.values():
                if any(keyword in req.description.lower() for keyword in keywords):
                    count += 1
            report['compliance_coverage'][compliance] = count
        
        return report
    
    def export_rtm_csv(self, filename: str) -> None:
        """Export RTM to CSV format"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = [
                'ID', 'Parent_ID', 'Title', 'Description', 'Source_Doc',
                'Verification_Method', 'Status', 'Created_Date', 'Modified_Date',
                'System_Scope', 'Business_Value', 'Risk_Level', 'Owner',
                'Dependencies', 'Test_ID', 'Implementation_Status'
            ]
            
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for req in sorted(self.requirements.values(), key=lambda x: x.id):
                writer.writerow({
                    'ID': req.id,
                    'Parent_ID': req.parent_id,
                    'Title': req.title,
                    'Description': req.description,
                    'Source_Doc': req.source_doc,
                    'Verification_Method': req.verification_method,
                    'Status': req.status,
                    'Created_Date': req.created_date,
                    'Modified_Date': req.modified_date,
                    'System_Scope': req.system_scope,
                    'Business_Value': req.business_value,
                    'Risk_Level': req.risk_level,
                    'Owner': req.owner,
                    'Dependencies': req.dependencies,
                    'Test_ID': req.test_id,
                    'Implementation_Status': req.implementation_status
                })
        
        logger.info(f"RTM exported to {output_path}")
    
    def generate_impact_report(self, requirement_id: str, filename: str) -> None:
        """Generate detailed impact analysis report"""
        impact = self.analyze_impact(requirement_id)
        
        report = {
            'requirement_id': requirement_id,
            'analysis_date': datetime.now().isoformat(),
            'impact_analysis': impact
        }
        
        if requirement_id in self.requirements:
            report['requirement_details'] = asdict(self.requirements[requirement_id])
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
        
        logger.info(f"Impact report for {requirement_id} exported to {output_path}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='RTM Generator for FY.WB.Midway Logistics Platform')
    parser.add_argument('--requirements-dir', required=True, help='Requirements directory path')
    parser.add_argument('--output-dir', required=True, help='Output directory path')
    parser.add_argument('--rtm-csv', help='Existing RTM CSV file to load')
    parser.add_argument('--export-csv', default='RTM_Generated.csv', help='Output CSV filename')
    parser.add_argument('--coverage-report', default='coverage_report.json', help='Coverage report filename')
    parser.add_argument('--impact-analysis', help='Requirement ID for impact analysis')
    parser.add_argument('--impact-report', default='impact_report.json', help='Impact report filename')
    
    args = parser.parse_args()
    
    # Initialize RTM generator
    rtm_gen = RTMGenerator(args.requirements_dir, args.output_dir)
    
    # Load existing RTM if provided
    if args.rtm_csv:
        rtm_gen.load_requirements_from_csv(args.rtm_csv)
    
    # Generate outputs
    rtm_gen.export_rtm_csv(args.export_csv)
    
    # Generate coverage report
    coverage = rtm_gen.generate_coverage_report()
    coverage_path = Path(args.output_dir) / args.coverage_report
    with open(coverage_path, 'w', encoding='utf-8') as file:
        json.dump(coverage, file, indent=2, ensure_ascii=False)
    logger.info(f"Coverage report exported to {coverage_path}")
    
    # Generate impact analysis if requested
    if args.impact_analysis:
        rtm_gen.generate_impact_report(args.impact_analysis, args.impact_report)
    
    logger.info("RTM generation completed successfully")

if __name__ == '__main__':
    main()