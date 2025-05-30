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