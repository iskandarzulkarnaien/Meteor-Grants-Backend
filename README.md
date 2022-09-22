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

`tox` - Integrates with GitHub Actions to automatically run tests for Windows and Ubuntu environments.

`pytest` - Testing framework for writing tests.

`flake8` - Python linting tool to enforce good code style.

Project Management is done via GitHub issues, with to-dos and current tasks or problems faced documented in the [Issue Tracker](https://github.com/iskandarzulkarnaien/Meteor-Grants-Backend/issues).

The project utilizes two primary working branches: `main` and `dev`. Branch protection rules have been set up to forbid direct pushes to `main`. Merging is instead performed via pull requests, which have been set up to require that all status checks pass and at least one approving review has been given (this requirement is overridden due to being the only developer for this project).

The project has also been deployed to Heroku and can be found [here](https://meteor-grants-backend.herokuapp.com/).

<em>Note: As there is no Frontend, a 404 is to be expected when visiting the URL.</em>

## Project Setup

Before setting up the project, ensure you have a working installation of Python 3 on your system.

This project was developed and tested on Python 3.10.

#### Here are the instructions to setup the project:

1. Clone the project

```bash
$ git clone https://github.com/iskandarzulkarnaien/Meteor-Grants-Backend.git
```
2. Setup a python virtual environment. If you are unsure of how to setup a virtual environment on your system, [here](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/) is a handy guide to doing so. 

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

Once the flask web server is running, you may send HTTP requests with the appropriate verbs and data to the endpoints listed in the [API specifications](#api-endpoints-specifications).

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
The following is a list of definitions used both in this README and within the app to refer to persons of various ages or occupation types.

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
        
        String[]: 'HouseholdTypes'
        String[]: 'Family Member Names'
        Integer[]: 'FamilyMembersLimits'
        Integer[]: 'NumBabiesLimits'
        Integer[]: 'NumChildrenLimits'
        Integer[]: 'NumAdultsLimits'
        Integer[]: 'NumEldersLimits'
        Integer[]: 'NumTeenageStudentsLimits'
        Integer[]: 'TotalAnnualIncomeLimits'

        [Note: 'limits' is of format [lower_limit, upper_limit]. A value of 0 indicates unbounded]
        [Example: [1, 0] represents at least one]
        [Assumption: Search params are not given in the assignment docs. I have included a list of search params I believe are useful, especially if they are related to the grants]
    
    Response Format:
        
        Same as endpoint 3, but only inclusive of the households that match the search params. 
        
        Unlike endpoint 3, the returned family members do not include Spouse as a field as it is not included in the assignment document

        [Assumption: Since this is a search endpoint, it returns all the households which match the params given (AND-Based Matching, i.e. all given params must match)]

2. List the households and qualifying family members of a grant disbursement
    
    Route: `'/household/grants'`
    
    Type: `'GET'`
    
    Params:

        String: 'GrantType' => {'Student Encouragement Bonus', 'Multigeneration Scheme', 'Elder Bonus', 'Baby Sunshine Grant', 'YOLO GST Grant'}

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

## Project Architecture

The project is structured into two main folders: `src` for source code and `tests` for test related code. Helper packages have also been defined within the respective folders for reusable shared logic.

## Database Schema

The database schema is as shown in the following diagram:

![Schema Diagram](./readme_assets/schema_diagram.png)<br>

## Helpers and Utils
Several helpers and utilities classes have been designed to facilitate in either the working functionality of the application or automated testing. The following section showcases several noteworthy classes that utilize the [Builder Design Pattern](https://refactoring.guru/design-patterns/builder).

## HouseholdBuilder / PersonBuilder
The `HouseholdBuilder` and `PersonBuilder` class facilitates modular construction of `Households` and `Persons` for testing purposes.

```python
# Example to showcase creation of household with husband and wife and two teenage students.
household = HouseholdBuilder().hdb().create_and_write()

husband = PersonBuilder(household).name('Bob').gender_male().married().employed(30000).adult().create_and_write()
wife = PersonBuilder(household).name('Alice').gender_female().married(husband).employed(30000).adult().create_and_write()
teen_student1 = PersonBuilder(household).name('Cody').student().teenager().create_and_write()
teen_student2 = PersonBuilder(household).name('Dany').student().teenager().create_and_write()
```

As a future improvement, these classes could instead be shifted to the `/src` directory and used as the exclusive method of instantiating a `person` instance. This has the effect of also resolving the [spouse-to-spouse relationship issue](#notable-issues).

## QueryBuilder
The `QueryBuilder` class facilitates the modular construction of an SQL query to search for `Households` and `Persons` from the database.

```python
# Example to showcase creation of search query for 'HDB' households with annual income less than $200,000
query = QueryBuilder().set_household_types(['HDB']).set_total_annual_income_limits([0, 200000]).generate_query()
```

## Heroku Deployment

The app has been deployed to Heroku and can be found [here](https://meteor-grants-backend.herokuapp.com/).

<em>Note: As there is no Frontend, a 404 is to be expected when visiting the URL.</em>


The deployment process involved the creation of a Procfile to start a `gunicorn` HTTP Server.

```Procfile
web: gunicorn run:app
```

The deployment initially failed due to a missing `gunicorn` import, which was difficult to debug due to Heroku returning a generic 503 error.

## Future Improvements

Some possible improvements for the future of the project are as follows:

1. More robust API endpoints (e.g. Edit, Update and Delete).
2. Better logical organization of code.
    - Some functionality can be better abstracted into their own classes or packages (`/helpers/utils.py/` and the `QueryBuilder` class is a good example of this).
3. Make the code more DRY (Do not Repeat Yourself). There are quite a few instances of repeated logic, especially within the tests, that can be extracted into their own methods and reused.
4. Stronger validations. Some sections (such as limits in search params), do not have validation to ensure that malformed data is rejected.

## Notable Issues

1. Enforcing one-to-one relationship for spouses in `Person` class.
   - Issue explained and documented as  [Issues#9](https://github.com/iskandarzulkarnaien/Meteor-Grants-Backend/issues/9) on GitHub.
