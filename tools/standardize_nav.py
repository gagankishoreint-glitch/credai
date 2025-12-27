import os

target_dir = r"d:\projects\credit-evaluation-system\frontend"
standard_nav_actions = """            <div class="navbar-actions">
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
                    <svg id="themeIcon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                </button>
                <a href="login.html" class="btn btn-ghost" id="navLoginBtn" style="padding: 0.6rem 1.5rem;">Login</a>
                <a href="dashboard.html" class="btn btn-primary" id="navDashboardBtn" style="padding: 0.6rem 1.5rem;">Dashboard</a>
            </div>"""

for filename in os.listdir(target_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the start and end of navbar-actions
        start_marker = '<div class="navbar-actions">'
        end_marker = '</div>'
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            # Find the closing div for this block. Assuming it's the next </div>
            # A bit fragile if nested, but looking at the files, navbar-actions usually contains just the button and links.
            # Let's count braces to be safe or just find the first </div> after the content inside.
            # Actually, the button contains SVGs which have closing tags.
            # We can rely on the indentation or just specific known patterns.
            
            # Simple approach: Replace the known block from compare.html roughly
            # Better approach: rely on the fact that `navbar-actions` ends before `</div>\n        </div>\n    </nav>`
            
            # Let's try to locate the closing div by context.
            # It usually ends with </div> followed by </div> (container) and </nav>
            
            # Let's assume standard formatting:
            # <div class="navbar-actions"> ... </div>
            
            # We will use regex for robustness across variations
            import re
            pattern = re.compile(r'<div class="navbar-actions">(.*?)</div>', re.DOTALL)
            
            # Check if replacement is needed (if it doesn't already allow login/dashboard in the standard way)
            if 'id="navLoginBtn"' not in content or 'id="navDashboardBtn"' not in content:
                new_content = re.sub(r'<div class="navbar-actions">.*?</div>', standard_nav_actions, content, flags=re.DOTALL)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {filename}")
            else:
                print(f"Skipped {filename} (already standard)")
