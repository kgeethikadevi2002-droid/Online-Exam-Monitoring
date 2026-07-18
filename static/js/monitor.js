let candidate_id = document.getElementById("candidate_id") ? document.getElementById("candidate_id").value : "unknown";

function logEvent(event_type, remarks="") {
    fetch('/log_event', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            'candidate_id': candidate_id,
            'event_type': event_type,
            'remarks': remarks
        })
    });
}

// Tab switching / Window blur
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        logEvent("Browser Tab Switched", "User switched tab or minimized window");
    }
});

// Focus lost
window.addEventListener('blur', function() {
    logEvent("Browser Focus Lost", "User clicked outside browser");
});

window.addEventListener('focus', function() {
    logEvent("Browser Focus Gained", "User came back to tab");
});


