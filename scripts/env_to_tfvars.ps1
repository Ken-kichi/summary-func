# Windows PowerShell 用スクリプト
# .env ファイルから Terraform 用の .tfvars ファイルを生成
# 使用方法: powershell -ExecutionPolicy Bypass -File scripts/env_to_tfvars.ps1

$EnvFile = ".env"
$TfvarsFile = "terraform/secret.tfvars"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# .env ファイルの確認
if (-not (Test-Path "$ProjectRoot/$EnvFile")) {
    Write-Host "❌ エラー: $EnvFile ファイルが見つかりません" -ForegroundColor Red
    exit 1
}

Write-Host "📖 $EnvFile から値を読み込み中..." -ForegroundColor Cyan

# .env ファイルから値を読み込む
$EnvContent = Get-Content "$ProjectRoot/$EnvFile" | Where-Object { $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*$' }

$EnvDict = @{}
foreach ($line in $EnvContent) {
    $key, $value = $line -split '=', 2
    if ($key -and $value) {
        $EnvDict[$key.Trim()] = $value.Trim()
    }
}

# 必須値の確認
$RequiredKeys = @("ENDPOINT", "MODEL_NAME", "SUBSCRIPTION_KEY")
foreach ($key in $RequiredKeys) {
    if (-not $EnvDict.ContainsKey($key)) {
        Write-Host "❌ エラー: $key が .env に見つかりません" -ForegroundColor Red
        exit 1
    }
}

# secret.tfvars を生成
$TfvarsContent = @"
# このファイルは scripts/env_to_tfvars.ps1 で自動生成されました
# 手動編集は避けてください

openai_endpoint = "$($EnvDict['ENDPOINT'])"
openai_model = "$($EnvDict['MODEL_NAME'])"
openai_api_key = "$($EnvDict['SUBSCRIPTION_KEY'])"
api_version = "$($EnvDict['API_VERSION'] ?? '2024-02-15-preview')"
"@

Set-Content -Path "$ProjectRoot/$TfvarsFile" -Value $TfvarsContent

Write-Host "✅ 成功: $TfvarsFile が生成されました" -ForegroundColor Green
Write-Host ""
Write-Host "📋 生成された設定:" -ForegroundColor Cyan
Write-Host "  - Endpoint: $($EnvDict['ENDPOINT'])"
Write-Host "  - Model: $($EnvDict['MODEL_NAME'])"
Write-Host "  - API Version: $($EnvDict['API_VERSION'] ?? '2024-02-15-preview')"
Write-Host ""
Write-Host "🚀 次のコマンドでデプロイを実行してください:" -ForegroundColor Yellow
Write-Host "  cd terraform"
Write-Host "  terraform plan -var-file=`"secret.tfvars`""
Write-Host "  terraform apply -var-file=`"secret.tfvars`""
