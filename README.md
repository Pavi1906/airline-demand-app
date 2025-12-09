airline-demand-app

📊 Airline Booking Market Demand — Streamlit Web App

A lightweight web application that analyzes global airline routes, simulates market demand trends, and retrieves live flight data using the AviationStack API.

This project was built as part of a technical evaluation requiring Python, web scraping, API integration, and web application development skills.

✨ Features

1. Route Data Exploration

* Fetches global airline route data from the OpenFlights public dataset
* Displays top origin–destination routes
* Allows selecting any popular route for deeper exploration

2. Market Demand Simulation

* Generates realistic 36-month price trends
* Simulates booking volume using seasonal patterns
* Provides summary tables and visual charts (Plotly)

3. Live Flight Data (AviationStack API)

* Shows real-time flights for the selected route
* Secure API integration using Streamlit Secrets

4. Interactive Dashboard

* Built with Streamlit
* Includes route maps, filters, and intuitive layout
* Fully deployed and accessible online

🚀 Live Demo

👉 [https://airline-demand-demo.streamlit.app](https://airline-demand-demo.streamlit.app)

🛠️ Technology Used

* Python 3
* Streamlit
* Pandas, NumPy
* Plotly Express
* Requests
* OpenFlights Dataset
* AviationStack API
* Git + GitHub

▶️ How to Run Locally

bash
git clone https://github.com/Pavi1906/airline-demand-app
cd airline-demand-app
pip install -r requirements.txt
streamlit run app.py

Create a `.env` file:

```
AVIATIONSTACK_KEY=your_api_key
```


🔐 Deployment Secrets (Streamlit Cloud)

Add this in **Settings → Secrets**:

```
AVIATIONSTACK_KEY="your_api_key"
```

This keeps keys secure (do not commit `.env` to GitHub).

📌 Notes

* OpenFlights provides publicly available airline route data
* Price and booking trends are simulated for demonstration purposes
* API integration is modular and extendable (e.g., pricing, trends, demand forecasting)

👩‍💻 Author

Pavithra P
Python Developer | Python Enthusiast
