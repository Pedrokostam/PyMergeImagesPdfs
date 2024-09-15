[CmdletBinding()]
param (
)
try {
    Push-Location $PSScriptRoot
    pigar generate  --question-answer yes --with-referenced-comments
} finally {
    Pop-Location
}
