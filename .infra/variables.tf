variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west1"
}

variable "network_name" {
  description = "The name of the VPC network"
  type        = string
  default     = "my-vpc"
}

variable "subnet_name" {
  description = "The name of the subnet"
  type        = string
  default     = "my-subnet"
}

variable "subnet_cidr" {
  description = "The CIDR range for the subnet"
  type        = string
  default     = "10.0.0.0/24"
}