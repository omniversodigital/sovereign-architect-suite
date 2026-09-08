package system.authz

import future.keywords.in
import future.keywords.if

default allow := false

# Allow if request has valid authorization context and passes policy rules
allow if {
    is_valid_token
    not is_rate_limited
    has_permission
}

# Token validation
is_valid_token if {
    input.token.valid == true
    input.token.expires_at > time.now_ns() / 1000000000
}

# Rate limiting guard
is_rate_limited if {
    input.request_count > 1000
}

# Role-Based & Attribute-Based Access Control
has_permission if {
    input.user.role == "PrincipalArchitect"
}

has_permission if {
    input.user.role == "MissionOperator"
    input.action in ["telemetry:read", "swarm:status", "policy:eval"]
}

has_permission if {
    input.user.role in ["AlgoTrader", "QuantEngineer"]
    input.action in ["order:submit", "order:cancel", "market:telemetry"]
    input.execution_risk_level in ["LOW", "MEDIUM"]
}

# Sub-millisecond audit decision payload
decision_metadata := {
    "eval_timestamp_ns": time.now_ns(),
    "allowed": allow,
    "user_id": input.user.id,
    "action": input.action
}
