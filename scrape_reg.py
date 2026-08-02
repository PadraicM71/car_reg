# HOBBY PROJECT - VEHICLE DETAILS - reg.py


# THIS IS WORKING - BUT IT NEEDS TIDYING UP BELOW!!! its filthy!!!

# NOTE: For this web site (gov.ie) you need to use a browser automation tool that handles JavaScript. Playwright 
# is the modern recommendation, but Selenium is also common.
# i chose Playwright (Recommended)


from playwright.sync_api import sync_playwright
import time



def vehicle_reg(registration):
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False) # Set to True to run in background
        browser = p.chromium.launch(headless=True) # NEEDED FOR RENDER
        page = browser.new_page()
        
        page.goto("https://www.vehicleservices.gov.ie/cmv")

        # if Playwright cant find a label etc., its default timeout is 30 seconds
        # this default value is changed to 1 second below
        page.set_default_timeout(100000)

        # 2. Handle the Cookie Popup - Add a Cookie Clicker!
        # This looks for a button containing the word "Accept"
        try:
            # Use a specific selector or search for the text on the button
            accept_button = page.get_by_role("button", name="Use Only Essential Cookies")
        
            # Check if it's visible before clicking to avoid errors if it doesn't show
            # Wait for it! Some banners take a second to slide in. Using is_visible(timeout=5000) gives 
            # it a 5-second window to appear - changed this timing here as it appears quickly.
            if accept_button.is_visible(timeout=500):
                accept_button.click()
                print("Cookie popup accepted...")
        except Exception:
            print("No cookie popup appeared...")


        # 3: Fill the field
        # Playwright waits for the JavaScript to load the element automatically
        # page.fill("#regNumber", "04lh262") # this one has no tax - for testing
        page.fill("#regNumber", registration)
        print('Registration number inserted...')
        

        # 4. Submit the reg number:
        # Option A:
        # Click the Submit Button -     NOTE:   this would not work for me - went with option b below
        #                                       maybe try later
        # Click by the text on the button (Most reliable for these sites)
        # page.get_by_role("button", name="Search").click()
        # # OR if the button says "Submit":
        # # page.get_by_role("button", name="Submit").click()
        #
        # Option B: Press 'Enter' while inside the input field
        page.wait_for_timeout(500) # not sure if needed - play with timing - might need longer when deployed?
        # 1.  This will not work here - input field is not active on page load - use option 2 below
        # page.keyboard.press("Enter")
        # 2. Send 'Enter' specifically to that field
        page.locator("#regNumber").press("Enter")
        #
        # NOTE: might need to do it this way in the future:
        # Focus First, then Press
        # If the website has strict focus requirements (common in Angular apps), manually focus the element 
        # before using the keyboard. 
        # code:
        # page.locator("#regNumber").focus() # Explicitly focus the field
        # page.keyboard.press("Enter") # Now the keyboard 'Enter' will work because focus is set
        print('Registration number entered...')
        

        # 5. Scrape the results:
        #
        # NOTE: delay timing may be needed when deployed etc....
        # print("Delay for data load...")
        # time.sleep(1) 
        # print("Done!")
        #
        # open the extended tax tabs for Tax and NCT: (turns out i dont need to do this!)
        #                                             (this data is still in the html anyway!)
        # page.get_by_role("button", name="More Motor Tax Details").click()
        # try:
        #     page.get_by_role("button", name="More NCT Details").click()
        # except:
        #     print('No NCT tab detected...')
        #
        #
        ######### come back to this - for now use a delay timer if needed (not needed at moment)
        # (maybe use 'Motor Tax Expiry Date' as its last to load?)
        # ensue all content is fully rendered before continuing 
        # Before scraping, you must wait for a specific element that only appears on the results 
        # page (e.g., the vehicle's Make or Model) to ensure the content is fully rendered.
        # Wait for a specific element that indicates the results have appeared
        # Replace '.vehicle-details' with a real class or ID from your results page
        # page.wait_for_selector(".vehicle-details", state="visible")
        ######### come back to this - for now use a delay timer if needed
        # print("Delay for data load...")
        # time.sleep(0.5) 
        # print("Done!")
        #
        # lets scrape!
        #
        # print(page.content()) # for testing
        #
        # The "Bulletproof" Scraper Code below - uses Playwright's ability to find elements by their visible text, which is much 
        # more reliable than using CSS classes that might change.
        # Using text-based locators is usually the secret to beating those stubborn Angular and Government-style "Govie" design 
        # systems because the labels stay the same even if the code behind them changes.
        # 1. Wait for the data to fully render NOTE: not needed here - maybe after deployment etc...
        # We wait for the word 'Expiry Date' to appear anywhere on the page
        # page.get_by_text("Expiry Date", exact=False).wait_for(state="visible", timeout=10000)
        #
        # 2. List the specific labels you want to capture
        # 'ErrorTesting' was added to check for when a field was not found - just left it here - why not! no effect
        target_labels = ["Make", "Model", "Colour", "Motor Tax Expiry Date", "Current Annual Motor Tax Rate", "Tax Class", "NCT Expiry Date", "spare for testing"]
        vehicle_results = {}
        #
        for label in target_labels:
            try:
                # Find the element containing the label, then get its sibling (the value)
                # This works even if the CSS classes are weird or missing
                value = page.locator(f"dt:has-text('{label}') + dd").inner_text()
                vehicle_results[label] = value.strip()
            except:
                # Fallback: try looking for text in the next div if it's not a dt/dd list
                try:
                    value = page.get_by_text(label).locator("xpath=../..").locator(".govie-summary-list__value").inner_text()
                    vehicle_results[label] = value.strip()
                except:
                    vehicle_results[label] = "Not Applicable"
        # add registration to results
        vehicle_results['Registration'] = registration.upper()
        #
        # 3. Print your clean data
        print("\n--- Final Vehicle Data ---")
        for key, val in vehicle_results.items():
            print(f"{key}: {val}")
        #
        print('Scraping complete...')
        # scraping complete

        # input("Press Enter to quit and close window...")
    return vehicle_results



if __name__ == "__main__":
    # for testing
    reg = "191d11886"
    # reg = "251d6240"
    # reg = "11wx1679"
    # reg = "182d9116"
    # reg = "132mh699"
    # reg = "232d1880"

    print('TESTING reg.py ...')
    print('reg.py running as __main__ ...')
    print('\tdemo reg:', reg)

    print('Padraic\'s Vehicle Web App BETA - Stage 1 - THIS IS reg.py running on its own ...')
    print('Vehicle registrtation:', reg)
    lookup = vehicle_reg(reg)
    print('vehicle_reg function finished - this is the returned dict:')
    print(lookup)

# ENDS
