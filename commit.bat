@echo off
chcp 65001 >nul
echo ========================================
echo           手动提交工具
echo ========================================
echo.
echo 当前目录：%cd%
echo.
set /p commit_msg="请输入提交信息（按回车确认）："

if "%commit_msg%"=="" (
    echo.
    echo [警告] 提交信息不能为空，请重新运行。
    pause
    exit /b
)

echo.
echo [1/4] 正在检查远程更新...
git pull

echo.
echo [2/4] 正在添加所有变更...
git add .

echo.
echo [3/4] 正在提交...
git commit -m "%commit_msg%"

echo.
echo [4/4] 正在推送到GitHub...
git push

echo.
echo ========================================
echo           提交完成！
echo ========================================
echo.
pause