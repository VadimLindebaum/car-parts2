# car-parts2

Python + Flask versioon

Eeldused
	•	Python ≥ 3.10
	•	Pip

Install & käivitus
pip install -r requirements.txt
python server.py

Server kuulab http://localhost:3300.

Märkused
	•	LE.txt formaat: veendu, et CSV-s on päised (name, price, serial_number vms). Vajadusel kohanda koodi.
	•	Faili suurus: kuni 600 MB → RAM kasutus võib olla mitu GB.
	•	Turvalisus: API on vaikimisi avatud. Produktsioonis lisa autentimine ja rate limiting.
 
