# ESP32-Real-Time-Motion-Capture-Object-Animation-for-Blender
This project enables real-time motion capture and object animation in Blender using an ESP32 microcontroller. It utilizes Wi-Fi and UDP communication to send bone rotations and object positions from the ESP32 to Blender, allowing for real-time skeletal and object-based animations.
Features
✅ Multi-Bone Motion Capture – Stream roll, pitch, and yaw data for multiple bones.
✅ Object Position Tracking – Send X, Y, Z coordinates to animate objects dynamically.
✅ Real-Time UDP Communication – Low-latency data transfer between ESP32 and Blender.
✅ Blender Integration – Custom Blender add-on for mapping ESP32 motion data to bones and objects.
✅ Wi-Fi Connectivity – ESP32 connects wirelessly for seamless motion capture.
✅ Customizable Mapping – Manually assign ESP32 bones and objects to Blender elements.

How It Works
ESP32 Sends Motion Data:

Generates random or sensor-based bone rotations (roll, pitch, yaw).
Sends object position updates for animations like walking.
Transmits data as a JSON packet via UDP to Blender.
Blender Receives & Animates:

The Blender add-on listens for UDP packets.
Updates bone rotations and object positions in real-time.
Inserts keyframes for smooth animation playback.
Setup & Installation
1. ESP32 Setup
Flash the provided Arduino code to your ESP32.
Update the Wi-Fi credentials (SSID, Password).
Set the correct Blender PC IP (blenderIP).
Connect ESP32 to Wi-Fi and start sending motion data.
2. Blender Add-on Installation
Install the provided Blender Python script as an add-on.
Enable the add-on in Blender Preferences > Add-ons.
Use the N-Panel (ESP32 Motion Tab) to map bones and objects.
Start real-time motion capture!
Future Enhancements
🔹 Sensor Integration (IMU/Accelerometer/Gyro) for Real-world Motion Capture
🔹 Improved Object Movement with Linear and Smooth Transitions
🔹 Optimized Network Performance for Faster Data Transmission

License
This project is open-source and available under the MIT License. Feel free to contribute, modify, and improve it! 🚀
