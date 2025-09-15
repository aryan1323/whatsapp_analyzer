# WhatsApp Chat Analyzer

Welcome to **WhatsApp Chat Analyzer**, a React-based web application that lets you upload your exported WhatsApp chat files and gain insightful statistics, trends, charts, and summaries about your conversations.

---

## Demo & Source Code

- **Frontend:** [https://whatsapp-analyzer-ten.vercel.app/](https://whatsapp-analyzer-ten.vercel.app/)  
- **Backend:** [https://aryan-whatsapp-2.onrender.com](https://aryan-whatsapp-2.onrender.com)  



---

## Project Description

This tool analyzes WhatsApp chat `.txt` files exported from your Android/iOS device. It provides:

- User-wise message stats (count, words, active days)
- Multiple interactive charts (messages by hour, day, user contribution, word clouds, emoji usage, and more)
- Date range summarization with top senders and keywords
- Upload via drag-and-drop or file selection
- User search and filter for targeted analysis
- Zoom-in on charts for detailed view
- Send additional recommendations via a built-in form

The UI is responsive with a dark theme and animated loading messages to enhance user experience.

---

## Features & Animations

- **Animated Loading Overlay:** Rotating descriptive messages with blinking dots during data processing.
- **Drag-and-Drop Upload:** Visual highlight when dragging files over drop-zone.
- **Dynamic Chart Selection:** Show/hide charts with smooth checkbox toggles.
- **Zoom Animation:** Click on charts to smoothly zoom in with overlay and click-out to close.
- **Search Filter:** Real-time user list filtering with debounced input for performance.
- **Status Feedback:** Timely messages when sending recommendations or catching errors.

---

## How to Use

### 1. Export Your WhatsApp Chat File

**On Android:**
- Open desired chat → Tap ⋮ menu → More → Export chat → Without/Include Media → Save or send file.

**On iOS:**
- Open chat → Tap contact/group name → Export Chat → Attach/Without Media → Save or share file.

### 2. Upload Chat File

- Drag and drop your `.txt` chat file onto the upload area or click to select from your device.

### 3. Explore the Analysis

- View overall stats and charts generated automatically.
- Use the user search box to filter participants and analyze specific users.
- Select/deselect charts to customize visible data.
- Filter by date range and click *Summarize* for summary insights.
- Click chart images to zoom in.
- Add and send recommendations or feedback via the text box and button.

### 4. Start New Analysis

- Click *New Chat* to reset and upload a different chat.

---

## Installation & Setup

### Backend
git clone https://github.com/aryan1323/whatsapp-chat-analyzer-backend.git
cd whatsapp-chat-analyzer-backend
pip install -r requirements.txt
python app.py


Runs Flask backend on `http://localhost:5000`

### Frontend


Runs React app on `http://localhost:3000` and connects to backend via configured API URL.

---

## Technologies Used

- React with Hooks  
- Axios HTTP Client  
- Flask API backend  
- Pandas, Matplotlib, Seaborn, WordCloud (backend charts)  
- CSS Grid & Flexbox layout with animations  
- CORS enabled for API calls

---

## Contribution & Feedback

Contributions and fixes are welcome. Open issues or pull requests on GitHub repositories. Suggestions can also be sent via the recommendation feature in the app.

---


This README provides a comprehensive overview of the project with working repo links, animations descriptions, and usage steps to get started quickly.

