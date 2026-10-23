import os
from pathlib import Path

import pytest
import selenium.webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pretty_jupyter._resources import resource_path


@pytest.fixture()
def driver():
    # Selenium (>=4.11) locates/downloads a matching driver by itself. CHROME_BIN and
    # CHROMEDRIVER can point to a specific browser/driver when that is not possible.
    chromedriver = os.environ.get("CHROMEDRIVER")
    chrome_service = Service(chromedriver) if chromedriver else Service()

    chrome_options = Options()
    if os.environ.get("CHROME_BIN"):
        chrome_options.binary_location = os.environ["CHROME_BIN"]
    options = [
        "--headless=new",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]
    for option in options:
        chrome_options.add_argument(option)

    driver = selenium.webdriver.Chrome(service=chrome_service, options=chrome_options)

    yield driver

    driver.quit()


@pytest.fixture
def fixture_dir():
    return "tests/test_notebooks/fixture"


@pytest.fixture
def templates_path():
    return str(Path(resource_path("templates")).as_posix())


@pytest.fixture
def input_path():
    raise NotImplementedError()


@pytest.fixture
def out_path(tmpdir, input_path):
    path = str((Path(tmpdir) / f"{Path(input_path).stem}.html").absolute())

    yield path

    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def page_url(out_path):
    return os.path.normpath(f"file:/{out_path}")
