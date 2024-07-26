from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

from selenium.webdriver.common.keys import Keys
import time
from TaskQueue import queue_decorator
import threading

# from WebDriverPool import global_driver_pool
from DriverWindowManager import global_driver_manager
import pyperclip


# def queue_decorator(func):
#     def wrapper(*args, **kwargs):
#         method_wrapper(args[0].task_queue, func, *args, **kwargs)

#     return wrapper


class ClaudeInterface:

    _instance_count = 0

    def __init__(self):
        self.instance_id = ClaudeInterface._instance_count
        ClaudeInterface._instance_count += 1
        self.lock = threading.Lock()
        self.base_url = "https://claude.ai"
        self.current_chat_id = None
        # self.wait = None
        # self.driver = None

    # def _get_driver(self):
    #     if self.driver is None:
    #         self.driver = global_driver_pool.get_driver(self.instance_id)
    #         self.wait = WebDriverWait(self.driver, 10)
    #     return self.driver

    @queue_decorator
    def enter_to_base_url(self):
        with self.lock:
            global_driver_manager.switch_to_window(self.instance_id)
            driver = global_driver_manager.driver
            # self._get_driver()
            driver.get(self.base_url)
            # wait for it to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@contenteditable='true']")
                )
            )
        #

    def start_new_chat(self):
        try:
            new_chat_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'New chat')]")
                )
            )
            new_chat_button.click()
            self.current_chat_id = self.driver.current_url.split("/")[-1]
        except TimeoutException:
            print("Couldn't find the 'New chat' button")

    @queue_decorator
    def send_message(self, message):
        # driver = self._get_driver()
        with self.lock:
            global_driver_manager.switch_to_window(self.instance_id)
            driver = global_driver_manager.driver
            try:
                input_field = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@contenteditable='true']")
                    )
                )
                input_field.clear()
                pyperclip.copy(message)
                # input_field.send_keys(Keys.COMMAND, "v")
                # ---
                ActionChains(driver).click(input_field).key_down(
                    Keys.COMMAND
                ).send_keys("v").key_up(Keys.COMMAND).perform()
                # -----
                # input_field.send_keys(message)
                # -----
                # driver.execute_script(
                #     "arguments[0].innerHTML = arguments[1];", input_field, message
                # )
                # driver.execute_script(
                #     "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                #     input_field,
                # )

                send_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@aria-label='Send Message']")
                    )
                )
                time.sleep(1)
                send_button.click()
                # don't let go until claude has finished typing
                el = driver.find_element(
                    By.XPATH, "//button[@aria-label='Stop Response']"
                )
                while el.is_displayed():
                    time.sleep(0.1)
            except TimeoutException:
                print("Couldn't find the input field or send button")
            except (NoSuchElementException, StaleElementReferenceException):
                pass

    @queue_decorator
    def get_latest_response(self, timeout=300, check_interval=0.5):
        try:
            with self.lock:
                global_driver_manager.switch_to_window(self.instance_id)
                driver = global_driver_manager.driver
                start_time = time.time()

                print(f"Instance {self.instance_id}: Starting to get latest response")

                def claude_finished_typing():
                    try:
                        stop_button = driver.find_element(
                            By.XPATH, "//button[@aria-label='Stop Response']"
                        )
                        is_typing = (
                            stop_button.is_displayed() and stop_button.is_enabled()
                        )
                        print(
                            f"Instance {self.instance_id}: Claude is {'still typing' if is_typing else 'finished typing'}"
                        )
                        return not is_typing
                    except (NoSuchElementException, StaleElementReferenceException):
                        print(
                            f"Instance {self.instance_id}: Stop button not found, assuming Claude finished typing"
                        )
                        return True

                try:
                    WebDriverWait(driver, 5, 0.1).until(
                        lambda d: claude_finished_typing()
                    )
                except TimeoutException:
                    print(
                        f"Instance {self.instance_id}: Timed out waiting for Claude to finish typing"
                    )

                print(f"Instance {self.instance_id}: Attempting to retrieve response")

                try:
                    response_elements = WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//div[contains(@class, 'font-claude-message')]")
                        )
                    )
                    response = response_elements[-1].text
                    print(
                        f"Instance {self.instance_id}: Successfully retrieved response"
                    )
                    print(
                        f"Instance {self.instance_id}: Time taken: {time.time() - start_time:.2f} seconds"
                    )
                    return response
                except TimeoutException:
                    print(
                        f"Instance {self.instance_id}: Timed out waiting for response elements"
                    )
                except NoSuchElementException:
                    print(
                        f"Instance {self.instance_id}: Could not find response elements"
                    )
                except Exception as e:
                    print(
                        f"Instance {self.instance_id}: Unexpected error retrieving response: {str(e)}"
                    )

        except Exception as e:
            print(
                f"Instance {self.instance_id}: Error in get_latest_response: {str(e)}"
            )

        print(
            f"Instance {self.instance_id}: Failed to get response. Time taken: {time.time() - start_time:.2f} seconds"
        )
        return None

    def is_claude_typing(self):
        try:
            driver = global_driver_manager.driver
            driver.find_element(By.XPATH, "//button[@aria-label='Stop Response']")
            return True
        except NoSuchElementException:
            return False

    def upload_file(self, file_path):
        try:
            file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
            file_input.send_keys(file_path)
            print(f"File uploaded: {file_path}")
        except NoSuchElementException:
            print("Couldn't find the file upload input")

    # def close_browser(self):
    #     if self.driver is not None:
    #         self.driver.quit()

    def get_conversation_history(self):
        try:
            global_driver_manager.switch_to_window(self.instance_id)
            driver = global_driver_manager.driver
            message_elements = driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'group relative') or contains(@class, 'font-claude-message')]",
            )
            conversation = []
            for element in message_elements:
                if "font-claude-message" in element.get_attribute("class"):
                    conversation.append(("Claude", element.text))
                else:
                    conversation.append(("Human", element.text))
            return conversation
        except NoSuchElementException:
            print("Couldn't retrieve conversation history")
            return []

    def switch_to_chat(self, chat_id):
        try:
            self.driver.get(f"{self.base_url}/chat/{chat_id}")
            self.current_chat_id = chat_id
        except:
            print(f"Couldn't switch to chat with ID: {chat_id}")

    def get_active_chats(self):
        try:
            chat_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'chat-history-item')]"
            )
            chats = []
            for element in chat_elements:
                chat_id = element.get_attribute("data-testid").split("-")[-1]
                chat_title = element.find_element(
                    By.XPATH, ".//div[contains(@class, 'chat-title')]"
                ).text
                chats.append((chat_id, chat_title))
            return chats
        except NoSuchElementException:
            print("Couldn't retrieve active chats")
            return []


# claude = ClaudeInterface()
# claude.enter_to_base_url()
# # claude.start_new_chat()
# claude.send_message("Hey, can you help me with something?")
# response = claude.get_latest_response()
# print(response)

# # Input loop
# while True:
#     message = input("You: ")
#     claude.send_message(message)
#     response = claude.get_latest_response()
#     print("Claude:", response)
#     if message.lower() == "exit":
#         break

# hist = claude.get_conversation_history()
# print(hist)
# claude.close_browser()
