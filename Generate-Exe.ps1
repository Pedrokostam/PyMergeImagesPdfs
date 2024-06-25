Push-Location $PSScriptRoot
if ((Test-Path .venv) -and -not $env:VIRTUAL_ENV){
    . ./.venv/Scripts/activate.ps1
}
python ./cx_freeze_generate_exe.py build
Pop-Location