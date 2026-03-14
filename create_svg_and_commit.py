import os
import base64
import subprocess
from PIL import Image

def run_git_command(command, commit_msg=None):
    if commit_msg:
        print(f"Git: {commit_msg}")
        os.system("git add .")
        os.system(f'git commit -m "{commit_msg}"')
    else:
        os.system(command)

def png_to_svg_embedded(input_path, output_path):
    print(f"Converting {input_path} to SVG (Preserving 100% Quality)...")
    img = Image.open(input_path)
    width, height = img.size
    
    with open(input_path, 'rb') as f:
        png_data = f.read()
    
    b64_data = base64.b64encode(png_data).decode('utf-8')
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <title>High Quality Converted Image</title>
  <image width="{width}" height="{height}" href="data:image/png;base64,{b64_data}"/>
</svg>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"✅ Saved to {output_path}")

def main():
    # Setup directories
    os.chdir("/home/wikki/animater")
    os.makedirs('output/high_quality', exist_ok=True)
    
    # 1. Initialize git if not already
    if not os.path.exists('.git'):
        run_git_command("git init")
        run_git_command(None, "Initial repository setup")
    
    # 2. Convert first image
    if os.path.exists("image.png"):
        png_to_svg_embedded("image.png", "output/high_quality/image.svg")
        run_git_command(None, "feat: image.png rasmi sifatini saqlagan holda SVG ga o'girildi")
    else:
        print("image.png topilmadi!")

    # 3. Convert second image
    if os.path.exists("image copy.png"):
        png_to_svg_embedded("image copy.png", "output/high_quality/image_copy.svg")
        run_git_command(None, "feat: image copy.png rasmi sifatini saqlagan holda SVG ga o'girildi")
    else:
        print("image copy.png topilmadi!")

    print("\n🎉 Barcha amallar bajarildi va muvaffaqiyatli commit qilindi!")

if __name__ == "__main__":
    main()
