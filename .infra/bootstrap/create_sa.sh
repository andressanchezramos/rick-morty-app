#!/bin/bash

# === CONFIGURATION ===
PROJECT_ID="coherent-span-464616-q7"
SA_NAME="terraform-vpc-sa"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
KEY_FILE="terraform-vpc-key.json"
ROLES=(
  "roles/serviceusage.serviceUsageAdmin"
  "roles/container.admin"
  "roles/compute.networkAdmin"
  "roles/iam.serviceAccountUser"
  "roles/resourcemanager.projectIamAdmin"
  )

# === FUNCTIONS ===

function check_command_success {
  if [ $? -ne 0 ]; then
    echo "❌ Error: $1 failed. Exiting."
    exit 1
  fi
}

# === CREATE SERVICE ACCOUNT ===
echo "🔍 Checking if service account '$SA_NAME' exists..."
if gcloud iam service-accounts list --project="$PROJECT_ID" --filter="email:$SA_EMAIL" --format="value(email)" | grep -q "$SA_EMAIL"; then
  echo "✅ Service account '$SA_EMAIL' already exists."
else
  echo "➕ Creating service account '$SA_NAME'..."
  gcloud iam service-accounts create "$SA_NAME" \
    --project="$PROJECT_ID" \
    --description="Service account for Terraform to manage VPCs" \
    --display-name="Terraform VPC SA"
  check_command_success "Service account creation"
fi

# === ASSIGN IAM ROLES ===
for ROLE in "${ROLES[@]}"; do
  echo "🔍 Checking if IAM role '$ROLE' is already assigned..."
  if gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:serviceAccount:$SA_EMAIL AND bindings.role:$ROLE" | grep -q "$ROLE"; then
    echo "✅ Role '$ROLE' already assigned to '$SA_EMAIL'."
  else
    echo "➕ Assigning role '$ROLE' to '$SA_EMAIL'..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:$SA_EMAIL" \
      --role="$ROLE"
    check_command_success "IAM role assignment"
  fi
done

# === CREATE SERVICE ACCOUNT KEY ===
echo "🔍 Checking if key file '$KEY_FILE' exists..."
if [ -f "$KEY_FILE" ]; then
  echo "✅ Key file '$KEY_FILE' already exists. Skipping key creation."
else
  echo "🔑 Creating service account key..."
  gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SA_EMAIL"
  check_command_success "Key creation"
fi

echo "🎉 All done! Service account is ready for Terraform use."