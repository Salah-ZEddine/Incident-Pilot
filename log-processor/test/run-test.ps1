# Incident Pilot - Log Generator Test Script (PowerShell)
# This script generates test logs that trigger anomaly detection rules

Write-Host "🚀 Incident Pilot - Log Generator Test Script" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Set parameters
$Count = 3
$Delay = 1.5
$OutputPath = "~/test-logs.log"

# Allow user to customize parameters
$userInput = Read-Host "Press Enter to use defaults (3 batches, 1.5s delay) or type 'custom' for custom settings"

if ($userInput -eq "custom") {
    $Count = Read-Host "Number of batches (default: 3)"
    if ([string]::IsNullOrWhiteSpace($Count)) { $Count = 3 }
    
    $Delay = Read-Host "Delay between batches in seconds (default: 1.5)"
    if ([string]::IsNullOrWhiteSpace($Delay)) { $Delay = 1.5 }
    
    $customOutput = Read-Host "Output file path (default: ~/test-logs.log)"
    if (![string]::IsNullOrWhiteSpace($customOutput)) { $OutputPath = $customOutput }
}

Write-Host ""
Write-Host "📝 Starting log generation with settings:" -ForegroundColor Yellow
Write-Host "   📦 Batches: $Count" -ForegroundColor White
Write-Host "   ⏱️ Delay: $Delay seconds" -ForegroundColor White
Write-Host "   📁 Output: $OutputPath" -ForegroundColor White
Write-Host ""

# Run the log generator
try {
    python test.py --count $Count --delay $Delay --output $OutputPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Log generation completed successfully!" -ForegroundColor Green
        $expandedPath = [System.IO.Path]::GetFullPath([System.Environment]::ExpandEnvironmentVariables($OutputPath.Replace("~", $env:USERPROFILE)))
        Write-Host "📁 Logs saved to: $expandedPath" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "📋 Next Steps:" -ForegroundColor Yellow
        Write-Host "   1. 🔍 View logs: Get-Content '$expandedPath' | Select-Object -First 10" -ForegroundColor White
        Write-Host "   2. 🚀 Start your log processor service" -ForegroundColor White
        Write-Host "   3. 🚀 Start your anomaly detector service" -ForegroundColor White
        Write-Host "   4. 📊 Feed these logs into your pipeline" -ForegroundColor White
        Write-Host "   5. 🔍 Monitor anomaly detection results" -ForegroundColor White
        
        # Show sample logs
        $showSample = Read-Host "`nWould you like to see a sample of generated logs? (y/N)"
        if ($showSample -eq 'y' -or $showSample -eq 'Y') {
            Write-Host ""
            Write-Host "📄 Sample logs (first 5 lines):" -ForegroundColor Cyan
            Write-Host "================================" -ForegroundColor Cyan
            Get-Content $expandedPath | Select-Object -First 5 | ForEach-Object {
                $logObj = $_ | ConvertFrom-Json
                Write-Host "🔹 [$($logObj.timestamp)] [$($logObj.log_level)] $($logObj.source): $($logObj.message)" -ForegroundColor Gray
            }
        }
        
    } else {
        Write-Host ""
        Write-Host "❌ Log generation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error running log generator: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
