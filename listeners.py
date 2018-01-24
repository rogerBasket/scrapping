from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

import traceback
import sys
import string
import re
import signal

from equivalencias import *
from exceptions import ScrappingError, DestinationError, OriginationError

TIEMPO_ESPERA = 10

config = {
    'service_args': ['--ignore-ssl-errors=true', '--ssl-protocol=any'],
}

def valida_cp(cp): pass

def cm_to_m(medida):
    medida = float(medida)

    if medida < 100.0:
        return '1.0'
    else:
        return '{:.1f}'.format(medida / 100.0)

def form_decorator(function):
    def wrapper(self, cp_origen, cp_destino, *args, **kwargs):
        try:
            valida_cp(cp_origen)
            valida_cp(cp_destino)

            args_str = []
            for a in args:
                if isinstance(a, int):
                    args_str.append(str(a))
                elif isinstance(a, float):
                    args_str.append(str(a))
                elif isinstance(a, str):
                    args_str.append(a)
                else:
                    raise RuntimeError('error al convertir datos')

            return function(self, cp_origen, cp_destino, *args_str, **kwargs)
        except Exception as exp:
            traceback.print_exception(*sys.exc_info())

            if isinstance(exp, ScrappingError):
                raise exp

            if isinstance(exp, TimeoutException):
                raise exp

            return None
        finally:
            if self.driver:
                print 'quit'

                self.driver.service.process.send_signal(signal.SIGTERM)
                self.driver.quit()

    return wrapper

class PaqueteriaEnvio(object):

    def __init__(self, *args, **kwargs):
        self.df = args[0] # data frame equivalencias
        #self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS(**kwargs)
        self.wait = WebDriverWait(self.driver, TIEMPO_ESPERA)

class PaqueteExpress(PaqueteriaEnvio):
    __URL = 'https://www.paquetexpress.com.mx/cotizador-de-envios'
    regex_precio = re.compile(r'(\s*)(\$)(\s*)([0-9]+,{0,1}[0-9]+\.{0,1}[0-9]*)(\s*$)')

    def __init__(self, *args, **kwargs):
        super(PaqueteExpress, self).__init__(*args, **kwargs)
        self.driver.get(self.__URL)

    @form_decorator
    def scrapping(self, cp_origen, cp_destino, no_piezas, peso, largo, alto, ancho):
        codigo_postal_origen = self.driver.find_element_by_id('zipcodeOrigin')
        codigo_postal_origen.clear()
        codigo_postal_origen.send_keys(cp_origen)

        element_origen = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//select[@id="sublocalityListOrigin"]/option[1]'))
        )

        select_colonia_origen = \
            Select(self.driver.find_element_by_id('sublocalityListOrigin'))
        
        select_colonia_origen.select_by_value(element_origen.get_attribute('value'))
        
        codigo_postal_destino = self.driver.find_element_by_id('zipcodeDestination')
        codigo_postal_destino.clear()
        codigo_postal_destino.send_keys(cp_destino)
        
        element_destino = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//select[@id="sublocalityDestination"]/option[1]'))
        )
        
        select_colonia_destino = \
            Select(self.driver.find_element_by_id('sublocalityDestination'))
        
        select_colonia_destino.select_by_value(element_destino.get_attribute('value'))

        boton_seguir_paso1 = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="m-button-2 m-button--flat-2"]'))
        )
        boton_seguir_paso1.click()

        input_paquetes = self.wait.until(
            EC.presence_of_element_located((By.ID, 'productParcels'))
        )
        input_paquetes.clear()
        input_paquetes.send_keys(no_piezas)

        boton_seguir_paso2 = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="pure-u-1"]'
                                                  '/div[@class="pure-u-1 pure-u-md-1-2 grid-width-hack"]'
                                                  '/button[@class="m-button m-button--flat fl-r"]'))
        )
        boton_seguir_paso2.click()

        input_peso = self.wait.until(
            EC.presence_of_element_located((By.ID, 'parcelsWeight'))
        )
        input_peso.clear()
        input_peso.send_keys(peso)

        input_largo = self.driver.find_element_by_id('parcelsLength')
        input_largo.clear()
        input_largo.send_keys(largo)

        input_ancho = self.driver.find_element_by_id('parcelsWidth')
        input_ancho.clear()
        input_ancho.send_keys(ancho)

        input_alto = self.driver.find_element_by_id('parcelsHeight')
        input_alto.clear()
        input_alto.send_keys(alto)

        boton_seguir_paso3 = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="pure-u-1"]/button[@class="m-button m-button--flat fl-r"]'))
        )
        boton_seguir_paso3.click()

        boton_cotizar = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@class="pure-u-1"]/button[@class="m-button m-button--flat fl-r"]'))
        )

        boton_cotizar.click()

        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@class="preloader-message"]'))
        )

        return self.driver.page_source

    def obtener_precio(self, cadena):
        precio = self.regex_precio.search(cadena)

        return precio

    def get_data(self, source):
        html = BeautifulSoup(source, 'html.parser')

        paquete_html = html \
            .find_all('div', {'class': 'l-tab-highlighted l-tab-row-additional-services-total'})

        for p in paquete_html:
            paquete_html = p.find('div', {'class': 'pure-u-1'}).find('strong', {'class': 'fl-r'}).getText()

        #print paquete_html

        paquete_cotizaciones = html \
            .find_all('div', {'class': 'pure-u-1 l-tab-row l-tab-row-additional-services l-underlined l-gray-back'})

        cotizaciones = []
        for paquete_cotizacion in paquete_cotizaciones:
            cotizaciones.append(
                paquete_cotizacion.find('div', {'class': "pure-u-1-3 m-regular-content right-aligned"}).getText())

        paquete_html = self.obtener_precio(paquete_html)

        for i, cotizacion in enumerate(cotizaciones):
            cotizaciones[i] = self.obtener_precio(cotizacion)

        iva, subtotal = [c.group(2) + ' ' + c.group(4) for c in cotizaciones]
        total = paquete_html.group(2) + ' ' + paquete_html.group(4)

        return total, iva, subtotal

class Pitic(PaqueteriaEnvio):
    __URL = 'https://www.tpitic.com.mx/clientes/sitio2015/cotizacliente.php'

    def __init__(self, *args, **kwargs):
        super(Pitic, self).__init__(*args, **dict(kwargs, **config))
        self.driver.get(self.__URL)

    @form_decorator
    def scrapping(self, cp_origen, cp_destino, no_piezas, peso, largo, alto, ancho):
        # print self.driver.page_source

        largo = cm_to_m(largo)
        alto = cm_to_m(alto)
        ancho = cm_to_m(ancho)

        volumen = str(float(largo)*float(alto)*float(ancho))

        fila_origen = self.df[self.df['c.p'] == cp_origen]
        origen = fila_origen[PITIC].values[0]

        fila_destino = self.df[self.df['c.p'] == cp_destino]
        destino = fila_destino[PITIC].values[0]

        origen_unicode = origen.decode('utf-8')
        destino_unicode = destino.decode('utf-8')

        '''
        print origen, destino
        print largo, alto, ancho
        '''

        origen_flag = False
        destino_flag = False

        select_origen = Select(self.driver.find_element_by_id('ofiori'))
        for option in select_origen.options:
            # print 'origen', type(origen_unicode), type(option.text)
            if string.upper(origen_unicode) == string.upper(option.text):
                option.click()
                origen_flag = True
                break

        select_destino = Select(self.driver.find_element_by_id('dest'))
        for option in select_destino.options:
            # print 'destino', type(destino_unicode), type(option.text)
            if string.upper(destino_unicode) == string.upper(option.text):
                option.click()
                destino_flag = True
                break

        if not origen_flag:
            raise OriginationError()

        if not destino_flag:
            raise DestinationError()

        #input_largo = self.driver.find_element_by_id('inputLar')
        input_largo = self.wait.until(
            EC.presence_of_element_located((By.ID, 'inputLar'))
        )
        input_largo.clear()
        input_largo.send_keys(largo)

        input_ancho = self.driver.find_element_by_id('inputAnc')
        input_ancho.clear()
        input_ancho.send_keys(ancho)

        input_alto = self.driver.find_element_by_id('inputAlt')
        input_alto.clear()
        input_alto.send_keys(alto)

        input_volumen = self.driver.find_element_by_id('inputVolM3')
        input_volumen.clear()
        input_volumen.send_keys(volumen)

        boton_cotizar = self.driver.find_element_by_id('submitRealizarCotizacion')
        boton_cotizar.click()

        self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="retotal"]'))
        )

        #print self.driver.page_source

        return self.driver.page_source

    def get_data(self, source):
        html = BeautifulSoup(source, 'html.parser')

        subtotal = html.find('input', {'name': 'resubtotal'}).attrs['value']
        iva = html.find('input', {'name': 'reiva'}).attrs['value']
        total = html.find('input', {'name': 'retotal'}).attrs['value']

        return total, iva, subtotal

class Castores(PaqueteriaEnvio):
    __URL = 'http://www.castores.com.mx/cotizador/'
    __NOT_FOUND = 'NINGUNA COINCIDENCIA'

    def __init__(self, *args, **kwargs):
        super(Castores, self).__init__(*args, **kwargs)
        self.driver.get(self.__URL)

    @form_decorator
    def scrapping(self, cp_origen, cp_destino, no_piezas, peso, largo, alto, ancho):
        fila_origen = self.df[self.df['c.p'] == cp_origen]
        origen = fila_origen[CASTORES].values[0].decode('utf-8')

        fila_destino = self.df[self.df['c.p'] == cp_destino]
        destino = fila_destino[CASTORES].values[0].decode('utf-8')

        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
        )

        frame_cotizador = self.wait.until(
            EC.presence_of_element_located((By.ID, 'iframe_cotizador'))
        )
        
        self.driver.switch_to.frame(frame_cotizador)

        '''
        frame_cotizador = self.wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe_cotizador'))
        )
        '''

        input_origen = self.driver.find_element_by_id('txtOrigen')
        input_origen.clear()
        input_origen.send_keys(origen)
        #input_origen.send_keys('MEXICO')

        '''
        input_origen.send_keys(Keys.RETURN)

        input_value_origen = self.driver.find_element_by_id('idtxtOrigen')
        print input_value_origen.get_attribute('value')

        raise Exception()
        '''

        autocomplete_origen = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="ui-id-2"]/li[@class="ui-menu-item"]/a'))
        )

        if string.upper(autocomplete_origen[0].text) == self.__NOT_FOUND:
            raise OriginationError()
        else:
            autocomplete_origen[0].click()

        input_destino = self.driver.find_element_by_id('txtDestino')
        input_destino.clear()
        input_origen.send_keys(destino)
        #input_destino.send_keys('ACAPULCO')

        autocomplete_destino = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//ul[@id="ui-id-1"]/li[@class="ui-menu-item"]/a'))
        )

        if string.upper(autocomplete_destino[0].text) == self.__NOT_FOUND:
            raise DestinationError()
        else:
            autocomplete_destino[0].click()

        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
        )

        input_piezas = self.driver.find_element_by_id('txtPiezas')
        input_piezas.clear()
        input_piezas.send_keys(no_piezas)

        input_peso = self.driver.find_element_by_id('txtPeso')
        input_peso.clear()
        input_peso.send_keys(peso)

        input_largo = self.driver.find_element_by_id('txtLargo')
        input_largo.clear()
        input_largo.send_keys(largo)

        input_alto = self.driver.find_element_by_id('txtAlto')
        input_alto.clear()
        input_alto.send_keys(alto)

        input_ancho = self.driver.find_element_by_id('txtAncho')
        input_ancho.clear()
        input_ancho.send_keys(ancho)

        select_empaque = Select(self.driver.find_element_by_id('cmbEmpaque'))
        select_empaque.select_by_value('1027') # tipo de empaque, bolsas

        input_contenido = self.driver.find_element_by_id('txtContenido')
        input_contenido.clear()
        input_contenido.send_keys('zapatos') # contenido del empaque

        autocomplete_contenido = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'ui-id-3'))
        )

        #input_contenido.send_keys(Keys.ARROW_DOWN)
        input_contenido.send_keys(Keys.ENTER)

        self.wait.until(
            EC.invisibility_of_element_located((By.ID, 'ui-id-3'))
        )

        self.driver.execute_script('return siguientePaso();')

        '''
        boton_cotizar = self.driver.find_element_by_xpath('//button[@onclick="siguientePaso();"]')
        boton_cotizar.click()
        '''

        link_importes = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@onclick="cargaPasoTab(2);"]'))
        )

        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
        )

        '''
        tab_importe = self.wait.until(
            EC.visibility_of_element_located((By.ID, 'tabDatosImporte'))
        )
        '''

        return self.driver.page_source

    def get_data(self, source):
        html = BeautifulSoup(source, 'html.parser')

        subtotal = html \
            .find('td', {'class': 'importe', 'id': 'previosubtotal'}).getText()

        iva = html \
            .find('td', {'class': 'importe', 'id': 'previoiva'}).getText()

        total = html \
            .find('td', {'class': 'importe', 'id': 'previototal'}).getText()

        return total, iva, subtotal

class Tresguerras(PaqueteriaEnvio):
    __URL = 'http://www.tresguerras.com.mx/3G/cotizadorcp.php'

    class variable_value(object):

        def __init__(self): pass

        def __call__(self, driver):
            value = driver.execute_script('return PageStart')

            return value != 'undefined'

    class select_has_values(object):

        def __init__(self, locator):
            self.locator = locator

        def __call__(self, driver):
            element = driver.find_element(*self.locator)

            all_options= element.find_elements_by_tag_name('option')

            if len(all_options) <= 1:
                return False
            else:
                return Select(element)

    def __init__(self, *args, **kwargs):
        super(Tresguerras, self).__init__(*args, **kwargs)
        self.driver.get(self.__URL)

    @form_decorator
    def scrapping(self, cp_origen, cp_destino, no_piezas, peso, largo, alto, ancho):
        largo = cm_to_m(largo)
        alto = cm_to_m(alto)
        ancho = cm_to_m(ancho)

        for i in range(2):
            self.wait.until(
                EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
            )

        self.wait.until(
            Tresguerras.variable_value()
        )

        input_cp_origen = self.driver.find_element_by_id('cpor')
        input_cp_origen.clear()
        input_cp_origen.send_keys(cp_origen)
        input_cp_origen.send_keys(Keys.RETURN)

        select_origen = self.wait.until(
            EC.staleness_of(self.driver.find_element(By.XPATH, '//select[@id="origen"]/option[@value="@"]'))
        )

        select_destino = self.wait.until(
            Tresguerras.select_has_values((By.ID, 'destino'))
        )

        input_cp_destino = self.driver.find_element_by_id('cpdes')
        input_cp_destino.clear()
        input_cp_destino.send_keys(cp_destino)
        input_cp_destino.send_keys(Keys.RETURN)

        self.wait.until(
            EC.staleness_of(self.driver.find_element(By.XPATH, '//select[@id="destino"]/option[@value="@"]'))
        )

        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
        )

        input_no_bultos = self.driver.find_element_by_id('C_0')
        input_no_bultos.clear()
        input_no_bultos.send_keys(no_piezas)

        input_peso = self.driver.find_element_by_id('P_0')
        input_peso.clear()
        input_peso.send_keys(peso)

        input_largo = self.driver.find_element_by_id('L_0')
        input_largo.clear()
        input_largo.send_keys(largo)

        input_ancho = self.driver.find_element_by_id('A_0')
        input_ancho.clear()
        input_ancho.send_keys(ancho)

        input_alto = self.driver.find_element_by_id('T_0')
        input_alto.clear()
        input_alto.send_keys(alto)

        self.wait.until(
            EC.invisibility_of_element_located((By.XPATH, '//div[@class="blockUI blockMsg blockPage"]'))
        )

        boton_cotizar = self.driver.find_element_by_xpath('//button[@onclick="Cotizando();"]')
        boton_cotizar.click()

        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[@id="Cotizado"]/button[@onclick="NewQuote();"]'))
        )

        # print self.driver.page_source

        return self.driver.page_source

    def get_data(self, source):
        html = BeautifulSoup(source, 'html.parser')

        total = 'Total : '
        iva = 'IVA : '
        subtotal = 'Subtotal : '

        etiquetas = [subtotal, iva, total]

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

        return datos_etiqueta[total], datos_etiqueta[iva], datos_etiqueta[subtotal]
