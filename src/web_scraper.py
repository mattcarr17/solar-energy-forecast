from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os

class EnergyScraper:

    '''
    A class used to scrape data from University of Illinois Solar Farm Dashboard.

    Attributes:
    -----------
    url: str
        URL of dashboard
    directory: str, optional
        directory for scraped files to be stored in

    Methods:
    --------
    create_driver():
        Creates webdriver instance
    
    next_page():
        Moves dashboard to next page so the file for the next day can be downloaded

    download():
        Downloads file from dashboard

    download_files(start_date, end_date):
        Downloads files for all dates beginning at start_date and ending at end_date

    close_driver():
        Closes driver instance
    '''

    def __init__(self, directory=None):
        '''Initializes Selenium scraper object
        
        Parameters:
        -----------
        directory: str, optional
            Directory for files to be stored in. If no value
            is passed in, files will be stored in current directory.
        '''

        self.url = 'http://s35695.mini.alsoenergy.com/Dashboard/2a5669735065572f4a42454b772b714d3d'
        if directory:
            self.pref = {'download.default_directory': directory}
        else: 
            self.pref = {'download.default_directory': os.getcwd()}
        EnergyScraper.driver = self.create_driver()
        EnergyScraper.driver.get(self.url)
    
    def create_driver(self):
        '''Creates driver instance.
        
        Uses chromedriver_autoinstaller to create a chromedriver in current directory.
        Chromedriver is required to use Selenium with Chrome. Adds options to driver instance
        that prevent pop up window and sets directory (if passed) for which the files will
        stored in.'''

        driver = chromedriver_autoinstaller.install(cwd=True)
        options = Options() 
        options.add_argument('--headless')
        options.add_experimental_option('prefs', self.pref)
        driver = webdriver.Chrome(driver, 
                                options=options)
        return driver 

    
    def next_page(self):
        '''Clicks button on webpage to move driver to next page'''

        EnergyScraper.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/table/tbody/tr/td[2]/div/div[1]/div/div/nav/ul/li[1]/div/a[2]').click()

    def download(self):
        '''Downloads file on current page'''

        EnergyScraper.driver.find_element_by_class_name('highcharts-button').click()
        EnergyScraper.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div/table/tbody/tr/td[2]/div/div[2]/div[1]/div/div[1]/div/div/div[3]/div/div[2]').click()

    def download_files(self, start_date, end_date):
        '''Calls download and next_page methods above to download all files.
        
        User passes in both start date and end date for scraper to gather data for.
        The scraper instance will collect all data beginning at start_date and ending
        at end_date. 
        
        Parameters:
        -----------
        start_date: str, required
            The first date the scraper will collect file for (ex. February 5, 2019)
        end_date: str, required
            The last date the scraper will collect file for (ex. December 20, 2020)'''

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        date = pd.to_datetime(EnergyScraper.driver.find_element_by_class_name('highcharts-xaxis-title').text)

        days_to_end = (date - end).days
        days_to_start = (end - start).days

        for _ in range(days_to_end):
            self.next_page()

        for _ in range(days_to_start + 1):
            attempts = 0
            while attempts < 2:
                try:
                    self.download()
                    break
                except:
                    attempts += 1

            self.next_page()
        
    def close_driver(self):
        '''Closes driver instance'''

        EnergyScraper.driver.close()