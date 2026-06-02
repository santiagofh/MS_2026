@echo off
REM ============================================
REM Script de actualización automatizado REM
REM ============================================
echo Iniciando proceso de actualización...
echo.

REM Cambiar al directorio de trabajo
echo [1/6] Cambiando directorio...
cd /d "C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\Salud Pública\MS_2026"

echo Directorio actual: %CD%
echo.

REM Ejecutar scripts Python
echo [2/6] Ejecutando Calculo MS-2026.py...
python "Calculo MS-2026.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar el primer script Python.
    pause
    exit /b 1
)
echo.

echo [3/6] Ejecutando Calculo_fecha_corte_REM.py...
python "Calculo_fecha_corte_REM.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar el segundo script Python.
    pause
    exit /b 1
)
echo.

echo.
echo ============================================
echo ¡Proceso completado exitosamente!
echo ============================================
pause
