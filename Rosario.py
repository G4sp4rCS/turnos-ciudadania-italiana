from __future__ import division
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
import sys
import time
import ConfigParser
import datetime#from datetime import datetime, date, timedelta
from datetime import datetime
import glob
import random
import numpy as np
import pyscreenshot as ImageGrab
#import captcha_final
import deathbycaptcha
from selenium.webdriver.firefox.options import Options

def horaGet():
	config = ConfigParser.RawConfigParser()
	config.read('configRosario.ini')
	horario = config.getint('horaApertura', 'horario')
	changui = config.getint('offset', 'changui')
	print ('changui = ', changui)
	print ('hora apertura', horario)
	hora_changui =      horario*3600000 - changui
	hora_arrancar = (horario-1)*3600000 + 55*60000
	res = [horario, hora_changui, hora_arrancar]
	return res

def telefonoGet():
	config = ConfigParser.RawConfigParser()
	config.read('configRosario.ini')
	res = config.get('tel', 'telefono')
	return res


def credencialesGet():
	config = ConfigParser.RawConfigParser()
	config.read('configRosario.ini')
	usuario = config.get('credenciales', 'mail')
	password = config.get('credenciales', 'psw')
	res = [usuario, password]
	return res 

def configDisplay():
	config = ConfigParser.RawConfigParser()
	config.read('configRosario.ini')
	dsp = config.getint('display', 'visible')
	display = Display(visible=dsp, size =(1366,768))
	display.start()
	return display

def configDriver():
	profile = webdriver.FirefoxProfile()
	options = Options()
	options.preferences.update({"javascript.enabled": False})
	options.preferences.update({"general.useragent.override": "Mozilla/5.0 Gecko/20100101 Firefox/66"})
	options.preferences.update({"extensions.lastPlatformVersion": "66"})
	options.preferences.update({"distribution.abut": "Mozilla Firefox"})
	driver = webdriver.Firefox(firefox_profile=profile, options=options)
	return driver

def waitForTime(hora):
	dt = datetime.now()
	actual = (dt.hour * 3600000) + (dt.minute * 60000) + (dt.second * 1000) + (dt.microsecond / 1000)
	print "hora actual:", actual / 1000,". hora a esperar:", hora / 1000
	
	espero = ((hora - actual)/1000)
	print "esperando", espero, "segundos"
	if espero > 0:
		time.sleep(espero)
		pass

def sacarLogo():
	im = ImageGrab.grab()
	area = (9,11,24,24)#(76,66,91,79)
	logo = im.crop(area)
	logo.save('logo.png')
	#print('copie el logo')

def comparaLogo():
	logo = Image.open('logo.png')
	logoref = Image.open('logoreferencia.png')
	logbytes = logo.tobytes() 
	refbytes = logoref.tobytes()
	res = hash(refbytes) == hash(logbytes)
	#print('compare logos')
	return res

def esperar():
	sacarLogo()
	offst = time.time()
	cargo = False
	while not cargo:
		sacarLogo()
		cargo = comparaLogo()
		time.sleep(0.1)
		pass

	offst = time.time() - offst
	print "ya cargo la pagina, espere: ",offst 
	return offst

def solveCaptcha(driver, area):
	esperar()
	im = ImageGrab.grab()
	im.save('scrinchot.jpeg')
	#area = (864, 122, 970, 166)#(899, 122, 999, 166)
	cap = im.crop(area)
	cap.save('catcha.png')
	var = DBCcaptcha('catcha.png')
	return  var

def DBCcaptcha(cap_name):
    usr = "#####"
    psw = "#####"
    captcha_file_name = cap_name
    timeout = 120
    client = deathbycaptcha.SocketClient(usr, psw)

    try:
        alance = client.get_balance()
        captcha = client.decode(captcha_file_name, timeout)
        if captcha:

            print "CAPTCHA %s resuelto: %s" % (captcha["captcha"], captcha["text"])

    except deathbycaptcha.AccessDeniedException:
        print('fallo login')#todo: que pruebe con otras credenciales si falla

    return captcha

def reportCaptcha(captcha):
	usr = "######"
	psw = "######"
	client = deathbycaptcha.SocketClient(usr, psw)
	client.report(captcha)

def probarCaptchaFinal(driver):
	area = (442,305,642,379)
	solucion = solveCaptcha(driver, area)
	fill_captcha_final = driver.find_element_by_id('ctl00_ContentPlaceHolder1_captchaConf') 
	fill_captcha_final.click()
	fill_captcha_final.clear()
	print "pruebo captcha:", solucion["text"]
	fill_captcha_final.send_keys(solucion["text"])
	esperar()
	element = None
	try:
		element = driver.find_element_by_id('ctl00_ContentPlaceHolder1_lnkPrint')
	except NoSuchElementException:
		try:
			element = driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnFinalConf')
		except NoSuchElementException:
			print"error fatal"
	if element.get_attribute("id") == 'ctl00_ContentPlaceHolder1_btnFinalConf':
		print("error")

		reportCaptcha(solucion["captcha"])
		#element.send_keys(Keys.ENTER)
		time.sleep(2)
		return False
		pass
	print("exito captcha")
	element.send_keys(Keys.ENTER)
	return True

def probarCaptchaLogin(driver):
	area = (860, 190, 965, 240)		#es el area donde aparece el captcha cuando haces login
	solucion = solveCaptcha(driver, area)
	logcap = driver.find_element_by_id('loginCaptcha')
	logcap.click
	logcap.clear
	logcap.send_keys(solucion["text"])#solucion
	print "pruebo captcha:", solucion["text"]
	driver.find_element_by_id('BtnConfermaL').send_keys(Keys.ENTER)
	esperar()
	element = None
	try:
		element = driver.find_element_by_id('ctl00_repFunzioni_ctl00_btnMenuItem')
	except NoSuchElementException:
		try:
			element = driver.find_element_by_id('BtnLoginKo')
		except NoSuchElementException:
			print"error fatal"
	if element.get_attribute("id") == 'BtnLoginKo':
		print("error")

		reportCaptcha(solucion["captcha"])
		#element.send_keys(Keys.ENTER)
		time.sleep(5)
		return False
		pass
	print("exito captcha")
	#element.send_keys(Keys.ENTER)
	return True
def ultimoCaptcha(driver):
	correct = False
	while not correct:
		print ('pruebo captcha final')
		correct = probarCaptchaFinal(driver)
		esperar()
		pass

	return
def LogIn(driver):
	driver.find_element_by_xpath("//*[contains(@title, 'Italiano')]").click()
	esperar()
	driver.find_element_by_name("BtnLogin").send_keys(Keys.ENTER)
	print ("Login -> click")	
	esperar()

	credenciales = credencialesGet()
	usuario = credenciales[0]
	password = credenciales[1]
	print "usuario:",usuario
	print "password:",password
	correct = False
	while not correct:
		usr_fill = driver.find_element_by_id('UserName')
		psw_fill = driver.find_element_by_id('Password')

		usr_fill.clear()
		psw_fill.clear()
		usr_fill.click()
		usr_fill.send_keys(Keys.CONTROL + "a")
		usr_fill.send_keys(usuario)
		psw_fill.click()
		psw_fill.send_keys(Keys.CONTROL + "a")
		psw_fill.send_keys(password)
		print ('pruebo Captcha')
		correct = probarCaptchaLogin(driver)
		esperar()
		pass
	return

def irReconstrCiudadana(driver):
	telefono = telefonoGet() 
	driver.find_element_by_xpath("//*[contains(@title, 'Prenota il servizio')]").click()
	print ("prenota servicio -> click")
	esperar()
	#time.sleep(5)
	#driver.find_element_by_xpath("//*[contains(@title, 'Cittadinanza')]").click()
	#print ("ciudadania -> click")
	#esperar()
	driver.find_element_by_xpath("//*[contains(@title, 'ricostruzione')]").click()
	print ("reconstruccion -> click")
	esperar()
	#input_telefono = driver.find_element_by_id('ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol1')
	boton_continua = driver.find_element_by_xpath("//*[contains(@title, 'Conferma')]").click()
	#print "telefono:",telefono
	#input_telefono.click()
	esperar()
	#input_telefono.clear()
	#input_telefono.send_keys(telefono)
	#boton_continua.click()
	return

def navergarCalendario(driver, hora_changui):

	driver.find_element_by_xpath("//*[contains(@title, 'mese precedente')]").click()
	esperar()
	mes_actual = driver.find_element_by_xpath("//*[contains(@title, 'mese successivo')]")
	print ('espero: ', hora_changui/1000)
	waitForTime(hora_changui)
	mes_actual.click()

	WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@title, 'disponibili')]"))
    ).click()
	old_page = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(@title, 'Conferma')]"))
    )
	old_page.click()
	avanzo = False
	while not avanzo:
		esperar()
		print ('trato de nuevo')
		try:
			driver.find_element_by_id('ctl00_ContentPlaceHolder1_acc_Calendario1_repFasce_ctl01_btnConferma').click()
			pass
		except NoSuchElementException:
			avanzo = True
		pass
	print('avanzo')
	esperar()
	return

if __name__ == '__main__':
	print('comenzando:...')
	horario = horaGet()

	hora = horario[0] #18:00hs hora habilitacion turnos menos unos segundos que tarda la pagina en cargar 68400000 - 3500#
	hora_changui = horario[1]
	hora_arrancar = horario[2]
	
	display = configDisplay()
	driver = configDriver()
	waitForTime(hora_arrancar)
	driver.get("##########")
	#censuro sitio porque
	#legitimamente me da miedo que me descubran que hice esto y me anulen el tramite
	LogIn(driver)
	irReconstrCiudadana(driver)

	#time.sleep(5*60)
	#driver.navigate().refresh()
	navergarCalendario(driver, hora_changui)
	ultimoCaptcha(driver)
	print ('exito turno')
	