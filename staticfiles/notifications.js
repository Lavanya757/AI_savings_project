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
});
