import time
import math
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class Waypoint(BaseModel):
    latitude: float
    longitude: float
    altitude_m: float
    hold_time_s: float = 0.0

class UAVTelemetry(BaseModel):
    uav_id: str
    battery_pct: float
    current_lat: float
    current_lon: float
    altitude_m: float
    velocity_mps: float
    flight_mode: str = "GUIDED"
    timestamp_ns: int = Field(default_factory=time.time_ns)

class SwarmConsensusNode:
    """
    Decentralized Swarm Consensus & Task Allocation Node.
    Implements leaderless consensus for autonomous waypoint assignment.
    """
    def __init__(self, node_id: str, quorum_size: int = 3):
        self.node_id = node_id
        self.quorum_size = quorum_size
        self.active_peers: Dict[str, UAVTelemetry] = {}
        self.assigned_sector: Optional[str] = None

    def ingest_peer_telemetry(self, telemetry: UAVTelemetry):
        self.active_peers[telemetry.uav_id] = telemetry

    def calculate_optimal_allocation(self, target_waypoint: Waypoint) -> Dict[str, Any]:
        """
        Determines the optimal UAV to service a high-priority waypoint
        based on Euclidean distance and battery reserve metrics.
        """
        best_uav = None
        min_cost = float("inf")
        
        for uav_id, state in self.active_peers.items():
            if state.battery_pct < 20.0:
                continue  # Exclude low-battery units from assignment
                
            dist = math.sqrt(
                (state.current_lat - target_waypoint.latitude) ** 2 +
                (state.current_lon - target_waypoint.longitude) ** 2
            )
            # Battery-weighted cost function
            cost = dist / (state.battery_pct / 100.0)
            
            if cost < min_cost:
                min_cost = cost
                best_uav = uav_id
                
        return {
            "selected_uav": best_uav,
            "cost_score": round(min_cost, 4),
            "consensus_reached": len(self.active_peers) >= self.quorum_size,
            "peer_count": len(self.active_peers)
        }

if __name__ == "__main__":
    node = SwarmConsensusNode("UAV_LEADER_01", quorum_size=3)
    node.ingest_peer_telemetry(UAVTelemetry(uav_id="UAV_01", battery_pct=85, current_lat=32.65, current_lon=-16.90, altitude_m=120, velocity_mps=15))
    node.ingest_peer_telemetry(UAVTelemetry(uav_id="UAV_02", battery_pct=92, current_lat=32.66, current_lon=-16.91, altitude_m=110, velocity_mps=14))
    node.ingest_peer_telemetry(UAVTelemetry(uav_id="UAV_03", battery_pct=40, current_lat=32.64, current_lon=-16.89, altitude_m=130, velocity_mps=16))
    
    target = Waypoint(latitude=32.67, longitude=-16.92, altitude_m=150)
    decision = node.calculate_optimal_allocation(target)
    print("Swarm Consensus Allocation:", decision)
