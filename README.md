# EventFlow

- Current: An endpoint "/health" that returns a JSON {"status":"ok"}.

- Current: An endpoint POST "/invitados" for adding guests.

- Current: An endpoint GET "/invitados?evento_id=", with 404 error for nonexistent events.

- Current: An endpoint PATCH "/invitados/{id}/ingreso", validates the guest entries once & returns a 409 error when a guest is already in the event.

- Current: Automated tests with pytest cover the main cases of the endpoints.

- Planned: It generates a QR code for each guest.

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

