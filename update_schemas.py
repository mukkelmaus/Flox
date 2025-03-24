import os
import re

def update_pydantic_config(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace orm_mode with from_attributes
    updated_content = re.sub(
        r'(\s+)orm_mode(\s*=\s*True)',
        r'\1from_attributes\2',
        content
    )
    
    # Also update Config class if needed for V2 compatibility
    updated_content = re.sub(
        r'(\s+)class Config:',
        r'\1class Config:  # Updated for Pydantic V2',
        updated_content
    )
    
    if content != updated_content:
        with open(file_path, 'w') as file:
            file.write(updated_content)
        return True
    return False

def main():
    schema_dir = 'app/schemas'
    updated_files = []
    
    for root, _, files in os.walk(schema_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                if update_pydantic_config(file_path):
                    updated_files.append(file_path)
    
    print(f"Updated {len(updated_files)} files:")
    for file in updated_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main()