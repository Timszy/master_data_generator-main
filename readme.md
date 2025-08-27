

## Overview

The synthetic data models a basic structure of healthcare organizations, including their departments, personnel, and associated addresses, focusing on European countries (Netherlands, Austria, Estonia). Each healthcare organization is linked to service departments, healthcare personnel (who are also represented in the Person table), and addresses. The script ensures realistic data patterns, such as appropriate names, addresses, and email formats for the specified regions.

## Tables and Relationships

- **HealthcareOrganization**: Main table representing healthcare organizations.
- **HealthcarePersonnel**: Contains healthcare personnel, linked to organizations.
- **Person**: Inherits from HealthcarePersonnel, adding personal information.
- **ServiceDepartment**: Represents departments within an organization, linked to it.
- **Address**: Contains address details, used by organizations and departments.
- **ContactPoint**: Contains contact point details, used by organizations and departments.

## Note

This script is intended for generating synthetic data for development and testing purposes. 

The generated data is not real and should not be used for any production purposes.

