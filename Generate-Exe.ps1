Push-Location $PSScriptRoot
if ((Test-Path .venv) -and -not $env:VIRTUAL_ENV){
    . ./.venv/Scripts/activate.ps1
}
python ./cx_freeze_generate_exe.py build

# Remove-Item .\dist -ea silentlycontinue -Recurse
# pyinstaller --noconfirm `
#     --onedir --console `
#     --icon "$psscriptroot\icon.ico" `
#     --add-data=language.json:. `
#     --add-data=config.toml:. `
#     --add-data 'implementation:implementation' `
#     --paths . `
#     --clean `
#     "$psscriptroot\merge_documents.py" 

Pop-Location