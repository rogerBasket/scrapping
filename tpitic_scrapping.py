from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import string

driver = webdriver.Firefox()
driver.get('https://www.tpitic.com.mx/clientes/sitio2015/cotizacliente.php')

'''
select_origen = Select(driver.find_element_by_id('ofiori'))
select_origen.select_by_value('GDL')

select_destino = Select(driver.find_element_by_id('dest'))
select_destino.select_by_value('TLA')
'''

select_origen = Select(driver.find_element_by_id('ofiori'))
for option in select_origen.options:
    if 'IZTAPALAPA' in string.upper(option.text):
        option.click()
        break

select_destino = Select(driver.find_element_by_id('dest'))
for option in select_destino.options:
    if 'GUADALAJARA' in string.upper(option.text):
        option.click()
        break

input_largo = driver.find_element_by_id('inputLar')
input_largo.clear()
input_largo.send_keys('1')

input_ancho = driver.find_element_by_id('inputAnc')
input_ancho.clear()
input_ancho.send_keys('1')

input_alto = driver.find_element_by_id('inputAlt')
input_alto.clear()
input_alto.send_keys('1')

input_volumen = driver.find_element_by_id('inputVolM3')
input_volumen.clear()
input_volumen.send_keys('1.0')

boton_cotizar = driver.find_element_by_id('submitRealizarCotizacion')
boton_cotizar.click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@name="retotal"]'))
)

html = BeautifulSoup(driver.page_source, 'html.parser')

resultados = {}

resultados['subtotal'] = html.find('input', {'name': 'resubtotal'}).attrs['value']
resultados['iva'] = html.find('input', {'name': 'reiva'}).attrs['value']
resultados['total'] = html.find('input', {'name': 'retotal'}).attrs['value']

print resultados
