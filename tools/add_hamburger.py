import os
import re

target_dir = r"d:\projects\credit-evaluation-system\frontend"

hamburger_button = """
                <button class="menu-toggle" id="menuToggle" aria-label="Toggle menu" style="margin-right: 0.5rem;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                </button>"""

# Regex to find navbar-actions div start
# We want to insert after <div class="navbar-actions">
action_pattern = re.compile(r'(<div class="navbar-actions">)', re.IGNORECASE)

for filename in os.listdir(target_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if hamburger already exists
        if 'id="menuToggle"' in content:
            print(f"Hamburger already in {filename}")
            continue
            
        if '<div class="navbar-actions">' in content:
            # Insert hamburger
            new_content = action_pattern.sub(r'\1' + hamburger_button, content)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Added hamburger to {filename}")
        else:
            print(f"No navbar-actions found in {filename}")
