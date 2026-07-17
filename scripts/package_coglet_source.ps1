param(
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path,
    [string]$OutputZip = (Join-Path (Split-Path $ProjectRoot -Parent) "CogletESP-camera-version-clean-source.zip")
)

$ErrorActionPreference = "Stop"
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("CogletESP-source-" + [guid]::NewGuid())
$tempProject = Join-Path $tempRoot (Split-Path $ProjectRoot -Leaf)

$excludedDirectories = @(
    ".git",
    ".cache",
    ".vscode",
    ".devcontainer",
    "build",
    "managed_components",
    "components"
)

$excludedFiles = @(
    "sdkconfig.old",
    "main\assets\lang_config.h",
    "README_覆盖说明.txt"
)

New-Item -ItemType Directory -Path $tempProject -Force | Out-Null

try {
    $sourcePrefix = $ProjectRoot.TrimEnd('\') + '\'

    Get-ChildItem -LiteralPath $ProjectRoot -Recurse -Force | ForEach-Object {
        $relative = $_.FullName.Substring($sourcePrefix.Length)
        $parts = $relative -split '[\\/]'

        if ($parts | Where-Object { $excludedDirectories -contains $_ }) {
            return
        }
        if ($excludedFiles -contains $relative) {
            return
        }

        $target = Join-Path $tempProject $relative
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $target -Force | Out-Null
        } else {
            New-Item -ItemType Directory -Path (Split-Path $target -Parent) -Force | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        }
    }

    if (Test-Path $OutputZip) {
        Remove-Item $OutputZip -Force
    }
    Compress-Archive -Path $tempProject -DestinationPath $OutputZip -CompressionLevel Optimal
    Write-Host "Created: $OutputZip"
}
finally {
    if (Test-Path $tempRoot) {
        Remove-Item $tempRoot -Recurse -Force
    }
}
