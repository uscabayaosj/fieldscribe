// Journal entries related JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const entryForm = document.querySelector('#entry-form');
    const deleteButtons = document.querySelectorAll('.delete-entry');
    const shareButtons = document.querySelectorAll('.share-entry');
    const exportButtons = document.querySelectorAll('.export-entry');

    if (entryForm) {
        entryForm.addEventListener('submit', handleEntrySubmit);
    }

    deleteButtons.forEach(button => {
        button.addEventListener('click', handleDeleteEntry);
    });

    shareButtons.forEach(button => {
        button.addEventListener('click', handleShareEntry);
    });

    exportButtons.forEach(button => {
        button.addEventListener('click', handleExportEntry);
    });

    initializeLocationCapture();
});

async function handleEntrySubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await fetch(event.target.action, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to save entry', 'error');
        }
    } catch (error) {
        console.error('Entry submission error:', error);
        showNotification('An error occurred while saving the entry', 'error');
    }
}

async function handleDeleteEntry(event) {
    if (confirm('Are you sure you want to delete this entry?')) {
        const entryId = event.target.dataset.entryId;
        try {
            const response = await fetch(`/entry/${entryId}/delete`, {
                method: 'POST',
            });

            if (response.ok) {
                window.location.reload();
            } else {
                const data = await response.json();
                showNotification(data.error || 'Failed to delete entry', 'error');
            }
        } catch (error) {
            console.error('Delete entry error:', error);
            showNotification('An error occurred while deleting the entry', 'error');
        }
    }
}

async function handleShareEntry(event) {
    const entryId = event.target.dataset.entryId;
    try {
        const response = await fetch(`/entry/${entryId}/share`, {
            method: 'POST',
        });

        if (response.ok) {
            const data = await response.json();
            navigator.clipboard.writeText(data.share_url);
            showNotification('Share link copied to clipboard');
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to generate share link', 'error');
        }
    } catch (error) {
        console.error('Share entry error:', error);
        showNotification('An error occurred while generating the share link', 'error');
    }
}

function handleExportEntry(event) {
    const entryId = event.target.dataset.entryId;
    window.open(`/entry/${entryId}/export`, '_blank');
}

function initializeLocationCapture() {
    const locationInput = document.querySelector('#location');
    if (locationInput && 'geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition((position) => {
            const { latitude, longitude } = position.coords;
            locationInput.value = `${latitude}, ${longitude}`;
        }, (error) => {
            console.error('Geolocation error:', error);
        });
    }
}
