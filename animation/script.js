document.addEventListener("DOMContentLoaded", () => {
    const svgContainer = document.getElementById("svg-container");
    const btnImage = document.getElementById("btn-image");
    const btnImageCopy = document.getElementById("btn-image-copy");
    const btnReplay = document.getElementById("btn-replay");

    let currentSvgPath = "../output/true_vector/image.svg";

    async function loadAndAnimateSVG(svgUrl) {
        svgContainer.innerHTML = "<p style='color: #000; font-size: 18px;'>SVG tayyorlanmoqda...</p>";
        
        try {
            // SVG matnini yuklab olamiz
            const response = await fetch(svgUrl);
            if (!response.ok) throw new Error("Fayl topilmadi yoki o'qishda xatolik yuz berdi");
            const text = await response.text();
            
            // SVG kodini container ga joylaymiz
            svgContainer.innerHTML = text;
            const svgElement = svgContainer.querySelector("svg");
            
            if (svgElement) {
                // Responsiveness uchun moslashuv
                svgElement.style.width = "100%";
                svgElement.style.height = "100%";
                
                // SVG da chizilgan Path larni ajratib olamiz
                const paths = svgElement.querySelectorAll("path");
                
                // Animate logic -> Chizish effekti
                animateDrawing(paths);
            }
        } catch (error) {
            svgContainer.innerHTML = `<p style='color: red'>Xato: ${error.message}</p>`;
        }
    }

    function animateDrawing(paths) {
        // 1-QADAM: Barcha elementlarni yashirin chiziqli ko'rinishga o'tkazish
        paths.forEach(path => {
            // O'zining original uzunligini o'lchaymiz!
            const length = path.getTotalLength();
            
            // O'zini haqiqiy qora rangi saqlanib qolinadi
            const originalFill = path.getAttribute("fill") || "#000000";
            path.dataset.originalFill = originalFill;
            
            // Avvaliga uning ichi bo'sh (<fill="transparent">)
            // va atrofidagi Stroke (chizig'i) qalamdek aylantiriladi
            path.style.fill = "transparent";
            path.style.stroke = "#2d3436";
            path.style.strokeWidth = "2px";
            
            // Dash array uzoqligiga path uznunligini berib qo'yiladi 
            path.style.strokeDasharray = length;
            path.style.strokeDashoffset = length;
            
            // Trace qilinayotganda transition bilan bir tekis yuritadi
            path.classList.add("trace-path");
            
            // UI chizildi deb o'ylamasligi uchun uni forcing redrawing qilamiz
            path.getBoundingClientRect();
        });

        // 2-QADAM: Bir oz vaqt o'tgach, chizishni "Start" qilish
        setTimeout(() => {
            paths.forEach((path) => {
                // Haqiqiy tabiatga o'xshashi uchun ozgina random kechikish (Stagger effect) 
                const delay = Math.random() * 800; // 0 dan 0.8 soniyagacha orasida aralash tasodif

                setTimeout(() => {
                    // Dash offsetni 0 ga beramiz-> SVG qizilib atrofini huddi odam qo'lidek chizib o'tadi
                    path.style.strokeDashoffset = "0";
                    
                    // Chizig' chizilib butkul atrofini o'rab olgach, ichini huddi bo'yoq to'kilgandek (fill) asil rangga burkaymiz
                    setTimeout(() => {
                        path.style.fill = path.dataset.originalFill;
                        path.style.stroke = "transparent";
                    }, 3500); // 3.5 soniya - Asosiy stroke transition tugagandan keyin!
                    
                }, delay);
            });
        }, 150);
    }

    // Tugmalar nazorati (Event Listeners)
    btnImage.addEventListener("click", () => {
        btnImage.classList.add("active");
        btnImageCopy.classList.remove("active");
        currentSvgPath = "../output/true_vector/image.svg";
        loadAndAnimateSVG(currentSvgPath);
    });

    btnImageCopy.addEventListener("click", () => {
        btnImageCopy.classList.add("active");
        btnImage.classList.remove("active");
        currentSvgPath = "../output/true_vector/image_copy.svg";
        loadAndAnimateSVG(currentSvgPath);
    });

    btnReplay.addEventListener("click", () => {
        // Shunchaki o'sha tanlangan resurisni yana yuklaymiz
        loadAndAnimateSVG(currentSvgPath);
    });

    // Sahifa yuklanganida avtomat birinchi SVG chiziladi
    loadAndAnimateSVG(currentSvgPath);
});
