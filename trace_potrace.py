import os
import subprocess
from PIL import Image

def vectorize_with_potrace(input_file, output_file):
    print(f"🔄 Haqiqiy SVG vektor chiziqlarini yaratish boshlandi: {input_file}...")
    
    bmp_path = input_file + ".bmp"
    # Convert PNG to BW BMP using PIL (potrace requirement)
    try:
        img = Image.open(input_file).convert('L')
        # Binarize with threshold
        img = img.point(lambda p: p > 200 and 255)
        img.save(bmp_path)
    except Exception as e:
        print(f"Xatolik: Rasmni o'qishda muammo: {e}")
        return

    # Run potrace to generate true scalable vectors
    try:
        subprocess.run(
            ["potrace", bmp_path, "-s", "-o", output_file],
            check=True
        )
        print(f"✅ Mukammal (infinite zoom) SVG tayyor: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Xatolik: potrace ishlashdan to'xtadi: {e}")
    finally:
        # Cleanup
        if os.path.exists(bmp_path):
            os.remove(bmp_path)

def main():
    os.makedirs('output/true_vector', exist_ok=True)
    
    if os.path.exists("image.png"):
        vectorize_with_potrace("image.png", "output/true_vector/image.svg")
    else:
        print("image.png topilmadi!")

    if os.path.exists("image copy.png"):
        vectorize_with_potrace("image copy.png", "output/true_vector/image_copy.svg")
    else:
        print("image copy.png topilmadi!")

if __name__ == "__main__":
    main()
