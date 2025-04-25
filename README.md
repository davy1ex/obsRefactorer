# obsRefactorer
## Description
One day I set a goal to clean up my obsidian repository of 2000+ notes, some of which were just stupidly added attachments to the assets folder. So I created a cli python script that:
![kek](https://github.com/davy1ex/obsRefactorer/blob/master/docs/2025-04-25%2014-52-15.gif?raw=true)
## Requirements in project:
- `Python` (in my project it 3.12.3)
- `click` (in my project it click==8.1.8)
- `Markdown` (in my project it Markdown==3.8)
- `markdown-it-py` (in my project it markdown-it-py==3.0.0)
- `mdurl` (in my project it mdurl==0.1.2)
U can install it by
```python
pip install -r requirements.txt
```
## What does it do?
1. Looks at files inside 04_archive (this is the PARA method)
2. Find here notes with attachments
3. Search attachemnts inside 03_references
4. Move it to path what u want (it ask u)
5. Repeat!

## How it use?
```bash
git clone https://github.com/davy1ex/obsRefactorer
cd obsRefactorer
pip install -r requirements.txt
python3 main.py
```

## Features:
- U can locate attachemnts to archive folder
- Revert changes: I also added a log to movement_history.txt for fun so that you can return everything back to how it was
