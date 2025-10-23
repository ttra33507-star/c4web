document.addEventListener('DOMContentLoaded', function() {
    // Get all elements with the 'group' class
    const groupElements = document.querySelectorAll('.group');
    
    groupElements.forEach(element => {
        let touchTimeout;
        
        // Add touch start event
        element.addEventListener('touchstart', function(e) {
            // Prevent default to avoid unwanted behaviors
            e.preventDefault();
            
            // Add a class that will mimic the hover state
            element.classList.add('touch-active');
            
            // Set a timeout to remove the class after 3 seconds
            touchTimeout = setTimeout(() => {
                element.classList.remove('touch-active');
            }, 3000);
        });
        
        // Add touch end event
        element.addEventListener('touchend', function() {
            // Clear the timeout if it exists
            if (touchTimeout) {
                clearTimeout(touchTimeout);
            }
            
            // Remove the class after a short delay
            setTimeout(() => {
                element.classList.remove('touch-active');
            }, 1000);
        });
    });
});