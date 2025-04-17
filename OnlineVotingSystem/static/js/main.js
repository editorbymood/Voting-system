/**
 * VoteSecure - Enhanced JavaScript Functionality
 * Provides interactive UI elements and animations for the voting system
 */

"use strict";

// Main initialization function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all Bootstrap components
    initBootstrapComponents();
    
    // Initialize custom UI behaviors
    initCustomBehaviors();
    
    // Add special animation effects
    initAnimations();
    
    // Set up form validation
    initFormValidation();
    
    // Initialize charts with animations if present
    initCharts();
    
    // Add scroll effects
    initScrollEffects();
});

// Initialize Bootstrap components
function initBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            boundary: document.body,
            animation: true
        });
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            html: true,
            trigger: 'hover focus',
            animation: true
        });
    });
    
    // Auto-dismiss flash messages after 6 seconds with fade
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.alert:not(.alert-important)');
        flashMessages.forEach(function(message) {
            fadeOut(message, 500, function() {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            });
        });
    }, 6000);
}

// Initialize custom UI behaviors
function initCustomBehaviors() {
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn, .nav-link');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover');
        });
    });
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize animations
function initAnimations() {
    // Animate stats numbers
    const statsValues = document.querySelectorAll('.stats-value');
    if (statsValues.length > 0) {
        statsValues.forEach(stat => {
            const targetValue = parseInt(stat.textContent, 10);
            let currentValue = 0;
            const duration = 1500; // ms
            const stepTime = 30; // ms
            const steps = duration / stepTime;
            const increment = targetValue / steps;
            
            stat.textContent = '0';
            
            const counter = setInterval(() => {
                currentValue += increment;
                if (currentValue >= targetValue) {
                    clearInterval(counter);
                    stat.textContent = targetValue;
                } else {
                    stat.textContent = Math.floor(currentValue);
                }
            }, stepTime);
        });
    }
    
    // Animate progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('aria-valuenow') + '%';
        setTimeout(() => {
            bar.style.width = width;
        }, 300);
    });
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Add shake animation to invalid fields
                const invalidInputs = form.querySelectorAll(':invalid');
                invalidInputs.forEach(input => {
                    input.classList.add('shake-animation');
                    setTimeout(() => {
                        input.classList.remove('shake-animation');
                    }, 650);
                });
                
                // Scroll to first invalid field
                if (invalidInputs.length > 0) {
                    invalidInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    invalidInputs[0].focus();
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Password strength meter
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const meter = document.getElementById(this.id + '-strength');
            if (!meter) return;
            
            const val = this.value;
            let strength = 0;
            
            if (val.length >= 8) strength += 1;
            if (val.match(/[A-Z]/)) strength += 1;
            if (val.match(/[0-9]/)) strength += 1;
            if (val.match(/[^A-Za-z0-9]/)) strength += 1;
            
            meter.value = strength;
            
            const strengthText = document.getElementById(this.id + '-strength-text');
            if (strengthText) {
                const texts = ['Weak', 'Fair', 'Good', 'Strong'];
                const colors = ['danger', 'warning', 'info', 'success'];
                
                strengthText.textContent = texts[strength - 1] || '';
                strengthText.className = 'text-' + (colors[strength - 1] || 'danger');
            }
        });
    });
}

// Initialize charts with animations
function initCharts() {
    // Enhance any Chart.js charts if present
    if (typeof Chart !== 'undefined') {
        // Set global defaults for all charts
        Chart.defaults.elements.line.tension = 0.4; // Smoother lines
        Chart.defaults.elements.line.borderWidth = 3;
        Chart.defaults.animations.duration = 2000;
        Chart.defaults.animations.easing = 'easeOutQuart';
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Add custom animation effects
        const originalLineDraw = Chart.controllers.line.prototype.draw;
        Chart.controllers.line.prototype.draw = function() {
            originalLineDraw.apply(this, arguments);
            
            const ctx = this.chart.ctx;
            const _stroke = ctx.stroke;
            ctx.stroke = function() {
                ctx.save();
                ctx.shadowColor = 'rgba(0, 0, 0, 0.25)';
                ctx.shadowBlur = 8;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 4;
                _stroke.apply(this, arguments);
                ctx.restore();
            };
        };
    }
}

// Scroll effects
function initScrollEffects() {
    // Highlight active nav item on scroll
    const sections = document.querySelectorAll('section[id]');
    
    if (sections.length > 0) {
        window.addEventListener('scroll', () => {
            let scrollY = window.pageYOffset;
            
            sections.forEach(section => {
                const sectionHeight = section.offsetHeight;
                const sectionTop = section.offsetTop - 100;
                const sectionId = section.getAttribute('id');
                
                if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                    document.querySelector(`.nav-link[href*='${sectionId}']`)?.classList.add('active');
                } else {
                    document.querySelector(`.nav-link[href*='${sectionId}']`)?.classList.remove('active');
                }
            });
        });
    }
    
    // Reveal elements on scroll
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    
    if (revealElements.length > 0) {
        const revealOnScroll = function() {
            const windowHeight = window.innerHeight;
            const revealPoint = 150;
            
            revealElements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                
                if (elementTop < windowHeight - revealPoint) {
                    element.classList.add('revealed');
                }
            });
        };
        
        window.addEventListener('scroll', revealOnScroll);
        revealOnScroll(); // Check on initial load
    }
}

// Utility functions
function fadeOut(element, duration, callback) {
    let opacity = 1;
    const step = 16.7 / duration; // 60fps
    
    const fadeEffect = setInterval(() => {
        if (opacity <= 0) {
            clearInterval(fadeEffect);
            element.style.display = 'none';
            if (typeof callback === 'function') callback();
        }
        element.style.opacity = opacity;
        opacity -= step;
    }, 16.7);
}

function fadeIn(element, duration, callback) {
    let opacity = 0;
    element.style.opacity = opacity;
    element.style.display = 'block';
    
    const step = 16.7 / duration; // 60fps
    
    const fadeEffect = setInterval(() => {
        if (opacity >= 1) {
            clearInterval(fadeEffect);
            if (typeof callback === 'function') callback();
        }
        element.style.opacity = opacity;
        opacity += step;
    }, 16.7);
}

// Confirmation functions for destructive actions with custom modal
function confirmDelete(formId, itemName) {
    // Check if we have a custom modal
    const modalElement = document.getElementById('confirmDeleteModal');
    
    if (modalElement) {
        // Use the custom modal
        const itemNameElement = document.getElementById('deleteItemName');
        if (itemNameElement) {
            itemNameElement.textContent = itemName;
        }
        
        const confirmBtn = document.getElementById('confirmDeleteBtn');
        confirmBtn.onclick = function() {
            document.getElementById(formId).submit();
        };
        
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else {
        // Fallback to basic confirm dialog
        if (confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`)) {
            document.getElementById(formId).submit();
        }
    }
}

// Vote confirmation function with custom animation
function confirmVote(form, candidateName) {
    const modalElement = document.getElementById('confirmVoteModal');
    const candidateNameElement = document.getElementById('candidateName');
    
    if (candidateNameElement) {
        candidateNameElement.textContent = candidateName;
    }
    
    const confirmBtn = document.getElementById('confirmVoteBtn');
    if (confirmBtn) {
        confirmBtn.onclick = function() {
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Show voting animation
            const votingOverlay = document.createElement('div');
            votingOverlay.className = 'voting-overlay';
            votingOverlay.innerHTML = `
                <div class="voting-animation">
                    <i class="fas fa-check-circle voting-icon"></i>
                    <div class="voting-text">Casting Your Vote</div>
                    <div class="voting-progress">
                        <div class="voting-progress-bar"></div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(votingOverlay);
            
            setTimeout(() => {
                form.submit();
            }, 1500);
        };
    }
    
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}
