document.addEventListener("DOMContentLoaded", () => {
    // We expect window.SESSION_ID and window.PREVIEW_URL to be set by the template
    const sessionId = window.SESSION_ID;
    const previewUrl = window.PREVIEW_URL;
    
    if (!sessionId) {
        console.error("No session ID found");
        return;
    }

    const evtSource = new EventSource('/progress/' + sessionId);
    
    evtSource.onmessage = function(e) {
        const data = JSON.parse(e.data);
        
        if (data.type === "done") {
            evtSource.close();
            window.location.href = previewUrl;
        } else if (data.type === "error") {
            evtSource.close();
            alert("Error processing file: " + data.message);
            window.location.href = "/";
        } else if (data.type === "progress") {
            // Un-active all
            document.querySelectorAll('.step').forEach(el => {
                el.classList.remove('active');
            });
            // Mark previous as done
            for (let i = 1; i < data.step; i++) {
                const prev = document.getElementById('step-' + i);
                if(prev) {
                    prev.classList.add('done');
                    prev.classList.remove('active');
                }
            }
            // Mark current as active
            const curr = document.getElementById('step-' + data.step);
            if(curr) {
                curr.classList.add('active');
            }
        }
    };

    evtSource.onerror = function(e) {
        evtSource.close();
        alert("Connection to server lost. Please try again.");
        window.location.href = "/";
    };
});
