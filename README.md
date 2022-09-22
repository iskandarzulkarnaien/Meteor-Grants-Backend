# Meteor Grants Backend API 

![Tests](https://github.com/iskandarzulkarnaien/Meteor-Grants-Backend/actions/workflows/tests.yml/badge.svg)

## Summary

This project aims to implement an API for creating households and their associated family members, with the ability to search and filter by those who are qualified to receive various government grants.

## Project Methodology

<em>Note: This section details my process for developing the app. If you wish to immediately setup the project and view the API specifications, kindly skip this section.</em>

This project was developed using the Test Driven Development methodology, with automated API tests written before the implementation of the various API endpoints.

Automated testing via GitHub actions has been setup and may be viewed under the [actions tab](https://github.com/iskandarzulkarnaien/Meteor-Grants-Backend/actions).

The project uses the Python Flask framework for routing and handling requests and uses SQLite for the database.

For testing and code cleanliness, the following libraries are used:

`tox` - Integrates with GitHub Actions to automatically run tests for Windows and Ubuntu environments

`pytest` - Testing framework for writing tests

`flake8` - Python linting tool to enforce good code style

## Project Setup

Before setting up the project, ensure you have a working installation of Python 3 on your system.

This project was developed and tested on Python 3.10.

#### Here are the instructions to setup the project:

1. Clone the project

```bash
$ git clone https://github.com/iskandarzulkarnaien/Meteor-Grants-Backend.git
```
2. Setup a python virtual environment. If you are unsure of how to do setup a virtual environment on your system, [here](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/) is a handy guide to doing so. 

```bash
# For Windows using git bash
# To create the virtual environment
$ python -m venv venv

# To activate the virtual environment
$ . venv/Scripts/activate
```
3. Setup project dependencies

```bash
$ pip install -r requirements.txt
```

4. Start the Flask web server
```bash
$ python run.py
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

The flask web server is now ready to receive HTTP requests.

<em>Note: The sqlite database has been configured to auto-setup on server start. There is no need to run any SQL scripts or database migrations</em>

## How to use this project

Once the flask web server is running, you may send HTTP requests with the appropriate verbs and data to the endpoints listed in the [API specifications](#api-endpoint-specifications).

## Running Automated Tests

Automated tests may be run through the command line

```
# Runs tests located in /tests/test_grants.py
$ pytest
```

```
# Check code-style for files in /src and /tests
$ flake8 src tests
```

```
# Automatically runs pytest and flake8
$ tox
```
The test environment has been setup to automatically create and tear down the test database on each test to ensure complete test isolation and prevent previous results from polluting other tests.

## Project Requirements
The following section outlines the requirements of the API as understood by myself and lists any assumptions made. It also defines keywords that may be referenced later on in the document or within the project code.

## Definitions
The following is a list of definitions used both in this README and within the app to refer to persons of various ages.

Note that some categories may intentionally overlap.

- Baby: Person of age < 8 months
- Student: Person of occupation_type == student
- Teenager: Person of age < 16 years
- Child: Person of age < 18 years
- Adult: Person of age >= 18 years and <= 55 years
- Elder: Person of age > 55 years

## API Endpoints Specifications

Note: Depending on context, "Params" may refer to either the data items to be received by the endpoint or returned by the endpoint

1. Create Household
    
    Route: `'/household/new'`
    
    Type: `'POST'`
    
    Params:

        String: 'Housing Type' => {'Landed', 'Condominium', 'HDB'}

2. Add a family member to household
    
    Route: `'/household/{id}/family/new'`
    
    Type: `'POST'`
    Params:
    
        String: 'Name'

        String: 'Gender' => {'M', 'F'} 
        [Assumption: M/F only]

        String: 'MaritalStatus' => {'Single', 'Married', 'Widowed', 'Separated', 'Divorced', 'Not Reported'}
        [Assumption: Lack of spacing between 'Marital' and 'Status' is intentional, similar assumptions made for other variables regarding spacing as referenced from assignment document]
        [Assumption: Marital Statuses conform to the national standard: https://www.singstat.gov.sg/-/media/files/standards_and_classifications/scms.ashx]
        
        Integer: 'Spouse'
        [Assumption: Primary key of 'Persons' table]
        [Assumption: Spouse value is not cleared on Widowed, Separated or Divorced unless the individual remarries]
        
        String: 'OccupationType' => {'Unemployed', 'Student', 'Employed'}
        Integer: 'AnnualIncome'
        Date: 'DOB'

3. List all households
    
    Route: `'/household/all'`
    
    Type: `'GET'`
    
    Params: `None`
    
    Response Format:

        Array: [
            Dictionary: {
                String: 'HouseholdType',
                [Assumption: 'HouseholdType' in assignment document assumed to refer to 'Housing Type']
                Array: 'Family Members' [
                    {
                        String: 'Name'
                        String: 'Gender'
                        String: 'MaritalStatus'
                        Integer: 'Spouse'
                        String: 'OccupationType'
                        Integer: 'AnnualIncome'
                        Date: 'DOB'
                    },
                    ...
               ]
            },
           ...
        ]


1. Search for a specific household

    Assumption: "Search" for a specific household refers to a literal search, which returns all households which meet the search criteria

    Route: `'/household/search'`
    
    Type: `'POST'`
    
    Params:
        
        String: 'HouseholdType'
        String: 'Family Member Name'
        Integer: 'Num Family Members'
        Integer: 'Num Baby'
        Integer: 'Num Child'
        Integer: 'Num Adults'
        Integer: 'Num Elder'
        Integer: 'Num Teenage Students'
        Integer: 'Total Annual Income'

        [Assumption: Search params are not given in the assignment docs. I have included a list of search params I believe are useful, especially if they are related to the grants]
    
    Response Format:
        
        Same as endpoint 3, but only inclusive of the households that match the search params. 
        
        Unlike endpoint 3, the returned family members do not include Spouse as a field as it is not included in the assignment document

        [Assumption: Since this is a search endpoint, it returns all the households which match the params given (AND-Based Matching, i.e. all given params must match)]

2. List the households and qualifying family members of a grant disbursement
    
    Route: `'/household/grants'`
    
    Type: `'GET'`
    
    Params:

        String: 'Grant Type' => {'Student Encouragement Bonus', 'Multigeneration Scheme', 'Elder Bonus', 'Baby Sunshine Grant', 'YOLO GST Grant'}

    Response Format:

        Same as endpoint 4, but only inclusive of the households and their respective qualifying members of a given grant 


## Grant Schemes

This section details the various grant schemes outlined in the assignment document and the assumptions made for each.

1. Student Encouragement Bonus

    Criteria:
    - At least one student with age < 16 years old
    - Households with income of less than $200,000
    
    Qualifying Members:
    - All students < 16 years old
    
    Assumption: The qualifying member must also be a student (not stated in assignment document)

2. Multigeneration Scheme
    
    Criteria:
    - At least one adult (18 <= age <= 55) and at least one elder (age > 55)
    - OR
    - At least one child (age < 18) and at least one elder (age > 55)
    - AND
    - Households with income of less than $150,000
    
    Qualifying Members:
    - All members of the household
    
    Assumption:
    This varies quite a bit from the exact wording of the assignment document. 
    
    Following the exact wording of "Households with either members(s) < 18 years or member(s) above the age of 55" would result in scenarios such as: a household with only one member, who is 80 years old, qualifying for the multi-generation scheme, which seems odd.
    
    The new interpretation of the API requirements as stated in this document is more in line with the current multi-generation scheme available for HDB applicants, as seen [here](https://www.hdb.gov.sg/residential/buying-a-flat/buying-procedure-for-new-flats/application/priority-schemes).

3. Elder Bonus:

    Criteria:
    - HDB Household
    - At least one member > 55 years old
    
    Assumption: Conflicting information in assignment docs - "above the age of 55" and ">= 55 years old" are both stated.
    
    I am assuming this is a typo, and it should be instead "> 55 years old".
    
    Qualifying:
    - All members > 55 years old

4. Baby Sunshine Grant
    
    Criteria:
    - At least one member < 8 months old
    
    Qualifying:
    - All members < 8 months old

5. YOLO GST Grant
    
    Criteria:
    - HDB Household
    - Total annual income < $100,000
    
    Qualifying:
    - All members

## Database Schema

The database schema is as shown in the following diagram:

![Schema Diagram](./readme_assets/schema_diagram.png)<br>
