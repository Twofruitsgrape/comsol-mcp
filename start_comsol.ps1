# COMSOL 启动脚本
$ComsolPath = "C:\Program Files\COMSOL\COMSOL62\Multiphysics"

Write-Host "启动 COMSOL 服务器..." -ForegroundColor Cyan
Start-Process -FilePath "$ComsolPath\bin\win64\comsolmphserver.exe" -ArgumentList "-port 2036 -multi on -graphics"

Start-Sleep -Seconds 3

Write-Host "启动 COMSOL Desktop..." -ForegroundColor Cyan
Start-Process -FilePath "$ComsolPath\bin\win64\comsolmphclient.exe" -ArgumentList "-host 127.0.0.1 -port 2036"

Write-Host "COMSOL 已启动！" -ForegroundColor Green
