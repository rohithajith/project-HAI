# Agent Flow Test Script

This script tests the flow of the agent system when different types of requests are made. It verifies that:

1. The supervisor agent correctly routes requests to the appropriate specialized agents
2. The specialized agents process the requests correctly
3. The appropriate dashboards receive notifications

## Requirements

Install the required dependencies:

```bash
pip install -r test_requirements.txt
```

## Usage

First, make sure the Flask server is running:

```bash
python backend/flask_app.py
```

Then, in a separate terminal, run the test script:

```bash
python backend/test_agent_flow.py
```

### Command Line Options

- `--server`: Server URL (default: http://localhost:5000)
- `--wait`: Wait time in seconds between sending a message and checking for updates (default: 180)

Example with custom options:

```bash
python backend/test_agent_flow.py --server http://localhost:5000 --wait 300
```

## Test Cases

The script tests three different scenarios:

1. **Towel Request**: Tests if a request for towels is correctly routed to the room service agent and notifications appear on the room service dashboard.
2. **Food Order Request**: Tests if a food order request is correctly routed to the room service agent and notifications appear on the room service dashboard.
3. **Maintenance Request**: Tests if a maintenance request is correctly routed to the maintenance agent and notifications appear on the admin dashboard.

## Output

The script generates a detailed report that includes:

- Summary of test results
- Detailed results for each test case
- Response and notification times
- Any errors encountered

The report is displayed in the console with color-coding and also saved to a text file for reference.

## Troubleshooting

If the tests fail, check the following:

1. Make sure the Flask server is running
2. Verify that the server URL is correct
3. Increase the wait time if the model is slow to respond
4. Check the error messages in the report for specific issues

## Example Report

```
======================================================
                AGENT FLOW TEST REPORT
======================================================

Test Run Time: 2025-04-02 18:15:30
Server URL: http://localhost:5000
Wait Time: 180 seconds

======= SUMMARY =======
Total Tests: 3
Passed Tests: 3
Failed Tests: 0
Success Rate: 100.00%

======= DETAILED RESULTS =======

Test #1: Towel Request - PASSED
  Start Time: 2025-04-02 18:10:30
  End Time: 2025-04-02 18:13:30
  Message: I am in room 101. I need extra towels please
  Expected Agent: room_service_agent
  Expected Dashboard: room_service
  Response Received: True
  Correct Agent Used: True
  Correct Dashboard Notified: True
  Response Time: 15.23 seconds
  Notification Time: 16.45 seconds

Test #2: Food Order Request - PASSED
  Start Time: 2025-04-02 18:13:35
  End Time: 2025-04-02 18:16:35
  Message: I am in room 102. I would like to order a burger and fries
  Expected Agent: room_service_agent
  Expected Dashboard: room_service
  Response Received: True
  Correct Agent Used: True
  Correct Dashboard Notified: True
  Response Time: 18.76 seconds
  Notification Time: 19.12 seconds

Test #3: Maintenance Request - PASSED
  Start Time: 2025-04-02 18:16:40
  End Time: 2025-04-02 18:19:40
  Message: I am in room 103. The sink in my bathroom is leaking
  Expected Agent: maintenance_agent
  Expected Dashboard: admin
  Response Received: True
  Correct Agent Used: True
  Correct Dashboard Notified: True
  Response Time: 14.89 seconds
  Notification Time: 15.32 seconds

======= CONCLUSION =======
All tests passed successfully! The agent system is working as expected.

======================================================