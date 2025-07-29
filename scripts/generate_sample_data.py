#!/usr/bin/env python3
"""
Generate sample test data for the dashboard.
This script creates realistic test results for development and testing purposes.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Configuration
OUTPUT_DIR = Path("dashboard/data")
OUTPUT_FILE = OUTPUT_DIR / "test_results.json"

# Sample test data
test_suites = [
    "unit",
    "integration",
    "contract",
    "performance",
    "e2e",
    "security",
    "ui",
    "api"
]

test_cases = {
    "unit": [
        "test_user_creation",
        "test_post_validation",
        "test_authentication",
        "test_authorization",
        "test_serialization",
        "test_deserialization",
        "test_validation",
        "test_edge_cases"
    ],
    "integration": [
        "test_database_connection",
        "test_external_api",
        "test_service_integration",
        "test_data_flow",
        "test_error_handling",
        "test_concurrency"
    ],
    "contract": [
        "test_api_contract",
        "test_data_contract",
        "test_schema_validation",
        "test_version_compatibility"
    ],
    "performance": [
        "test_load_homepage",
        "test_api_response_time",
        "test_concurrent_users",
        "test_memory_usage",
        "test_cpu_utilization"
    ],
    "e2e": [
        "test_user_journey",
        "test_checkout_flow",
        "test_payment_processing",
        "test_email_notifications"
    ],
    "security": [
        "test_authentication",
        "test_authorization",
        "test_input_validation",
        "test_sql_injection",
        "test_xss_protection"
    ],
    "ui": [
        "test_layout_rendering",
        "test_responsive_design",
        "test_form_validation",
        "test_navigation"
    ],
    "api": [
        "test_endpoints",
        "test_request_validation",
        "test_response_format",
        "test_error_responses"
    ]
}

error_messages = [
    "AssertionError: Expected 200 but got 404",
    "TimeoutError: Request timed out after 5000ms",
    "ConnectionError: Could not connect to database",
    "ValidationError: Invalid input data",
    "PermissionError: User not authorized",
    "ValueError: Invalid parameter value",
    "TypeError: Cannot read property 'name' of undefined",
    "ReferenceError: function is not defined"
]

def generate_test_case(suite_name: str, test_name: str) -> Dict[str, Any]:
    """Generate a test case with random status and duration."""
    # 90% pass rate, 5% fail, 5% skip
    status = random.choices(
        ["passed", "failed", "skipped"],
        weights=[90, 5, 5],
        k=1
    )[0]
    
    # Random duration between 10ms and 2000ms
    duration = random.randint(10, 2000)
    
    test_case = {
        "name": test_name,
        "status": status,
        "time": duration
    }
    
    # Add error message for failed tests
    if status == "failed":
        test_case["error"] = random.choice(error_messages)
    
    return test_case

def generate_test_suite(suite_name: str) -> Dict[str, Any]:
    """Generate a test suite with random test cases."""
    # Get test cases for this suite
    cases = test_cases.get(suite_name, [])
    if not cases:
        # If no specific test cases for this suite, generate some
        num_cases = random.randint(5, 20)
        cases = [f"test_{suite_name}_{i+1}" for i in range(num_cases)]
    
    # Generate test cases
    test_cases_data = [
        generate_test_case(suite_name, case) for case in cases
    ]
    
    # Calculate suite statistics
    passed = sum(1 for tc in test_cases_data if tc["status"] == "passed")
    failed = sum(1 for tc in test_cases_data if tc["status"] == "failed")
    skipped = sum(1 for tc in test_cases_data if tc["status"] == "skipped")
    total = len(test_cases_data)
    duration = sum(tc["time"] for tc in test_cases_data)
    
    return {
        "name": f"{suite_name.capitalize()} Tests",
        "tests": total,
        "failures": failed,
        "errors": 0,
        "skipped": skipped,
        "time": duration / 1000,  # Convert to seconds
        "test_cases": test_cases_data
    }

def generate_performance_metrics() -> Dict[str, Any]:
    """Generate performance metrics."""
    # Generate response times (slightly randomized around a baseline)
    baseline = random.randint(50, 200)
    response_times = [
        max(10, baseline + random.randint(-20, 50)) 
        for _ in range(20)
    ]
    
    # Calculate 95th percentile
    sorted_times = sorted(response_times)
    p95 = sorted_times[int(len(sorted_times) * 0.95)]
    
    return {
        "response_times": response_times,
        "requests_per_second": random.uniform(10.5, 50.7),
        "failures": random.randint(0, 5),
        "p95": p95
    }

def generate_coverage() -> Dict[str, Any]:
    """Generate code coverage data."""
    coverage = random.uniform(70.0, 95.0)
    total_lines = random.randint(5000, 20000)
    covered_lines = int((coverage / 100) * total_lines)
    
    return {
        "coverage_percent": round(coverage, 2),
        "lines_covered": covered_lines,
        "lines_total": total_lines
    }

def generate_test_results() -> Dict[str, Any]:
    """Generate complete test results."""
    # Generate test suites
    suites = [generate_test_suite(suite) for suite in test_suites]
    
    # Calculate total statistics
    total_tests = sum(suite["tests"] for suite in suites)
    total_passed = sum(
        suite["tests"] - suite["failures"] - suite.get("errors", 0) - suite["skipped"] 
        for suite in suites
    )
    total_failed = sum(suite["failures"] + suite.get("errors", 0) for suite in suites)
    total_skipped = sum(suite["skipped"] for suite in suites)
    total_duration = sum(suite["time"] for suite in suites)
    
    # Generate performance and coverage data
    performance = generate_performance_metrics()
    coverage = generate_coverage()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "suites": suites,
        "stats": {
            "total": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "duration": total_duration
        },
        "coverage": coverage,
        "performance": performance
    }

def main():
    """Generate and save sample test results."""
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate test results
    test_results = generate_test_results()
    
    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"Sample test results generated: {OUTPUT_FILE}")
    print(f"Total tests: {test_results['stats']['total']}")
    print(f"Passed: {test_results['stats']['passed']}")
    print(f"Failed: {test_results['stats']['failed']}")
    print(f"Skipped: {test_results['stats']['skipped']}")
    print(f"Coverage: {test_results['coverage']['coverage_percent']}%")

if __name__ == "__main__":
    main()
