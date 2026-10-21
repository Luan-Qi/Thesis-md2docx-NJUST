@echo off
setlocal

pushd "%~dp0"

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

if "%THESIS_DOCX2PDF_BACKEND%"=="" set "THESIS_DOCX2PDF_BACKEND=auto"
if "%THESIS_PDF_PREVIEW_DPI%"=="" set "THESIS_PDF_PREVIEW_DPI=120"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "md2docx.py" "example\thesis-demo.md" --pdf --pages --out "example\output" --backend "%THESIS_DOCX2PDF_BACKEND%" --dpi "%THESIS_PDF_PREVIEW_DPI%"
) else (
  python "md2docx.py" "example\thesis-demo.md" --pdf --pages --out "example\output" --backend "%THESIS_DOCX2PDF_BACKEND%" --dpi "%THESIS_PDF_PREVIEW_DPI%"
)

set STATUS=%errorlevel%
if not %STATUS%==0 goto done

rem Write real table-of-contents page numbers into the DOCX (needs Word;
rem the PDF above is already correct either way).
py -3 "md2docx.py" refresh-fields "example\output\thesis-demo.docx" >nul 2>nul
if not %errorlevel%==0 echo note: refresh-fields skipped (Microsoft Word not available)

echo Generated: %cd%\example\output\thesis-demo.docx
echo Generated: %cd%\example\output\thesis-demo.pdf
if %STATUS%==0 echo Generated PDF pages: %cd%\example\output\pages\page-*.png

:done
popd
exit /b %STATUS%
