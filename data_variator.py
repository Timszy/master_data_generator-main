import pandas as pd
from variation_helpers import introduce_variations, address_variation, person_variation, organization_name_variation, email_variation, department_name_variation, export_duplicate_registry
# When data already exists, we can introduce variations to existing records to create a more diverse dataset.
# Load existing CSV files
# addresses = pd.read_csv('Data_source/Sample_35_train/train_data/Address.csv').to_dict('records')
# healthcare_organization = pd.read_csv('Data_source/Sample_35_train/train_data/HealthcareOrganization.csv').to_dict('records')
# service_department = pd.read_csv('Data_source/Sample_35_train/train_data/ServiceDepartment.csv').to_dict('records')
# persons = pd.read_csv('Data_source/Sample_35_train/train_data/Person.csv').to_dict('records') 
# healthcare_personnel = pd.read_csv('Data_source/Sample_35_train/train_data/HealthcarePersonnel.csv').to_dict('records')
# contact_points = pd.read_csv('Data_source/Sample_35_train/train_data/ContactPoint.csv').to_dict('records')

addresses = pd.read_csv('Data_source/Sample_15_test/sample_data/Address_s.csv').to_dict('records') 
healthcare_organization = pd.read_csv('Data_source/Sample_15_test/sample_data/HealthcareOrganization_s.csv').to_dict('records')
service_department = pd.read_csv('Data_source/Sample_15_test/sample_data/ServiceDepartment_s.csv').to_dict('records')
persons = pd.read_csv('Data_source/Sample_15_test/sample_data/Person_s.csv').to_dict('records') 
healthcare_personnel = pd.read_csv('Data_source/Sample_15_test/sample_data/HealthcarePersonnel_s.csv').to_dict('records')
contact_points = pd.read_csv('Data_source/Sample_15_test/sample_data/ContactPoint_s.csv').to_dict('records')

##################
noise_severity = "high"
##################
# Apply additional variations (with a smaller rate to avoid overwhelming the dataset)
print("Adding more variations to the dataset...")
dupe_addresses = introduce_variations(addresses, address_variation, variation_rate=0.8, entity_type='Address', noise=noise_severity)

dupe_healthcare_organization = introduce_variations(healthcare_organization, organization_name_variation, variation_rate=0.8, entity_type='HealthcareOrganization', noise=noise_severity)

dupe_service_department = introduce_variations(service_department, department_name_variation, variation_rate=0.8, entity_type='ServiceDepartment', noise=noise_severity)

dupe_persons = introduce_variations(persons, person_variation, variation_rate=0.8, entity_type='Person', noise=noise_severity)

dupe_healthcare_personnel = introduce_variations(healthcare_personnel, email_variation, variation_rate=0.8, entity_type='HealthcarePersonnel', noise=noise_severity)

dupe_contact_points = introduce_variations(contact_points, email_variation, variation_rate=0.8, entity_type='ContactPoint', noise=noise_severity)

# Export the updated duplicate registry
export_duplicate_registry('test_golden_standard_high.csv')

print("Additional variations applied and registered in 'train_golden_standard_duplicates.csv'")
