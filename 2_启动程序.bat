@echo off
setlocal

call .venv\Scripts\activate
python annotation_tool.py

@echo off start "" "http://127.0.0.1:7860"