param(
    [Parameter(Mandatory = $true)]
    [string]$ApiBaseUrl,

    [Parameter(Mandatory = $true)]
    [string]$FrontendOrigin,

    [string]$SessionCookie = "",
    [string]$TestEmail = "",
    [string]$NotificationSecret = ""
)

$ErrorActionPreference = "Stop"
$api = $ApiBaseUrl.TrimEnd("/")
$origin = $FrontendOrigin.TrimEnd("/")

function Assert-StatusOk {
    param(
        [string]$Name,
        [string]$Path
    )

    $response = Invoke-WebRequest -Uri "$api$Path" -Method Get
    if ($response.StatusCode -ne 200) {
        throw "$Name failed with HTTP $($response.StatusCode)"
    }
    Write-Host "[ok] $Name $Path"
}

function Assert-JsonStatusOk {
    param(
        [string]$Name,
        [string]$Path
    )

    $payload = Invoke-RestMethod -Uri "$api$Path" -Method Get
    if ($payload.status -ne "ok") {
        throw "$Name returned unexpected status: $($payload | ConvertTo-Json -Compress)"
    }
    Write-Host "[ok] $Name $Path"
}

function Assert-Cors {
    $headers = @{
        Origin = $origin
        "Access-Control-Request-Method" = "GET"
    }
    $response = Invoke-WebRequest -Uri "$api/api/auth/me" -Method Options -Headers $headers
    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]
    $allowCredentials = $response.Headers["Access-Control-Allow-Credentials"]
    if ($allowOrigin -ne $origin) {
        throw "CORS origin mismatch. Expected '$origin', got '$allowOrigin'"
    }
    if ($allowCredentials -ne "true") {
        throw "CORS credentials header mismatch. Expected 'true', got '$allowCredentials'"
    }
    Write-Host "[ok] CORS allows $origin with credentials"
}

function Assert-GoogleLoginStart {
    try {
        $response = Invoke-WebRequest -Uri "$api/api/auth/google/login" -Method Get -MaximumRedirection 0
    } catch {
        $response = $_.Exception.Response
    }
    if (-not $response) {
        throw "Google OAuth login did not return a response"
    }
    $statusCode = [int]$response.StatusCode
    if ($statusCode -ne 302) {
        throw "Google OAuth login expected HTTP 302, got $statusCode"
    }
    $location = $response.Headers["Location"]
    if (-not ($location -like "https://accounts.google.com/*")) {
        throw "Google OAuth login Location is unexpected: $location"
    }
    $setCookie = $response.Headers["Set-Cookie"]
    if (-not ($setCookie -match "finlight_oauth_state=")) {
        throw "Google OAuth login did not set the OAuth state cookie"
    }
    Write-Host "[ok] Google OAuth login starts and redirects to Google"
}

function Assert-AuthenticatedEmailSubscription {
    if (-not $SessionCookie) {
        Write-Host "[skip] Email subscription smoke test needs SessionCookie from a production Google login"
        return
    }
    if (-not $TestEmail) {
        Write-Host "[skip] Email subscription smoke test needs TestEmail"
        return
    }

    $headers = @{ Cookie = $SessionCookie }
    $initial = Invoke-RestMethod -Uri "$api/api/email-subscription" -Method Get -Headers $headers
    Write-Host "[ok] Email subscription read returned status '$($initial.status)'"

    $body = @{
        email = $TestEmail
        dailySummary = $true
        immediateRed = $true
        immediateYellow = $true
    } | ConvertTo-Json
    $updated = Invoke-RestMethod `
        -Uri "$api/api/email-subscription" `
        -Method Put `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $body
    if ($updated.status -ne "pending" -and $updated.status -ne "active") {
        throw "Email subscription returned unexpected status '$($updated.status)'"
    }
    Write-Host "[ok] Email subscription update returned status '$($updated.status)'"
}

function Assert-NotificationDispatchAuth {
    if (-not $NotificationSecret) {
        Write-Host "[skip] Notification dispatch smoke test needs NotificationSecret"
        return
    }
    $dedupe = "deploy-smoke-$(Get-Date -Format yyyyMMddHHmmss)"
    $body = @{
        type = "daily_summary"
        subject = "[FinLightAI] deploy smoke daily summary"
        body = "Production smoke test daily summary."
        dedupeKey = $dedupe
        channels = @("email")
    } | ConvertTo-Json
    $result = Invoke-RestMethod `
        -Uri "$api/api/notifications/dispatch" `
        -Method Post `
        -Headers @{ "X-Notification-Secret" = $NotificationSecret } `
        -ContentType "application/json" `
        -Body $body
    Write-Host "[ok] Notification dispatch returned sent=$($result.sent), skipped=$($result.skipped), failed=$($result.failed), duplicate=$($result.duplicate)"
}

Assert-JsonStatusOk "liveness" "/health/live"
Assert-JsonStatusOk "readiness" "/health/ready"
Assert-StatusOk "briefing API" "/api/briefing"
Assert-StatusOk "news guard API" "/api/news-guard"
Assert-StatusOk "industry impact API" "/api/industry-impact"
Assert-StatusOk "signals API" "/api/signals"
Assert-Cors
Assert-GoogleLoginStart
Assert-AuthenticatedEmailSubscription
Assert-NotificationDispatchAuth

Write-Host "[done] Deploy smoke checks completed"
