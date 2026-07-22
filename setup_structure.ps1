$ErrorActionPreference = "Stop"

# Define the base directory
$BaseDir = "e:\Kavach-main\Kavach-main\kavach-ai"

# Define the directory structure
$Directories = @(
    "apps/frontend/admin-dashboard",
    "apps/frontend/police-dashboard",
    "apps/frontend/bank-dashboard",
    "apps/frontend/telecom-dashboard",
    "apps/frontend/national-command-center",
    "apps/frontend/state-command-center",
    "apps/frontend/district-control-room",
    "apps/frontend/citizen-portal",
    "apps/backend/api-gateway",
    "apps/backend/core-service",
    "apps/backend/evidence-vault",
    "apps/backend/auth-service",
    "apps/backend/notification-service",
    "apps/ai/ai-intelligence-layer",
    "apps/ai/threat-fusion-engine",
    "apps/ai/llm-reasoning-engine",
    "apps/ai/vision-engine",
    "apps/ai/speech-engine",
    "apps/ai/graph-engine",
    "apps/ai/geo-engine",
    "apps/ai/prediction-engine",
    "apps/ai/explainability-engine",
    "apps/ai/threat-propagation-simulator",
    "packages/ui-components",
    "packages/database-models",
    "packages/logger",
    "packages/auth-utils",
    "packages/event-streams",
    "infra/docker",
    "infra/k8s",
    "infra/mlops/model-registry",
    "infra/mlops/experiment-tracking",
    "infra/observability/grafana",
    "infra/observability/prometheus",
    "infra/observability/loki",
    "datasets/vision",
    "datasets/speech",
    "datasets/graph",
    "datasets/nlp",
    "docs/architecture",
    "docs/api",
    "docs/deployment",
    "tests/e2e",
    "tests/integration",
    "tests/unit"
)

# Create base directory if it doesn't exist
if (-not (Test-Path -Path $BaseDir)) {
    New-Item -ItemType Directory -Path $BaseDir | Out-Null
}

# Create subdirectories and add a .gitkeep file to each
foreach ($dir in $Directories) {
    $FullPath = Join-Path -Path $BaseDir -ChildPath $dir
    if (-not (Test-Path -Path $FullPath)) {
        New-Item -ItemType Directory -Path $FullPath | Out-Null
        $GitKeepPath = Join-Path -Path $FullPath -ChildPath ".gitkeep"
        New-Item -ItemType File -Path $GitKeepPath | Out-Null
    }
}

Write-Host "KAVACH AI folder structure generated successfully at $BaseDir."
