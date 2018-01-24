from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver = webdriver.Firefox()
driver.get('http://www.castores.com.mx/cotizador/')

frame_cotizador = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'iframe_cotizador'))
)

#driver.switch_to_frame(frame_cotizador)
driver.switch_to.frame(frame_cotizador)

input_origen = driver.find_element_by_id('txtOrigen')
input_origen.clear()
input_origen.send_keys('mexico')

'''
autocomple_origen = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'ui-id-2'))
)
'''
autocomplete_origen = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="ui-id-2"]/li[@class="ui-menu-item"]/a'))
)

autocomplete_origen[0].click()

input_destino = driver.find_element_by_id('txtDestino')
input_destino.clear()
input_destino.send_keys('acapulco')

autocomplete_destino = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="ui-id-1"]/li[@class="ui-menu-item"]/a'))
)

autocomplete_destino[0].click()

input_piezas = driver.find_element_by_id('txtPiezas')
input_piezas.clear()
input_piezas.send_keys('1')

input_peso = driver.find_element_by_id('txtPeso')
input_peso.clear()
input_peso.send_keys('1.0')

input_largo = driver.find_element_by_id('txtLargo')
input_largo.clear()
input_largo.send_keys('100.0')

input_alto = driver.find_element_by_id('txtAlto')
input_alto.clear()
input_alto.send_keys('100.0')

input_ancho = driver.find_element_by_id('txtAncho')
input_ancho.clear()
input_ancho.send_keys('100.0')

select_empaque = Select(driver.find_element_by_id('cmbEmpaque'))
select_empaque.select_by_value('1027')

'''
autocomplete_contenido = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//li[@class="ui-menu-item"][@role="presentation"]/a[@class="ui-corner-all"]'))
)
'''

input_contenido = driver.find_element_by_id('txtContenido')
input_contenido.clear()
input_contenido.send_keys('zapatos')
#input_contenido.send_keys(Keys.RETURN)

autocomplete_contenido = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, 'ui-id-3'))
)

input_contenido.send_keys(Keys.RETURN)

WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.ID, 'ui-id-3'))
)

driver.execute_script("return siguientePaso();")

'''
#boton_cotizar = driver.find_element_by_xpath('//button[@onclick="siguientePaso();"]')
boton_cotizar = driver.find_element_by_xpath('//button[@class="btn btn-default btn-block"][@onclick="siguientePaso();"]')
boton_cotizar.click()

print boton_cotizar.text
print 'boton cotizar'
'''

link_importes = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//a[@onclick="cargaPasoTab(2);"]'))
)

import time
time.sleep(1)

tab_importea = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, 'tabDatosImporte'))
)

# print 'llego aqui, robot, visible'

html = BeautifulSoup(driver.page_source, "html.parser")

paquete_precio_subtotal = html \
    .find('td', {'class': 'importe','id': 'previosubtotal'}).getText()

paquete_precio_iva = html \
    .find('td', {'class': 'importe', 'id': 'previoiva'}).getText()

paquete_precio_total = html \
    .find('td', {'class': 'importe', 'id': 'previototal'}).getText()

print 'precio', paquete_precio_total
print 'iva, subtotal', paquete_precio_iva, paquete_precio_subtotal
