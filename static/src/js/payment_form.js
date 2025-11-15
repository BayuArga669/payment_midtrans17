/** @odoo-module **/

import { loadJS } from "@web/core/assets";

/**
 * Midtrans Payment Form Handler
 * 
 * This script handles the Midtrans Snap payment popup integration.
 * It loads the Midtrans Snap.js library and handles the payment flow.
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMidtransPayment);
    } else {
        initMidtransPayment();
    }

    function initMidtransPayment() {
        const payButton = document.getElementById('midtrans_pay_button');
        
        if (!payButton) {
            // No Midtrans payment button found on this page
            return;
        }

        // Get data from button attributes
        const snapToken = payButton.dataset.snapToken;
        const clientKey = payButton.dataset.clientKey;
        const snapUrl = payButton.dataset.snapUrl;
        
        if (!snapToken || !clientKey || !snapUrl) {
            console.error('Midtrans: Missing required data attributes');
            showError('Payment configuration error. Please contact support.');
            return;
        }

        // Update button text
        updateButtonText('Initializing Payment...');

        // Load Midtrans Snap script
        const snapScriptUrl = snapUrl + '/snap/snap.js';
        const snapScriptDataUrl = `data-client-key=${clientKey}`;
        
        console.log('Loading Midtrans Snap from:', snapScriptUrl);
        
        loadJS(snapScriptUrl)
            .then(() => {
                console.log('Midtrans Snap loaded successfully');
                
                // Check if snap object is available
                if (typeof window.snap === 'undefined') {
                    throw new Error('Snap object not available after loading script');
                }
                
                // Set client key
                window.snap.setClientKey(clientKey);
                
                // Enable button and update text
                payButton.disabled = false;
                updateButtonText('Pay Now');
                
                // Add click handler
                payButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    handlePayment(snapToken);
                });
            })
            .catch((error) => {
                console.error('Failed to load Midtrans Snap:', error);
                showError('Failed to initialize payment. Please refresh the page and try again.');
                updateButtonText('Payment Unavailable');
            });
    }

    /**
     * Handle payment by showing Midtrans Snap popup
     */
    function handlePayment(snapToken) {
        const payButton = document.getElementById('midtrans_pay_button');
        
        // Disable button during payment
        payButton.disabled = true;
        updateButtonText('Opening Payment...');

        // Show Snap payment popup
        window.snap.pay(snapToken, {
            onSuccess: function(result) {
                console.log('Payment success:', result);
                updateButtonText('Payment Successful!');
                
                // Show success message
                showSuccess('Payment successful! Redirecting...');
                
                // Redirect to payment status page
                setTimeout(() => {
                    window.location.href = '/payment/status';
                }, 1500);
            },
            
            onPending: function(result) {
                console.log('Payment pending:', result);
                updateButtonText('Payment Pending');
                
                // Show pending message
                showInfo('Your payment is being processed. You will receive confirmation shortly.');
                
                // Redirect to payment status page
                setTimeout(() => {
                    window.location.href = '/payment/status';
                }, 2000);
            },
            
            onError: function(result) {
                console.error('Payment error:', result);
                updateButtonText('Pay Now');
                payButton.disabled = false;
                
                // Show error message
                showError('Payment failed. Please try again or choose another payment method.');
            },
            
            onClose: function() {
                console.log('Payment popup closed by user');
                updateButtonText('Pay Now');
                payButton.disabled = false;
                
                // Show info message
                showInfo('Payment cancelled. Click "Pay Now" to try again.');
            }
        });
    }

    /**
     * Update button text
     */
    function updateButtonText(text) {
        const buttonText = document.querySelector('#midtrans_pay_button .button_text');
        if (buttonText) {
            buttonText.textContent = text;
        }
    }

    /**
     * Show success notification
     */
    function showSuccess(message) {
        showNotification(message, 'success');
    }

    /**
     * Show error notification
     */
    function showError(message) {
        showNotification(message, 'danger');
    }

    /**
     * Show info notification
     */
    function showInfo(message) {
        showNotification(message, 'info');
    }

    /**
     * Show notification (fallback to alert if no notification system)
     */
    function showNotification(message, type) {
        // Try to use Odoo's notification system
        if (window.odoo && window.odoo.notification) {
            window.odoo.notification.add(message, {
                type: type,
                sticky: false,
            });
        } 
        // Fallback to creating custom alert
        else {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.setAttribute('role', 'alert');
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            `;
            
            // Insert at top of payment form
            const form = document.querySelector('.midtrans_payment_form');
            if (form) {
                form.insertBefore(alertDiv, form.firstChild);
                
                // Auto dismiss after 5 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            } else {
                // Fallback to alert
                alert(message);
            }
        }
    }

})();