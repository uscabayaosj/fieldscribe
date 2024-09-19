// Main application JavaScript file

document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    initializeNavigation();
    initializeFormValidation();
});

function initializeNavigation() {
    const navToggle = document.querySelector('#nav-toggle');
    const navMenu = document.querySelector('#nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('hidden');
        });
    }
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white ${type === 'error' ? 'bg-red-500' : 'bg-green-500'}`;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function showWarningDialog(message, onConfirm) {
    const dialog = document.createElement('div');
    dialog.role = 'dialog';
    dialog.ariaModal = 'true';
    dialog.className = 'fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black bg-opacity-50';
    dialog.innerHTML = `
        <div class="relative bg-background rounded-lg shadow-lg p-6 w-full max-w-md m-4">
            <h3 class="text-lg font-semibold mb-4">${message}</h3>
            <div class="flex justify-end space-x-4">
                <button class="cancel-btn inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-3">Cancel</button>
                <button class="confirm-btn inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-9 px-3">Confirm</button>
            </div>
        </div>
    `;

    document.body.appendChild(dialog);

    dialog.querySelector('.cancel-btn').addEventListener('click', () => {
        document.body.removeChild(dialog);
    });

    dialog.querySelector('.confirm-btn').addEventListener('click', () => {
        onConfirm();
        document.body.removeChild(dialog);
    });
}

// Example usage:
// showWarningDialog('Are you sure you want to delete this entry?', () => {
//     // Deletion logic here
// });
