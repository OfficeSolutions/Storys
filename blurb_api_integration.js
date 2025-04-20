// Add Blurb API integration JavaScript for the improved bedtime story generator

// This JavaScript file contains the client-side functionality for the Blurb API integration
// It should be included in the story view page to enable book ordering functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize book format price variables
    const prices = {
        hardcover: 29.99,
        softcover: 19.99,
        shipping: 4.99
    };

    // Update pricing when book format changes
    const formatRadios = document.querySelectorAll('input[name="bookFormat"]');
    formatRadios.forEach(radio => {
        radio.addEventListener('change', updatePricing);
    });

    // Function to update pricing display
    function updatePricing() {
        const selectedFormat = document.querySelector('input[name="bookFormat"]:checked').value;
        const bookPrice = prices[selectedFormat];
        const shippingPrice = prices.shipping;
        const totalPrice = bookPrice + shippingPrice;
        
        document.getElementById('bookPrice').textContent = `$${bookPrice.toFixed(2)}`;
        document.getElementById('shippingPrice').textContent = `$${shippingPrice.toFixed(2)}`;
        document.getElementById('totalPrice').textContent = `$${totalPrice.toFixed(2)}`;
    }

    // Handle checkout button click
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            // Validate form
            const recipientName = document.getElementById('recipientName').value;
            if (!recipientName) {
                alert('Please enter recipient name');
                return;
            }
            
            // Show processing modal
            const processingModal = new bootstrap.Modal(document.getElementById('processingModal'));
            const orderModal = bootstrap.Modal.getInstance(document.getElementById('orderModal'));
            orderModal.hide();
            processingModal.show();
            
            // Simulate API call to Blurb
            simulateBlurbApiCall().then(response => {
                // Hide processing modal
                processingModal.hide();
                
                // Show success modal with order reference
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                document.getElementById('orderReference').textContent = response.orderReference;
                successModal.show();
            }).catch(error => {
                processingModal.hide();
                alert('There was an error processing your order. Please try again.');
                console.error('Blurb API error:', error);
            });
        });
    }

    // Simulate Blurb API call (to be replaced with actual API integration)
    function simulateBlurbApiCall() {
        return new Promise((resolve, reject) => {
            // Get form data
            const formData = {
                recipientName: document.getElementById('recipientName').value,
                dedicationText: document.getElementById('dedicationText').value,
                bookFormat: document.querySelector('input[name="bookFormat"]:checked').value,
                storyId: window.location.pathname.split('/').pop(),
                childName: document.querySelector('h2').textContent.split("'s")[0],
                theme: document.querySelector('.badge').textContent
            };
            
            // In a real implementation, this would be an actual API call to Blurb
            // For demonstration purposes, we're simulating a successful response
            setTimeout(() => {
                // Simulate successful API response
                const response = {
                    success: true,
                    orderReference: 'BLB-' + Math.floor(10000 + Math.random() * 90000),
                    estimatedDelivery: '7-10 business days',
                    trackingUrl: 'https://www.blurb.com/tracking'
                };
                
                console.log('Order data:', formData);
                console.log('Blurb API response:', response);
                
                resolve(response);
                
                // Uncomment to test error handling
                // reject(new Error('API connection failed'));
            }, 2000); // Simulate 2 second API call
        });
    }

    // Function to prepare book data for Blurb API
    function prepareBookData(storyHtml, childName, theme) {
        // In a real implementation, this would format the story and illustrations
        // according to Blurb's specifications
        const bookData = {
            title: `${childName}'s ${theme} Adventure`,
            author: 'Storybook Magic',
            size: '8x8',
            format: document.querySelector('input[name="bookFormat"]:checked').value,
            pages: []
        };
        
        // Extract story text and illustration descriptions
        const storyContent = document.querySelector('.story').innerHTML;
        const paragraphs = storyContent.split('<div class="illustration">');
        
        // Add dedication page
        bookData.pages.push({
            type: 'dedication',
            content: document.getElementById('dedicationText').value || `For ${childName}, with love`
        });
        
        // Add title page
        bookData.pages.push({
            type: 'title',
            title: bookData.title,
            author: bookData.author
        });
        
        // Process story content and illustrations
        let currentPage = {
            type: 'content',
            text: '',
            illustration: null
        };
        
        paragraphs.forEach(paragraph => {
            if (paragraph.includes('[ILLUSTRATION:')) {
                // This is an illustration description
                const illustrationDesc = paragraph.split('[ILLUSTRATION:')[1].split(']')[0].trim();
                
                // If we have text in the current page, save it and start a new page
                if (currentPage.text) {
                    bookData.pages.push(currentPage);
                    currentPage = {
                        type: 'content',
                        text: '',
                        illustration: null
                    };
                }
                
                // Add illustration page
                bookData.pages.push({
                    type: 'illustration',
                    description: illustrationDesc
                });
            } else {
                // This is regular text content
                currentPage.text += paragraph;
                
                // If text is getting long, create a new page
                if (currentPage.text.length > 500) {
                    bookData.pages.push(currentPage);
                    currentPage = {
                        type: 'content',
                        text: '',
                        illustration: null
                    };
                }
            }
        });
        
        // Add any remaining content
        if (currentPage.text) {
            bookData.pages.push(currentPage);
        }
        
        return bookData;
    }
});
