package system.authz_test

import future.keywords.if
import data.system.authz

# Test Principal Architect full authorization
test_principal_architect_allowed if {
    authz.allow with input as {
        "token": {"valid": true, "expires_at": 9999999999},
        "request_count": 10,
        "user": {"id": "usr_001", "role": "PrincipalArchitect"},
        "action": "system:reconfigure"
    }
}

# Test Mission Operator permitted action
test_operator_allowed_action if {
    authz.allow with input as {
        "token": {"valid": true, "expires_at": 9999999999},
        "request_count": 50,
        "user": {"id": "usr_002", "role": "MissionOperator"},
        "action": "swarm:status"
    }
}

# Test Mission Operator denied privileged action
test_operator_denied_privileged_action if {
    not authz.allow with input as {
        "token": {"valid": true, "expires_at": 9999999999},
        "request_count": 50,
        "user": {"id": "usr_002", "role": "MissionOperator"},
        "action": "system:reconfigure"
    }
}

# Test Expired token denied
test_expired_token_denied if {
    not authz.allow with input as {
        "token": {"valid": true, "expires_at": 1000},
        "request_count": 5,
        "user": {"id": "usr_001", "role": "PrincipalArchitect"},
        "action": "system:reconfigure"
    }
}

# Test Rate limited request denied
test_rate_limited_denied if {
    not authz.allow with input as {
        "token": {"valid": true, "expires_at": 9999999999},
        "request_count": 1500,
        "user": {"id": "usr_001", "role": "PrincipalArchitect"},
        "action": "system:reconfigure"
    }
}
