locals {
  services = [
    "container.googleapis.com",           # GKE
    "compute.googleapis.com",             # Compute Engine
    "iam.googleapis.com",                 # IAM
    "cloudresourcemanager.googleapis.com",# Resource Manager
    "serviceusage.googleapis.com",        # Service Usage
    "logging.googleapis.com",             # Cloud Logging (optional)
    "monitoring.googleapis.com"           # Cloud Monitoring (optional)
  ]
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "gke_services" {
  for_each = toset(local.services)
  service = each.key
}


resource "google_compute_network" "vpc_network" {
  depends_on = [resource.google_project_service.gke_services["compute.googleapis.com"]]

  name                    = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc_network.id
}