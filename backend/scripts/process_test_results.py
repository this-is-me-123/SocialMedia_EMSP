#!/usr/bin/env python3
"""
Process test results and generate data for the test dashboard.
This script parses JUnit XML files, performance test results, and coverage data
to generate a consolidated JSON file for the dashboard.
"""
import os
import json
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics

# Configuration
TEST_RESULTS_DIR = Path("test-results")
DASHBOARD_DATA_DIR = Path("dashboard/data")
COVERAGE_FILE = "coverage.xml"
LOCUST_STATS_FILE = "test-results/performance/locust_stats.csv"
DASHBOARD_DATA_FILE = DASHBOARD_DATA_DIR / "test_results.json"


def parse_junit_xml(xml_file: Path) -> Dict[str, Any]:
    """Parse a JUnit XML file and return test results."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Handle both JUnit and xUnit formats
    if root.tag == "testsuites":
        return parse_junit_testsuites(root)
    elif root.tag == "testsuite":
        return parse_junit_testsuite(root)
    else:
        raise ValueError(f"Unsupported XML format in {xml_file}")


def parse_junit_testsuites(root: ET.Element) -> Dict[str, Any]:
    """Parse a testsuites element."""
    suites = []
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    
    for suite in root.findall(".//testsuite"):
        suite_result = parse_junit_testsuite(suite)
        suites.append(suite_result)
        
        total_tests += suite_result["total"]
        total_failures += suite_result["failures"]
        total_errors += suite_result.get("errors", 0)
        total_skipped += suite_result.get("skipped", 0)
        total_time += float(suite_result.get("time", 0))
    
    return {
        "name": "All Tests",
        "tests": total_tests,
        "failures": total_failures,
        "errors": total_errors,
        "skipped": total_skipped,
        "time": total_time,
        "test_suites": suites
    }


def parse_junit_testsuite(suite: ET.Element) -> Dict[str, Any]:
    """Parse a testsuite element."""
    name = suite.get("name", "Unnamed Suite")
    tests = int(suite.get("tests", 0))
    failures = int(suite.get("failures", 0))
    errors = int(suite.get("errors", 0))
    skipped = int(suite.get("skipped", 0))
    time = float(suite.get("time", 0))
    
    test_cases = []
    
    for testcase in suite.findall(".//testcase"):
        case_name = testcase.get("name", "Unnamed Test")
        class_name = testcase.get("classname", "")
        if class_name:
            case_name = f"{class_name}.{case_name}"
        
        time_taken = float(testcase.get("time", 0))
        
        # Check for failures, errors, or skips
        status = "passed"
        error_msg = None
        
        failure = testcase.find("failure")
        if failure is not None:
            status = "failed"
            error_msg = failure.get("message") or failure.text or "Test failed"
        
        error = testcase.find("error")
        if error is not None:
            status = "error"
            error_msg = error.get("message") or error.text or "Test error"
        
        skip = testcase.find("skipped")
        if skip is not None:
            status = "skipped"
        
        test_cases.append({
            "name": case_name,
            "status": status,
            "time": time_taken,
            "error": error_msg
        })
    
    return {
        "name": name,
        "tests": tests,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "time": time,
        "test_cases": test_cases
    }


def parse_locust_stats(csv_file: Path) -> Dict[str, Any]:
    """Parse Locust stats CSV file."""
    if not csv_file.exists():
        return {
            "response_times": [],
            "requests_per_second": 0,
            "failures": 0,
            "p95": 0
        }
    
    import csv
    
    response_times = []
    requests_per_second = 0
    failures = 0
    p95 = 0
    
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"] == "Aggregated":
                response_times.append(int(row["Average Response Time"]))
                requests_per_second = float(row["Requests/s"])
                failures = int(row["Failures/s"])
                p95 = int(row["95%\xef%bc\x85"])
                break
    
    return {
        "response_times": response_times,
        "requests_per_second": requests_per_second,
        "failures": failures,
        "p95": p95
    }


def parse_coverage(coverage_file: Path) -> Dict[str, Any]:
    """Parse coverage.xml file."""
    if not coverage_file.exists():
        return {
            "coverage_percent": 0,
            "lines_covered": 0,
            "lines_total": 0
        }
    
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    # Handle different coverage formats
    if root.tag == "coverage":
        line_rate = float(root.get("line-rate", 0))
        lines_covered = int(root.get("lines-covered", 0))
        lines_valid = int(root.get("lines-valid", 0))
    else:
        # Try to find coverage metrics in the XML
        metrics = root.find(".//metrics")
        if metrics is not None:
            line_rate = float(metrics.get("line-rate", 0))
            lines_covered = int(metrics.get("coveredstatements", 0))
            lines_valid = int(metrics.get("statements", 0))
        else:
            line_rate = 0.0
            lines_covered = 0
            lines_valid = 0
    
    return {
        "coverage_percent": round(line_rate * 100, 2),
        "lines_covered": lines_covered,
        "lines_total": lines_valid
    }


def process_test_results() -> Dict[str, Any]:
    """Process all test results and return a consolidated report."""
    # Create output directory if it doesn't exist
    DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize result structure
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "suites": [],
        "stats": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration": 0.0
        },
        "coverage": {},
        "performance": {}
    }
    
    # Process JUnit XML files
    junit_files = list(TEST_RESULTS_DIR.glob("**/*.xml"))
    for xml_file in junit_files:
        try:
            suite_result = parse_junit_xml(xml_file)
            
            # Add to results
            if "test_suites" in suite_result:
                # This is a combined result with multiple suites
                for suite in suite_result["test_suites"]:
                    result["suites"].append(suite)
                    
                    # Update stats
                    result["stats"]["total"] += suite["tests"]
                    result["stats"]["passed"] += (suite["tests"] - suite["failures"] - 
                                                suite.get("errors", 0) - suite.get("skipped", 0))
                    result["stats"]["failed"] += suite["failures"] + suite.get("errors", 0)
                    result["stats"]["skipped"] += suite.get("skipped", 0)
                    result["stats"]["duration"] += suite["time"]
            else:
                # Single test suite
                result["suites"].append(suite_result)
                
                # Update stats
                result["stats"]["total"] += suite_result["tests"]
                result["stats"]["passed"] += (suite_result["tests"] - suite_result["failures"] - 
                                            suite_result.get("errors", 0) - suite_result.get("skipped", 0))
                result["stats"]["failed"] += suite_result["failures"] + suite_result.get("errors", 0)
                result["stats"]["skipped"] += suite_result.get("skipped", 0)
                result["stats"]["duration"] += suite_result["time"]
                    
        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
    
    # Process coverage data
    result["coverage"] = parse_coverage(COVERAGE_FILE)
    
    # Process performance data
    result["performance"] = parse_locust_stats(LOCUST_STATS_FILE)
    
    return result


def save_dashboard_data(data: Dict[str, Any]) -> None:
    """Save dashboard data to a JSON file."""
    with open(DASHBOARD_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Dashboard data saved to {DASHBOARD_DATA_FILE}")


def main():
    """Main function to process test results and generate dashboard data."""
    print("Processing test results...")
    
    # Process all test results
    dashboard_data = process_test_results()
    
    # Save the results
    save_dashboard_data(dashboard_data)
    
    print("Done!")


if __name__ == "__main__":
    main()
