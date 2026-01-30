# Industrial Asset Guardian (IAG) 🛡️

![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple) ![Tech Stack](https://img.shields.io/badge/Python-OWL_JS-blue) ![Industry](https://img.shields.io/badge/Industry-Mining_%26_Energy-orange)

## 📖 Executive Summary
**Industrial Asset Guardian** bridges the gap between physical machinery (IoT) and Enterprise Resource Planning (ERP).

Designed for the high-demand industrial sector (Mining, Oil & Gas), this module transforms Odoo into a **Predictive Maintenance Hub**. It ingests real-time telemetry from assets (motors, pumps, conveyors) to predict failures before they happen, automating workflows directly within the standard Odoo ecosystem.

---

## 🚀 Key Features

### 1. 🧠 Smart Health Scoring Algorithms
Instead of relying on manual inspections, IAG uses a proprietary logic engine (`_compute_health_score`) to assess asset condition in real-time.
* **Dynamic Logic:** Continuously compares live telemetry against technical thresholds (Max Temp/Vibration).
* **Weighted Penalties:** Applies non-linear penalties based on severity (e.g., >20% overheat results in critical score reduction).

### 2. ⚙️ Automated "Zero-Touch" Maintenance
Eliminates human delay in reporting critical faults.
* **Trigger:** When `Health Score` drops below **50%**.
* **Action:** Automatically changes asset status to **"In Maintenance"** and generates a **Work Order** in the official Odoo Maintenance module.
* **Smart Deduplication:** Includes logic to prevent "alert fatigue" by checking for existing open tickets before creating new ones.

### 3. ☢️ Dynamic UI: The "Panic Gauge" (OWL Framework)
A custom frontend widget built using the **Odoo Web Library (OWL)** to enhance User Experience.
* **Visual Feedback:** Replaces static numbers with a reactive progress bar (Green/Yellow/Red).
* **Haptic/Visual Alert:** If a metric becomes critical (e.g., Temp > 90°C), the component triggers a CSS-based **shaking animation**, instantly drawing the operator's attention to the specific failure.

---

## 📡 IoT Integration (API Documentation)

IAG exposes a lightweight **REST/HTTP Endpoint** designed for low-power IoT devices (PLCs, ESP32, Node-RED).

### Endpoint Specification
* **URL:** `/iag/api/update_metrics`
* **Method:** `POST`
* **Format:** `application/json`

### Payload Structure
The system accepts a simplified JSON payload to minimize bandwidth usage in remote industrial sites.

```json
{
    "serial_number": "SN-12345",   // Required: Matches Odoo Asset Serial
    "temperature": 85.5,           // Optional: Updates temp & recalcs score
    "vibration": 3.2               // Optional: Updates vib & recalcs score
}
```

### 💻 Quick Test (PowerShell)
Simulate a sensor reading using Windows PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8069/iag/api/update_metrics" `
-Method Post `
-ContentType "application/json" `
-Body '{"serial_number": "SN-TEST", "temperature": 98.5, "vibration": 1.5}'
```

---

## 🛠️ Installation & Setup

Designed for modular deployment on Odoo 19 (Community or Enterprise).

1.  **Deploy**: Copy the `industrial_asset_guardian` folder to your Odoo addons path (or mount via Docker).
2.  **Install**: Search for "Industrial Asset Guardian" in the Apps menu and click **Activate**.
3.  **Dependencies**: Automatically installs the standard `maintenance` module.
4.  **Verify**: Access the new "Industrial Guardian" menu icon.

---

## 🧪 Validation Scenario (Proof of Concept)

To validate the full loop (IoT -> ERP -> Maintenance):

1.  **Setup**: Create an asset with Serial Number `SN-TEST`. Set Max Temp to `90.0`.
2.  **Inject Fault**: Send an API request with temperature: `95.0` (Critical Overheat).
3.  **Observe Results**:
    *   **Dashboard**: Asset turns red and the gauge widget begins to shake.
    *   **Automation**: A new Maintenance Request appears in the Maintenance App titled "CRITICAL: Overheating detected".

---

## ❓ Troubleshooting

| Issue | Likely Cause | Solution |
| :--- | :--- | :--- |
| **API: Asset not found** | Serial Mismatch | Ensure JSON `serial_number` exactly matches the Odoo record. |
| **No "Shake" Animation** | Browser Cache | Hard refresh (`Ctrl+Shift+R`) to reload new OWL assets. |
| **Request not created** | Logic Threshold | Ensure the fault sent actually lowers the Health Score below 50%. |