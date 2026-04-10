# PIN DROP: Master Project Report

> [!NOTE]
> This document serves as the comprehensive architectural and functional overview of **Pin Drop**, a hyper-secure, aesthetically refined Lost & Found application tailored for the Bengaluru City University (Central College) community.

## 1. Project Concept & Identity
**Pin Drop** evolved from a standard lost-and-found system into an "Elite Telemetry Dashboard." The application aims to solve the persistent issue of lost items on a university campus by turning the reporting and claiming process into an engaging, secure, and geographically precise experience. It prioritizes accountability, user privacy, and an ultra-premium dark-mode aesthetic known as "Obsidian & Emerald."

## 2. Technology Stack & Architecture
*   **Backend Framework**: Python / Flask
*   **Database**: SQLAlchemy / SQLite (Development) & PostgreSQL handling for Production (Render compatible).
*   **Authentication**: Flask-Login, Werkzeug Security (Bcrypt password hashing).
*   **Frontend Technologies**: HTML5, Vanilla JavaScript, CSS3.
*   **UI Framework**: Bootstrap 5 (heavily customized with bespoke CSS tokens).
*   **Geospatial Visualization**: Leaflet.js with CartoDB Dark Matter base maps and Nominatim for reverse geocoding.

## 3. The Design System: "Obsidian & Emerald"
The entire application was extensively refactored to align with a luxury, elite institutional design language.
*   **Color Palette**: Deep slates (`#0f172a`), pitch blacks (`#000`), and vibrant emerald accents (`#00E676`).
*   **Micro-interactions**: Subtle `glow-hover` effects, hairline borders, and `fade-in-up` CSS animations provide a premium, dynamic feel without resorting to heavy JavaScript frameworks.
*   **Typography**: Clean, wide-spaced uppercase typography utilizing varying opacities and hairline structural separators to guide the user's eye.

## 4. Database Schema (Models)
The application relies on 5 core relational models:
1.  **User**: Stores credentials, role (`STUDENT` or `HOD`), and departmental affiliations.
2.  **Item**: The central model storing `LOST` or `FOUND` status, descriptions, geographic coordinates (`latitude`, `longitude`), and the generated `verification_code`.
3.  **Category**: Pre-defined classifications (Electronics, ID Cards, Wallets, etc.).
4.  **Match**: A connective tissue containing proximity/keyword similarity scores between reported Lost and Found items.
5.  **Report / Integrity**: A moderation tool allowing the community to flag malicious or spam entries.

## 5. Security & Authentication Protocols
Pin Drop employs a strict dual-tier authentication system to separate standard users from administrative faculty.
*   **Student Access**: Standard registration and login for general campus members.
*   **HOD (Head of Department) Portal**: An isolated, hyper-secure login route (`/hod_login`). HOD accounts are pre-provisioned via a secure python script (`create_hod.py`).
*   **Immutable Credentials**: HOD passwords utilize an immutable protocol—meaning once an HOD sets their custom password from their dashboard, it locks into the system entirely, preventing hijacking or unauthorized resets.

## 6. Core Features & Workflows

### A. Geospatial Reporting
When a user reports an item (`post_item.html`), they are presented with an interactive Leaflet map accurately restricted to the **Bengaluru City University Central College Campus** bounds.
*   Users tap the map to drop an emerald pin.
*   The system uses Nominatim API to instantly reverse-geocode the coordinates into a readable location sector string.
*   The map features hardcoded, accurate markers for major campus landmarks (Jnana Jyothi Auditorium, Admin Block, Central Library, UVCE) to aid orientation.

### B. "Optic" Evidence Capture
Users can upload existing photos or instantly invoke their mobile/desktop webcams using custom HTML5 device integrations to snap a picture. The base64 data is intercepted and efficiently converted to timestamped files on the backend.

### C. The Verification Code Sequence
To prevent fraudulent claims, Pin Drop implements a zero-trust handover protocol:
1.  When a user successfully reports a **LOST** item, a unique 8-character verification code is generated.
2.  This code is hidden from the public feed but remains accessible to the owner via a **Bell Notification Dropdown** in the main navigation bar.
3.  When a finder reports a matching **FOUND** item, they possess the physical object but not the code.
4.  To resolve the record (`CLAIMED`), the "Finder" must input the "Loser's" verification code during a physical handover.

### D. High-Value Asset Management
Users can classify certain items (like laptops or expensive equipment) as "High Value" and assign them to a specific department upon reporting. These items are immediately routed to the isolated HOD Dashboards for secondary faculty oversight.

### E. Trust Ledger (Integrity)
A public-facing audit page where the community can view a read-only list of successfully reunited items alongside any active fraud/spam reports submitted by other users. 

## 7. Deployment & Infrastructure
The project is containerization and deployment ready. 
*   It includes a `render.yaml` configuration file for immediate deployment on Render.com.
*   The `app.py` logic automatically intercepts `postgres://` environment strings provided by modern cloud hosts and converts them to the SQLAlchemy-compliant `postgresql://` format.
*   Secure `SECRET_KEY` configuration ensures sessions are tamper-proof across deployments.
