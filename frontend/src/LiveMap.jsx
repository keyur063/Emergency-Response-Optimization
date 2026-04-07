import React, { useEffect, useRef, useState } from 'react';
import './LiveMap.css';

const LiveMap = () => {
    // UI State
    const [hospital, setHospital] = useState('KEM Hospital');
    const [accident, setAccident] = useState('Vadala Road Station');
    const [ambulanceNo, setAmbulanceNo] = useState('MH 02 AB 1234');
    
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [routeData, setRouteData] = useState(null);

    // Leaflet Refs (Keeps data without triggering React re-renders)
    const mapRef = useRef(null);
    const mapInstance = useRef(null);
    const routingControl = useRef(null);
    const ambulanceMarker = useRef(null);
    const simulationInterval = useRef(null);
    const routeCoordinates = useRef([]);

    // Initialize Map Only Once
    useEffect(() => {
        if (!mapInstance.current) {
            // Wait for window.L (Leaflet) to load from index.html
            if (!window.L) return;

            mapInstance.current = window.L.map(mapRef.current, {
                zoomControl: false
            }).setView([19.2215, 72.9781], 14);

            window.L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OSM &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(mapInstance.current);

            window.L.control.zoom({ position: 'bottomright' }).addTo(mapInstance.current);
        }

        // Cleanup function
        return () => {
            if (simulationInterval.current) clearInterval(simulationInterval.current);
        };
    }, []);

    // Geocoding Helper
    const geocode = async (address) => {
        try {
            const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`;
            const response = await fetch(url, { headers: { 'Accept-Language': 'en-US,en;q=0.9' } });
            const data = await response.json();
            
            if (data && data.length > 0) return { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon), displayName: data[0].display_name };
            
            if (!address.toLowerCase().includes("thane")) {
                const fbResponse = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address + ", Thane")}&limit=1`);
                const fbData = await fbResponse.json();
                if (fbData && fbData.length > 0) return { lat: parseFloat(fbData[0].lat), lng: parseFloat(fbData[0].lon), displayName: fbData[0].display_name };
            }
            return null;
        } catch (error) { return null; }
    };

    // Icons
    const createIcons = () => {
        const L = window.L;
        return {
            start: L.divIcon({ html: `<div style="font-size: 24px; background: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); border: 2px solid #10b981;">📍</div>`, iconSize: [40, 40], iconAnchor: [20, 20] }),
            end: L.divIcon({ html: `<div style="font-size: 24px; background: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); border: 2px solid #f43f5e;">🏁</div>`, iconSize: [40, 40], iconAnchor: [20, 20] }),
            amb: L.divIcon({ html: `<div style="font-size: 26px; filter: drop-shadow(0 0 10px rgba(255,255,255,0.5)); transform: scaleX(-1);">🚑</div>`, className: 'ambulance-marker', iconSize: [40, 40], iconAnchor: [20, 20] })
        };
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg('');
        setRouteData(null);
        setLoading(true);

        const L = window.L;
        if (simulationInterval.current) clearInterval(simulationInterval.current);
        if (ambulanceMarker.current) mapInstance.current.removeLayer(ambulanceMarker.current);

        const hospitalCoords = await geocode(hospital);
        const accidentCoords = await geocode(accident);

        if (!hospitalCoords || !accidentCoords) {
            setErrorMsg('Could not find locations. Please try more specific addresses.');
            setLoading(false);
            return;
        }

        if (routingControl.current) mapInstance.current.removeControl(routingControl.current);
        
        mapInstance.current.eachLayer((layer) => {
            if (!layer._url) mapInstance.current.removeLayer(layer);
        });

        const latLng1 = L.latLng(hospitalCoords.lat, hospitalCoords.lng);
        const latLng2 = L.latLng(accidentCoords.lat, accidentCoords.lng);
        const icons = createIcons();

        L.marker(latLng1, { icon: icons.start }).addTo(mapInstance.current).bindPopup("<b>Starting Point</b><br>" + hospitalCoords.displayName);
        L.marker(latLng2, { icon: icons.end }).addTo(mapInstance.current).bindPopup("<b>Destination</b><br>" + accidentCoords.displayName);

        routingControl.current = L.Routing.control({
            waypoints: [latLng1, latLng2],
            routeWhileDragging: false,
            addWaypoints: false,
            fitSelectedRoutes: true,
            showAlternatives: true,
            lineOptions: { styles: [{ color: '#f43f5e', opacity: 0.8, weight: 6, dashArray: '10, 10' }] },
            createMarker: () => null
        }).addTo(mapInstance.current);

        routingControl.current.on('routesfound', (e) => {
            const summary = e.routes[0].summary;
            const distKm = (summary.totalDistance / 1000).toFixed(1);
            const baseTimeMin = summary.totalTime / 60;
            const estTimeMin = Math.round(baseTimeMin * (1.2 + Math.random() * 0.2));

            routeCoordinates.current = e.routes[0].coordinates;
            setRouteData({ distance: distKm, time: estTimeMin });
            setLoading(false);

            startSimulation(estTimeMin, icons.amb);
        });

        routingControl.current.on('routingerror', () => {
            setErrorMsg('Routing failed. Please try different locations.');
            setLoading(false);
        });
    };

    const startSimulation = (initialTime, ambIcon) => {
        if (routeCoordinates.current.length < 2) return;
        let step = 0;
        
        ambulanceMarker.current = window.L.marker([routeCoordinates.current[0].lat, routeCoordinates.current[0].lng], {
            icon: ambIcon, zIndexOffset: 1000
        }).addTo(mapInstance.current);

        simulationInterval.current = setInterval(() => {
            if (step >= routeCoordinates.current.length - 1) {
                clearInterval(simulationInterval.current);
                setRouteData(prev => ({ ...prev, time: 'Arrived' }));
                return;
            }
            step++;
            const nextCoord = routeCoordinates.current[step];
            ambulanceMarker.current.setLatLng([nextCoord.lat, nextCoord.lng]);
            
            if (step % 20 === 0) {
                const ratio = (routeCoordinates.current.length - step) / routeCoordinates.current.length;
                setRouteData(prev => ({ ...prev, time: Math.max(1, Math.round(initialTime * ratio)) }));
            }
        }, 150);
    };

    return (
        <div id="app-container">
            <div className="glass-panel" id="controls-panel">
                <div className="panel-header">
                    <div className="brand">
                        <span className="pulse-dot active"></span>
                        <h1>MediTrak</h1>
                    </div>
                    <p className="subtitle">Live Emergency Routing</p>
                </div>

                <form className="routing-form" onSubmit={handleFormSubmit}>
                    <div className="input-group">
                        <label>Starting Point (Pickup)</label>
                        <div className="input-wrapper">
                            <span className="icon">🏥</span>
                            <input type="text" value={hospital} onChange={(e) => setHospital(e.target.value)} required />
                        </div>
                    </div>

                    <div className="input-group">
                        <label>Destination (Dropoff)</label>
                        <div className="input-wrapper">
                            <span className="icon">⚠️</span>
                            <input type="text" value={accident} onChange={(e) => setAccident(e.target.value)} required />
                        </div>
                    </div>

                    <div className="input-group">
                        <label>Ambulance Number</label>
                        <div className="input-wrapper">
                            <span className="icon">🚑</span>
                            <input type="text" value={ambulanceNo} onChange={(e) => setAmbulanceNo(e.target.value)} required />
                        </div>
                    </div>

                    <button type="submit" className="primary-btn" disabled={loading}>
                        {!loading ? <span>Find Best Route</span> : <div className="loader"></div>}
                    </button>
                </form>

                {errorMsg && (
                    <div className="error-message">
                        <p>{errorMsg}</p>
                    </div>
                )}

                {routeData && (
                    <div className="route-info">
                        <h3>Route Information</h3>
                        <div className="info-grid">
                            <div className="info-card">
                                <span className="info-label">Distance</span>
                                <span className="info-value">{routeData.distance} km</span>
                            </div>
                            <div className="info-card highlight">
                                <span className="info-label">Est. Time</span>
                                <span className="info-value" style={{ color: routeData.time === 'Arrived' ? '#10b981' : 'inherit' }}>
                                    {routeData.time} {routeData.time !== 'Arrived' && 'min'}
                                </span>
                            </div>
                            <div className="info-card">
                                <span className="info-label">Tracking ID</span>
                                <span className="info-value">{ambulanceNo}</span>
                            </div>
                        </div>
                        <div className="tracking-status">
                            <div className="status-indicator">
                                <span className="pulse-dot active"></span>
                                <p>Live Tracking Active</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div ref={mapRef} id="map"></div>
        </div>
    );
};

export default LiveMap;