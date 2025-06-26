"""Monitoring and logging configuration"""
import pulumi
from pulumi_gcp import projects, monitoring

def enable_stackdriver():
    # Enable Stackdriver Kubernetes Monitoring
    projects.Service(
        "monitoring-service",
        service="monitoring.googleapis.com",
        disable_on_destroy=False,
    )
    
    # Enable Stackdriver Logging
    projects.Service(
        "logging-service",
        service="logging.googleapis.com",
        disable_on_destroy=False,
    )
    
    # Create custom dashboard
    dashboard = monitoring.Dashboard(
        "ai-serving-dashboard",
        dashboard_json=pulumi.Output.all().apply(lambda _: """{
            "displayName": "AI Serving Metrics",
            "gridLayout": {
                "widgets": [
                    {
                        "title": "CPU Utilization",
                        "xyChart": {
                            "dataSets": [{
                                "timeSeriesQuery": {
                                    "timeSeriesFilter": {
                                        "filter": "metric.type=\"kubernetes.io/container/cpu/limit_utilization\"",
                                        "aggregation": {
                                            "perSeriesAligner": "ALIGN_MEAN"
                                        }
                                    }
                                }
                            }]
                        }
                    }
                ]
            }
        }""")
    )
    
    return dashboard