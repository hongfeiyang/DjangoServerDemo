from enum import Enum
from logging import fatal
from typing import Dict, List, Union
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import re
from bs4.element import Tag
from selenium.webdriver.chrome.options import Options
from django.conf import settings
from selenium.common.exceptions import TimeoutException
import os
import json

ACT_POSTCODES = ['2617']
NSW_POSTCODES = ['2000', '2150', '2153', '2518', '2800',
                 '2640', '2899', '2340', '2650', '2290', '2444']
NT_POSTCODES = ['0870', '0820']
QLD_POSTCODES = ['4000', '4814', '4670',
                 '4870', '4680', '4740', '4226', '4350', '4825']
SA_POSTCODES = ['5000', '5014', '5700']
TAS_POSTCODES = ['7000', '7250']
VIC_POSTCODES = ['3008', '3088', '3131', '3500', '3072', '3350']
WA_POSTCODES = ['6000', '6330', '6725', '6230',
                '6701', '6798', '6531', '6430', '6743', '6714']


class BupaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BupaLocation):
            return obj.__dict__
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class BupaMedicalItem(Enum):
    MedicalExamination = 501
    ChestXRay = 502
    SerumCreatinine = 704
    HIVTest = 707
    HepatitisBTest = 708
    SyphilisTest = 712
    LiverFunctionTests = 715
    HepatitisCTest = 716
    TBScreeningTestIGRATST = 719


class BupaBookingType(Enum):
    INDIVIDUAL = 'individual'
    FAMILY = 'family'


class BupaLocation(object):
    name: str
    address: str
    postcode: str

    def __init__(self, raw_string: str = None, fallbackPostcode: str = None, jsonString=None):
        if raw_string is not None:
            splits = raw_string.split('\n')
            self.name = splits[0]
            self.postcode = splits[-1].split(' ')[-1]
            if not self.postcode.isnumeric():
                self.postcode = fallbackPostcode
            self.address = ', '.join([i.strip(',') for i in splits[1:]])

        if jsonString is not None:
            self.fromJson(jsonString)

    def __lt__(self, other):
        return self.postcode+self.name+self.address < other.postcode+other.name+other.address

    def __str__(self) -> str:
        return f'{self.name} @ {self.address}'

    def __hash__(self) -> int:
        return hash((self.name, self.address, self.postcode))

    def __eq__(self, other) -> bool:
        if not isinstance(other, BupaLocation):
            return False

        return self.name == other.name and self.address == other.address and self.postcode == other.postcode

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def fromJson(self, jsonString):
        obj = json.loads(jsonString)
        self.name = obj['name']
        self.address = obj['address']
        self.postcode = obj['postcode']


class BupaBookingChecker():

    driver: WebDriver
    bookingType: BupaBookingType
    medicalItems: List[BupaMedicalItem]
    # locations: List[BupaLocation]
    # availabilities: Dict[BupaLocation, Dict[str, List[str]]]

    def __init__(self, bookingType: BupaBookingType, medicalItems: List[BupaMedicalItem], driver: WebDriver = None) -> None:
        self.bookingType = bookingType
        self.medicalItems = [] + medicalItems
        self.driver = driver
        if driver is None:
            self._setup()
        assert self.driver is not None
        assert self.bookingType is not None
        assert self.medicalItems is not None
        assert len(self.medicalItems) > 0, 'must have at least one medical item'

    def tearDown(self):
        self.driver.close()

    def _setup(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        chrome_options.add_argument("--disable-extensions")
        # disable gpu if running on Windows with --headless option
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--no-sandbox")  # linux only
        # if you need to set this up on a server
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(os.path.join(
            settings.BASE_DIR, 'bupaBooking/utils/chromedriver'), options=chrome_options)

    def simulateSlowNetwork(self):
        self.driver.set_network_conditions(
            offline=False,
            latency=200,  # additional latency (ms)
            download_throughput=100 * 1024,
            upload_throughput=100 * 1024,
        )

    def _tryDismissCovid19Alert(self):
        try:
            a = self.driver.switch_to.alert
            a.accept()
        except:
            pass

    def _tryDismissNeedHelpPopUp(self):
        try:
            e = self.driver.find_element_by_id("lpNoThanks")
            e.click()
        except:
            pass

    def _findAvailableDates(self):

        def hasAvailableDates(tag: Tag):
            if tag.name == 'script' and tag.string is not None:
                return 'gAvailDates' in tag.string
            return False

        def transformDate(date):
            components = date.strip().split(',')
            if len(components) != 3:
                print('illegal format dates entered')
                return None
            # NOTE: add 1 to month becuase Bupa programmers dont know how to count numbers in their javascript
            return f'{components[2]}/{int(components[1])+1}/{components[0]}'

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        elements = soup.findAll(hasAvailableDates)
        if len(elements) != 1:
            exit()
        elem = elements[0]
        dates = map(lambda x: x.strip(), re.split(';|\n', elem.string))
        dates = [i for i in dates if i.startswith('gAvailSlotText')]
        # here we have the dates and number of appointments available

        # sometimes there are dates that are shown as available but have no available timeslot
        if len(dates) == 0:
            return []

        startIndex = dates[0].index('(')+1
        endIndex = dates[0].index(')')
        dates = [i[startIndex:endIndex] for i in dates]

        dates = [transformDate(i) for i in dates]

        return dates

    def _findAllTimeSlots(self):

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        def isTimeSlot(tag):
            return tag.name == 'label' and tag.parent.name == 'td'

        tags = soup.findAll(isTimeSlot)

        slots = map(lambda x: x.string, tags)

        return list(slots)

    def _findAndClickNextButton(self):
        nextButton = self.driver.find_element_by_id(
            'ContentPlaceHolder1_btnCont')
        nextButton.click()

    def _bookEarliestSlot(self, earliestDate, earliestTime):

        def findSlotButtonAndClick():
            button = self.driver.find_element_by_xpath(
                f"//input[contains(@id, 'ContentPlaceHolder1_SelectTime1_rblResults')][./parent::td/label[contains(normalize-space(text()), '{earliestTime}')]]")
            button.click()
            nextButton = self.driver.find_element_by_id(
                'ContentPlaceHolder1_btnCont')
            nextButton.click()

        self._selectOneDate(earliestDate)
        findSlotButtonAndClick()

        # NOTE: Application may throw a NotEnoughVacantTimeError if we switch dates too fast, click the
        # timeslot again to ensure the timeslot is selected before proceeding to next page
        # Bupa programmers, sigh...
        try:
            notEnoughVacantTimeError = self.driver.find_element_by_id(
                'ContentPlaceHolder1_lblErrors')
            findSlotButtonAndClick()
        except:
            pass

    def _fillInApplicantDetails(self):
        textFieldDict = {
            'ContentPlaceHolder1_txtHAPID': '26265974',
            'ContentPlaceHolder1_txtHAPID2': '26265974',
            'ContentPlaceHolder1_txtFirstName': 'Hongfei',
            'ContentPlaceHolder1_txtSurname': 'YANG',
            'ContentPlaceHolder1_txtPassportNo': 'E42338094',
            'ContentPlaceHolder1_txtPassportCountry': 'China',
            'ContentPlaceHolder1_txtDOB': '15/02/1995',
            'ContentPlaceHolder1_txtAddress1': 'U1008, 197 Castlereagh St',
            'ContentPlaceHolder1_txtAddress2': '',  # optional
            'ContentPlaceHolder1_txtSuburb': 'Sydney',
            'ContentPlaceHolder1_txtPostCode': '2000',
            'ContentPlaceHolder1_txtEmail': 'yhf19950216@gmail.com',
            'ContentPlaceHolder1_txtEmail2': 'yhf19950216@gmail.com',
            'ContentPlaceHolder1_txtMobile': '0450580215',
        }

        selectDict = {
            # must start with AU + 3 digit visa subclass
            'ContentPlaceHolder1_ddlVisaSubClass': 'AU190',
            'ContentPlaceHolder1_ddlGender': 'M',  # M, F, U
            'ContentPlaceHolder1_ddlState': 'NSW'  # Uppercase state codes eg NSW, ACT
        }

        for key, value in textFieldDict.items():
            elem = self.driver.find_element_by_id(key)
            elem.clear()
            elem.send_keys(value)

        for key, value in selectDict.items():
            elem = self.driver.find_element_by_id(key)
            elemSelect = Select(elem)
            elemSelect.select_by_value(value)

        saveButton = self.driver.find_element_by_id(
            'ContentPlaceHolder1_btnSaveChanges')
        saveButton.click()

    def _selectOneDate(self, date):
        dateInput = self.driver.find_element_by_id(
            "ContentPlaceHolder1_SelectTime1_txtAppDate")
        self._tryDismissNeedHelpPopUp()
        dateInput.clear()
        dateInput.send_keys(date)
        dateInput.send_keys(Keys.ENTER)
        self._tryWaitForBlockUISpinnerToDisappear()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@id, 'ContentPlaceHolder1_SelectTime1_divSearchResults')]/div/h2")))

    def _lookThroughAllDates(self) -> Dict[str, List[str]]:
        dates = self._findAvailableDates()

        result = {}
        for date in dates:
            self._selectOneDate(date)
            result[date] = self._findAllTimeSlots()

        return result

    def _acceptSurcharge(self):
        button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.ID, "ContentPlaceHolder1_chkAcceptSurcharge")))
        button.click()

    def _runInitialFlow(self):
        self.driver.get(
            "https://bmvs.onlineappointmentscheduling.net.au/oasis/")

        newIndividualBooking = self.driver.find_element_by_id(
            "ContentPlaceHolder1_btnInd")
        newFamilyBooking = self.driver.find_element_by_id(
            "ContentPlaceHolder1_btnFam")

        if self.bookingType == BupaBookingType.INDIVIDUAL:
            newIndividualBooking.click()
        elif self.bookingType == BupaBookingType.FAMILY:
            newFamilyBooking.click()
        else:
            fatal('booking type not registered')

        WebDriverWait(self.driver, 10).until(EC.url_contains(
            "https://bmvs.onlineappointmentscheduling.net.au/oasis/Location.aspx"))

    def _findAndClickBackButton(self):
        backButton = self.driver.find_element_by_xpath(
            "//button[contains(normalize-space(text()), 'Back')]")
        backButton.click()

    def discoverLocations(self, serialized=False) -> List[Union[BupaLocation, str]]:
        self._runInitialFlow()
        result = set()
        postcodes = set(ACT_POSTCODES + NSW_POSTCODES + VIC_POSTCODES + WA_POSTCODES +
                        SA_POSTCODES + QLD_POSTCODES + TAS_POSTCODES + NT_POSTCODES)
        for postcode in postcodes:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.ID, "ContentPlaceHolder1_SelectLocation1_txtSuburb")))
            postcodeTextField = self.driver.find_element_by_id(
                'ContentPlaceHolder1_SelectLocation1_txtSuburb')
            postcodeTextField.click()
            postcodeTextField.clear()
            postcodeTextField.send_keys(postcode)
            postcodeTextField.send_keys(Keys.ENTER)

            # wait for please wait spinner to disappear
            blockUISpinner = self.driver.find_element_by_xpath(
                "//div[contains(@class, 'blockUI')]")
            WebDriverWait(self.driver, 10).until(
                EC.staleness_of(blockUISpinner))

            location_name_query = "//tr[contains(@class, 'trlocation')]/td[contains(@class, 'tdloc_name')]/span"
            location_names = self.driver.find_elements_by_xpath(
                location_name_query)
            if len(location_names) > 0:
                result.update([BupaLocation(raw_string=loc.text, fallbackPostcode=postcode)
                               for loc in location_names])

            else:
                continue

        result = sorted(result)

        if serialized:
            return list(map(lambda x: x.toJson(), result))

        return result

    def _tryWaitForBlockUISpinnerToDisappear(self):
        try:
            blockUISpinner = self.driver.find_element_by_xpath(
                "//div[contains(@class, 'blockUI')]")
            WebDriverWait(self.driver, 10).until(
                EC.staleness_of(blockUISpinner))
        except:
            pass

    def discoverTimesForLocation(self, location: BupaLocation) -> Dict[str, List[str]]:

        self._runInitialFlow()

        postcodeTextField = self.driver.find_element_by_id(
            'ContentPlaceHolder1_SelectLocation1_txtSuburb')
        postcodeTextField.click()
        postcodeTextField.clear()
        postcodeTextField.send_keys(location.postcode)
        postcodeTextField.send_keys(Keys.ENTER)

        # wait for please wait spinner to disappear
        self._tryWaitForBlockUISpinnerToDisappear()

        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "trlocation")))

        locationElem = self.driver.find_element_by_xpath(
            f"//tr[contains(@class, 'trlocation')][td/span[contains(normalize-space(text()), '{location.name}')]]")

        locationElem.click()

        # optional alert here
        self._tryDismissCovid19Alert()

        self._findAndClickNextButton()

        WebDriverWait(self.driver, 10).until(EC.url_contains(
            'bmvs.onlineappointmentscheduling.net.au/oasis/Products.aspx'))

        for item in self.medicalItems:
            itemButton = self.driver.find_element_by_xpath(
                f"//tr[contains(@class, 'product-label')][./td/label[contains(text(), '{item.value}')]]/td/input")
            itemButton.click()

        self._findAndClickNextButton()

        try:
            WebDriverWait(self.driver, 3).until(EC.url_contains(
                'bmvs.onlineappointmentscheduling.net.au/oasis/AppointmentTime.aspx'))
        except TimeoutException:
            # handle cases where no appointment is needed, this means that this appointment center is always available
            currentUrl: str = self.driver.current_url
            applicationDetailsUrl = "bmvs.onlineappointmentscheduling.net.au/oasis/ApplicantDetails.aspx"
            if applicationDetailsUrl in currentUrl:
                return {}

        datesAndTimes = self._lookThroughAllDates()

        return datesAndTimes

        # commands for next steps
        # self._bookEarliestSlot(earliestDate, earliestTime)
        # self.fillInApplicantDetails()
        # self.findAndClickNextButton()
        # self.acceptSurcharge()
