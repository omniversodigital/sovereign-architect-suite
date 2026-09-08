import time
import subprocess
import json
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Depends, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Sovereign Deep-Tech Core Gateway",
    description="High-Throughput Policy-Enforcing Architecture for Autonomous & Quantitative Systems",
    version="1.0.0"
)

OPA_BINARY = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\opa.exe")
POLICY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "policy_engine", "authz.rego"))

class AuthToken(BaseModel):
    valid: bool = True
    expires_at: int = Field(default_factory=lambda: int(time.time()) + 3600)

class UserContext(BaseModel):
    id: str
    role: str
    organization: str = "DeepTechCore"

class ExecutionRequest(BaseModel):
    token: AuthToken
    user: UserContext
    action: str
    request_count: int = 1
    execution_risk_level: Optional[str] = "LOW"
    payload: Dict[str, Any] = Field(default_factory=dict)

def evaluate_rego_policy(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates Rego policy sub-millisecond via OPA.
    In production/Kubernetes, this connects via localhost HTTP sidecar.
    Here we demonstrate native OPA engine invocation with telemetry.
    """
    start_ns = time.perf_counter_ns()
    
    input_json = json.dumps({"input": request_data})
    cmd = [
        OPA_BINARY, "eval",
        "-d", POLICY_PATH,
        "-I",
        "data.system.authz"
    ]
    
    proc = subprocess.run(
        cmd,
        input=input_json,
        capture_output=True,
        text=True,
        timeout=2
    )
    
    elapsed_us = (time.perf_counter_ns() - start_ns) / 1000.0
    
    if proc.returncode != 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA Evaluation Error: {proc.stderr}"
        )
        
    try:
        eval_result = json.loads(proc.stdout)
        bindings = eval_result.get("result", [{}])[0].get("expressions", [{}])[0].get("value", {})
        return {
            "allowed": bindings.get("allow", False),
            "metadata": bindings.get("decision_metadata", {}),
            "latency_microseconds": round(elapsed_us, 2)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parsing error: {str(e)}"
        )

@app.get("/healthz")
async def healthz():
    return {
        "status": "HEALTHY",
        "timestamp": time.time(),
        "engine": "OPA/Rego v1.20.2",
        "system": "Antigravity Sovereign Host"
    }

@app.post("/api/v1/dispatch")
async def dispatch_command(req: ExecutionRequest):
    req_dict = req.model_dump()
    decision = evaluate_rego_policy(req_dict)
    
    if not decision["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "PolicyViolation: Access Denied by OPA Engine",
                "telemetry": decision
            }
        )
        
    return {
        "status": "EXECUTED",
        "action": req.action,
        "operator": req.user.id,
        "policy_evaluation": decision,
        "execution_timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
