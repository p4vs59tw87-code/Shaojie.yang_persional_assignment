REQUIRMENTS:
streamlit
pandas
numpy
plotly
wrds account
psycopg2-binary

Use "pip install streamlit pandas numpy plotly wrds psycopg2-binary" in Powershell to install

Link for streamlit:https://okdwtyratge5brvceq6hy4.streamlit.app/
I highly recommend that you:
Creat a file like this: Shaojie.yang_persional_assignment\.streamlit\secrets.toml
and Enter your user name and password in it like this:
[wrds]
username = "Enter your wrds username"
password = "Enter your wrds password"

Use: 
cd "Shaojie.yang_persional_assignment"(replace with your actual project folder path)
streamlit run app.py
in Powershell to start

Tip:
the "__pycache__" file in this program is opptional, which means the program will creat one foryou even if you do not download one.
