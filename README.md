# CardioCare — Heart Disease Prediction

A Flask web app using a deep learning model to predict heart disease risk.

## Project Structure
```
cardiocare/
├── app.py                  # Flask routes
├── config.py               # Paths & MongoDB config
├── requirements.txt
├── model/
│   └── train_model.py      # Run this first!
├── utils/
│   ├── predictor.py        # Model inference
│   ├── risk_engine.py      # Risk levels + care tips
│   └── pdf_generator.py    # PDF report builder
├── static/css/             # Stylesheets
├── static/js/              # Chart.js + form logic
├── templates/              # Jinja2 HTML pages
├── dataset/
│   └── heart.csv           # UCI Cleveland dataset
└── reports/                # Generated PDFs (auto-created)
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your dataset
Place your `heart.csv` inside the `dataset/` folder.

### 3. Train the model (run once)
```bash
python model/train_model.py
```
This creates `model/heart_model.h5` and `model/scaler.pkl`.

### 4. Start MongoDB
```bash
mongod
```

### 5. Run the app
```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Pages
| Route      | Description                        |
|------------|------------------------------------|
| /          | Dashboard with charts & stats      |
| /predict   | Enter patient data, get prediction |
| /history   | View & delete past reports         |
| /model     | Model architecture & feature info  |
| /download/<file> | Download PDF report          |
"# cardiocare" 
