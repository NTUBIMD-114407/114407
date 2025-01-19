// Initialize and add the map
let map;

async function initMap() {
  // The location of the specified position
  const position = { lat: 25.042540721636726, lng: 121.52626372981624 };

  
    // Request needed libraries
    //@ts-ignore
    const { Map } = await google.maps.importLibrary("maps");
    const { PlacesService } = await google.maps.importLibrary("places");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    const { InfoWindow } = await google.maps.importLibrary("maps");
  
    // Initialize the map
    map = new Map(document.getElementById("map"), {
      zoom: 15,
      center: position,
      mapId: "DEMO_MAP_ID", // Replace with your custom map ID
    });
  
    // Create a marker
    const marker = new AdvancedMarkerElement({
      map: map,
      position: position,
      title: "Fetching data...",
    });
  
    // Initialize the InfoWindow
    const infoWindow = new InfoWindow();
  
    // Fetch place details from Places API
    const service = new PlacesService(map);
  
    service.nearbySearch(
      {
        location: position,
        radius: 50, // Search within a 50-meter radius
        type: "establishment", // Search for any establishment
      },
      (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results.length > 0) {
          const place = results[0]; // Get the first result
          const content = `
            <div style="font-size:14px;">
              <h3 style="margin:0;">${place.name}</h3>
              <p><strong>Rating:</strong> ${place.rating || "N/A"} ⭐</p>
              <p><strong>Business Hours:</strong><br>
              ${place.opening_hours?.weekday_text?.join("<br>") || "No hours available"}
              </p>
              <p>Latitude: ${position.lat}<br>Longitude: ${position.lng}</p>
            </div>
          `;
  
          infoWindow.setContent(content);
          marker.title = place.name;
        } else {
          infoWindow.setContent("<p>No place data found for this location.</p>");
        }
      }
    );
  
    // Add a click listener to the marker to show the InfoWindow
    marker.addListener("click", () => {
      infoWindow.open(map, marker);
    });
  }
  
  initMap();
  