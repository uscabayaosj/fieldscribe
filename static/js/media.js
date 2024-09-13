// Media handling JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const mediaUploadForm = document.querySelector('#media-upload-form');
    const deleteMediaButtons = document.querySelectorAll('.delete-media');

    if (mediaUploadForm) {
        mediaUploadForm.addEventListener('submit', handleMediaUpload);
    }

    deleteMediaButtons.forEach(button => {
        button.addEventListener('click', handleDeleteMedia);
    });

    initializeMediaCapture();
});

async function handleMediaUpload(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
        const response = await fetch(event.target.action, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            showNotification('Media uploaded successfully');
            // Update the UI to show the new media
            updateMediaDisplay(data.filename);
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to upload media', 'error');
        }
    } catch (error) {
        console.error('Media upload error:', error);
        showNotification('An error occurred while uploading media', 'error');
    }
}

async function handleDeleteMedia(event) {
    if (confirm('Are you sure you want to delete this media?')) {
        const mediaId = event.target.dataset.mediaId;
        try {
            const response = await fetch(`/media/${mediaId}/delete`, {
                method: 'POST',
            });

            if (response.ok) {
                event.target.closest('.media-item').remove();
                showNotification('Media deleted successfully');
            } else {
                const data = await response.json();
                showNotification(data.error || 'Failed to delete media', 'error');
            }
        } catch (error) {
            console.error('Delete media error:', error);
            showNotification('An error occurred while deleting the media', 'error');
        }
    }
}

function initializeMediaCapture() {
    const photoCapture = document.querySelector('#photo-capture');
    const audioCapture = document.querySelector('#audio-capture');
    const videoCapture = document.querySelector('#video-capture');

    if (photoCapture) {
        photoCapture.addEventListener('change', capturePhoto);
    }

    if (audioCapture) {
        audioCapture.addEventListener('change', captureAudio);
    }

    if (videoCapture) {
        videoCapture.addEventListener('change', captureVideo);
    }
}

function capturePhoto(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'w-full h-auto';
            document.querySelector('#media-preview').appendChild(img);
        }
        reader.readAsDataURL(file);
    }
}

function captureAudio(event) {
    const file = event.target.files[0];
    if (file) {
        const audio = document.createElement('audio');
        audio.src = URL.createObjectURL(file);
        audio.controls = true;
        document.querySelector('#media-preview').appendChild(audio);
    }
}

function captureVideo(event) {
    const file = event.target.files[0];
    if (file) {
        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        video.controls = true;
        video.className = 'w-full h-auto';
        document.querySelector('#media-preview').appendChild(video);
    }
}

function updateMediaDisplay(filename) {
    const mediaPreview = document.querySelector('#media-preview');
    const fileExtension = filename.split('.').pop().toLowerCase();

    if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
        const img = document.createElement('img');
        img.src = `/static/uploads/${filename}`;
        img.className = 'w-full h-auto';
        mediaPreview.appendChild(img);
    } else if (fileExtension === 'mp3') {
        const audio = document.createElement('audio');
        audio.src = `/static/uploads/${filename}`;
        audio.controls = true;
        mediaPreview.appendChild(audio);
    } else if (fileExtension === 'mp4') {
        const video = document.createElement('video');
        video.src = `/static/uploads/${filename}`;
        video.controls = true;
        video.className = 'w-full h-auto';
        mediaPreview.appendChild(video);
    }
}
