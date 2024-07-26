from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import threading


class WebDriverManager:
    def __init__(self, num_windows):
        self.driver = self._create_driver()
        self.windows = {}
        self.lock = threading.Lock()

        # Create initial window
        self.windows[0] = self.driver.current_window_handle

        # Create additional windows
        for i in range(1, num_windows):
            self.driver.execute_script("window.open('');")
            self.windows[i] = self.driver.window_handles[i]
        for window in self.driver.window_handles:
            self.driver.switch_to.window(window)
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                    Object.defineProperty(navigator, 'webself.driver', {
                        get: () => undefined
                    })
                """
                },
            )
            useragentarray = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            ]

            for i in range(len(useragentarray)):
                # Setting user agent iteratively as Chrome 108 and 107
                self.driver.execute_cdp_cmd(
                    "Network.setUserAgentOverride", {"userAgent": useragentarray[i]}
                )
                print(self.driver.execute_script("return navigator.userAgent;"))

    def _create_driver(self):
        chrome_options = ChromeOptions()
        # Add all your Chrome options here
        # ...

        # Set the user data directory to use the existing profile
        # Replace 'YourUsername' with your actual macOS username
        user_data_dir = "/Users/mirzabicer/Library/Application Support/Google/Chrome"
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # Use a specific profile (replace 'Default' with the profile name if needed)
        chrome_options.add_argument("--profile-directory=Default")

        driver = webdriver.Chrome(
            options=chrome_options,
            service=Service("/opt/homebrew/bin/chromedriver"),
        )
        # self._local.wait = WebDriverWait(driver, 10)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)
        # self._local.wait = WebDriverWait(driver, 10)

        # driver = webdriver.Chrome(
        #     options=chrome_options, service=Service("/opt/homebrew/bin/chromedriver")
        # )
        # driver.execute_script(
        #     "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        # )
        # # Set user agent and other configurations
        # # ...

        return driver

    def get_window(self, instance_id):
        with self.lock:
            # window_id = instance_id % len(self.windows)
            return self.windows[instance_id]

    def switch_to_window(self, instance_id):
        window = self.get_window(instance_id)
        self.driver.switch_to.window(window)

    def close_all(self):
        self.driver.quit()


# Create a global WebDriverManager
global_driver_manager = WebDriverManager(num_windows=6)  # Adjust the number as needed
