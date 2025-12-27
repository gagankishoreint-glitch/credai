import os
import re

target_dir = r"d:\projects\credit-evaluation-system\frontend"

# The standardized menu structure (Removing Compare and Calculator)
standard_nav_menu = """            <ul class="navbar-menu">
                <li><a href="index.html">Home</a></li>
                <li><a href="application.html">Application</a></li>
                <li><a href="dashboard.html">Dashboard</a></li>
                <li><a href="methodology.html">Docs</a></li>
                <li><a href="contact.html">Contact Us</a></li>
            </ul>"""

# Regex to find the navbar-menu ul
# It typically starts with <ul class="navbar-menu"> and ends with </ul>
# We use DOTALL to match across newlines
pattern = re.compile(r'<ul class="navbar-menu">.*?</ul>', re.DOTALL)

for filename in os.listdir(target_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if the file has a navbar-menu
        if '<ul class="navbar-menu">' in content:
            # Perform replacement
            new_content = pattern.sub(standard_nav_menu, content)
            
            if new_content != content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated menu in {filename}")
            else:
                print(f"Menu already standard in {filename}")
        else:
            print(f"No navbar-menu found in {filename}")
