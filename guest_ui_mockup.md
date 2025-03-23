# Guest UI Visual Mockup

## Dashboard Layout

```
+-------------------------------------------------------+
|                    HOTEL LOGO                         |
|  Guest Dashboard                           User Menu  |
+-------------------------------------------------------+
|                                                       |
|  +-------------------+    +----------------------+    |
|  |                   |    |                      |    |
|  |  ROOM CONTROLS    |    |  CHATBOT INTERFACE   |    |
|  |                   |    |                      |    |
|  |  [Temperature]    |    |  +----------------+  |    |
|  |  18°C [====] 30°C |    |  | Hotel AI       |  |    |
|  |                   |    |  | Welcome! How   |  |    |
|  |  [Lighting]       |    |  | can I help?    |  |    |
|  |  Brightness: 70%  |    |  +----------------+  |    |
|  |  [===========]    |    |                      |    |
|  |                   |    |  +----------------+  |    |
|  |  Color: Warm      |    |  | You            |  |    |
|  |  [====|====]      |    |  | Can I order    |  |    |
|  |  Warm     Cool    |    |  | room service?  |  |    |
|  |                   |    |  +----------------+  |    |
|  |  [Presets]        |    |                      |    |
|  |  +-----------+    |    |  +----------------+  |    |
|  |  | 😴 Sleep  |    |    |  | Hotel AI       |  |    |
|  |  +-----------+    |    |  | Yes, I can help|  |    |
|  |                   |    |  | with that...   |  |    |
|  |  +-----------+    |    |  | [typing...]    |  |    |
|  |  | 📖 Reading|    |    |  +----------------+  |    |
|  |  +-----------+    |    |                      |    |
|  |                   |    |  [Debug Panel ▼]     |    |
|  |  +-----------+    |    |  Status: Connected   |    |
|  |  | 🌱 Eco    |    |    |  Last msg: Registered|    |
|  |  +-----------+    |    |  Response: From model|    |
|  |                   |    |                      |    |
|  |  Current Mode:    |    |  +----------------+  |    |
|  |  Reading          |    |  | Type message   |  |    |
|  |                   |    |  | [Send] [Clear] |  |    |
|  +-------------------+    +----------------------+    |
|                                                       |
+-------------------------------------------------------+
```

## Room Controls Detail

### Temperature Control
```
Temperature Control
+------------------------------------------+
|  Current: 23°C                           |
|                                          |
|  18°C [==========|=======] 30°C          |
|       ^                                  |
|     Cool                Warm             |
+------------------------------------------+
```

### Lighting Control
```
Lighting Control
+------------------------------------------+
|  Brightness: 70%                         |
|  [==============|=====]                  |
|                                          |
|  Color Temperature:                      |
|  [=========|========]                    |
|  Warm              Cool                  |
|                                          |
|  Preview:                                |
|  +--------------------------------+      |
|  |                                |      |
|  |     [Light visualization]      |      |
|  |                                |      |
|  +--------------------------------+      |
+------------------------------------------+
```

### Preset Controls
```
Preset Controls
+------------------------------------------+
|                                          |
|  +-------------+  +-------------+        |
|  |             |  |             |        |
|  |  😴 Sleep   |  |  📖 Reading |        |
|  |             |  |             |        |
|  +-------------+  +-------------+        |
|                                          |
|  +-------------+  +-------------+        |
|  |             |  |             |        |
|  |  🌱 Eco     |  | 🏠 Custom   |        |
|  |             |  |             |        |
|  +-------------+  +-------------+        |
|                                          |
|  Active Preset: Reading                  |
|  +--------------------------------+      |
|  | • Warm light at 60% brightness |      |
|  | • Temperature set to 23°C      |      |
|  +--------------------------------+      |
+------------------------------------------+
```

## Enhanced Chatbot Detail

### Message Bubbles
```
+------------------------------------------+
|                                          |
|  +--------------------------------+      |
|  | Hotel AI                       |      |
|  | How can I assist you today?    |      |
|  +--------------------------------+      |
|                                          |
|              +-------------------+       |
|              | You               |       |
|              | Can I get extra   |       |
|              | towels?           |       |
|              +-------------------+       |
|                                          |
|  +--------------------------------+      |
|  | Hotel AI                       |      |
|  | Of course! I'll arrange for    |      |
|  | extra towels to be delivered   |      |
|  | to your room right away.       |      |
|  | Is there anything else you     |      |
|  | need?                          |      |
|  +--------------------------------+      |
|                                          |
+------------------------------------------+
```

### Typing Indicator
```
+------------------------------------------+
|  +--------------------------------+      |
|  | Hotel AI                       |      |
|  | ●●● [animated dots]            |      |
|  +--------------------------------+      |
+------------------------------------------+
```

### Debug Panel (Expandable)
```
+------------------------------------------+
|  [Debug Panel ▼]                         |
+------------------------------------------+
|  Message Status:                         |
|  • Last message: Successfully registered |
|  • Model processing: Complete            |
|  • Response source: LangGraph API        |
|                                          |
|  API Details:                            |
|  • Endpoint: /api/chat                   |
|  • Request time: 1.2s                    |
|  • Status code: 200                      |
|                                          |
|  Agent Information:                      |
|  • Active agent: room_service_agent      |
|  • Confidence: 0.92                      |
|                                          |
|  [Raw JSON Response ▼]                   |
+------------------------------------------+
```

## Animation Concepts

### Message Appearance
- User messages slide in from right with subtle bounce effect
- AI messages fade in from left
- New messages trigger automatic smooth scrolling

### Typing Indicator
- Three dots with wave animation
- Subtle pulsing effect
- Appears immediately after user sends message

### Status Indicators
- Small colored dots with status text:
  - 🟢 Connected
  - 🟡 Sending...
  - 🟠 Processing...
  - 🔴 Error

### Preset Transitions
- Room control values animate smoothly between states
- Light preview transitions with fade effect
- Active preset button has subtle glow effect

## Color Scheme

- **Primary**: #1976d2 (Hotel brand blue)
- **Secondary**: #f5f5f5 (Light gray for backgrounds)
- **Accent**: #ff9800 (Orange for highlights and active states)
- **Text**: #212121 (Dark gray for primary text)
- **Subtle Text**: #757575 (Medium gray for secondary text)
- **Success**: #4caf50 (Green for positive status)
- **Warning**: #ff9800 (Orange for warnings)
- **Error**: #f44336 (Red for errors)
- **Background**: #ffffff (White)
- **Card Background**: #ffffff (White with subtle shadow)

## Typography

- **Primary Font**: Roboto (Already used in Material-UI)
- **Headings**: Roboto Medium, various sizes
- **Body Text**: Roboto Regular, 16px
- **Small Text**: Roboto Regular, 14px
- **Micro Text**: Roboto Regular, 12px (for debug panel)

## Responsive Behavior

- On mobile devices, the layout will stack:
  - Room controls at the top
  - Chatbot interface below
- On tablets, the layout will maintain side-by-side but with adjusted proportions
- On desktop, the layout will be as shown in the mockup