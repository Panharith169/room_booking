let bookingToCancel = null;

function editBooking(bookingId) {
    // Redirect to edit booking page
    window.location.href = `/accounts/edit-booking/${bookingId}/`;
}

function cancelBooking(bookingId) {
    bookingToCancel = bookingId;
    document.getElementById('cancelModal').style.display = 'block';
}

function closeCancelModal() {
    document.getElementById('cancelModal').style.display = 'none';
    bookingToCancel = null;
}

function confirmCancel() {
    if (bookingToCancel) {
        // Send AJAX request to cancel booking
        fetch(`/accounts/cancel-booking/${bookingToCancel}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Booking cancelled successfully!');
                // Refresh the page to show updated status
                location.reload();
            } else {
                alert('Error cancelling booking: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error cancelling booking');
        });
    }
    closeCancelModal();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('cancelModal');
    if (event.target === modal) {
        closeCancelModal();
    }
}

// Print booking details
function printBooking() {
    window.print();
}

// Add smooth animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate info sections
    const sections = document.querySelectorAll('.info-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.transition = 'all 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add button click animations
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
});