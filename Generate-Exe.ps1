Push-Location $PSScriptRoot
if ((Test-Path .venv) -and -not $env:VIRTUAL_ENV) {
    . ./.venv/Scripts/activate.ps1
}
python ./merge_documents.py --generate-help-preview
python ./cx_freeze_generate_exe.py build
Pop-Location