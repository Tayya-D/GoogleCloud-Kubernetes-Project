"""IAM configuration for GKE workloads"""
import pulumi
from pulumi_gcp import serviceaccount, projects

def create_service_accounts(cluster):
    # Create workload identity service account
    gke_sa = serviceaccount.Account(
        "model-serving-sa",
        account_id="model-serving",
        display_name="Model Serving Workload Identity SA",
    )
    
    # Grant Kubernetes service account access
    projects.IAMMember(
        "workload-identity-binding",
        project=pulumi.get_project(),
        role="roles/iam.workloadIdentityUser",
        member=pulumi.Output.all(
            gke_sa.project,
            gke_sa.email
        ).apply(lambda args: f"serviceAccount:{args[0]}.svc.id.goog[model-serving/model-serving]"),
    )
    
    # Add cloud storage access for model artifacts
    serviceaccount.IAMMember(
        "storage-access",
        service_account_id=gke_sa.name,
        role="roles/storage.objectViewer",
        member=gke_sa.email.apply(lambda email: f"serviceAccount:{email}"),
    )
    
    return gke_sa