// Add Blurb API integration to the improved bedtime story generator
// This updates the existing modal with actual Blurb API integration

// Update the order modal in the STORY_TEMPLATE section of improved_bedtime_story_generator.py

const UPDATED_ORDER_MODAL = `
<!-- Order Modal -->
<div class="modal fade" id="orderModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Order Your Printed Book</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <div class="book-preview mb-4">
                            <div class="book">
                                <div class="book-spine"></div>
                                <div class="book-cover">
                                    <div class="book-title">{{ child_name }}'s Story</div>
                                    <div class="book-author">A personalized adventure</div>
                                    <div class="mt-4">
                                        <i class="bi bi-stars fs-1"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <h5 class="mt-4">Book Details:</h5>
                        <ul class="list-group list-group-flush mb-4">
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-book-half text-primary me-2"></i>
                                8.5" x 8.5" Hardcover Book
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-image text-primary me-2"></i>
                                Full-color illustrations
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-card-text text-primary me-2"></i>
                                Premium paper quality
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-pencil text-primary me-2"></i>
                                Personalized dedication page
                            </li>
                            <li class="list-group-item d-flex align-items-center">
                                <i class="bi bi-truck text-primary me-2"></i>
                                Worldwide shipping available
                            </li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <div class="card border-primary">
                            <div class="card-header bg-primary text-white">
                                <h5 class="card-title mb-0">Complete Your Order</h5>
                            </div>
                            <div class="card-body">
                                <form id="orderForm">
                                    <div class="mb-3">
                                        <label for="recipientName" class="form-label">Recipient's Name</label>
                                        <input type="text" class="form-control" id="recipientName" value="{{ child_name }}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="dedicationText" class="form-label">Dedication Message</label>
                                        <textarea class="form-control" id="dedicationText" rows="2" placeholder="For [name], with love..."></textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Book Format</label>
                                        <div class="form-check">
                                            <input class="form-check-input" type="radio" name="bookFormat" id="hardcover" value="hardcover" checked>
                                            <label class="form-check-label" for="hardcover">
                                                Hardcover ($29.99)
                                            </label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input" type="radio" name="bookFormat" id="softcover" value="softcover">
                                            <label class="form-check-label" for="softcover">
                                                Softcover ($19.99)
                                            </label>
                                        </div>
                                    </div>
                                    <div class="d-flex justify-content-between mb-2 mt-4">
                                        <span>Book Price:</span>
                                        <span id="bookPrice">$29.99</span>
                                    </div>
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>Shipping:</span>
                                        <span id="shippingPrice">$4.99</span>
                                    </div>
                                    <hr>
                                    <div class="d-flex justify-content-between fw-bold">
                                        <span>Total:</span>
                                        <span id="totalPrice">$34.98</span>
                                    </div>
                                    <div class="d-grid gap-2 mt-4">
                                        <button type="button" id="checkoutBtn" class="btn btn-primary">
                                            <i class="bi bi-credit-card me-2"></i> Proceed to Checkout
                                        </button>
                                    </div>
                                    <div class="text-center mt-3">
                                        <small class="text-muted">Powered by Blurb Print-on-Demand</small>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Processing Modal -->
<div class="modal fade" id="processingModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-body text-center p-5">
                <div class="spinner-border text-primary mb-4" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h4>Processing Your Order</h4>
                <p class="mb-0">Please wait while we prepare your book for printing...</p>
            </div>
        </div>
    </div>
</div>

<!-- Success Modal -->
<div class="modal fade" id="successModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-success text-white">
                <h5 class="modal-title">Order Successful!</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-center p-4">
                <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                <h4 class="mt-3">Thank You For Your Order</h4>
                <p>Your personalized book is being prepared for printing. You'll receive an email with tracking information once it ships.</p>
                <p class="fw-bold mb-0">Order Reference: <span id="orderReference">BLB-12345</span></p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>
`;
