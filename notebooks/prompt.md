create a streamlit application that uses google sheets as a database which should be authenticated using oauth during the first page and check for chit_fund_db excel file. if it is already available use the existing and if not available create new file and the datamodel should be atomic and follow typical acid properties. once authenticated, store the auth token in session state and browser cookies/local storage to prevent multiple re authentication in the browser. once authenticated the application is 3 stage application 

stage 1:
creating new chit fund entry form:
    1. user need to input the chit name, description, chit type(method 1, method 2)(Note currently only method 1 implementation is available in chitfund analyzer module, method 2 will be implemented in future), total bid amount, total installments, chit frequency per year, first bid/installment date  . validate all inputs using pydantic models.
existing chit fund update/analysis:
    1. check the chit fund names from the google sheets and display as dropdown. once user selects the chit fund name fetch all the details basic chit details and previous installment details from the google sheets and 
stage 2:
    next input is to update the previous installments paid till date if the first installment date is <= today. display a table with previous installment numbers, installment dates as table that needs to be updated as input fields with its status. validate the inputs using pydantic models(make sure installment amount will not be <60% of winner installment amount) and update the config session state and push it to google sheets

stage 3:
    This is the analysis stage where user can input the bid amount and the current installment/bid number for current installment and click on analyze button to get the insight results, plots displayed on the page. Also Add a scenario analysis to perform IRR analysis of various bids between user input min and max bid amount and provide necessary plots and table for various bid amounts, also provide an option to download the report as excel file which should have all the configuration details and results in a formatted way.
    show necessary plots and tables for the analysis that you feel is necessary for the user to take decision on bidding.

Guidelines:
- First step is to make a plan, design, implementation document for the application covering all the above points in detail.
- please find the google oauth credentials in the oauth_credentials.json
- Analyze and Use the chit fund analyzer package for all calculations which is the core engine.
- Use Streamlit for the web application framework.
- Use Pydantic for data validation and settings management.
- Use Google Sheets API for database operations, ensuring proper OAuth authentication.
- Ensure the data model adheres to ACID properties for reliability.
- Structure the application into clear stages as described.
- Provide user-friendly error messages and input validations.
- make the application more modular ,maintainable, less code, easy to extend and configurable in future.
- use clean code practices and add comments where necessary.
- organize the code and scripts into appropriate files and directories.
- ensure the application is responsive and works well on different devices.
- test the application thoroughly to ensure all functionalities work as expected.

