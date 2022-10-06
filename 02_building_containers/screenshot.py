# ---
# integration-test: false
# output-directory: "/tmp/screenshots"
# ---
# # Screenshot with headless Chromium

# In this example, we use Modal functions and the `playwright` package to screenshot websites from a list of urls in parallel.
# Please also see our [introductory guide](/docs/guide/web-scraper) for another example of a web-scraper, with more in-depth examples.
#
# You can run this example on the command line, like this:
#
# ```
# python 02_building_containers/screenshot.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
# ```
#
# This should take a few seconds then write a `/tmp/screenshots/screenshot.png` file.
# This is what the file should look like:
#
# ![screenshot](./screenshot.png)
#
# ## Setup
#
# First we import the `modal` client library:

import pathlib
import sys

import modal

stub = modal.Stub()

# ## Defining a custom image
#
# We need an image with the `playwright` Python package as well as its `chromium` plugin pre-installed.
# This requires intalling a few Debian packages, as well as setting up a new Debian repository.
# Modal lets you run arbitrary commands, just like in Docker:


image = modal.Image.debian_slim().run_commands(
    [
        "apt-get install -y software-properties-common",
        "apt-add-repository non-free",
        "apt-add-repository contrib",
        "apt-get update",
        "pip install playwright==1.20.0",
        "playwright install-deps chromium",
        "playwright install chromium",
    ],
)

# ## Defining the screenshot function
#
# Next, the scraping function which runs headless Chromium, goes to a website, and takes a screenshot.
# This is a Modal function which runs inside the remote container.


@stub.function(image=image)
async def screenshot(url):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path="screenshot.png")
        await browser.close()
        data = open("screenshot.png", "rb").read()
        print("Screenshot of size %d bytes" % len(data))
        return data


# ## Entrypoint code
#
# Let's kick it off by reading a bunch of URLs from a txt file and scrape some of those.

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) >= 2 else "https://modal.com"
    filename = pathlib.Path("/tmp/screenshots/screenshot.png")
    with stub.run():
        data = screenshot(url)
        filename.parent.mkdir(exist_ok=True)
        with open(filename, "wb") as f:
            f.write(data)
        print(f"wrote {len(data)} bytes to {filename}")
