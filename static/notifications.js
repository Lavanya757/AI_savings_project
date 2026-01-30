document.addEventListener('DOMContentLoaded', function() {
    const bell = document.querySelector('.notification-bell');
    if (!bell) return;
    const dropdown = bell.querySelector('.notification-dropdown');

    bell.addEventListener('click', function(event) {
        event.stopPropagation();
        if (dropdown.style.display === 'none' || dropdown.style.display === '') {
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    });

    document.addEventListener('click', function() {
        dropdown.style.display = 'none';
    });

    // Dismiss alert on close button click
    document.querySelectorAll('.notification-dropdown .btn-close').forEach(button => {
        button.addEventListener('click', function(event) {
            const alert = event.target.closest('.alert');
            if (alert) {
                alert.remove();
                // Optionally update notification count badge
                const badge = bell.querySelector('.badge');
                if (badge) {
                    let count = parseInt(badge.textContent);
                    count = Math.max(count - 1, 0);
                    if (count === 0) {
                        badge.style.display = 'none';
                    } else {
                        badge.textContent = count;
                    }
                }
            }
        });
    });
});
