[CmdletBinding()]
param (
)
try {
    Push-Location $PSScriptRoot
    pipreqs.exe . --encoding=utf8 --force --ignore .venv --ignore dist --ignore build --ignore .idea
} finally {
    Pop-Location
}
