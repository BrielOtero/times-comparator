from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import logging
from datetime import datetime
from crono_timing import CronoTiming
import argparse


def Timing(wd, url):
    times = dict()
    wd.get(url)
    time.sleep(20)

    thereAreMoreTd = True
    row = 0

    while thereAreMoreTd:
        try:
            id = wd.find_element(
                By.XPATH, f'//*[@id="row{row}"]/td[2]').text.replace('# ', '')
            start_time = wd.find_element(
                By.XPATH, f'//*[@id="row{row}"]/td[6]').text
            finish_time = wd.find_element(
                By.XPATH, f'//*[@id="row{row}"]/td[8]').text
            times[id] = CronoTiming(start_time, finish_time)
            row = row + 1
        except:
            thereAreMoreTd = False

    return times


def Scores(wd, url):
    times = dict()

    wd.get(url)
    time.sleep(30)

    thereAreMoreTd = True
    thereAreMoreColumns = True
    row = 1
    column = 2

    while thereAreMoreColumns:
        try:
            wd.find_element(f'//*[@id="main"]/div/table/thead/tr[2]/th[{column}]/a')
            column = column + 1
        except:
            thereAreMoreColumns = False


    while thereAreMoreTd:
        try:
            id = wd.find_element(
                By.XPATH, f'//*[@id="main"]/div/table/tbody/tr[{row}]/td[1]/a/span').text.replace('# ', '')
            start_time = wd.find_element(
                By.XPATH, f'//*[@id="main"]/div/table/tbody/tr[{row}]/td[2]/a').text
            finish_time = wd.find_element(
                By.XPATH, f'//*[@id="main"]/div/table/tbody/tr[{row}]/td[4]/a').text
            times[id] = CronoTiming(start_time, finish_time)
            row = row + 1
        except:
            thereAreMoreTd = False

    return times


def CompareTimes(logger, firstTime, secondTime, key):
    try:
        first_format_string = "%H:%M:%S.%f" if '.' in firstTime else "%H:%M:%S"
        second_format_string = "%H:%M:%S.%f" if '.' in secondTime else "%H:%M:%S"

        date1 = datetime.strptime(firstTime, first_format_string)
        date2 = datetime.strptime(secondTime, second_format_string)
        time_difference = date2 - date1
        logger.info(
            f'{float(time_difference.total_seconds()):8.1f} sec | {key:<5} | {firstTime:<15} | {secondTime:<15}')
    except:
        logger.info(f'ERROR: {firstTime} {secondTime}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timing', help='Timing url', default=argparse.SUPPRESS)
    parser.add_argument('--scores', help='Scores url',default=argparse.SUPPRESS)
    
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as exc:
        print(exc.message, '\n', exc.argument_name)
    
    if hasattr(args, 'timing')and hasattr(args, 'scores'):
        try:
            timing_url = args.timing
            scores_url = args.scores

            # Initialize chrome driver
            chrome_options = Options()
            chrome_options.set_capability("detach", True)
            wd = uc.Chrome(use_subprocess=True, options=chrome_options)
            wd.implicitly_wait(10)

            # Logging
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

            # Create a file handler
            handler = logging.FileHandler('times.txt')
            handler.setLevel(logging.INFO)

            # Create a custom formatter without the INFO:root: prefix
            formatter = logging.Formatter('%(message)s')

            # Set the custom formatter for the file handler
            handler.setFormatter(formatter)

            # Add the handler to the logger
            logger.addHandler(handler)

            timesTiming = Timing(wd, timing_url)
            timesScores = Scores(wd, scores_url)

            logger.info(f'-- New Times')

            logger.info(f'- Start Times\n')
            logger.info(
                f'{"Difference":<13}| {"key":<5} | {"firstTime":<15} | {"secondTime":<15}')
            for key in timesTiming:
                if key in timesScores:
                    CompareTimes(
                        logger, timesTiming[key].start_time, timesScores[key].start_time, key)
                else:
                    logger.info(f'Not pair for key {key}')

            logger.info(f'\n- Finish Times\n')
            logger.info(
                f'{"Difference":<13}| {"key":<5} | {"firstTime":<15} | {"secondTime":<15}')

            for key in timesTiming:
                if key in timesScores:
                    CompareTimes(
                        logger, timesTiming[key].finish_time, timesScores[key].finish_time, key)
                else:
                    logger.info(f'Not pair for key {key}')
                    
        except:
            print('- ERROR: Scraping webs')
    else:
        print('- ERROR: Check the params with --help or -h')


if __name__ == '__main__':
    main()
