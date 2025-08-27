from faker import Faker
import random
import csv

# This script generates synthetic healthcare data for testing purposes.
# It creates addresses, healthcare organizations, service departments, contact points, healthcare personnel, and persons
# Initialize Faker
fake = Faker()
Faker.seed(0)

# Configuration: set desired dataset sizes here
NUM_ORGANIZATIONS = 50               # number of HealthcareOrganization to create
MIN_DEPARTMENTS_PER_ORG = 5          # minimum ServiceDepartments per organization
MAX_DEPARTMENTS_PER_ORG = 10         # maximum ServiceDepartments per organization
MIN_PERSONNEL_PER_ORG = 15           # min total personnel per organization
MAX_PERSONNEL_PER_ORG = 40           # max total personnel per organization


# Function to store table data as CSV
def store_table_as_csv(data, filename):
    fieldnames = data[0].keys()
    with open(f"src/Data_Source/{filename}", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f'{filename} stored with {len(data)} records')

def generate_address(country_code):
    """
    Generate a random address for a given country code with aligned city and postal code
    """
    locales = {"NL": "nl_NL", "AT": "de_AT", "EE": "et_EE"}
    fake_locale = Faker(locales[country_code])
    
    # First generate a coherent address
    if country_code == "NL":
        # Dutch addresses: use postcode pattern and consistent city
        city = fake_locale.city()
        # Dutch postcodes are 4 digits + 2 letters (e.g., 1234 AB)
        postal_code = f"{random.randint(1000, 9999)} {fake_locale.lexify(text='??', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        street = f"{fake_locale.street_name()} {random.randint(1, 150)}"
    elif country_code == "AT":
        # Austrian addresses: postal codes correspond to regions
        city = fake_locale.city()
        # Austrian postcodes are 4 digits, with certain ranges for different regions
        postal_code = f"{random.randint(1000, 9999)}"
        street = f"{fake_locale.street_name()} {random.randint(1, 150)}"
    elif country_code == "EE":
        # Estonian addresses
        city = fake_locale.city()
        # Estonian postcodes are 5 digits
        postal_code = f"{random.randint(10000, 99999)}"
        street = f"{fake_locale.street_name()} {random.randint(1, 150)}"
    
    # Format the full address text with consistent components
    address_text = f"{street}, {postal_code} {city}, {country_code}"
    
    return {
        "identifier": fake.uuid4(),
        "text": street,
        "city": city,
        "postalCode": postal_code,
        "country": country_code
    }

def generate_related_address(parent_address, country_code):
    """
    Generate an address related to a parent address (for departments in the same organization)
    """
    # Get the parent address components
    parent_data = next((a for a in addresses if a["identifier"] == parent_address), None)
    
    if not parent_data:
        # Fallback to generating a new address
        return generate_address(country_code)
    
    # Parse the parent address
    parts = parent_data["text"].split(", ")
    if len(parts) < 2:
        return generate_address(country_code)
        
    street_part = parts[0]
    city_postal_part = parts[1]
    
    # Keep the same city and postal code but modify the street/building number
    locales = {"NL": "nl_NL", "AT": "de_AT", "EE": "et_EE"}
    fake_locale = Faker(locales[country_code])
    
    # Extract street name without number
    street_components = street_part.split()
    try:
        # Try to identify the number part and replace it
        if street_components[-1].isdigit():
            street_name = " ".join(street_components[:-1])
            new_number = random.randint(1, 150)
            new_street = f"{street_name} {new_number}"
        else:
            # If no number found, use the same street but different building/suite indicator
            new_street = f"{street_part}, Suite {random.randint(100, 999)}"
    except IndexError:
        # Fallback for any parsing issues
        new_street = f"{fake_locale.street_name()} {random.randint(1, 150)}"
    
    # Create new address text with same city/postal but different street
    address_text = f"{new_street}, {city_postal_part}"
    
    return {
        "identifier": fake.uuid4(),
        "text": new_street,
        "city": parent_data["city"],
        "postalCode": parent_data["postalCode"],
        "country": parent_data["country"]
    }


# Function to generate a random canonical name based on country
def generate_organization_name(country_code):
    if country_code == "NL":
        return fake.company() + " Zorg"
    elif country_code == "AT":
        return fake.company() + " Gesundheitszentrum"
    elif country_code == "EE":
        return fake.company() + " Tervisekeskus"
    else:
        return fake.company() + " Healthcare"
    

def generate_organization(organization_name, address, contact_point):
    return {
        "identifier": fake.uuid4(),
        "healthcareOrganizationName": organization_name,
        "address": address["identifier"],
        "contactPoint": contact_point["identifier"]
    }

def generate_contact_point(entity_type, country_code="NL", organization_name=None, department_name=None):
    """
    Generate a comprehensive contact point with multiple communication channels
    
    Parameters:
        entity_type: "organization" or "department" to customize contact types
        country_code: Country code to determine language and phone format
    
    Returns:
        A dictionary with contact information
    """
    # Set up language options based on country
    language_map = {
        "NL": ["nl", "en"],
        "AT": ["de", "en"],
        "EE": ["et", "en", "ru"]
    }
    available_languages = language_map.get(country_code, ["en"])
    
    # Define possible contact types based on entity
    if entity_type == "organization":
        contact_types = ["General Inquiries", "Patient Services", "Media Relations", 
                         "Administrative", "Billing"]
    else:  # department
        contact_types = ["Appointments", "Information", "Emergency", "Staff", "Referrals"]
    
    # Generate localized faker for phone numbers
    locales = {"NL": "nl_NL", "AT": "de_AT", "EE": "et_EE"}
    fake_locale = Faker(locales.get(country_code, "en_US"))
    
    # Email domain based on entity type
    email_domains = {
        "organization": ["healthcare.org"],
        "department": ["dept.healthcare.org"]
    }
    
    # Remove punctuation and take first word
    organization_name_first = ''.join(c for c in organization_name.split()[0] if c.isalnum())
    department_name_first = department_name.split()[0] if department_name else fake.word()
    # Create contact point
    contact_point = {
        "identifier": fake.uuid4(),
        "contactType": random.choice(contact_types),
        "phone": fake_locale.phone_number(),
        "email": f"{organization_name_first}@{random.choice(email_domains[entity_type])}" if entity_type == "organization" else f"{organization_name_first}.{department_name_first}@{random.choice(email_domains[entity_type])}",
        "availableLanguage": [available_languages[0]] + (["en"] if "en" in available_languages and random.choice([True, False]) else []),
        "fax": fake_locale.phone_number()
    }
    
    return contact_point


# Predefined list of medical department names
medical_departments = [
    "Anesthesia",
    "Cardiovascular",
    "Community Health",
    "Dentistry",
    "Dermatology",
    "Diet Nutrition",
    "Emergency",
    "Endocrine",
    "Gastroenterologic",
    "Genetic",
    "Geriatric",
    "Gynecologic",
    "Hematologic",
    "Infectious",
    "Laboratory Science",
    "Midwifery",
    "Musculoskeletal",
    "Neurologic",
    "Nursing",
    "Obstetric",
    "Oncologic",
    "Optometric",
    "Otolaryngologic",
    "Pathology",
    "Pediatric",
    "Pharmacy Specialty",
    "Physiotherapy",
    "Plastic Surgery",
    "Podiatric",
    "Primary Care",
    "Psychiatric",
    "Public Health",
    "Pulmonary",
    "Radiography",
    "Renal",
    "Respiratory Therapy",
    "Rheumatologic",
    "Speech Pathology",
    "Surgical",
    "Toxicologic",
    "Urologic"
]

def generate_service_department(organization):
    """
    Generate a single service department for a healthcare organization
    
    Parameters:
        organization: Dictionary containing the healthcare organization data
    
    Returns:
        A dictionary containing the service department data
    """
    # Find the organization's address identifier
    org_address_id = organization["address"]
    org_country = next((a["country"] for a in addresses if a["identifier"] == org_address_id), "NL")
    
    # Select a department name
    department_name = random.choice(medical_departments)
    
    # Generate a related address for the department
    dept_address = generate_related_address(org_address_id, org_country)
    addresses.append(dept_address)  # Add this new address to our addresses list
    
    # Generate contact point for department
    contact_point = generate_contact_point("department", org_country, organization["healthcareOrganizationName"], department_name)
    contact_points.append(contact_point)

    department = {
        "identifier": fake.uuid4(),
        "serviceDepartmentName": department_name,
        "address": dept_address["identifier"],  # Use the new related address
        "isPartOf": organization["identifier"],
        "contactPoint": contact_point["identifier"]
    }
    
    return department

# Create a dictionary to map departments to relevant job titles
department_job_titles = {
    "Anesthesia": ["Anesthesiologist", "Anesthesiology Nurse", "Anesthesiology Assistant"],
    "Cardiovascular": ["Cardiologist", "Cardiovascular Surgeon", "Cardiac Nurse", "EKG Technician"],
    "Community Health": ["Public Health Nurse", "Community Health Worker", "Health Educator"],
    "Dentistry": ["Dentist", "Dental Hygienist", "Orthodontist", "Dental Assistant"],
    "Dermatology": ["Dermatologist", "Dermatology Nurse", "Skin Care Specialist"],
    "Diet Nutrition": ["Dietitian", "Nutritionist", "Diet Technician", "Nutrition Counselor"],
    "Emergency": ["Emergency Physician", "ER Nurse", "Trauma Surgeon", "Emergency Medical Technician"],
    "Endocrine": ["Endocrinologist", "Diabetes Educator", "Endocrine Nurse"],
    "Gastroenterologic": ["Gastroenterologist", "GI Nurse", "GI Technician"],
    "Genetic": ["Geneticist", "Genetic Counselor", "Clinical Genetics Specialist"],
    "Geriatric": ["Geriatrician", "Gerontology Nurse", "Elderly Care Specialist"],
    "Gynecologic": ["Gynecologist", "Women's Health Nurse", "Obstetrics Technician"],
    "Hematologic": ["Hematologist", "Blood Bank Technologist", "Hematology Nurse"],
    "Infectious": ["Infectious Disease Specialist", "Epidemiologist", "Infection Control Nurse"],
    "Laboratory Science": ["Lab Technician", "Medical Laboratory Scientist", "Pathologist"],
    "Midwifery": ["Midwife", "Obstetric Nurse", "Doula"],
    "Musculoskeletal": ["Orthopedic Surgeon", "Physical Therapist", "Orthopedic Nurse"],
    "Neurologic": ["Neurologist", "Neurosurgeon", "Neurological Nurse", "EEG Technician"],
    "Nursing": ["Registered Nurse", "Nurse Practitioner", "Licensed Practical Nurse", "Nurse Manager"],
    "Obstetric": ["Obstetrician", "Labor & Delivery Nurse", "Neonatal Nurse"],
    "Oncologic": ["Oncologist", "Radiation Therapist", "Oncology Nurse"],
    "Optometric": ["Optometrist", "Ophthalmologist", "Optician", "Vision Therapist"],
    "Otolaryngologic": ["Otolaryngologist", "ENT Specialist", "Audiologist"],
    "Pathology": ["Pathologist", "Histology Technician", "Cytotechnologist", "Morgue Attendant"],
    "Pediatric": ["Pediatrician", "Pediatric Nurse", "Child Life Specialist", "School Nurse"],
    "Pharmacy Specialty": ["Pharmacist", "Pharmacy Technician", "Clinical Pharmacologist"],
    "Physiotherapy": ["Physiotherapist", "Physical Therapy Assistant", "Rehabilitation Specialist"],
    "Plastic Surgery": ["Plastic Surgeon", "Cosmetic Surgery Nurse", "Reconstructive Specialist"],
    "Podiatric": ["Podiatrist", "Foot Care Nurse", "Orthotic Specialist"],
    "Primary Care": ["Family Physician", "General Practitioner", "Primary Care Nurse", "Medical Assistant"],
    "Psychiatric": ["Psychiatrist", "Psychologist", "Mental Health Nurse", "Therapist"],
    "Public Health": ["Epidemiologist", "Public Health Officer", "Community Outreach Specialist"],
    "Pulmonary": ["Pulmonologist", "Respiratory Therapist", "Lung Function Technician"],
    "Radiography": ["Radiologist", "X-Ray Technician", "MRI Technologist", "CT Scan Technician"],
    "Renal": ["Nephrologist", "Dialysis Nurse", "Renal Dietitian"],
    "Respiratory Therapy": ["Respiratory Therapist", "Pulmonary Function Technologist", "Sleep Technician"],
    "Rheumatologic": ["Rheumatologist", "Arthritis Specialist", "Rheumatology Nurse"],
    "Speech Pathology": ["Speech Pathologist", "Speech Therapist", "Communication Disorders Specialist"],
    "Surgical": ["Surgeon", "Surgical Nurse", "Anesthesia Assistant", "Surgical Technologist"],
    "Toxicologic": ["Toxicologist", "Poison Control Specialist", "Environmental Health Officer"],
    "Urologic": ["Urologist", "Urology Nurse", "Urodynamics Technician"]
}


def generate_healthcare_personnel(organization, department):
    """
    Generate a single healthcare personnel record with associated person record
    
    Parameters:
        organization: Dictionary containing the healthcare organization data
        department: Dictionary containing the service department data
    
    Returns:
        Tuple of (person_dict, personnel_dict) - the created person and personnel records
    """
    department_name = department["serviceDepartmentName"]
    
    # Select an appropriate job title based on the department
    job_titles = department_job_titles.get(department_name, ["Healthcare Specialist", "Medical Professional"])
    job_title = random.choice(job_titles)
    
    person_name = fake.name()
    email_local_part = person_name.lower().replace(" ", "").replace(".", "").replace("'", "")
    email_address = f"{email_local_part}@healthcare.org"

    # Create person record
    person = {
        "identifier": fake.uuid4(),
        "personName": person_name,
        "birthDate": fake.date_of_birth(minimum_age=25, maximum_age=65).isoformat(),
        "gender": random.choice(["Male", "Female", "Other"]),
        "knowsLanguage": random.choice(["nl", "de", "et"])
    }

    # Create personnel record
    personnel = {
        "identifier": person["identifier"],
        "institution": organization["identifier"],
        "department": department["identifier"],
        "jobTitle": job_title,
        "email": email_address
    }
    
    return person, personnel



#################################################################################################################
#################################################################################################################
###### Start of data generation ######
#################################################################################################################
#################################################################################################################
addresses = []
healthcare_organization = []
contact_points = []
service_department = []
healthcare_personnel = []
persons = []
## how many HCO do we want?
for _ in range(NUM_ORGANIZATIONS):  # Select the amount of organizations
    country_code = random.choice(["NL", "AT", "EE"])
    address = generate_address(country_code)
    addresses.append(address)

    organization_name = generate_organization_name(country_code)

    # Generate contact point for organization
    contact_point = generate_contact_point("organization", country_code, organization_name)
    contact_points.append(contact_point)
    organization = generate_organization(organization_name, address, contact_point)
    healthcare_organization.append(organization)

# Dictionary to store the departments by organization
org_departments = {}
# Generate data for ServiceDepartment and organize by institution
for org in healthcare_organization:
    org_departments[org["identifier"]] = []
    # Find the organization's address identifier
    for _ in range(random.randint(MIN_DEPARTMENTS_PER_ORG, MAX_DEPARTMENTS_PER_ORG)):  # Select the amount of departments
        department = generate_service_department(org)
        service_department.append(department)
        org_departments[org["identifier"]].append(department)

# Generate personnel for each organization
for org in healthcare_organization:
    # Skip if org has no departments
    if not org_departments.get(org["identifier"], []):
        continue
        
    # Define target personnel count for this organization
    target_total_personnel = random.randint(MIN_PERSONNEL_PER_ORG, MAX_PERSONNEL_PER_ORG)  # Select the amount of personnel
    current_personnel_count = 0
    
    # First ensure all departments have at least 2 personnel
    for department in org_departments[org["identifier"]]:
        department_name = department["serviceDepartmentName"]
        
        # Add exactly 2 personnel to each department first
        for _ in range(2):
            person, personnel = generate_healthcare_personnel(org, department)
            persons.append(person)
            healthcare_personnel.append(personnel)
            current_personnel_count += 1
    
    # Then add remaining personnel to reach the desired total
    while current_personnel_count < target_total_personnel:
        # Randomly select a department for additional personnel
        department = random.choice(org_departments[org["identifier"]])
        department_name = department["serviceDepartmentName"]
        
        person, personnel = generate_healthcare_personnel(org, department)
        persons.append(person)
        healthcare_personnel.append(personnel)       
        current_personnel_count += 1


# store tables
store_table_as_csv(addresses, 'Address.csv')
store_table_as_csv(healthcare_organization, 'HealthcareOrganization.csv')
store_table_as_csv(service_department, 'ServiceDepartment.csv')
store_table_as_csv(contact_points, 'ContactPoint.csv')
store_table_as_csv(healthcare_personnel, 'HealthcarePersonnel.csv')
store_table_as_csv(persons, 'Person.csv')


#################################################################################################################
####################################################Original Data stored#########################################

# from variation_helpers import introduce_variations, address_variation, person_variation, organization_name_variation, email_variation, department_name_variation
# # Apply variations with explicit entity type registration
# dupe_addresses = introduce_variations(addresses, address_variation, variation_rate=0.2, entity_type='Address')
# dupe_healthcare_organization = introduce_variations(healthcare_organization, organization_name_variation, variation_rate=0.2, entity_type='HealthcareOrganization')
# dupe_service_department = introduce_variations(service_department, department_name_variation, variation_rate=0.2, entity_type='ServiceDepartment')
# dupe_persons = introduce_variations(persons, person_variation, variation_rate=0.2, entity_type='Person')
# dupe_healthcare_personnel = introduce_variations(healthcare_personnel, email_variation, variation_rate=0.2, entity_type='HealthcarePersonnel')
# dupe_contact_points = introduce_variations(contact_points, email_variation, variation_rate=0.2, entity_type='ContactPoint')

# # Export the duplicate registry for validation
# from variation_helpers import export_duplicate_registry
# export_duplicate_registry('ground_truths/golden_standard_duplicates.csv')


