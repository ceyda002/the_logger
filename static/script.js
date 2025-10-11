console.log('Script loaded!');


window.addEventListener('beforeunload', () => {
    if (savedRunning && runningStartTime) {
        // Add elapsed time up to this moment
        elapsed = getElapsed();
        localStorage.setItem('stopwatchElapsed', elapsed);
        // Set runningStartTime to now so it continues properly
        runningStartTime = Date.now();
        localStorage.setItem('stopwatchRunningStart', runningStartTime);
    }
});
function getElapsed() {
    if (savedRunning && runningStartTime) {
        return elapsed + (Date.now() - runningStartTime);
    }
    return elapsed;
}




const searchInput = document.getElementById('tag-search');

if (searchInput) {
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase();
        document.querySelectorAll('.course-card').forEach(card => {
            const tags = card.querySelectorAll('.tag');
            let match = false;
            tags.forEach(tag => {
                if (tag.innerText.toLowerCase().includes(query)) match = true;

            });
            card.style.display = match || query === '' ? '' : 'none';
        });
    });
}



document.addEventListener('DOMContentLoaded', () => {
    const audio = document.getElementById('studyAudio');
    const toggleBtn = document.getElementById('audioToggle');
    const statusSpan = document.getElementById('audioStatus');

    if (!audio || !toggleBtn || !statusSpan) return;

    // Initialize audio based on saved preference
    const savedTime = parseFloat(localStorage.getItem('studyAudioTime')) || 0;
    audio.currentTime = savedTime;
    if (localStorage.getItem('studyAudio') === 'on') {
        audio.play().catch(() => console.log("Autoplay blocked."));
    }

    // Update the status initially
    statusSpan.textContent = audio.paused ? '🔈 Off' : '🔊 On';

    // Listen for clicks
    toggleBtn.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().then(() => {
                statusSpan.textContent = '🔊 On';
                localStorage.setItem('studyAudio', 'on');
            }).catch(() => {
                console.log("Autoplay blocked, try clicking the button again.");
            });
        } else {
            audio.pause();
            statusSpan.textContent = '🔈 Off';
            localStorage.setItem('studyAudio', 'off');
        }
    });

    // Optional: Keep status in sync in case audio ends or is paused by other means
    audio.addEventListener('pause', () => statusSpan.textContent = '🔈 Off');
    audio.addEventListener('play', () => statusSpan.textContent = '🔊 On');

    window.addEventListener('beforeunload', () => {
        localStorage.setItem('studyAudioTime', audio.currentTime);
    });
});

audio.volume = 0;
audio.play().then(() => {
    let vol = 0;
    const fade = setInterval(() => {
        vol += 0.05;
        if (vol >= 1) {
            vol = 1;
            clearInterval(fade);
        }
        audio.volume = vol;
    }, 50);
});
