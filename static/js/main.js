// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application loaded');
    // Add your JavaScript code here
});

// Function to create and show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} slide-in`;
    
    // Add icon based on alert type
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 'info-circle';
    
    alert.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.classList.add('slide-out');
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Handle flash messages on page load
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.classList.add('slide-out');
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Function to toggle the three-dot menu
function toggleMenu(trigger) {
    // Close all other open menus first
    document.querySelectorAll('.menu-content.show').forEach(menu => {
        if (menu !== trigger.nextElementSibling) {
            menu.classList.remove('show');
        }
    });
    
    // Toggle the clicked menu
    const menu = trigger.nextElementSibling;
    menu.classList.toggle('show');
}

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.menu-container')) {
        document.querySelectorAll('.menu-content.show').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});

// Prevent menu from closing when clicking inside it
document.querySelectorAll('.menu-content').forEach(menu => {
    menu.addEventListener('click', function(event) {
        event.stopPropagation();
    });
}); 