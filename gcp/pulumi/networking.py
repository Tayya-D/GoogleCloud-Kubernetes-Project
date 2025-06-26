"""Network resources for GKE cluster"""
import pulumi
from pulumi_gcp import compute

def create_network():
    # Create custom VPC
    network = compute.Network(
        "ai-serving-vpc",
        name="ai-serving-vpc",
        auto_create_subnetworks=False,
        description="Custom VPC for AI Serving Platform",
    )
    
    # Subnet with secondary ranges for pods/services
    subnet = compute.Subnetwork(
        "ai-serving-subnet",
        name="ai-serving-subnet",
        network=network.self_link,
        ip_cidr_range="10.2.0.0/16",
        region="us-central1",
        secondary_ip_ranges=[
            {
                "rangeName": "pods",
                "ipCidrRange": "10.3.0.0/16",
            },
            {
                "rangeName": "services",
                "ipCidrRange": "10.4.0.0/16",
            },
        ],
    )
    
    # Firewall rules
    compute.Firewall(
        "allow-internal",
        name="allow-internal",
        network=network.self_link,
        allows=[
            {
                "protocol": "tcp",
                "ports": ["0-65535"],
            },
            {
                "protocol": "udp",
                "ports": ["0-65535"],
            },
            {
                "protocol": "icmp",
            },
        ],
        source_ranges=["10.2.0.0/16", "10.3.0.0/16", "10.4.0.0/16"],
    )
    
    return network, subnet