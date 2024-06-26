from  DTOs.numberify import NumberifyDTO

import requests
from bs4 import BeautifulSoup
import json
import os
import re



regexCode = r'[\+]?[\s\([0-9\)]*\d[0-9\-\s]*\d' # for all numbers in text
generationRegexCode = rf'[\+]#exactCallingCode##exactExtraCode#(\s?[0-9]\s?0?)#extraNumberLength#' # for special country
numberExtraCodeRegexCode = r'\(?[0-9\(\)\/]+'

exactCallingCode = ''
exactExtraCode = ''
extraNumberLength = ''
numberifies = []
text = """ Yalnızlıkla dolu bir gecede, telefonumun ekranında beliren numaralar yüreğimi yerinden oynatmıştı. +61 2 1234 5678, +86 10 1234 5678, +1 (555) 123-4567, +994 55 555 55 55,    10 225 35 15, +994 050 343 33 11 , +994 55 555 55 55 numaraları... Hepsi birer umut ışığı gibi parlamıştı karanlık odamda. Gözlerim hızla numaraları okurken, kalbim fısıldıyordu: "Acaba kim?"

Birkaç kez nefes alıp verdim, cesaretimi toplamak için. Sonra, titrek bir el ile bir numarayı tuşlamaya başladım. Her tuşa bastığımda kalbim biraz daha hızlanıyor, heyecanla doluyordum. Sanki birinin sesini duymak, onunla konuşmak bana gerçeklik duygusunu yeniden kazandırıyordu.

Çağrı tonları, kalbimin ritmiyle ahenk oluşturuyordu. Ve sonra, karşımdaki ses... O sıcak, tanıdık ses. O an içimde bir şeyler kıpırdandı, belki de umut.

"Merhaba," dedi o ses, "Sizi düşünüyordum."

Sanki o cümle ile dünyalar değişti. O an, göğsümde bir sıcaklık hissettim. O ses, sanki yıllardır kayıp olan bir parçayı bulmuş gibiydi. Ve şimdi, o parçayı yerine yerleştirecek kadar cesaretim vardı.

Telefonun diğer ucunda, yüreğimi dinleyerek konuştum. Sımsıcak bir sohbetin içinde kaybolduk, geçmişin acılarına rağmen. Her sözde, umut yeşeriyordu içimde.

Ve o an, telefonun diğer ucundaki ses, bana ait olmak için mi yoksa sadece bir anlık mı olduğuna karar vermeye çalışırken, kalbimin derinliklerinde bir şeyler hissettim. Belki de aşkın, karanlığın içinde bile umut ışığı olabileceğini anladım.

Sonunda, o numaralar artık sadece telefon numaraları değildi. Onlar, yüreğimdeki sesin, umudun ve belki de aşkın ta kendisiydi.

Telefonumun kaydettiği diğer numaralara baktığımda, o anın özel olduğunu hissettim. O numaralar, başka hiçbir numaraya benzemiyordu. Onlar, benim umut ışığımın, yalnızlığımı aydınlatan tek ışık gibiydi. """



def scrape_table_to_json(url):
    # Fetch HTML content
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find the table
        table = soup.find('table')

        if table:
            
            for row in table.find_all('tr'):
                # Extract table cells
                country = row.select('td:nth-child(1)')
                callingCode = row.select('td:nth-child(2)')
                numberSize = row.select('td:nth-child(5)')

                numberify = NumberifyDTO()

                isUsed = False

                if country: 
                    numberify.Country = [a.text.strip() for a in country]
                    isUsed = True
                if callingCode: 
                    numberify.CallingCode =  [a.text.strip() for a in callingCode]
                    isUsed = True
                if numberSize: # this side must be refactor
                    numberLength = [a.text.strip() for a in numberSize][0].split('digits')[0].strip()
                    numberify.NumberLength = numberLength

                    numbers = re.findall(numberExtraCodeRegexCode,numberify.NumberLength)


                    for number in numbers:
                        if str.__contains__(number,')'):
                            number =  number.replace(')','').replace('(','')
                            numberify.ExtraCode = number 
                            if str.__contains__(number,'/'):
                                numberify.ExtraCode =  number.replace('/',',')
                        numberify.NumberLength = number

                    print(numberLength)

                    if str.__contains__(numberLength,'to'):
                        numberify.NumberLength = numberLength.replace('to',',').replace(' ','')
                    
                    isUsed = True

                if isUsed: numberifies.append(numberify)

            json_data = json.dumps([obj.__dict__ for obj in numberifies], indent=4)

            return json_data
        else:
            return "No table found on the webpage."
    else:
        return "Failed to fetch webpage. Status code: {}".format(response.status_code)


json_data = scrape_table_to_json('https://www.iban.com/dialing-codes')

file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'text.txt')

with open(file_path, 'w') as file:
    file.write(json_data)


user_exactCountry = input("Enter a Country: ")

for numberify in numberifies:
    if numberify.Country[0] == user_exactCountry:
        exactCallingCode = numberify.CallingCode[0]
        extraNumberLength = f'{{{numberify.NumberLength}}}'
        exactExtraCode = numberify.ExtraCode
        print(numberify.CallingCode[0])

generationRegexCode = generationRegexCode.replace('#exactCallingCode#',exactCallingCode)
generationRegexCode = generationRegexCode.replace('#exactExtraCode#',exactExtraCode)
generationRegexCode = generationRegexCode.replace('#extraNumberLength#',extraNumberLength)

print(generationRegexCode)

for match in re.finditer(generationRegexCode, text):
    # Eşleşen değerleri yazdır
    print("Tam Eşleşme:", match.group(0))
    print("Ülke Kodu:", match.group(1))