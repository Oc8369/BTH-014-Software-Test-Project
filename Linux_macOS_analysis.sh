#!/bin/bash

echo "============================================"
echo "Running hash comparison for all test modules"
echo "============================================"
echo

echo "[Boundary Test] Comparing Test Results of different Python versions..."
python tools/analysis.py blackbox_test/boundary/result_different_python_version res python
echo

echo "[Boundary Test] Comparing Test Results of different System versions..."
python tools/analysis.py blackbox_test/boundary/result_different_system_version res system
echo

echo "[ECP Test] Comparing Test Results of different Python versions..."
python tools/analysis.py blackbox_test/ecp/result_different_python_version res python
echo

echo "[ECP Test] Comparing Test Results of different System versions..."
python tools/analysis.py blackbox_test/ecp/result_different_system_version res system
echo

echo "[Fuzzing Test] Comparing Test Results of different Python versions..."
python tools/analysis.py blackbox_test/fuzzing/result_different_python_version res python
echo

echo "[Fuzzing Test] Comparing Test Results of different System versions..."
python tools/analysis.py blackbox_test/fuzzing/result_different_system_version res system
echo

echo "[State Machine Test] Comparing Test Results of different Python versions..."
python tools/analysis.py blackbox_test/state_machine/result_different_python_version res python
echo

echo "[State Machine Test] Comparing Test Results of different System versions..."
python tools/analysis.py blackbox_test/state_machine/result_different_system_version res system
echo

echo "[All-Def Test] Comparing Test Results of different Python versions..."
python tools/analysis.py whitebox_test/all_defs/result_different_python_version res python
echo

echo "[All-Def Test] Comparing Test Results of different System versions..."
python tools/analysis.py whitebox_test/all_defs/result_different_system_version res system
echo

echo "[Coverage Test] Comparing Test Results of different Python versions..."
python tools/analysis.py whitebox_test/statement_coverage_and_branch_coverage/result_different_python_version res python
echo

echo "[Coverage Test] Comparing Test Results of different System versions..."
python3 tools/analysis.py whitebox_test/statement_coverage_and_branch_coverage/result_different_system_version res system
echo

echo "All hash comparisons completed."
read -p "Press Enter to exit..."
