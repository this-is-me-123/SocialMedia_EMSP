# Lint All Project Files (PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File .\lint-all.ps1

Write-Host "--- PHP Lint ---"
Get-ChildItem -Recurse -Include *.php | ForEach-Object {
    $result = php -l $_.FullName
    if ($result -notmatch 'No syntax errors detected') {
        Write-Host $result -ForegroundColor Red
    }
}

Write-Host "--- Python Lint ---"
Get-ChildItem -Recurse -Include *.py | ForEach-Object {
    try {
        python -m py_compile $_.FullName
    } catch {
        Write-Host "ERROR: $($_.FullName) $_" -ForegroundColor Red
    }
}

Write-Host "--- YAML Lint ---"
$yamlfiles = Get-ChildItem -Recurse -Include *.yml,*.yaml
foreach ($file in $yamlfiles) {
    $result = yamllint $file.FullName
    if ($LASTEXITCODE -ne 0) {
        Write-Host $result -ForegroundColor Red
    }
}

Write-Host "--- JavaScript Lint ---"
Get-ChildItem -Recurse -Include *.js | ForEach-Object {
    $result = node --check $_.FullName
    if ($LASTEXITCODE -ne 0) {
        Write-Host $result -ForegroundColor Red
    }
}


