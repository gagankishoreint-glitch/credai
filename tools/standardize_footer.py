import os
import re

target_dir = r"d:\projects\credit-evaluation-system\frontend"

footer_content = """    <!-- Shared Footer -->
    <footer style="background: var(--color-bg-primary); border-top: 1px solid var(--color-border); padding: 4rem 0;">
        <div class="container">
            <div class="grid grid-2 gap-xl">
                <div>
                    <a href="index.html" class="navbar-logo" style="margin-bottom: 1.5rem; display: inline-flex;">
                        <img src="assets/logo.png" alt="CE Logo" class="logo-image">
                        <span style="font-size: 1.5rem;">Credit Evaluator</span>
                    </a>
                    <p style="color: var(--color-text-secondary); line-height: 1.6; max-width: 400px;">
                        Professional AI-driven credit assessment for modern businesses. Fast, transparent, and secure evaluation.
                    </p>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1.5rem;">Frequently Asked Questions</h3>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="margin-bottom: 0.5rem; color: var(--color-text-primary);">What is this site about?</h4>
                        <p style="color: var(--color-text-secondary); font-size: 0.95rem;">
                            This platform uses advanced Machine Learning (XGBoost) to evaluate business creditworthiness instantly. We analyze financial parameters like revenue, EBITDA, and debt service coverage to provide a real-time risk assessment without manual delays.
                        </p>
                    </div>

                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="margin-bottom: 0.5rem; color: var(--color-text-primary);">How trustworthy is the evaluation?</h4>
                        <p style="color: var(--color-text-secondary); font-size: 0.95rem;">
                            Our system is calibrated on thousands of historical credit records, achieving over 75% accuracy. While we provide a high-confidence "Decision Assistant," final approvals are always reviewed by human underwriters to ensure fairness and compliance.
                        </p>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--color-border); text-align: center; color: var(--color-text-muted); font-size: 0.9rem;">
                &copy; 2025 Credit Evaluator. All rights reserved.
            </div>
        </div>
    </footer>"""

# Regex: Find existing footer (if any) or find place to insert
# Strategy: If footer exists, replace it. If not, insert before </body>
footer_pattern = re.compile(r'<footer.*?</footer>', re.DOTALL)

for filename in os.listdir(target_dir):
    if filename.endswith(".html") and filename != "login.html": # Skip login? Maybe. The user said 'home page... also the footer... regarding our site'. Usually login pages are simple. I'll include it or skip it. I'll skip login to keep it clean.
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        if '<footer' in content:
            # Replace existing
            new_content = footer_pattern.sub(footer_content, content)
            action = "Updated"
        else:
            # Insert before script tags or body
            # Try to place before <script src="js/theme.js"> if it exists, else before </body>
            if '<script' in content:
                 # Find first script occurrence to be safe, or just before body? 
                 # Usually footer is before scripts.
                 # Let's find </body>
                 script_idx = content.find('<script')
                 if script_idx != -1:
                     new_content = content[:script_idx] + footer_content + "\n\n    " + content[script_idx:]
                     action = "Inserted (before scripts)"
                 else:
                     new_content = content.replace('</body>', footer_content + '\n</body>')
                     action = "Inserted (before body)"
            else:
                new_content = content.replace('</body>', footer_content + '\n</body>')
                action = "Inserted (before body)"
        
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"{action} footer in {filename}")
        else:
            print(f"Footer already up to date in {filename}")
