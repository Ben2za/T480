$ErrorActionPreference = 'Stop'
$Build = '2026-08-04.4'
$T480Address = '192.168.1.21'
$WindowsSshPort = 2222
$PublicKey = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPV1qaTfvyHgmvMjxVqKHQ8CdO3ILC3rZ8L/ZpwW5hkN ctos-lenovo-apple-2026-08-04'

function Write-Section([string]$Name) {
    Write-Output ""
    Write-Output "--- $Name ---"
}

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run SETUP_LENOVO_REMOTE.bat as Administrator.'
}

Write-Section 'Identity'
Write-Output "BOOTSTRAP_BUILD=$Build"
whoami.exe
hostname.exe
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber, OsArchitecture

Write-Section 'OpenSSH capability'
$capability = Get-WindowsCapability -Online | Where-Object Name -Like 'OpenSSH.Server*' | Select-Object -First 1
if ($null -eq $capability) {
    throw 'Windows does not publish an OpenSSH.Server capability on this installation.'
}
$capability | Select-Object Name, State
if ($capability.State -ne 'Installed') {
    Add-WindowsCapability -Online -Name $capability.Name | Format-List
}
$capability = Get-WindowsCapability -Online | Where-Object Name -Like 'OpenSSH.Server*' | Select-Object -First 1
if ($capability.State -ne 'Installed') {
    throw "OpenSSH Server capability did not reach Installed state: $($capability.State)"
}

$sshdCandidates = @(
    (Join-Path $env:WINDIR 'System32\OpenSSH\sshd.exe')
    (Join-Path $env:WINDIR 'Sysnative\OpenSSH\sshd.exe')
    (Join-Path $env:ProgramFiles 'OpenSSH\sshd.exe')
)
$sshdExe = $sshdCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($null -eq $sshdExe) {
    throw "OpenSSH Server is marked Installed but sshd.exe is absent. Checked: $($sshdCandidates -join ', ')"
}

Write-Section 'Dedicated administrator key'
$authPath = Join-Path $env:ProgramData 'ssh\administrators_authorized_keys'
if (-not (Test-Path -LiteralPath $authPath)) {
    New-Item -ItemType File -Path $authPath -Force | Out-Null
}
$present = Select-String -LiteralPath $authPath -SimpleMatch $PublicKey -Quiet -ErrorAction SilentlyContinue
if (-not $present) {
    Add-Content -LiteralPath $authPath -Value $PublicKey -Encoding ascii
}
# Use well-known SIDs so this works regardless of the Windows display language.
& icacls.exe $authPath /inheritance:r /grant '*S-1-5-32-544:F' /grant '*S-1-5-18:F'

Write-Section 'Dedicated Windows OpenSSH port'
$configPath = Join-Path $env:ProgramData 'ssh\sshd_config'
$defaultConfig = Join-Path $env:WINDIR 'System32\OpenSSH\sshd_config_default'
if (-not (Test-Path -LiteralPath $configPath)) {
    if (Test-Path -LiteralPath $defaultConfig) {
        Copy-Item -LiteralPath $defaultConfig -Destination $configPath
    } else {
        @(
            "Port $WindowsSshPort"
            'AddressFamily any'
            'ListenAddress 0.0.0.0'
            'ListenAddress ::'
            'PubkeyAuthentication yes'
            'PasswordAuthentication no'
            'AuthorizedKeysFile .ssh/authorized_keys'
            'Subsystem sftp sftp-server.exe'
            'Match Group administrators'
            '       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys'
        ) | Set-Content -LiteralPath $configPath -Encoding ascii
    }
}
$configLines = Get-Content -LiteralPath $configPath
$filteredLines = @($configLines | Where-Object { $_ -notmatch '^\s*Port\s+\d+\s*$' })
$newConfig = @("Port $WindowsSshPort") + $filteredLines
Set-Content -LiteralPath $configPath -Value $newConfig -Encoding ascii

$sshKeygenExe = Join-Path (Split-Path -Parent $sshdExe) 'ssh-keygen.exe'
& $sshKeygenExe -A
& $sshdExe -t -f $configPath

$ruleName = 'CTOS-Windows-OpenSSH-2222'
if (-not (Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name $ruleName -DisplayName 'Windows OpenSSH - T480 only' `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort $WindowsSshPort `
        -Profile Any -RemoteAddress $T480Address | Out-Null
} else {
    Set-NetFirewallRule -Name $ruleName -Enabled True -Direction Inbound -Action Allow `
        -Profile Any -RemoteAddress $T480Address
}

Set-Service -Name sshd -StartupType Automatic
Start-Service -Name sshd
Restart-Service -Name sshd

Write-Section 'Network'
Get-NetConnectionProfile | Select-Object Name, InterfaceAlias, NetworkCategory, IPv4Connectivity
Get-NetIPConfiguration | Select-Object InterfaceAlias, IPv4Address, IPv4DefaultGateway, DNSServer
Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed
Test-Connection -ComputerName $T480Address -Count 2

Write-Section 'Result'
Get-Service -Name sshd | Select-Object Name, Status, StartType
Get-NetTCPConnection -LocalPort $WindowsSshPort -State Listen | Select-Object LocalAddress, LocalPort, State
Write-Output "WINDOWS_SSH_PORT=$WindowsSshPort"
Write-Output 'READY_FOR_T480_SSH=true'
Write-Output 'No password or Apple Account credential was collected.'
