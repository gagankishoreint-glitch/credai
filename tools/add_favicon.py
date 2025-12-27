import os
import re

target_dir = r"d:\projects\credit-evaluation-system\frontend"
favicon_link = '    <link rel="icon" type="image/png" href="assets/favicon.png">\n'

for filename in os.listdir(target_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if favicon already exists
        if 'rel="icon"' in content or 'rel="shortcut icon"' in content:
             print(f"Favicon already present in {filename}")
             # Optional: could force replace if needed, but let's assume if it exists it might be old and needs update?
             # For now, let's just log it. If user wants *this* logo, we might need to update the href.
             # Let's simple-replace any existing favicon line or add if missing.
             content = re.sub(r'<link rel="icon".*?>\n?', '', content)
             content = re.sub(r'<link rel="shortcut icon".*?>\n?', '', content)
        
        # Inser links after <title>...
        if '</title>' in content:
            new_content = content.replace('</title>', f'</title>\n{favicon_link}')
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Added favicon to {filename}")
        else:
            print(f"No title tag found in {filename}")
