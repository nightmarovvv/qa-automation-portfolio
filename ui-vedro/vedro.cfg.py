import os

import vedro
import vedro_allure_reporter as allure_reporter
import vedro_playwright as playwright
from dotenv import load_dotenv

load_dotenv()


class Config(vedro.Config):

    default_scenarios_dir = "scenarios/"

    class Plugins(vedro.Config.Plugins):

        class Playwright(playwright.Playwright):
            enabled = True

        class AllureReporter(allure_reporter.AllureReporter):
            enabled = True
            report_dir = os.getenv("ALLURE_RESULTS_DIR", "allure-results")
