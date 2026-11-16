"""
AI-assisted troubleshooting recommendation engine for NOC Incident Intelligence.
"""
import json
from typing import List, Dict, Any

RECOMMENDATIONS_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "Server Overload": [
        {
            "action": "Inspect CPU-intensive processes via top/htop/tasklist",
            "reason": "Server CPU utilization has exceeded operational thresholds, indicating potential runaway thread or runaway application process.",
            "priority": "HIGH",
            "expected_outcome": "Identify specific PID consuming abnormal core cycles.",
            "manual_verification_required": True
        },
        {
            "action": "Check application request queues and active thread pools",
            "reason": "Bursts in web/API traffic can saturate worker processes.",
            "priority": "HIGH",
            "expected_outcome": "Determine if traffic spike or locked threads caused the resource saturation.",
            "manual_verification_required": True
        },
        {
            "action": "Trigger horizontal load balancing or spin up auxiliary instance",
            "reason": "Distributes incoming computational load away from the saturated node.",
            "priority": "MEDIUM",
            "expected_outcome": "CPU drops back under 70% threshold across the cluster.",
            "manual_verification_required": True
        },
        {
            "action": "Audit recent deployments and configuration changes",
            "reason": "Regressions or unoptimized database queries in recent software releases frequently manifest as sudden CPU spikes.",
            "priority": "LOW",
            "expected_outcome": "Confirm whether a rollback or hotfix is required.",
            "manual_verification_required": True
        }
    ],
    "Network Failure": [
        {
            "action": "Verify physical and logical network interface status (UP/DOWN)",
            "reason": "Device is unreachable or reporting zero network availability.",
            "priority": "HIGH",
            "expected_outcome": "Verify whether transceiver, virtual NIC, or cable link has dropped.",
            "manual_verification_required": True
        },
        {
            "action": "Check BGP/OSPF neighbor adjacency and routing tables",
            "reason": "Routing protocol flaps isolate network nodes from gateway paths.",
            "priority": "HIGH",
            "expected_outcome": "Restore dynamic routes or failover to secondary path.",
            "manual_verification_required": True
        },
        {
            "action": "Check connectivity between adjacent switches and upstream gateways",
            "reason": "Correlate with upstream core router to rule out broad datacenter backbone outage.",
            "priority": "HIGH",
            "expected_outcome": "Isolate localized node failure from fabric-wide outage.",
            "manual_verification_required": True
        },
        {
            "action": "Review switch and router syslog logs for hardware faults",
            "reason": "ASIC errors, fan failures, or power supply faults can cause sudden network device dropouts.",
            "priority": "MEDIUM",
            "expected_outcome": "Identify physical hardware degradation.",
            "manual_verification_required": True
        }
    ],
    "High Latency": [
        {
            "action": "Trace network hops using traceroute/MTR along the data path",
            "reason": "Latency has spiked above acceptable round-trip time thresholds.",
            "priority": "HIGH",
            "expected_outcome": "Pinpoint the specific intermediate hop or router introducing delay.",
            "manual_verification_required": True
        },
        {
            "action": "Examine interface bandwidth utilization and buffer queuing (bufferbloat)",
            "reason": "Saturated links cause queue build-up leading to severe jitter and latency.",
            "priority": "HIGH",
            "expected_outcome": "Confirm whether traffic shaping or QoS rate limits are engaged.",
            "manual_verification_required": True
        },
        {
            "action": "Compare cross-datacenter latency metrics against baseline SLA",
            "reason": "Determine if latency is localized to this link or caused by transit provider degradation.",
            "priority": "MEDIUM",
            "expected_outcome": "Validate whether ISP transit provider ticket needs escalation.",
            "manual_verification_required": True
        }
    ],
    "Packet Loss": [
        {
            "action": "Inspect interface CRC errors, frame drops, and collisions",
            "reason": "Packet loss above 1% corrupts TCP windows and degrades application throughput.",
            "priority": "HIGH",
            "expected_outcome": "Detect faulty optic fiber cables, dirty connectors, or duplex mismatches.",
            "manual_verification_required": True
        },
        {
            "action": "Check for network microbursts causing switch output drop queues",
            "reason": "Microbursts exceed interface packet buffers even when average bandwidth looks modest.",
            "priority": "HIGH",
            "expected_outcome": "Adjust buffer allocation or deploy traffic policing.",
            "manual_verification_required": True
        },
        {
            "action": "Test end-to-end MTU size and path MTU discovery (PMTUD)",
            "reason": "Mismatched MTUs result in fragmented packets that firewalls or routers may silently drop.",
            "priority": "MEDIUM",
            "expected_outcome": "Eliminate packet fragmentation issues.",
            "manual_verification_required": True
        }
    ],
    "DNS Failure": [
        {
            "action": "Verify local and upstream DNS resolver availability (port 53 UDP/TCP)",
            "reason": "DNS resolution queries failed, preventing hostname-to-IP translation across services.",
            "priority": "HIGH",
            "expected_outcome": "Ensure DNS daemon (named/unbound/CoreDNS) is responsive.",
            "manual_verification_required": True
        },
        {
            "action": "Test reachability to fallback recursive resolvers (e.g., internal secondary DNS)",
            "reason": "Failure of primary resolver should cleanly failover to secondary nameserver.",
            "priority": "HIGH",
            "expected_outcome": "Verify resolver failover mechanism is operating properly.",
            "manual_verification_required": True
        },
        {
            "action": "Inspect DNS query logs for NXDOMAIN flood or upstream timeout errors",
            "reason": "Can uncover misconfigured zone records, expired TTLs, or DNS amplification attacks.",
            "priority": "MEDIUM",
            "expected_outcome": "Restore zone propagation and clear corrupted resolver caches.",
            "manual_verification_required": True
        }
    ],
    "Disk Capacity Issue": [
        {
            "action": "Identify top space-consuming directories and unrotated log files",
            "reason": "Disk utilization has breached 80-90% safe margins, risking database corruption and OS crashes.",
            "priority": "HIGH",
            "expected_outcome": "Locate runaway log files, crash dumps, or orphaned temp directories.",
            "manual_verification_required": True
        },
        {
            "action": "Verify logrotate execution and truncate old debug/audit logs",
            "reason": "Unrotated application logs frequently exhaust available filesystem blocks.",
            "priority": "HIGH",
            "expected_outcome": "Recover immediately 15-30% disk headspace.",
            "manual_verification_required": True
        },
        {
            "action": "Inspect inode allocation table (df -i)",
            "reason": "Exhaustion of file inodes causes write failures even when byte capacity appears available.",
            "priority": "MEDIUM",
            "expected_outcome": "Remove millions of tiny stale temporary or session files.",
            "manual_verification_required": True
        },
        {
            "action": "Plan storage volume expansion or LVM partition resizing",
            "reason": "Permanent operational growth requires volume scale-up.",
            "priority": "LOW",
            "expected_outcome": "Increase disk capacity permanently.",
            "manual_verification_required": True
        }
    ],
    "Memory Exhaustion": [
        {
            "action": "Identify top memory-consuming processes and resident set size (RSS)",
            "reason": "Memory utilization has exceeded 85-90% thresholds, triggering swapping or imminent OOM Killer.",
            "priority": "HIGH",
            "expected_outcome": "Pinpoint process leaking memory or holding unbounded object caches.",
            "manual_verification_required": True
        },
        {
            "action": "Examine Linux kernel dmesg / syslog for OOM Killer invocations",
            "reason": "Determines if critical services have already been terminated by kernel memory manager.",
            "priority": "HIGH",
            "expected_outcome": "Verify whether companion processes were unexpectedly killed.",
            "manual_verification_required": True
        },
        {
            "action": "Inspect swap space utilization and page thrashing rate",
            "reason": "Heavy swapping degrades CPU and disk I/O exponentially.",
            "priority": "HIGH",
            "expected_outcome": "Mitigate swap storm before total server unresponsiveness.",
            "manual_verification_required": True
        },
        {
            "action": "Restart leaking service gracefully or increase memory limit cgroups",
            "reason": "Reclaims leaked heap memory and stabilizes node.",
            "priority": "MEDIUM",
            "expected_outcome": "Free RAM and return usage below 70%.",
            "manual_verification_required": True
        }
    ],
    "Normal": [
        {
            "action": "Maintain routine synthetic heartbeat and telemetry polling",
            "reason": "Device is operating within all baseline service level indicators.",
            "priority": "LOW",
            "expected_outcome": "Continuous operational visibility.",
            "manual_verification_required": False
        }
    ]
}

def generate_recommendations(category: str, metrics: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Returns tailored troubleshooting recommendations for an incident category.
    """
    recs = RECOMMENDATIONS_CATALOG.get(category)
    if not recs:
        recs = RECOMMENDATIONS_CATALOG["Normal"]
    return recs

def generate_recommendations_json(category: str, metrics: Dict[str, Any] = None) -> str:
    """
    Returns recommendations serialized as a JSON string for database storage.
    """
    return json.dumps(generate_recommendations(category, metrics))
