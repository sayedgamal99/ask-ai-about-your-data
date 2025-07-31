// Constants - will be loaded from backend
let FASTAPI_URL = 'http://localhost:5599';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const csvFileInput = document.getElementById('csvFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const questionInput = document.getElementById('questionInput');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// Global variables
let uploadedFile = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkBackendStatus();
    
    // Check backend status periodically
    setInterval(checkBackendStatus, 30000); // Check every 30 seconds
});

function initializeEventListeners() {
    // File upload events
    uploadArea.addEventListener('click', () => csvFileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    csvFileInput.addEventListener('change', handleFileSelect);
    removeFileBtn.addEventListener('click', removeFile);
    
    // Question input events
    questionInput.addEventListener('input', validateForm);
    
    // Example questions
    const exampleTags = document.querySelectorAll('.example-tag');
    exampleTags.forEach(tag => {
        tag.addEventListener('click', function() {
            questionInput.value = this.dataset.question;
            validateForm();
        });
    });
    
    // Submit button
    submitBtn.addEventListener('click', handleSubmit);
}

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showError('Please select a CSV file');
        return;
    }
    
    uploadedFile = file;
    fileName.textContent = `${file.name} (${formatFileSize(file.size)})`;
    fileInfo.style.display = 'block';
    uploadArea.style.display = 'none';
    
    validateForm();
    
    // Add success animation
    fileInfo.style.opacity = '0';
    fileInfo.style.transform = 'translateY(20px)';
    setTimeout(() => {
        fileInfo.style.transition = 'all 0.3s ease';
        fileInfo.style.opacity = '1';
        fileInfo.style.transform = 'translateY(0)';
    }, 100);
}

function removeFile() {
    uploadedFile = null;
    csvFileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    resultsSection.style.display = 'none';
    validateForm();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form validation
function validateForm() {
    const hasFile = uploadedFile !== null;
    const hasQuestion = questionInput.value.trim().length > 0;
    
    submitBtn.disabled = !(hasFile && hasQuestion);
}

// Backend communication
async function checkBackendStatus() {
    try {
        const response = await fetch(`${FASTAPI_URL}/`, { 
            method: 'GET',
            timeout: 3000 
        });
        
        if (response.ok) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Backend Online';
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'Backend Offline';
    }
}

async function handleSubmit() {
    if (!uploadedFile || !questionInput.value.trim()) {
        showError('Please upload a file and enter a question');
        return;
    }
    
    showLoading(true);
    
    try {
        // Step 1: Upload the file first
        const uploadFormData = new FormData();
        uploadFormData.append('file', uploadedFile);
        
        const uploadResponse = await fetch(`${FASTAPI_URL}/upload`, {
            method: 'POST',
            body: uploadFormData
        });
        
        if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.status} - ${uploadResponse.statusText}`);
        }
        
        const uploadResult = await uploadResponse.json();
        const fileId = uploadResult.file_id;
        
        // Step 2: Ask the question with the file_id
        const questionResponse = await fetch(`${FASTAPI_URL}/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_id: fileId,
                question: questionInput.value.trim()
            })
        });
        
        if (!questionResponse.ok) {
            throw new Error(`Question failed: ${questionResponse.status} - ${questionResponse.statusText}`);
        }
        
        const result = await questionResponse.json();
        displayResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showError('Cannot connect to backend. Make sure the FastAPI server is running on localhost:5599');
        } else {
            showError(`Error: ${error.message}`);
        }
    } finally {
        showLoading(false);
    }
}

// UI functions
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
    submitBtn.disabled = show;
}

function showError(message) {
    // Create a temporary error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <div style="
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #dc3545;
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 400px;
            z-index: 1001;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        ">
            <strong>Error:</strong> ${message}
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

function displayResults(result) {
    // Populate answer
    document.getElementById('answerText').textContent = result.answer || 'No answer provided';
    
    // Show results section with animation
    resultsSection.style.display = 'block';
    resultsSection.style.opacity = '0';
    resultsSection.style.transform = 'translateY(30px)';
    
    setTimeout(() => {
        resultsSection.style.transition = 'all 0.5s ease';
        resultsSection.style.opacity = '1';
        resultsSection.style.transform = 'translateY(0)';
    }, 100);
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Enhanced error handling for fetch with timeout
async function fetchWithTimeout(resource, options = {}) {
    const { timeout = 30000 } = options;
    
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    const response = await fetch(resource, {
        ...options,
        signal: controller.signal
    });
    
    clearTimeout(id);
    return response;
}
