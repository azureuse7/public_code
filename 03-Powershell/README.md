# PowerShell Scripting

> Practical PowerShell snippets and examples covering cmdlets, file operations, Azure resource management, data structures, and control flow.

---

## Contents

| File | Topic |
|------|-------|
| [02-Select-Object.ps1](02-Select-Object.ps1) | `Select-Object` — filter and project object properties from the pipeline |
| [03-Start-Sleep.ps1](03-Start-Sleep.ps1) | `Start-Sleep` — pause script execution for a defined duration |
| [04-Create-ACR.ps1](04-Create-ACR.ps1) | Create an Azure Container Registry with `New-AzContainerRegistry` |
| [05-Create-File.ps1](05-Create-File.ps1) | `New-Item` — create files and directories |
| [06-Compare.ps1](06-Compare.ps1) | `Compare-Object` — diff two object sets (e.g., running vs saved processes) |
| [07-Where-Object.ps1](07-Where-Object.ps1) | `Where-Object` — filter pipeline objects by property value |
| [08-Replace-character-with.ps1](08-Replace-character-with.ps1) | String `.Replace()` — swap characters in a variable |
| [09-Get-all-Items-in-path.ps1](09-Get-all-Items-in-path.ps1) | `Get-ChildItem` — recursively list files in a directory |
| [10-Get-all-items-in-path-that-have-dockerfile.ps1](10-Get-all-items-in-path-that-have-dockerfile.ps1) | Filter `Get-ChildItem` output to Dockerfile paths only |
| [11-Remove-dockerfile from output and replace with.ps1](11-Remove-dockerfile%20from%20output%20and%20replace%20with.ps1) | Remove "Dockerfile" from path strings and replace with image tag |
| [12-Get the content of files.ps1](12-Get%20the%20content%20of%20files.ps1) | `Get-Content` — read file contents inside a loop |
| [13-Delete-everything.ps1](13-Delete-everything.ps1) | Delete all Azure resources in a subscription |
| [14-Function.ps1](14-Function.ps1) | Defining functions with `param` blocks |
| [15-Hash-table.ps1](15-Hash-table.ps1) | Hash tables and `PSCustomObject` |
| [16-if-statments.ps1](16-if-statments.ps1) | If / elseif / else control flow |
| [17-Switch.ps1](17-Switch.ps1) | Switch statements for multi-branch logic |
| [18-Write-host.ps1](18-Write-host.ps1) | `Write-Host` — coloured console output |
| [19-AzGettingStarted.ps1](19-AzGettingStarted.ps1) | Getting started with the Az PowerShell module |

---

## Quick Reference

### Pipeline operators
```powershell
# Select specific properties
Get-Process | Select-Object -Property Name, CPU

# Filter by condition
Get-Service | Where-Object -Property Status -eq "Running"
```

### File operations
```powershell
# Create a file
New-Item -Path "C:\temp" -Name "test.txt" -ItemType File

# Read file content
$content = Get-Content -Path "C:\temp\test.txt"

# List files recursively
$files = Get-ChildItem -Path . -Recurse -File -Name
```

### String manipulation
```powershell
# Replace characters
$result = $original.Replace("/", "-")

# String formatting
Write-Host "Value: $result" -ForegroundColor Green
```

### Data structures
```powershell
# Hash table / custom object
$obj = [PSCustomObject]@{
    Name = "example"
    Value = 42
}
```
