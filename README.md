# EventFlow

- Current: An endpoint (/health) that returns a JSON {"status":"ok"}

- Planned: It registers the guests. 

- Planned: It generates a QR code for each guest & validates if the guest has already entered, in order to avoid duplicated
 entries with the same QR code.

- Planned: It will import guest lists using AI & will also send the invite through WhatsApp. 


## Installation

```
python -m venv venv 
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

- You must copy .env.example to .env & fill in your real values.

```
Copy-Item .env.example .env
```

## Run

```
uvicorn main:app --reload
```
- Then open http://127.0.0.1:8000/health in your browser.

