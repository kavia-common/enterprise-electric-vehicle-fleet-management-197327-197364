#!/bin/bash
cd /home/kavia/workspace/code-generation/enterprise-electric-vehicle-fleet-management-197327-197364/iot_ev_fleet_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

