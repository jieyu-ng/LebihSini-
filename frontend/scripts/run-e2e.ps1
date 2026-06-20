$ErrorActionPreference = "Stop"

$backend = $null
$frontend = $null

function Wait-ForUrl {
  param(
    [string]$Url,
    [string]$Label
  )

  $deadline = (Get-Date).AddSeconds(120)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
        return
      }
    } catch {
      Start-Sleep -Seconds 1
    }
  }

  throw "$Label did not become ready at $Url"
}

try {
  $backend = Start-Process `
    -FilePath python `
    -ArgumentList "-m", "uvicorn", "lebihsini_greenproof.api.app:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory "C:\Users\ganka\Downloads\Imagine\LebihSini-" `
    -WindowStyle Hidden `
    -PassThru

  $frontend = Start-Process `
    -FilePath powershell `
    -ArgumentList "-NoProfile", "-Command", "$env:NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:8000/api'; & 'C:\Program Files\nodejs\npm.cmd' run dev" `
    -WorkingDirectory "C:\Users\ganka\Downloads\Imagine\LebihSini-\frontend" `
    -WindowStyle Hidden `
    -PassThru

  Wait-ForUrl -Url "http://127.0.0.1:8000/api/health" -Label "Backend"
  Wait-ForUrl -Url "http://localhost:3000" -Label "Frontend"

  & "C:\Program Files\nodejs\npx.cmd" playwright test --config playwright.config.ts
  exit $LASTEXITCODE
} finally {
  if ($frontend -and -not $frontend.HasExited) {
    Stop-Process -Id $frontend.Id -Force
  }
  if ($backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force
  }
}
