/**
 * Phone and Country Test Script
 * This script helps verify that the phone input and country select functionalities 
 * are working correctly.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Test for intlTelInput
  const phoneInput = document.querySelector('#id_phone_number');
  if (phoneInput) {
    console.log('Phone input found:', phoneInput);
    console.log('Is intlTelInput initialized:', typeof window.intlTelInput !== 'undefined');
    
    // Check if intlTelInput is properly initialized on the input
    if (phoneInput.closest('.iti')) {
      console.log('intlTelInput container found');
    } else {
      console.error('intlTelInput container not found. The phone input might not be properly initialized.');
    }
    
    // Monitor for changes in the phone input
    phoneInput.addEventListener('input', function() {
      console.log('Phone input value:', this.value);
      
      // Log the selected country if intlTelInput is initialized
      if (window.iti) {
        console.log('Selected country:', iti.getSelectedCountryData());
        console.log('Selected country code:', iti.getSelectedCountryData().dialCode);
      }
    });
  } else {
    console.error('Phone input not found in the document');
  }
  
  // Test for Select2 country dropdown
  const countrySelect = document.querySelector('#id_country');
  if (countrySelect) {
    console.log('Country select found:', countrySelect);
    console.log('Is Select2 initialized:', typeof $.fn.select2 !== 'undefined');
    
    // Check if countries.js is loaded
    console.log('Countries data available:', typeof countries !== 'undefined' ? countries.length + ' countries' : 'Not loaded');
    
    // Monitor for changes in the country select
    $(countrySelect).on('change', function() {
      console.log('Selected country:', this.value);
    });
  } else {
    console.error('Country select not found in the document');
  }
  
  // Monitor form submission
  const form = document.querySelector('form');
  if (form) {
    form.addEventListener('submit', function(e) {
      // For testing only - prevent actual submission
      // e.preventDefault();
      
      console.log('Form submission detected');
      
      // Log phone country code hidden field
      const phoneCountryCode = document.querySelector('#phone_country_code');
      if (phoneCountryCode) {
        console.log('Phone country code value:', phoneCountryCode.value);
      }
      
      // Log all form data
      const formData = new FormData(form);
      for (let [key, value] of formData.entries()) {
        console.log(key + ':', value);
      }
    });
  }
}); 