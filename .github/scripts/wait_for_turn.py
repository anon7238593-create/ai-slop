#!/usr/bin/env python3
"""
Workflow Run Serializer
=======================
Ensures that all GitHub Actions workflows run sequentially one by one,
preventing GitHub Actions concurrency cancellations and eliminating race
conditions on the shared artifacts branch.
"""

import json
import os
import subprocess
import sys
import time

VISUALIZATION_WORKFLOWS = {
    "Generate ball collision videos",
    "Generate GCD grid visualizations",
    "Generate Voronoi diagrams",
    "Generate traversal PDFs",
}


def get_active_runs(max_retries=5):
    for attempt in range(1, max_retries + 1):
        try:
            res = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--limit",
                    "50",
                    "--json",
                    "databaseId,workflowName,status,createdAt",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(res.stdout)
        except Exception as err:
            print(f"Notice: attempt {attempt}/{max_retries} to query gh run list failed: {err}")
            if attempt < max_retries:
                time.sleep(4)
    return []


def wait_for_turn():
    run_id_str = os.environ.get("GITHUB_RUN_ID")
    if not run_id_str:
        print("Not running in GitHub Actions (GITHUB_RUN_ID not set); skipping serialization.")
        return

    my_id = int(run_id_str)
    my_workflow = os.environ.get("GITHUB_WORKFLOW", "Unknown")
    print(f"Workflow serialization active for '{my_workflow}' (Run #{my_id})")

    max_wait_seconds = 1800  # 30 minutes
    start_time = time.time()
    poll_interval = 12

    while True:
        runs = get_active_runs()
        if not runs:
            print("Notice: No run data returned; proceeding to prevent stalling.")
            break

        elapsed = int(time.time() - start_time)

        # In-progress predecessors (always wait)
        in_progress_preds = [
            r
            for r in runs
            if r.get("workflowName") in VISUALIZATION_WORKFLOWS
            and r.get("status") == "in_progress"
            and int(r.get("databaseId", 0)) < my_id
        ]

        # Queued predecessors (wait only during the first 3 minutes to allow runner startup)
        queued_preds = []
        if elapsed < 180:
            queued_preds = [
                r
                for r in runs
                if r.get("workflowName") in VISUALIZATION_WORKFLOWS
                and r.get("status") in ("queued", "waiting", "requested", "pending")
                and int(r.get("databaseId", 0)) < my_id
            ]

        predecessors = in_progress_preds + queued_preds

        if not predecessors:
            print(f"Queue lock acquired after {elapsed}s! No earlier workflow is active. Proceeding.")
            break

        details = [
            f"{p.get('workflowName')} (#{p.get('databaseId')}, {p.get('status')})"
            for p in predecessors
        ]
        print(f"[{elapsed}s elapsed] Waiting for earlier workflow(s) to finish: {', '.join(details)}...")

        if elapsed > max_wait_seconds:
            print(f"Warning: Maximum wait timeout ({max_wait_seconds}s) reached. Proceeding.")
            break

        time.sleep(poll_interval)


if __name__ == "__main__":
    wait_for_turn()

