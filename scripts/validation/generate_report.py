#!/usr/bin/env python3
"""
Validation Report Generator
===========================
Generates consolidated validation reports from all validation components.

Usage:
    python generate_report.py [options]

Options:
    --workspace TYPE        Workspace type (personal or team, default: personal)
    --build-type TYPE       Build type (local or github, default: local)
    --output-dir DIR        Output directory (default: reports)
    --format FORMAT         Output format: markdown, json, both (default: both)
    --verbose               Enable verbose output

Components Integrated:
    - Secret configuration validation (validate-secrets.sh)
    - Pipeline output validation (validate-pipeline-outputs.sh)
    - Mock server verification (verify_mocks.py)
    - Newman test results (run_newman.sh)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ValidationReporter:
    """Generates consolidated validation reports."""

    def __init__(
        self,
        workspace: str = "personal",
        build_type: str = "local",
        output_dir: str = "reports",
        verbose: bool = False
    ):
        self.workspace = workspace
        self.build_type = build_type
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.timestamp = datetime.now()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str):
        """Print verbose log message."""
        if self.verbose:
            print(f"   {message}")

    def _parse_bash_validation_output(self, output: str, component: str) -> Dict:
        """Parse output from bash validation scripts."""

        # Extract pass/fail counts
        passed = 0
        failed = 0
        details = []

        for line in output.split('\n'):
            if '[PASS]' in line:
                passed += 1
                details.append({'status': 'pass', 'message': line.replace('[PASS]', '').strip()})
            elif '[FAIL]' in line:
                failed += 1
                details.append({'status': 'fail', 'message': line.replace('[FAIL]', '').strip()})
            elif '[INFO]' in line:
                details.append({'status': 'info', 'message': line.replace('[INFO]', '').strip()})

        # Extract summary
        status = "passed" if failed == 0 else "failed"

        return {
            'component': component,
            'status': status,
            'tests_total': passed + failed,
            'tests_passed': passed,
            'tests_failed': failed,
            'success_rate': (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
            'details': details
        }

    def _collect_secrets_validation(self) -> Optional[Dict]:
        """Collect results from secret configuration validation."""
        self._log("Collecting secret configuration validation results...")

        # Run validation script and capture output
        import subprocess

        try:
            result = subprocess.run(
                ['bash', 'tests/validate-secrets.sh'],
                capture_output=True,
                text=True,
                timeout=30
            )

            return self._parse_bash_validation_output(result.stdout, 'secrets')
        except Exception as e:
            self._log(f"Failed to collect secrets validation: {e}")
            return {
                'component': 'secrets',
                'status': 'error',
                'error': str(e),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

    def _collect_pipeline_validation(self) -> Optional[Dict]:
        """Collect results from pipeline output validation."""
        self._log("Collecting pipeline output validation results...")

        import subprocess

        try:
            result = subprocess.run(
                ['bash', 'tests/validate-pipeline-outputs.sh'],
                capture_output=True,
                text=True,
                timeout=60
            )

            return self._parse_bash_validation_output(result.stdout, 'pipeline')
        except Exception as e:
            self._log(f"Failed to collect pipeline validation: {e}")
            return {
                'component': 'pipeline',
                'status': 'error',
                'error': str(e),
                'tests_total': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }

    def _collect_mock_verification(self) -> Optional[Dict]:
        """Collect results from mock server verification."""
        self._log("Collecting mock server verification results...")

        # Check for recent mock verification JSON files
        json_files = sorted(self.output_dir.glob('mock-verification-*.json'))

        if not json_files:
            self._log("No mock verification results found")
            return None

        # Use most recent file
        latest_file = json_files[-1]

        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)

            # Aggregate results from all mocks
            total_passed = 0
            total_failed = 0

            for mock_name, mock_data in data.get('mocks', {}).items():
                total_passed += mock_data.get('passed', 0)
                total_failed += mock_data.get('failed', 0)

            total_tests = total_passed + total_failed
            status = "passed" if total_failed == 0 else "warning" if total_passed > 0 else "failed"

            return {
                'component': 'mocks',
                'status': status,
                'tests_total': total_tests,
                'tests_passed': total_passed,
                'tests_failed': total_failed,
                'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
                'mocks': data.get('mocks', {})
            }
        except Exception as e:
            self._log(f"Failed to parse mock verification: {e}")
            return None

    def _collect_newman_results(self) -> Optional[Dict]:
        """Collect results from Newman test execution."""
        self._log("Collecting Newman test results...")

        # Check for recent Newman JSON files
        json_files = sorted(self.output_dir.glob('newman-*.json'))

        if not json_files:
            self._log("No Newman test results found")
            return None

        # Use most recent file
        latest_file = json_files[-1]

        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)

            run = data.get('run', {})
            stats = run.get('stats', {})
            assertions = stats.get('assertions', {})
            requests = stats.get('requests', {})

            total = assertions.get('total', 0)
            failed = assertions.get('failed', 0)
            passed = total - failed

            status = "passed" if failed == 0 else "failed"

            return {
                'component': 'newman',
                'status': status,
                'tests_total': total,
                'tests_passed': passed,
                'tests_failed': failed,
                'success_rate': (passed / total * 100) if total > 0 else 0,
                'requests_total': requests.get('total', 0),
                'requests_failed': requests.get('failed', 0)
            }
        except Exception as e:
            self._log(f"Failed to parse Newman results: {e}")
            return None

    def aggregate_results(self) -> Dict:
        """Aggregate results from all validation components."""

        print(f"\n📊 Aggregating validation results...")

        results = {
            'timestamp': self.timestamp.isoformat(),
            'workspace': self.workspace,
            'build_type': self.build_type,
            'components': {}
        }

        # Collect from each component
        components = [
            ('secrets', self._collect_secrets_validation),
            ('pipeline', self._collect_pipeline_validation),
            ('mocks', self._collect_mock_verification),
            ('newman', self._collect_newman_results)
        ]

        for name, collector in components:
            data = collector()
            if data:
                results['components'][name] = data

        # Calculate summary
        total_tests = sum(c.get('tests_total', 0) for c in results['components'].values())
        total_passed = sum(c.get('tests_passed', 0) for c in results['components'].values())
        total_failed = sum(c.get('tests_failed', 0) for c in results['components'].values())

        results['summary'] = {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'status': 'passed' if total_failed == 0 else 'failed'
        }

        return results

    def generate_markdown(self, results: Dict) -> str:
        """Generate markdown report."""

        md = []

        # Header
        md.append("# C2M API V2 - Validation Report")
        md.append("")
        md.append(f"**Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"**Workspace**: {self.workspace.title()}")
        md.append(f"**Build Type**: {self.build_type.title()}")
        md.append("")

        # Summary
        summary = results['summary']
        status_icon = "✅" if summary['status'] == 'passed' else "❌"

        md.append("## Summary")
        md.append("")
        md.append(f"- **Status**: {status_icon} {summary['status'].upper()}")
        md.append(f"- **Total Tests**: {summary['total_tests']}")
        md.append(f"- **Passed**: {summary['passed']}")
        md.append(f"- **Failed**: {summary['failed']}")
        md.append(f"- **Success Rate**: {summary['success_rate']:.1f}%")
        md.append("")

        # Component details
        md.append("## Component Results")
        md.append("")

        for name, data in results['components'].items():
            status = data.get('status', 'unknown')
            icon = "✅" if status == 'passed' else "⚠️" if status == 'warning' else "❌"

            md.append(f"### {name.title()} {icon}")
            md.append("")
            md.append(f"- **Status**: {status.upper()}")
            md.append(f"- **Tests**: {data.get('tests_passed', 0)}/{data.get('tests_total', 0)} passed")

            if data.get('tests_failed', 0) > 0:
                md.append(f"- **Failed**: {data.get('tests_failed', 0)}")

            md.append(f"- **Success Rate**: {data.get('success_rate', 0):.1f}%")
            md.append("")

            # Add component-specific details
            if name == 'mocks' and 'mocks' in data:
                for mock_name, mock_data in data['mocks'].items():
                    md.append(f"**{mock_name.title()} Mock**:")
                    md.append(f"- URL: `{mock_data.get('url', 'N/A')}`")
                    md.append(f"- Endpoints Tested: {mock_data.get('endpoints_tested', 0)}")
                    md.append(f"- Passed: {mock_data.get('passed', 0)}")
                    md.append(f"- Failed: {mock_data.get('failed', 0)}")
                    md.append("")

            if name == 'newman':
                md.append(f"**Request Statistics**:")
                md.append(f"- Total Requests: {data.get('requests_total', 0)}")
                md.append(f"- Failed Requests: {data.get('requests_failed', 0)}")
                md.append("")

        # Footer
        md.append("---")
        md.append("")
        md.append("*Generated by C2M API V2 Post-Build Validation System*")
        md.append("")

        return '\n'.join(md)

    def generate_json(self, results: Dict) -> str:
        """Generate JSON report."""
        return json.dumps(results, indent=2)

    def save_reports(self, results: Dict, fmt: str = 'both'):
        """Save reports to files."""

        timestamp_str = self.timestamp.strftime('%Y%m%d-%H%M%S')
        base_name = f"validation-{timestamp_str}"

        if fmt in ['markdown', 'both']:
            md_file = self.output_dir / f"{base_name}.md"
            markdown = self.generate_markdown(results)
            md_file.write_text(markdown)
            print(f"   📝 Markdown report: {md_file}")

        if fmt in ['json', 'both']:
            json_file = self.output_dir / f"{base_name}.json"
            json_data = self.generate_json(results)
            json_file.write_text(json_data)
            print(f"   📄 JSON report: {json_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Generate consolidated validation reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--workspace',
        choices=['personal', 'team'],
        default='personal',
        help='Workspace type (default: personal)'
    )

    parser.add_argument(
        '--build-type',
        choices=['local', 'github'],
        default='local',
        help='Build type (default: local)'
    )

    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory (default: reports)'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'both'],
        default='both',
        help='Output format (default: both)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Create reporter
    reporter = ValidationReporter(
        workspace=args.workspace,
        build_type=args.build_type,
        output_dir=args.output_dir,
        verbose=args.verbose
    )

    # Aggregate results
    results = reporter.aggregate_results()

    # Save reports
    print(f"\n📋 Generating validation reports...")
    reporter.save_reports(results, args.format)

    # Print summary
    summary = results['summary']
    print(f"\n{'=' * 64}")
    if summary['status'] == 'passed':
        print(f"✅ Validation PASSED: {summary['passed']}/{summary['total_tests']} tests passed")
    else:
        print(f"❌ Validation FAILED: {summary['failed']}/{summary['total_tests']} tests failed")
    print(f"{'=' * 64}")
    print()

    # Exit with appropriate code
    sys.exit(0 if summary['status'] == 'passed' else 1)

if __name__ == '__main__':
    main()
