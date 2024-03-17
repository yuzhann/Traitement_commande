# Environment Configuration
pip install -r requirements.txt
python database.py

# Process supplier
In order to launch our supplier server, make sure we are under the directory of project, tape in terminal 
uvicorn fournisseur:app

# Process client
In order to place an order, tape in terminal
python client.py
