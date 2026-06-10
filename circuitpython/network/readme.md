# CircuitPython Network Tutorial

This tutorial covers connecting CircuitPython boards like Picopad to the internet using WiFi.

You'll learn to make HTTP requests, interact with web APIs, send sensor data to the cloud, and control devices remotely.

## What you'll learn

-   Connect to WiFi
-   Make HTTP requests
-   Parse JSON responses
-   Log sensor data to cloud
-   Control devices over internet
-   Build Telegram bot
-   Build web server dashboards
-   Real-time communication (polling, SSE, WebSocket)

## WiFi Test

Connect to WiFi network and print network info.

### Key concepts:

-   WiFi credentials
-   Printing MAC and IP
-   Use ping to test network connectivity

![cp_network_wifitest](https://github.com/MakerClassCZ/Picopad/assets/3875093/8586d82f-5dc1-45ac-9ff1-5d1ce81b4fed)

## WiFi Scanner

WiFi network scanner that visualizes nearby networks as parabolas on a channel graph, showing signal strength and channel usage at a glance. See the `wifi_scanner/readme.md` for details.

### Key concepts:

-   WiFi scanning
-   Signal strength visualization
-   Channel mapping

<img width="320" height="240" alt="wifi_scanner" src="https://github.com/user-attachments/assets/2b2316b3-47d4-4e97-90c8-8d058af90818" />


## Teletext

Three examples showing different approaches to fetching Czech Television teletext via [api.makerclass.cz](http://api.makerclass.cz):
- **teletext** - downloads 4-bit BMP image using raw sockets with `recv_into()` for direct control over memory allocation. No external libraries needed.
- **teletext_sdcard** - uses `adafruit_requests` to stream the BMP in chunks to SD card, then displays via `OnDiskBitmap`. SD card acts as cache.
- **teletext_textonly** - fetches page text as JSON via `adafruit_requests` and renders with a custom 8×12 bitmap font (`teletext.bdf`) with Czech diacritics.

![cp_network_teletext_image](https://github.com/MakerClassCZ/Picopad/assets/3875093/161c0029-e763-443f-bd32-5266838cf937)

![cp_network_teletext_text](https://github.com/MakerClassCZ/Picopad/assets/3875093/c8ef82b7-fbab-4ee1-99f9-b9d0f66641af)

### Key concepts:

-   Making HTTP requests
-   Use external JSON API
-   Downloading binary data
-   Saving images to storage

### Interesting techniques:
- raw socket with `recv_into()` and pre-allocated buffers to avoid memory fragmentation on repeated large downloads
- streaming HTTP response to SD card file in chunks
- saving memory techniques (garbage collector, bitmap labels, context managers)
- custom BDF font extracted from teletext test page with full Czech/Slovak diacritics
- rounding number to tens/hundreds with simple arithmetic


 ## Prague Public Transport Departures (Golemio)

  Live departure board for Prague public transport, using the city's open data platform
  [Golemio.cz](https://api.golemio.cz). Two variants are included:

  - **code.py** - prints the next departures to the serial console.
  - **code_display.py** - renders a full departure board on the display: stop name, line numbers color-coded by metro
  line (A green, B yellow, C red), destinations, air-conditioning marker, and minutes-to-departure.

 ### Key concepts:

  -   Using an open government / city data API
  -   HTTPS with a custom CA certificate
  -   API key authentication via request headers
  -   Parsing JSON responses
  -   Pre-allocated display layout for memory-efficient refreshes
     
<img width="320" height="240" alt="golemiot" src="https://github.com/user-attachments/assets/ff904d8f-1e67-425c-acb5-d009a56a4031" />
  
### Interesting techniques:

  - HTTPS to a specific host by loading the its certificate (`gtsr4.pem`) into the SSL context instead of bundling the full trust store
  - handling gzip-compressed API responses with `zlib.decompress`
  - deriving the current local time from the HTTP `Date` response header plus the API's ISO timezone offset - no NTP or RTC




## Network Clock

NTP-synced clock with animated day/night sky. The sun moves across the sky following real time, and stars appear at night via palette swap.

### Key concepts:

-   NTP time synchronization
-   Display animation and sprite layering
-   EU daylight saving time calculation

<img width="320" height="240" alt="network_clock" src="https://github.com/user-attachments/assets/e45158fa-2ad3-43c9-a970-bdd8762f0953" />


## Alarm Clock

NTP-synced alarm clock with time display and alarm functionality. Set the time and alarm using buttons on the device.

### Key concepts:

-   NTP time synchronization
-   Alarm scheduling
-   Audio output
-   Button-based UI for time and alarm setting

<img width="320" height="240" alt="alarm_clock" src="https://github.com/user-attachments/assets/e8228771-b875-4070-a1f3-9b7319e982d8" />


## Telegram Bot

Build a Telegram bot to control your board remotely.

### Key concepts:

-   Telegram bot API
-   Sending messages
-   Responding to commands

### Interesting techniques:
- Use long polling with Telegram API to reduce number of requests

![cp_network_telegram](https://github.com/MakerClassCZ/Picopad/assets/3875093/ebfd61ec-c9e4-430a-a811-07f92255d43d)

## Web Server

Three examples demonstrating different real-time communication patterns for a web dashboard running on the microcontroller. All three show CPU temperature, LED control, and button state. The frontend uses Alpine.js and Bulma CSS loaded from CDN.

- **webserver_polling** - the browser polls the server every 2 seconds for fresh data. Simplest approach.
- **webserver_sse** - the server pushes data to the browser via Server-Sent Events. Typically the best fit for MCU projects - the server streams sensor updates efficiently, and user interactions (like toggling an LED) are simple HTTP requests.
- **webserver_websocket** - full duplex communication via WebSocket. The browser can also send commands back through the same connection.

### Key concepts:

-   HTTP server on a microcontroller
-   Real-time communication patterns (polling, SSE, WebSocket)
-   Serving HTML files and JSON API
-   Alpine.js reactive frontend

<img width="515" height="375" alt="picopad_webserver" src="https://github.com/user-attachments/assets/3c1b12b7-ec06-4f6e-843b-1f44902a2a79" />


## Mapa tvoji mamy

Czech regions map with real-time environmental data fetched from tmep.cz. Select a region and see live sensor readings displayed on the map.

### Key concepts:

-   HTTP API integration
-   Data visualization and color mapping
-   Interactive UI

<img width="320" height="240" alt="image" src="https://github.com/user-attachments/assets/3ba3eb1b-0517-4efe-b9a3-ae39b20e3a5c" />


## Zivy obraz

E-ink / digital display integration with the zivyobraz.eu service. The device downloads a BMP image over HTTP and displays it, then enters deep sleep until the next scheduled update.

### Key concepts:

-   Streaming HTTP responses
-   BMP image processing
-   Deep sleep scheduling

## Summary

This tutorial covers a wide range of network concepts: WiFi connectivity and scanning, HTTP requests, JSON APIs, NTP time synchronization, Telegram bots, web servers with real-time dashboards (polling, SSE, WebSocket), live data visualization, and e-ink display integration. Follow along to connect your CircuitPython projects to the internet!
