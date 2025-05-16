import pandas as pd
from variation_helpers import introduce_variations, address_variation, person_variation, organization_name_variation, email_variation, department_name_variation, export_duplicate_registry

# Load existing CSV files
addresses = pd.read_csv('testdata/address.csv').to_dict('records')
healthcare_organization = pd.read_csv('testdata/HealthcareOrganization.csv').to_dict('records')
service_department = pd.read_csv('testdata/ServiceDepartment.csv').to_dict('records')
persons = pd.read_csv('testdata/Person.csv').to_dict('records') 
healthcare_personnel = pd.read_csv('testdata/HealthcarePersonnel.csv').to_dict('records')
contact_points = pd.read_csv('testdata/ContactPoint.csv').to_dict('records')

# Apply additional variations (with a smaller rate to avoid overwhelming the dataset)
print("Adding more variations to the dataset...")
dupe_addresses = introduce_variations(addresses, address_variation, variation_rate=0.1, entity_type='Address')
dupe_healthcare_organization = introduce_variations(healthcare_organization, organization_name_variation, 
                                                   variation_rate=0.1, entity_type='HealthcareOrganization')
dupe_service_department = introduce_variations(service_department, department_name_variation, 
                                              variation_rate=0.1, entity_type='ServiceDepartment')
dupe_persons = introduce_variations(persons, person_variation, variation_rate=0.1, entity_type='Person')
dupe_healthcare_personnel = introduce_variations(healthcare_personnel, email_variation, 
                                                variation_rate=0.1, entity_type='HealthcarePersonnel')
dupe_contact_points = introduce_variations(contact_points, email_variation, variation_rate=0.1, entity_type='ContactPoint')

# Export the updated duplicate registry
export_duplicate_registry('additional_duplicates.csv')
print("Additional variations applied and registered in 'additional_duplicates.csv'")

# If you want to merge with existing golden standard:
existing_duplicates = pd.read_csv('golden_standard_duplicates.csv', encoding='latin1')
new_duplicates = pd.read_csv('additional_duplicates.csv')
all_duplicates = pd.concat([existing_duplicates, new_duplicates]).drop_duplicates()
all_duplicates.to_csv('updated_golden_standard_duplicates.csv', index=False)
print("Combined duplicate registry saved as 'updated_golden_standard_duplicates.csv'")