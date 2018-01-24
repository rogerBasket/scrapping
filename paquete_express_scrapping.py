from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import re

regex_precio = re.compile(r'(\s*)(\$)(\s*)([0-9]+\.{0,1}[0-9]*)(\s*$)')

def obtener_precio(cadena):
    precio = regex_precio.search(cadena)

    return precio

driver = webdriver.Firefox()
driver.get('https://www.paquetexpress.com.mx/cotizador-de-envios')

codigo_postal_origen = driver.find_element_by_id('zipcodeOrigin')
codigo_postal_origen.clear()
codigo_postal_origen.send_keys('57410')

try:
    element_origen = WebDriverWait(driver, 80).until(
        EC.presence_of_element_located((By.XPATH, '//select[@id="sublocalityListOrigin"]/option[1]'))
    )

    select_colonia_origen = \
        Select(driver.find_element_by_id('sublocalityListOrigin'))

    select_colonia_origen.select_by_value(element_origen.get_attribute('value'))

    codigo_postal_destino = driver.find_element_by_id('zipcodeDestination')
    codigo_postal_destino.clear()
    codigo_postal_destino.send_keys('57310')

    element_destino = WebDriverWait(driver, 80).until(
        EC.presence_of_element_located((By.XPATH, '//select[@id="sublocalityDestination"]/option[1]'))
    )

    select_colonia_destino = \
        Select(driver.find_element_by_id('sublocalityDestination'))

    select_colonia_destino.select_by_value(element_destino.get_attribute('value'))

    boton_seguir_paso1 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@class="m-button-2 m-button--flat-2"]'))
    )
    boton_seguir_paso1.click()

    # scrapping para sobres
    '''
    sobres = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'productEnvelopes'))
    )
    sobres.clear()
    sobres.send_keys('1')

    boton_seguir_paso2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@class="m-button m-button--flat fl-r"]'))
    )
    boton_seguir_paso2.click()
    '''

    paquetes = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'productParcels'))
    )
    paquetes.clear()
    paquetes.send_keys('1')

    boton_seguir_paso2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="pure-u-1"]'
                                              '/div[@class="pure-u-1 pure-u-md-1-2 grid-width-hack"]'  
                                              '/button[@class="m-button m-button--flat fl-r"]'))
    )
    boton_seguir_paso2.click()

    peso = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'parcelsWeight'))
    )
    peso.clear()
    peso.send_keys('1')

    largo = driver.find_element_by_id('parcelsLength')
    largo.clear()
    largo.send_keys('10')

    ancho = driver.find_element_by_id('parcelsWidth')
    ancho.clear()
    ancho.send_keys('10')

    alto = driver.find_element_by_id('parcelsHeight')
    alto.clear()
    alto.send_keys('10')

    boton_seguir_paso3 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="pure-u-1"]/button[@class="m-button m-button--flat fl-r"]'))
    )
    boton_seguir_paso3.click()

    boton_cotizar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="pure-u-1"]/button[@class="m-button m-button--flat fl-r"]'))
    )

    boton_cotizar.click()

    '''
    if(WebDriverWait(driver, 10).until(
        EC.element_located_selection_state_to_be((By.ID, 'check_EAD'), False)
    )):
        check = driver.find_element_by_xpath('//label[@for="check_EAD"]')
        check.click()
    '''

    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, '//div[@class="preloader-message"]'))
    )

    # print 'llego aqui, robot'

    html = BeautifulSoup(driver.page_source, 'html.parser')

    # print soup

    '''
    paquete_html = html \
        .find('div', {'class': 'pure-u-1 l-tab-row l-underlined'}) \
        .find('div', {'class': 'pure-u-8-24 m-regular-content right-aligned'}).getText()
    '''

    paquete_html = html \
        .find('div', {'class': 'l-tab-highlighted l-tab-row-additional-services-total'}) \
        .find('div', {'class': 'pure-u-1'}) \
        .find('strong', {'class': 'fl-r'}).getText()

    paquete_cotizaciones = html \
        .find_all('div', {'class': 'pure-u-1 l-tab-row l-tab-row-additional-services l-underlined l-gray-back'})


    cotizaciones = []
    for paquete_cotizacion in paquete_cotizaciones:
        cotizaciones.append(paquete_cotizacion.find('div', {'class': "pure-u-1-3 m-regular-content right-aligned"}).getText())

    paquete_html = obtener_precio(paquete_html)

    for i, cotizacion in enumerate(cotizaciones):
        cotizaciones[i] = obtener_precio(cotizacion)

    print 'precio', paquete_html.group(2) + ' ' + paquete_html.group(4)
    print 'iva, subtotal', [c.group(2) + ' ' + c.group(4) for c in cotizaciones]

finally:
    # driver.quit()
    pass

