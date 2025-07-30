# Test Results Dashboard

This dashboard provides a comprehensive view of test results, including unit tests, integration tests, performance metrics, and code coverage.

## Features

- **Test Summary**: Overview of passed, failed, and skipped tests
- **Test Suites**: Detailed view of all test suites with individual test cases
- **Performance Metrics**: Response times, requests per second, and failure rates
- **Code Coverage**: Visual representation of test coverage
- **Historical Data**: Track test results over time

## Prerequisites

- Python 3.8+
- Node.js 14+ (for local development)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

## Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install JavaScript dependencies (for local development):
   ```bash
   cd dashboard
   npm install
   ```

## Usage

### Running Tests

Run the test suite using the following command:

```bash
# Run all tests
pytest

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run performance tests
locust -f tests/performance/test_performance.py
```

### Generating Test Reports

After running tests, generate the dashboard data:

```bash
python scripts/process_test_results.py
```

This will create a `dashboard/data/test_results.json` file with the latest test results.

### Viewing the Dashboard

#### Option 1: Local Development Server

1. Start the development server:
   ```bash
   cd dashboard
   python -m http.server 8000
   ```
2. Open your browser and navigate to `http://localhost:8000`

#### Option 2: Production Build (Docker)

1. Build the Docker image:
   ```bash
   docker build -t test-dashboard .
   ```
2. Run the container:
   ```bash
   docker run -p 80:80 test-dashboard
   ```
3. Open your browser and navigate to `http://localhost`

## Dashboard Features

### Test Summary

- **Total Tests**: The total number of tests executed
- **Passed**: Number of tests that passed successfully
- **Failed**: Number of tests that failed
- **Skipped**: Number of tests that were skipped
- **Duration**: Total execution time of all tests

### Test Suites

- Expand/collapse test suites to view individual test cases
- Color-coded test status (green for passed, red for failed, yellow for skipped)
- Detailed error messages for failed tests

### Performance Metrics

- **Response Times**: Graph of response times over time
- **Requests/Second**: Number of requests processed per second
- **95th Percentile**: 95th percentile response time
- **Failures**: Number of failed requests

### Code Coverage

- **Coverage Percentage**: Percentage of code covered by tests
- **Lines Covered**: Number of lines of code covered by tests
- **Total Lines**: Total number of lines of code

## CI/CD Integration

The dashboard is automatically updated as part of the CI/CD pipeline. Test results are published as artifacts and can be viewed in the GitHub Actions workflow.

## Customization

### Styling

To customize the dashboard's appearance, modify the CSS in `dashboard/static/css/styles.css`.

### Configuration

Dashboard behavior can be configured in `dashboard/static/js/config.js`.

## Troubleshooting

### No Test Results Found

If no test results are displayed:

1. Ensure tests have been run and the results are in the `test-results` directory
2. Check that the `process_test_results.py` script completed successfully
3. Verify that the `dashboard/data/test_results.json` file exists and contains valid JSON

### Performance Data Missing

If performance data is not showing:

1. Ensure Locust is installed: `pip install locust`
2. Run the performance tests: `locust -f tests/performance/test_performance.py`
3. Verify that the `test-results/performance/locust_stats.csv` file was generated

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
