# Project Requirements
This document outlines the requirements of the API as understood by myself and lists any assumptions made. It also defines keywords that may be referenced later on in the document.

## Definitions

<!-- TODO: Ensure these categories do not overlap e.g. Baby cannot also be Student -->
- Baby: Person of age < 8 months
- Student: Person of occupation_type == student
- Teenager: Person of age > 10 years and < 16 years
- Child: Person of age < 18 years
- Adult: Person of age >= 18 years and <= 55 years
- Elder: Person of age > 55 years

## End-points

```markdown
[Assumption: Depending on context, "Fields" may refer to the data items to be received by the endpoint or returned by the endpoint]

1. Create Household
    Route: '/household/new'
    Type: 'POST'
    Params: 
        String: 'Housing Type' => {'Landed', 'Condominium', 'HDB'}

2. Add a family member to household
    Route: '/household/{id}/family/new'
    Type: 'POST'
    Params:
        String: 'Name'
        String: 'Gender' => {'M', 'F'} 
        [Assumption: M/F only]
        String: 'MaritalStatus' => {'Single', 'Married', 'Widowed', 'Separated', 'Divorced', 'Not Reported'}
        [Assumption: Lack of spacing between 'Marital' and 'Status' is intentional, similar assumptions made for other variables regarding spacing as referenced from assignment document]
        [Assumption: Marital Statuses conform to the following standard: https://www.singstat.gov.sg/-/media/files/standards_and_classifications/scms.ashx]
        Integer: 'Spouse'
        [Assumption: Primary key of 'Persons' table]
        [Assumption: Spouse value is not cleared on Widowed, Separated or Divorced unless the individual remarries]
        String: 'OccupationType' => {'Unemployed', 'Student', 'Employed'}
        Integer: 'AnnualIncome'
        Date: 'DOB'

3. List all households
    Route: '/household/all'
    Type: 'GET'
    Params: None
    Response Format:
        Array: [
            Object: {
                Integer: 'HouseholdId',
                String: 'HouseholdType',
                [Assumption: 'HouseholdType' assumed to refer to 'Housing Type']
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

**TODO: Add more params that are relevant**
[Assumption: "Search" for a specific household refers to a literal search, which returns all households which meet the search criteria]
4. Search for a specific household
    Route: '/household/search'
    Type: 'POST'
    Params:
        Essential (Mandatory to implement):
            String: 'HouseholdType'
            String: 'Family Member Name'
            Integer: 'Num Family Members'
            Integer: 'Num Baby'
            Integer: 'Num Child'
            Integer: 'Num Adults'
            Integer: 'Num Elder'
            Integer: 'Num Teenage Students'
            Integer: 'Total Annual Income'

        Bonus (Not critical to API):
            Integer: 'Num Male'
            Integer: 'Num Female'
            Integer: 'Num Teenager'
            Boolean: 'Has {marital_status}'
            Integer: 'Num Students'
            Integer: 'Num Unemployed'
            Integer: 'Num Employed'

        [Assumption: Search params are not given in the assignment docs. I have included a list of search params I believe are useful, especially if they are related to the grants]
    Response Format:
        Same as endpoint 3, but only inclusive of the items that match the search params
        [Assumption: Since this is a search endpoint, it returns all the households which match the params given (AND-Based Matching, i.e. all given params must match)]

5. List the households and qualifying family members of a grant disbursement
    Route: '/household/grants'
    Type: 'GET'
    Params:
        String: 'Grant Type' => {'Student Encouragement Bonus', 'Multigeneration Scheme', 'Elder Bonus', 'Baby Sunshine Grant', 'YOLO GST Grant'}
    Response Format:
        Same as endpoint 3, but only inclusive of the households and their respective qualifying members of a given grant 

```

## Schemes

```markdown
1. Student Encouragement Bonus
    Criteria:
    - At least one student with age < 16 years old
    - Households income of less than $200,000
    Qualifying:
    - All students < 16 years old
    [Assumption: The qualifying member must also be a student (not stated in assignment docs)]

**TODO: Clarify Requirements**
2. Multigeneration Scheme
    - ???

3. Elder Bonus:
    Criteria:
    - HDB Household
    - At least one member > 55 years old
    [Assumption: Conflicting information in assignment docs - "above the age of 55" and ">= 55 years old" are both stated. I am assuming this is a typo, and it should be instead "> 55 years old".]
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
```

## Database Schema

The database schema is as shown in the following diagram:

![Schema Diagram](./readme_assets/schema_diagram.png)<br>
<em>Note: person.spouse to person.id is supposed to be 1 to [0, 1] instead of 1 to 1 as it is possible for spouse to be null<em>
