from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class select_has_values(object):

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)

        all_options = element.find_elements_by_tag_name('option')

        if len(all_options) <= 1:
            return False
        else:
            return Select(element)

        '''
        element = driver.find_element(*self.locator)
        select = Select(element)
        
        selected_option = select.first_selected_option

        print selected_option.text, selected_option.get_attribute('value')

        if self.value == selected_option.get_attribute('value'):
            return False
        else:
            return select
        '''

class variable_value(object):

    def __init__(self): pass

    def __call__(self, driver):
        value = driver.execute_script('return PageStart')

        print value

        return value != 'undefined'

driver = webdriver.Firefox()
driver.get('http://www.tresguerras.com.mx/3G/cotizadorcp.php')

'''
blockUI = driver.find_element_by_css_selector('blockUI')
unblockUI = driver.find_element_by_css_selector('unblockUI')
'''

'''
for i in range(2):
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.blockUI'))
    )
'''

for i in range(2):
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
    )

WebDriverWait(driver, 10).until(
    variable_value()
)

print 'invisible'

'''
import time
time.sleep(1)
'''

input_cp_origen = driver.find_element_by_id('cpor')

print input_cp_origen.is_displayed()
print input_cp_origen.is_enabled()

'''
input_cp_origen = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, 'cpor'))
)
'''

input_cp_origen.clear()
input_cp_origen.send_keys('64000')
input_cp_origen.send_keys(Keys.RETURN)

select_origen = WebDriverWait(driver, 10).until(
    EC.staleness_of(driver.find_element(By.XPATH, '//select[@id="origen"]/option[@value="@"]'))
)

print select_origen, type(select_origen)

select_destino = WebDriverWait(driver, 10).until(
    select_has_values((By.ID, 'destino'))
)

input_cp_destino = driver.find_element_by_id('cpdes')
input_cp_destino.clear()
input_cp_destino.send_keys('54145')
input_cp_destino.send_keys(Keys.RETURN)

'''
WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.blockUI'))
)
'''

WebDriverWait(driver, 10).until(
    EC.staleness_of(driver.find_element(By.XPATH, '//select[@id="destino"]/option[@value="@"]'))
)

WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
)

input_no_bultos = driver.find_element_by_id('C_0')
input_no_bultos.clear()
input_no_bultos.send_keys('1.0')

input_peso = driver.find_element_by_id('P_0')
input_peso.clear()
input_peso.send_keys('1.0')

input_largo = driver.find_element_by_id('L_0')
input_largo.clear()
input_largo.send_keys('1.0')

input_ancho = driver.find_element_by_id('A_0')
input_ancho.clear()
input_ancho.send_keys('1.0')

input_alto = driver.find_element_by_id('T_0')
input_alto.clear()
input_alto.send_keys('1.0')

WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
)

'''
WebDriverWait(driver, 19).until(
    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.blockUI'))
)
'''

boton_cotizar = driver.find_element_by_xpath('//button[@onclick="Cotizando();"]')
boton_cotizar.click()

WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//div[@id="Cotizado"]/button[@onclick="NewQuote();"]'))
)

html = BeautifulSoup(driver.page_source, 'html.parser')

etiquetas = ['Subtotal : ', 'IVA : ', 'Total : ']

'''
columnas = html \
    .find_all('div', {'class': 'col-lg-4 col-md-4'}) \
    .table \
    .find_all('tr')
'''

cotizacion = html \
    .find_all('div', {'class': 'col-lg-4 col-md-4'})[1] \
    .find_all('table')[1]

datos_etiqueta = {}
columnas = cotizacion.find_all('tr')

for columna in columnas:
    rows = columna.find_all('td')

    if rows[0].getText() in etiquetas:
        datos_etiqueta[rows[0].getText()] = rows[1].getText()

print datos_etiqueta

'''
select_origen = WebDriverWait(driver, 10).until(
    EC.staleness_of(driver.find_element(By.ID, 'origen'))
)
'''

'''
select_origen = WebDriverWait(driver, 10).until(
    select_has_not_value((By.ID, 'origen'), '@')
)

input_cp_destino = driver.find_element_by_id('cpdes')
input_cp_destino.clear()
input_cp_destino.send_keys('54145')

select_destino = WebDriverWait(driver, 10).until(
    select_has_not_value((By.ID, 'destino'), '@')
)
'''

# print 'aqui llego'

