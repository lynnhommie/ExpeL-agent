import sys
print("Starting...")
sys.stdout.flush()
try:
    from prompts.templates.human import RULE_TEMPLATE
    print("RULE_TEMPLATE OK")
    print("livestream in RULE_TEMPLATE:", 'livestream' in RULE_TEMPLATE)
    sys.stdout.flush()
except Exception as e:
    print("ERROR:", e)
    sys.stdout.flush()
