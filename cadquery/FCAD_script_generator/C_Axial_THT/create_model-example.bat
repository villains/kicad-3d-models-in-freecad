taskkill -im freecad.exe /f
@echo OFF
echo cadquery-freecad-module required
@echo ON
cd %~p0
start "" "c:\FreeCAD\bin\freecad" main_generator.py C_Axial_L12.0mm_D8.5mm_P20.00mm_Horizontal
:: C_Axial_L3.8mm_D2.6mm_P7.50mm_Horizontal
:: start "" "d:\FreeCAD_015\bin\freecad" main_generator.py %1

::pause