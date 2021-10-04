import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import re


#başlık kütüphenesini ve web adresi tanımlamak, böylece adreste ki datayı çekmek
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
web_adresi = "https://www.transfermarkt.co.uk/fenerbahce-istanbul/startseite/verein/36"
donut_objesi = requests.get(web_adresi, headers=headers)
butun_data = BeautifulSoup(donut_objesi.content, 'html.parser')

#Futbolcu isimlerine ulaşmak için ihtiyaç duyduğumuz liste ve dataframe
futbolcu_isimleri = []
isim_kumesi = butun_data.find_all("a", {"class": "spielprofil_tooltip"})

for futbolcu_ismi in isim_kumesi:
    futbolcu_isimleri.append(futbolcu_ismi.text)

# Kısaltılmış isimleri listeden düşürüyoruz
for a in range(1,32):
    futbolcu_isimleri.pop(a)   

#Tekrarlanan isimleri listeden siliyoruz
del futbolcu_isimleri[32:43]
    

#Futbolcu uyruklarına ulaşmak için ihtiyaç duyduğumuz liste ve dataframe
futbolcu_uyruklari = []
uyruk_kumesi = butun_data.find_all("td",{"class": "zentriert"})

for uyruk in uyruk_kumesi:
    #find() fonksiyonunun class'ı "flaggenrahmen" ve title'ı olan veriyi bulacak
    bayrak = uyruk.find("img", {"class": "flaggenrahmen"}, {"title":True})
    #image'ın title'ında ülke isimleri mevcut
    if(bayrak != None): # We will test if we have found any matches than add them
        futbolcu_uyruklari.append(bayrak['title'])

#Futbolcu piyasa değerlerine ulaşmak için ihtiyaç duyduğumuz liste ve dataframe
futbolcu_piyasa_degerleri = []
piyasa_degeri_kumesi = butun_data.find_all("td", {"class": "rechts hauptlink"})


for piyasa_degeri in piyasa_degeri_kumesi:
    #piyasa değeri kümesinin içinde bulunan veri string formatında. String çekip sayısal değer haline getirmeli
    #£ sembolünü düşürüp milyon anlamına gelen m'i 0000 ile ve bin anlamına gelen Th'i 000 değiştirdim
    text_pd = piyasa_degeri.text
    text_pd = text_pd.replace("£", "").replace("m","0000").replace("Th", "000").replace(".", "")
    #texti floata çevirip liseteye kaydettim
    futbolcu_piyasa_degerleri.append(float(text_pd))

#Futbolcu mevkilerine ve forma numaralarına ulaşmak için ihtiyaç duyduğumuz liste ve dataframe
mevki_kumesi = butun_data.find_all("td", {"class": "rueckennummer"})
mevkiler = []
forma_numaralari = []

for data in mevki_kumesi:
    #iki veriyide aynı kümede bulabiliyoruz, mevkiler title'da forma numaraları ise text
    mevkiler.append(data["title"])
    forma_numaralari.append(data.text)


#oyuncu yaşlarını almak için iki operasyona ihtiyaç duydum çünkü tablonun içinde odd ve even olarak 
#iki class altında saklanmış durumdaydı
even_data_kumesi = butun_data.find_all("tr",{"class": "even"})
even_yaslar = []
for data in even_data_kumesi:
    temp = data.find("td", {"class": "zentriert"}, title = False, img = False)
    even_yaslar.append(temp.text)

odd_data_kumesi = butun_data.find_all("tr",{"class": "odd"})
odd_yaslar = []
for data in odd_data_kumesi:
    temp = data.find("td", {"class": "zentriert"}, title = False, img = False)
    odd_yaslar.append(temp.text)

#odd ve even'ı bir araya getirdim
yas = []
for i in range(0,16):
    yas.append(odd_yaslar[i])
    yas.append(even_yaslar[i])

#veriden doğum tarihlerini ayıklayıp listeye atttım
yaslar = []
for b in yas:
    result = b[b.find('(')+1:b.find(')')]
    yaslar.append(float(result))
    

df = pd.DataFrame({"Forma Numarası": forma_numaralari,"İsim":futbolcu_isimleri,"Yaş": yaslar, "Piyasa Değeri":futbolcu_piyasa_degerleri,"Uyruk":futbolcu_uyruklari, "Mevki": mevkiler})


#Yaş ve piyasa değeri araştırması 

df = df.sort_values('Yaş', ascending = False)

df.plot(x ='Yaş', y='Piyasa Değeri', kind = 'scatter')

print(df.head())


