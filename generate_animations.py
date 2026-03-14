import os
import glob
import xml.etree.ElementTree as ET

def create_animated_svg(input_path, output_path):
    print(f"🔄 Avtomat animatsiyalanuvchi SVG yaratilmoqda: {input_path}...")
    
    # SVG namespace configuration
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    try:
        tree = ET.parse(input_path)
        root = tree.getroot()
        
        # Original SVG attributes
        namespace = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Hamma path larga pathLength="100" qo'shamiz va inline delay beramiz
        paths = root.findall('.//{http://www.w3.org/2000/svg}path')
        num_paths = len(paths)
        for i, path in enumerate(paths):
            path.set('pathLength', '100')
            # Bir tekisda boshlanishi uchun, 0 soniyadan 5 soniyagacha tarqatamiz:
            delay = (i / max(1, num_paths)) * 10.0
            path.set('style', f'animation-delay: {delay:.2f}s;')
            
            # O'rnatilgan fill larni o'chiramiz
            if 'fill' in path.attrib:
                del path.attrib['fill']
            if 'stroke' in path.attrib:
                del path.attrib['stroke']
                
        # CSS Animatsiyasini (style) SVG ichiga quyamiz (<style> tagni qo'shamiz)
        style_elem = ET.Element('{http://www.w3.org/2000/svg}style')
        style_elem.text = """
            path {
                vector-effect: non-scaling-stroke;
                stroke-dasharray: 100;
                stroke-dashoffset: 100; /* Boshida ko'rinmas turishi uchun 100 bo'lishi shart */
                stroke-width: 0.5px;
                stroke: black;
                fill: transparent;
                animation: draw_and_fill 4s linear both; /* ikkala tarafga ham apply() qiladi jami har biri 4sekund chizadi */
            }

            @keyframes draw_and_fill {
                0% {
                    stroke-dashoffset: 100;
                    fill: transparent;
                    stroke: black;
                }
                75% {
                    stroke-dashoffset: 0;
                    fill: transparent;
                    stroke: black;
                }
                100% {
                    stroke-dashoffset: 0;
                    fill: black;
                    stroke: transparent;
                }
            }
        """
        
        # Style tagini eng boshiga kiritamiz
        root.insert(0, style_elem)
        
        # Faylni saqlaymiz
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"✅ Animatsiyali fayl saqlandi: {output_path}")

    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")

def main():
    # Yangi chiqadigan papkani yaratish
    os.makedirs('output/animated', exist_ok=True)
    
    input_dir = 'output/true_vector'
    
    if not os.path.exists(input_dir):
        print("XATO: Avval 'trace_potrace.py' ni ishga tushirib vektorli SVG larni yarating!")
        return

    svg_files = glob.glob(os.path.join(input_dir, '*.svg'))
    if not svg_files:
        print("Hech qanday SVG topilmadi!")
        return
        
    for svg_file in svg_files:
        filename = os.path.basename(svg_file)
        # Nomiga '_animated' qoshib saqlaymiz
        name, ext = os.path.splitext(filename)
        output_file = os.path.join('output/animated', f"{name}_animated{ext}")
        
        create_animated_svg(svg_file, output_file)

if __name__ == "__main__":
    main()
