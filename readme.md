# AIDAVA Synthetic Master Data Generator

This simple Python script generates synthetic data for the master data tables in the AIDAVA schema. 

The database includes five main tables: 

- HealthcareOrganization
- HealthcarePersonnel
- Person
- ServiceDepartment
- Address. 

The script respects specified cardinality rules based on the Master Data schema [here](https://app.diagrams.net/#G1A9SWzA7fHmuCGt3QRDpzchrkbGse1_Bs#%7B%22pageId%22%3A%22h3iYOIc2TPLAYFRuhsep%22%7D)
and creates realistic, interconnected data suitable for testing or development purposes.


## Overview

The synthetic data models a basic structure of healthcare organizations, including their departments, personnel, and associated addresses, focusing on European countries (Netherlands, Austria, Estonia). Each healthcare organization is linked to service departments, healthcare personnel (who are also represented in the Person table), and addresses. The script ensures realistic data patterns, such as appropriate names, addresses, and email formats for the specified regions.

## Tables and Relationships

- **HealthcareOrganization**: Main table representing healthcare organizations.
- **HealthcarePersonnel**: Contains healthcare personnel, linked to organizations.
- **Person**: Inherits from HealthcarePersonnel, adding personal information.
- **ServiceDepartment**: Represents departments within an organization, linked to it.
- **Address**: Contains address details, used by organizations and departments.

## How to Use

1. **Prerequisites**: Ensure you have Python 3.10 installed on your system and the libraries detailed in `requirements.txt`.

Note:It is recommended you setup a virtual environment to run the script (e.g. venv)

    ```bash
    pip install -r requirements.txt
    ```

2. **Running the Script**: Navigate to the directory containing the script and run it using Python:

    ```bash
    python synthetic_master_data_generator.py
    ```

3. **Outputs**: The script generates a CSV file for each table, containing the synthetic data. The files are saved in the `data` directory.

4. **Customization**: You can modify the script to adjust the volume of data generated or to focus on specific countries or data patterns. The sections for generating each table can be customized individually.

## Customization Tips

- **Countries**: To generate data for different countries, modify the `country_code` selections and the `locales` dictionary in the `generate_address` function.
- **Data Volume**: Adjust the range values in the loops for generating entities to increase or decrease the amount of data generated.
- **Data Patterns**: The `Faker` library offers extensive options for customizing the generated data. Consult the [Faker documentation](https://faker.readthedocs.io/en/master/) for more details.
- **Variations**: The variations_helpers.py script introduces duplicates with slight variations to the data sets, for example changing the DOB or removing the postcode from an address

## Note

This script is intended for generating synthetic data for development and testing purposes. 

The generated data is not real and should not be used for any production purposes.

