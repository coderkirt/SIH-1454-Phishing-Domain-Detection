# Build apk/PhishEye.apk. The pages are packaged; the Python API stays on this PC.
$ErrorActionPreference = "Stop"
$apkDir = $PSScriptRoot
$root = Split-Path -Parent $apkDir
$frontend = Join-Path $root "frontend"
$www = Join-Path $apkDir "www"

if (-not $env:JAVA_HOME -or -not (Test-Path (Join-Path $env:JAVA_HOME "bin\java.exe"))) {
  $jdkGuess = Get-ChildItem "C:\Program Files\Microsoft\jdk-*" -Directory -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending |
    Select-Object -First 1
  if ($jdkGuess) { $env:JAVA_HOME = $jdkGuess.FullName }
}
if ($env:JAVA_HOME) {
  $env:Path = "$(Join-Path $env:JAVA_HOME 'bin');" + $env:Path
}

function Get-LanIPv4 {
  $candidates = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object {
      $_.IPAddress -notlike "127.*" -and
      $_.PrefixOrigin -ne "WellKnown" -and
      $_.IPAddress -notlike "169.254.*"
    } |
    Sort-Object -Property InterfaceMetric
  foreach ($row in $candidates) {
    if ($row.IPAddress -like "192.168.*" -or $row.IPAddress -like "10.*" -or $row.IPAddress -like "172.*") {
      return $row.IPAddress
    }
  }
  if ($candidates) { return $candidates[0].IPAddress }
  return $null
}

$apiUrl = $env:PHISHEYE_API_URL
if (-not $apiUrl) {
  $ip = Get-LanIPv4
  if (-not $ip) { throw "No LAN IPv4 found. Set PHISHEYE_API_URL, for example http://192.168.1.10:8000" }
  $apiUrl = "http://${ip}:8000"
}
$apiUrl = $apiUrl.TrimEnd("/")
Write-Host "Dashboard in this APK will call $apiUrl"

if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
  Write-Host "Installing frontend packages"
  Push-Location $frontend
  npm install
  Pop-Location
}

Write-Host "Building the dashboard"
Push-Location $frontend
$env:VITE_API_URL = $apiUrl
npm run build
if ($LASTEXITCODE -ne 0) { throw "frontend build failed" }
Pop-Location

$dist = Join-Path $frontend "dist"
if (-not (Test-Path $dist)) { throw "frontend/dist missing after build" }
if (Test-Path $www) { Remove-Item $www -Recurse -Force }
Copy-Item $dist $www -Recurse
@{ apiUrl = $apiUrl } | ConvertTo-Json | Set-Content -Path (Join-Path $www "api-config.json") -Encoding utf8

Push-Location $apkDir
if (-not (Test-Path (Join-Path $apkDir "node_modules"))) {
  npm install
  if ($LASTEXITCODE -ne 0) { throw "apk npm install failed" }
}
if (-not (Test-Path (Join-Path $apkDir "android"))) {
  npx cap add android
  if ($LASTEXITCODE -ne 0) { throw "cap add android failed" }
}

$manifest = Join-Path $apkDir "android\app\src\main\AndroidManifest.xml"
if (Test-Path $manifest) {
  $text = Get-Content $manifest -Raw
  if ($text -notmatch "usesCleartextTraffic") {
    $text = $text -replace '<application', '<application android:usesCleartextTraffic="true" android:networkSecurityConfig="@xml/network_security_config"'
    Set-Content -Path $manifest -Value $text -NoNewline
  }
}
$xmlDir = Join-Path $apkDir "android\app\src\main\res\xml"
New-Item -ItemType Directory -Force -Path $xmlDir | Out-Null
$nsConfig = Join-Path $xmlDir "network_security_config.xml"
@'
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
'@ | Set-Content -Path $nsConfig -Encoding utf8

npx cap sync android
if ($LASTEXITCODE -ne 0) { throw "cap sync failed" }

$sdk = $env:ANDROID_HOME
if (-not $sdk) { $sdk = $env:ANDROID_SDK_ROOT }
if (-not $sdk) {
  $guess = Join-Path $env:LOCALAPPDATA "Android\Sdk"
  if (Test-Path $guess) { $sdk = $guess }
}
if ($sdk) {
  $localProps = Join-Path $apkDir "android\local.properties"
  $sdkEscaped = ($sdk -replace "\\", "/")
  Set-Content -Path $localProps -Value "sdk.dir=$sdkEscaped" -Encoding ascii
}

$gradlew = Join-Path $apkDir "android\gradlew.bat"
if (-not (Test-Path $gradlew)) { throw "android/gradlew.bat missing. Install Android Studio, then re-run this script." }

Write-Host "Compiling PhishEye.apk"
Push-Location (Join-Path $apkDir "android")
& .\gradlew.bat assembleDebug --quiet
$gradleExit = $LASTEXITCODE
Pop-Location
Pop-Location
if ($gradleExit -ne 0) { throw "Gradle assembleDebug failed. Open apk/android in Android Studio if the SDK or licenses are missing." }

$built = Join-Path $apkDir "android\app\build\outputs\apk\debug\app-debug.apk"
if (-not (Test-Path $built)) { throw "Gradle did not produce app-debug.apk" }
Copy-Item $built (Join-Path $apkDir "PhishEye.apk") -Force
Write-Host "APK ready: $(Join-Path $apkDir 'PhishEye.apk')"
Write-Host "Install it on the phone, start apk/run-backend.ps1 on this PC, then scan from the same Wi-Fi."
