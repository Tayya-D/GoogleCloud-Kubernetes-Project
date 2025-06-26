"""Main Pulumi program for GKE cluster deployment"""
import pulumi
from pulumi_gcp import container, projects, compute
from networking import create_network
from iam import create_service_accounts
from monitoring import enable_stackdriver

# Import config
config = pulumi.Config('gke')
cluster_settings = config.require_object('cluster')

def create_gke_cluster():
    # Create network resources first
    network, subnet = create_network()
    
    # Enable required GCP services
    projects.Service(
        "container-service",
        service="container.googleapis.com",
        disable_on_destroy=False,
    )

    # Create GKE cluster
    cluster = container.Cluster(
        "ai-serving-gke",
        name=cluster_settings.get('name', 'ai-serving-cluster'),
        location=cluster_settings['region'],
        network=network.name,
        subnetwork=subnet.name,
        
        # Cluster configuration
        min_master_version="1.27",
        initial_node_count=3,
        remove_default_node_pool=True,  # We'll create custom node pools
        
        # Security hardening
        private_cluster_config={
            "enable_private_nodes": True,
            "master_ipv4_cidr_block": "172.16.0.0/28",
        },
        workload_identity_config={
            "workload_pool": f"{pulumi.get_project()}.svc.id.goog"
        },
        release_channel={
            "channel": "REGULAR"  # Stable releases
        },
        
        # Monitoring
        logging_service="logging.googleapis.com/kubernetes",
        monitoring_service="monitoring.googleapis.com/kubernetes",
    )
    
    # Create custom node pools
    container.NodePool(
        "spot-node-pool",
        name="spot-pool",
        location=cluster.location,
        cluster=cluster.name,
        node_count=3,
        node_config={
            "machine_type": "e2-standard-4",
            "disk_size_gb": 100,
            "disk_type": "pd-ssd",
            "preemptible": True,  # Cost savings
            "oauth_scopes": [
                "https://www.googleapis.com/auth/cloud-platform"
            ],
            "workload_metadata_config": {
                "mode": "GKE_METADATA"  # Required for Workload Identity
            },
        },
        management={
            "auto_repair": True,
            "auto_upgrade": True,
        },
        opts=pulumi.ResourceOptions(depends_on=[cluster]),
    )
    
    return cluster

# Deploy all components
cluster = create_gke_cluster()
service_accounts = create_service_accounts(cluster)
monitoring = enable_stackdriver()

# Export outputs
pulumi.export("cluster_name", cluster.name)
pulumi.export("endpoint", cluster.endpoint)
pulumi.export("kubeconfig", pulumi.Output.all(
    cluster.name, 
    cluster.endpoint, 
    cluster.master_auth
).apply(lambda args: f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {args[2]['cluster_ca_certificate']}
    server: https://{args[1]}
  name: {args[0]}
contexts:
- context:
    cluster: {args[0]}
    user: {args[0]}
  name: {args[0]}
current-context: {args[0]}
kind: Config
users:
- name: {args[0]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl
      provideClusterInfo: true
"""))