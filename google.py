# Web browser functionality for agents.
# The agents see the command instructions as follows:
"""
 "commands": [
                {
                    "cmd": "!google {query}",
                    "description": "Search for {query} in google. Results will be website titles as a numbered list. Index `0` of the list is a special element, and if it exists, it means google has found an answer automatically, and index `0` carries that."
                },
                {
                    "cmd": "!view {index}",
                    "description": "View the content of result at {index}. This is potentially costly."
                },
                {
                    "cmd": "!ask {index}",
                    "description": "Instead of viewing the whole page, you can ask your question to the page, and a small & less costly AI model will view the page and look for an answer. Don't do this for too complex tasks as smaller AI models may hallucinate or lose context."
                }
            ]
"""

# The commands are implemented in the following way, using selenium and chrome web browser:

from selenium import webdriver


def google(query):
    driver = webdriver.Chrome()
    driver.get(f"https://www.google.com/search?q={query}")
    results = driver.find_elements_by_css_selector(".tF2Cxc")
    google_answer = driver.find_elements_by_css_selector(".Z0LcW")
    result_list = []
    if google_answer:
        result_list.append(google_answer[0].text)
    for i, result in enumerate(results):
        result_list.append(result.text)

    def view(index):
        if index == 0:
            return result_list[0]
        driver.get(
            results[index - 1].find_element_by_css_selector("a").get_attribute("href")
        )
        return driver.page_source

    def ask(index, question):
        if index == 0:
            return result_list[0]
        driver.get(
            results[index - 1].find_element_by_css_selector("a").get_attribute("href")
        )
        result = driver.page_source
        # todo: implement a smaller AI model to answer the question
        return result

    driver.quit()
    return result_list, view, ask
