// Animated gradient and waves background
(function() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = window.innerWidth;
    let height = window.innerHeight;
    let t = 0;

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resize);
    resize();

    function lerp(a, b, n) { return a + (b - a) * n; }
    function drawGradient() {
        const grad = ctx.createLinearGradient(0, 0, width, height);
        grad.addColorStop(0, `hsl(${(t*20)%360}, 80%, 60%)`);
        grad.addColorStop(0.5, `hsl(${(t*20+60)%360}, 80%, 55%)`);
        grad.addColorStop(1, `hsl(${(t*20+120)%360}, 80%, 60%)`);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);
    }
    function drawWaves() {
        for (let i = 0; i < 3; i++) {
            ctx.save();
            ctx.globalAlpha = 0.18 + 0.08 * i;
            ctx.beginPath();
            const waveHeight = 32 + 18 * i;
            const yOffset = lerp(height * 0.5, height * (0.7 + i*0.1), Math.sin(t/2 + i));
            ctx.moveTo(0, yOffset);
            for (let x = 0; x <= width; x += 2) {
                const y = yOffset + Math.sin((x/width)*4*Math.PI + t*0.8 + i) * waveHeight * Math.sin(t/2 + i);
                ctx.lineTo(x, y);
            }
            ctx.lineTo(width, height);
            ctx.lineTo(0, height);
            ctx.closePath();
            ctx.fillStyle = `hsl(${(t*20+60*i)%360}, 80%, 70%)`;
            ctx.fill();
            ctx.restore();
        }
    }
    function animate() {
        ctx.clearRect(0, 0, width, height);
        drawGradient();
        drawWaves();
        t += 0.012;
        requestAnimationFrame(animate);
    }
    animate();
})();

const form = document.getElementById('story-form');
const resultDiv = document.getElementById('result');
const loadingDiv = document.getElementById('loading');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    resultDiv.textContent = '';
    loadingDiv.style.display = 'block';

    const genre = document.getElementById('genre').value;
    const runtime = document.getElementById('runtime').value;
    const characterCount = document.getElementById('characters').value;

    try {
        const response = await fetch('http://localhost:8000/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                genre,
                runtime: Number(runtime),
                character_count: Number(characterCount)
            })
        });
        if (!response.ok) {
            throw new Error('Failed to generate storyline.');
        }
        const data = await response.json();
        resultDiv.textContent = data.storyline;
    } catch (err) {
        resultDiv.textContent = 'Error: ' + err.message;
    } finally {
        loadingDiv.style.display = 'none';
    }
}); 
