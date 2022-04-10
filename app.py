from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table',attrs={'class':"table table-striped text-sm text-lg-normal"})
row = table.find_all('th',attrs={'class':'font-semibold text-center'})
scrap=soup.select('table.table-striped tbody tr')

row_length = len(row)

temp = [] #initiating a list 

for i in scrap:

    #scrapping process
    #ambil tanggal
    pick_date=i.select_one('th[scope="row"]').get_text(strip=True)
    
    #ambil volume
    pick_volume=i.select_one('td.text-center:nth-child(3)').get_text(strip=True)   
    
    temp.append((pick_date,pick_volume))

temp = temp[::-1]	

#change into dataframe
gecko_ete = pd.DataFrame(temp,columns=('Date','Volume'))

#insert data wrangling here
gecko_ete['Date']=pd.to_datetime(gecko_ete['Date'])
gecko_ete['Volume']=gecko_ete['Volume'].str.replace(pat='$',repl='',regex=True)
gecko_ete['Volume']=gecko_ete['Volume'].str.replace(',','')
gecko_ete['Volume']=gecko_ete['Volume'].astype('int64')
gecko_ete.set_index('Date')
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{gecko_ete["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	plt.style.use('seaborn')
	ax = plt.plot(gecko_ete['Date'],gecko_ete['Volume'])
	# plt.title("Pergerakan Volume Ethereum (Januari 2020-Juni 2021)")
	plt.xlabel('Tahun') 
	plt.xticks(rotation = 20)
	plt.ylabel('Volume') 

	
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)