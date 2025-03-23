document.addEventListener('DOMContentLoaded', function() {
    // Core application state variables
    let map, trackPolyline, userMarker;
    let trackPoints = [];
    let lastPosition = null;
    let distance = 0;
    let startTime = null;
    let totalElapsedTime = 0; 
    let pauseStartTime = null;
    let timerInterval = null;
    let watchId = null;
    let isTracking = false;
    let isPaused = false;
    let sessionId = null;


/******************* PART 1 : NEED TO CONNECT WITH THE BACKEND ************************/    
    // API 
    const API_BASE_URL = '/walkinggame';
    const API_ENDPOINTS = {
        SAVE_TRIP: '/save/',
        GET_TRIPS: '/history/',
    };

    // CSRF
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    


    /**
     * send walking data to backend
     * @param {Object} tripData 
     */
    async function sendTripDataToBackend(tripData) {
        try {
            showAlert('Saving trip data to server...');
            
            const formData = new FormData();
            formData.append('session_id', tripData.sessionId);
            formData.append('start_time', tripData.startTime.toISOString());
            formData.append('end_time', tripData.endTime.toISOString());
            formData.append('distance', tripData.distance.toFixed(2));
            formData.append('duration', tripData.duration);
            formData.append('is_completed', tripData.isCompleted);
            formData.append('points_earned', tripData.pointsEarned);
            
            formData.append('track_points_count', trackPoints.length);
            
            trackPoints.forEach((point, index) => {
                formData.append(`point_lat_${index}`, point.lat);
                formData.append(`point_lng_${index}`, point.lng);
                formData.append(`point_time_${index}`, point.timestamp);
            });
            
            const response = await fetch(API_BASE_URL + API_ENDPOINTS.SAVE_TRIP, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData,
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const responseText = await response.text();
                showAlert('Trip data saved to server successfully');
                
    
                try {
                    return responseText ? JSON.parse(responseText) : null;
                } catch (e) {
                    console.log('Server response is not JSON:', responseText);
                    return null;
                }
            } else {
                console.error('Server error:', response.status);
                showAlert('Failed to send data to server');
                return null;
            }
        } catch (error) {
            console.error('Error sending data:', error);
            showAlert('Connection error, please try again');
            return null;
        }
    }



   //get history from backend
   async function getTripsFromBackend() {
        try {
            const response = await fetch(API_BASE_URL + API_ENDPOINTS.GET_TRIPS, {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const htmlContent = await response.text();
                
                const historyList = document.getElementById('historyList');
                historyList.innerHTML = htmlContent;
                return null; 
                
        
            } else {
                console.error('Failed to load history:', response.status);
                return null;
            }
        } catch (error) {
            console.error('Error loading history:', error);
            return null;
        }
    }







    /******************************** PART 2: MAP and TRACKING ******************************/
    // Initialize map
    function initMap() {
        const defaultPosition = [51.6231, 3.9447];

        map = L.map('map');

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        trackPolyline = L.polyline([], {
            color: '#4CAF50',
            weight: 5,
            opacity: 0.7
        }).addTo(map);
        
        // Try to get user's location
        if (navigator.geolocation) {
            showAlert('Getting your location...');
            
            navigator.geolocation.getCurrentPosition(
                // Success
                position => {
                    const userLocation = [position.coords.latitude, position.coords.longitude];
                    map.setView(userLocation, 16);
                    
                    userMarker = L.marker(userLocation).addTo(map);
                    showAlert('Located your position');
                },
                // Error
                error => {
                    console.error('Failed to get location', error);
                    map.setView(defaultPosition, 12);
                    showAlert('Unable to get your location');
                }
            );
        } else {
            map.setView(defaultPosition, 12);
            showAlert('Your browser does not support geolocation');
        }
    }
    
    
    // Start tracking
    function startTracking() {
        if (!navigator.geolocation) {
            showAlert('Your browser does not support geolocation');
            return;
        }
        
        // If not resuming from pause, reset all data
        if (!isPaused) {
            distance = 0;
            trackPoints = [];
            trackPolyline.setLatLngs([]);
            updateDistanceDisplay();
            totalElapsedTime = 0; // Reset accumulated time
            sessionId = 'session_' + Date.now();
        }
        
        startTime = new Date();
        isTracking = true;
        isPaused = false;
        
        document.getElementById('startBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;
        
        updateTimer();

        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(updateTimer, 1000);
        
        watchId = navigator.geolocation.watchPosition(
            updatePosition,
            error => {
                showAlert('Location tracking error: ' + error.message);
                console.error('Tracking error:', error);
            },
            { enableHighAccuracy: true }
        );
    }
    
    function pauseTracking() {
        if (!isTracking) return;
        
        // Record pause start time
        pauseStartTime = new Date();
        
        // Add current session time to totalElapsedTime
        if (startTime) {
            const sessionDuration = pauseStartTime - startTime;
            totalElapsedTime += sessionDuration;
            console.log(`Paused after ${sessionDuration}ms, total elapsed: ${totalElapsedTime}ms`);
        }
        
        isTracking = false;
        isPaused = true;
        
        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }
        
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
    }
    
    async function stopTracking() {
        let endTime = new Date();
        
        // If tracking, stop first
        if (isTracking) {
            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }
            
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            
            if (startTime) {
                let finalSessionDuration = endTime - startTime;
                
                if (finalSessionDuration <= 0) {
                    console.log("Detected extremely short session, adjusting to 1ms");
                    finalSessionDuration = 1;
                }
                
                totalElapsedTime += finalSessionDuration;
                console.log(`Session stopped: lasted ${finalSessionDuration}ms, total ${totalElapsedTime}ms`);
            }
        }
        
        isTracking = false;
        isPaused = false;
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopBtn').disabled = true;
        
        // Ensure total duration is at least 1ms
        let finalDuration = totalElapsedTime;
        if (finalDuration <= 0) {
            console.log("Total duration too short, adjusting to 1ms");
            finalDuration = 1;
        }
        
        // Ensure valid start time
        let effectiveStartTime = startTime;
        if (!effectiveStartTime) {
            effectiveStartTime = new Date(endTime.getTime() - finalDuration);
        }
        
        // Collect trip data
        const tripData = {
            sessionId: sessionId || 'session_' + Date.now(), // Ensure session ID exists
            startTime: effectiveStartTime,
            endTime: endTime,
            distance: distance,
            duration: finalDuration,
            isCompleted: distance >= 3,
            pointsEarned: distance >= 3 ? 30 : 0
        };
    
        try {
            await sendTripDataToBackend(tripData);
            updateHistoryUI(); 
        } catch (err) {
            console.error('Backend sync failed:', err);
            showAlert('Failed to save your activity');
        }
        
        if (distance >= 3) {
            showCompletionSuccess();
        } else {
            showCompletionFailure();
        }
    }
    
    function updateTimer() {

        if (!isTracking) {
            // Convert to minutes and seconds
            const totalSeconds = Math.floor(totalElapsedTime / 1000);
            const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
            const seconds = (totalSeconds % 60).toString().padStart(2, '0');
            
            document.getElementById('timeValue').textContent = `${minutes}:${seconds}`;
            return;
        }
        
        // Calculate current session time
        let currentSessionTime = 0;
        if (startTime) {
            const now = new Date();
            currentSessionTime = now - startTime;
            
            // Ensure session time is not negative
            if (currentSessionTime < 0) {
                console.log("Negative session time detected, setting to 0");
                currentSessionTime = 0;
            }
        }
        
        const displayTime = totalElapsedTime + currentSessionTime;
        const totalSeconds = Math.floor(displayTime / 1000);
        const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
        const seconds = (totalSeconds % 60).toString().padStart(2, '0');
        
        document.getElementById('timeValue').textContent = `${minutes}:${seconds}`;
    }
    
    // Calculate distance between two points (Haversine formula)
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000; // Earth radius in meters
        const dLat = toRad(lat2 - lat1);
        const dLon = toRad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c; // Distance in meters
    }
    
    function toRad(degrees) {
        return degrees * Math.PI / 180;
    }
    
    function updateDistanceDisplay() {
        document.getElementById('distanceText').textContent = distance.toFixed(1);
    }

    function updateSpeedDisplay(speed) {
        let displaySpeed = 0;
        
        if (speed) {
            displaySpeed = speed * 3.6; // Convert to km/h
        }
        
        document.getElementById('speedValue').textContent = displaySpeed.toFixed(1);
    }
    
    
    // Show alert message
    function showAlert(message, duration = 3000) {
        const alert = document.getElementById('alert');
        
        // Automatically determine message type based on content
        let type = 'info'; 
        
        // Success type determination
        if (message.includes('Congratulation') || 
            message.includes('Located') ||
            message.includes('complete') || 
            message.includes('position') ||
            message.includes('granted')) {
            type = 'success';
        } 
        // Error type determination
        else if (message.includes('error') || 
                message.includes('failed') || 
                message.includes('Unable') ||
                message.includes('denied') ||
                message.includes('does not support')) {
            type = 'error';
        } 
        // Warning type determination
        else if (message.includes('Please') || 
                message.includes('please') ||
                message.includes('did not reach') ||
                message.includes('calibrated') ||
                message.includes('timed out')) {
            type = 'warning';
        }
        
        // Set type attribute
        alert.setAttribute('data-type', type);
        
        // Set progress bar animation duration
        document.documentElement.style.setProperty('--alert-duration', `${duration}ms`);
        
        // Set message content
        alert.textContent = message;

        alert.classList.add('show');
        
        // Auto-hide the alert
        setTimeout(() => {
            alert.classList.remove('show');
        }, duration);
    }
    
    // Show completion success (color: green)
    function showCompletionSuccess() {
    
        map.closePopup();
    
        document.querySelectorAll('.leaflet-popup').forEach(popup => {
            popup.remove();
        });
        
        const successPopupContent = `
            <div style="text-align: center;">
                <h3 style="margin: 5px 0 10px 0;">Congratulations!</h3>
                <div style="color:rgb(255, 255, 255); font-size: 28px; margin: 10px 0;">
                    <i class="fas fa-check-circle"></i>
                </div>
                <p style="margin: 10px 0;">You have successfully reduced 0.5kg of carbon emissions and earned 30 points!</p>
            </div>
        `;
        
        const popup = L.popup();
        
        popup.on('add', function(event) {
            setTimeout(() => {
                const popupElement = document.querySelector('.leaflet-popup');
                if (popupElement) {
                    const wrapper = popupElement.querySelector('.leaflet-popup-content-wrapper');
                    const tip = popupElement.querySelector('.leaflet-popup-tip');
                    
                    if (wrapper) wrapper.style.backgroundColor = '#4CAF50';  // 绿色
                    if (tip) tip.style.backgroundColor = '#4CAF50';  // 绿色
                    
                    popupElement.setAttribute('data-popup-type', 'success');
                }
            }, 10);
        });
        
        popup
            .setLatLng(userMarker.getLatLng())
            .setContent(successPopupContent)
            .openOn(map);
    }

    // Show completion failure (color: orange)
    function showCompletionFailure() {

        map.closePopup();
        
        document.querySelectorAll('.leaflet-popup').forEach(popup => {
            popup.remove();
        });
        
        const failurePopupContent = `
            <div style="text-align: center;">
                <h3 style="margin: 5px 0 10px 0;">Almost There!</h3>
                <div style="color:rgb(255, 255, 255); font-size: 28px; margin: 10px 0;">
                    <i class="fas fa-exclamation-circle"></i>
                </div>
                <p style="margin: 10px 0;">Activity recorded, but distance did not reach 3km. No points earned this time.</p>
                <p style="margin: 5px 0; font-size: 0.9rem; color: #fff;">Current distance: ${distance.toFixed(1)}km / Target: 3km</p>
            </div>
        `;
        
        const popup = L.popup();
        
        popup.on('add', function(event) {
            setTimeout(() => {
                const popupElement = document.querySelector('.leaflet-popup');
                if (popupElement) {
                    const wrapper = popupElement.querySelector('.leaflet-popup-content-wrapper');
                    const tip = popupElement.querySelector('.leaflet-popup-tip');
                
                    if (wrapper) wrapper.style.backgroundColor = '#FFB347';  
                    if (tip) tip.style.backgroundColor = '#FFB347'; 
                    
                    popupElement.setAttribute('data-popup-type', 'failure');
                }
            }, 50);  
        });
        
        popup
            .setLatLng(userMarker.getLatLng())
            .setContent(failurePopupContent)
            .openOn(map);
    }


/************************** PART 3: HISTORY UI (use the functions in part1) *******************************/

    // Save to history
    async function saveToHistory(tripData) {
  
        try {
            await sendTripDataToBackend(tripData);
            updateHistoryUI();
        } catch (error) {
            console.error('Error saving to backend:', error);
            showAlert('Failed to save your activity');
        }
    }
    
    // update history UI
    async function updateHistoryUI() {
        try {
            const backendHistory = await getTripsFromBackend();
            
            if (backendHistory === null) {
                return;
            }
        
        } catch (error) {
            console.error('Error updating history UI:', error);
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '<div class="no-records">Unable to load history. Please try again later.</div>';
            showAlert('Failed to load history');
        }
    }
    




    // Initialize app
    function initApp() {
        // Initialize map
        initMap();
        
        // Initialize button states
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopBtn').disabled = true;
        
        // Load history
        updateHistoryUI();
        
        // Bind button events
        document.getElementById('startBtn').addEventListener('click', startTracking);
        document.getElementById('pauseBtn').addEventListener('click', pauseTracking);
        document.getElementById('stopBtn').addEventListener('click', stopTracking);
        
        // Bind tab switching events
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                // Toggle tab active state
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Toggle panel display
                const tabName = this.dataset.tab;
                document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
                document.getElementById(`${tabName}Panel`).classList.add('active');
                
                // If switching to map tab, refresh map
                if (tabName === 'tracking' && map) {
                    setTimeout(() => map.invalidateSize(), 100);
                }
                
                if (tabName === 'history') {
                    updateHistoryUI();
                }
            });
        });
    }
    
    initApp();
});