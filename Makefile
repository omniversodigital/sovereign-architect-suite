.PHONY: all test test-opa test-python run-gateway docker-build benchmark clean help

SHELL := cmd.exe
OPA := C:\Users\Admin\AppData\Local\Microsoft\WinGet\Links\opa.exe
PYTHON := C:\Python313\python.exe

all: test

help:
	@echo ========================================================
	@echo  SOVEREIGN ARCHITECT DEEP-TECH SUITE AUTOMATION
	@echo ========================================================
	@echo  make test         - Run all OPA policy tests and Python tests
	@echo  make test-opa     - Run OPA Rego policy test suite
	@echo  make test-python  - Run Python verification tests
	@echo  make run-gateway  - Start FastAPI policy-enforcing gateway
	@echo  make benchmark    - Benchmark sub-millisecond OPA evaluation
	@echo  make clean        - Remove temporary test caches and logs
	@echo ========================================================

test: test-opa test-python

test-opa:
	@echo [*] Running Open Policy Agent Rego test suite...
	"$(OPA)" test policy_engine -v

test-python:
	@echo [*] Running Python verification suite...
	"$(PYTHON)" fintech_algo/order_engine.py
	"$(PYTHON)" autonomous_uav/swarm_consensus.py

benchmark:
	@echo [*] Running sub-millisecond OPA policy benchmark...
	"$(OPA)" bench -d policy_engine/authz.rego "data.system.authz.allow"

run-gateway:
	@echo [*] Launching Sovereign Distributed Gateway on port 8080...
	"$(PYTHON)" distributed_core/gateway.py

clean:
	@echo [*] Cleaning environment...
	if exist __pycache__ rd /s /q __pycache__
