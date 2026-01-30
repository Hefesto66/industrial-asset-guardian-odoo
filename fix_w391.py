def clean_file(path):
    try:
        with open(path, 'rb') as f:
            content = f.read()
        # Decode as utf-8
        text = content.decode('utf-8')
        # Right strip all whitespace (newlines, spaces, tabs) from the end
        text = text.rstrip()
        # Add exactly one newline
        text += '\n'
        # Write back ensuring LF
        with open(path, 'w', newline='\n', encoding='utf-8') as f:
            f.write(text)
        print(f"Cleaned {path}")
    except Exception as e:
        print(f"Error {path}: {e}")


files = [
    'extra-addons/industrial_asset_guardian/tests/__init__.py',
    'extra-addons/industrial_asset_guardian/tests/test_api.py',
    'extra-addons/industrial_asset_guardian/tests/test_logic.py',
    'extra-addons/industrial_asset_guardian/tests/test_security.py'
]

for f in files:
    clean_file(f)
