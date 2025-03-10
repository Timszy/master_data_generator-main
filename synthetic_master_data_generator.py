from faker import Faker
import random
from variation_helpers import introduce_variations, address_variation, person_names_variation, person_dob_variation, organization_name_variation, email_variation, department_name_variation
from helpers import store_table_as_csv

# Initialize Faker
fake = Faker()
Faker.seed(0)



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
        "text": address_text,
        "city": city,
        "postalCode": postal_code,
        "country": country_code
    }

# Function to generate many variations of a canonical name
def generate_name_variations(canonical_name, num_variations=10):
    variations = set()
    variations.add(canonical_name)

    while len(variations) < num_variations:
        variation = list(canonical_name)

        # Randomly decide on the type of variation
        variation_type = random.choice(['swap', 'duplicate', 'missing', 'extra', 'case_change'])

        if variation_type == 'swap' and len(variation) > 1:
            i = random.randint(0, len(variation) - 2)
            variation[i], variation[i + 1] = variation[i + 1], variation[i]

        elif variation_type == 'duplicate' and len(variation) > 0:
            i = random.randint(0, len(variation) - 1)
            variation.insert(i, variation[i])

        elif variation_type == 'missing' and len(variation) > 1:
            i = random.randint(0, len(variation) - 1)
            del variation[i]

        elif variation_type == 'extra':
            variation.insert(random.randint(0, len(variation)), random.choice("abcdefghijklmnopqrstuvwxyz"))

        elif variation_type == 'case_change':
            i = random.randint(0, len(variation) - 1)
            variation[i] = variation[i].upper() if variation[i].islower() else variation[i].lower()

        variations.add("".join(variation))

    return list(variations)


# Function to generate a random canonical name based on country
def generate_canonical_name(country_code):
    if country_code == "NL":
        return fake.company() + " Zorg"
    elif country_code == "AT":
        return fake.company() + " Gesundheitszentrum"
    elif country_code == "EE":
        return fake.company() + " Tervisekeskus"
    else:
        return fake.company() + " Healthcare"


healthcare_organization = []
addresses = []
for _ in range(100):
    country_code = random.choice(["NL", "AT", "EE"])
    address = generate_address(country_code)
    addresses.append(address)

    canonical_name = generate_canonical_name(country_code)
    name_variations = generate_name_variations(canonical_name, num_variations=25)
    organization_name = random.choice(name_variations)

    healthcare_organization.append({
        "identifier": fake.uuid4(),
        "healthcareOrganizationName": organization_name,
        #"canonicalName": canonical_name,  # Keep track of the canonical name
        "address": address["identifier"],
        "contact": f"Contact: {fake.phone_number()}"
    })


service_department = []
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

# Dictionary to store the departments by organization
org_departments = {}

# Generate data for ServiceDepartment and organize by institution
for org in healthcare_organization:
    org_departments[org["identifier"]] = []
    for _ in range(random.randint(3, 5)):  # Each org has 3-5 departments
        department_name = random.choice(medical_departments)
        department = {
            "identifier": fake.uuid4(),
            "serviceDepartmentName": department_name,
            "address": random.choice(addresses)["identifier"],  # Randomly assign existing address
            "isPartOf": org["identifier"],
            "contact": f"Contact: {fake.phone_number()}"
        }
        service_department.append(department)
        org_departments[org["identifier"]].append(department)

# Generate data for HealthcarePersonnel and Person
healthcare_personnel = []
persons = []
for org in healthcare_organization:
    # Check if the organization has departments
    if not org_departments.get(org["identifier"], []):
        continue
        
    for _ in range(random.randint(10, 20)):  # Each org has 10-20 personnel
        # Choose a department for this person within their organization
        department = random.choice(org_departments[org["identifier"]])
        department_name = department["serviceDepartmentName"]
        
        # Select an appropriate job title based on the department
        job_titles = department_job_titles.get(department_name, ["Healthcare Specialist", "Medical Professional"])
        job_title = random.choice(job_titles)
        
        person_name = fake.name()
        email_local_part = person_name.lower().replace(" ", "").replace(".", "").replace("'", "")
        email_domain = "healthcare.org"
        email_address = f"{email_local_part}@{email_domain}"

        person = {
            "identifier": fake.uuid4(),
            "personName": person_name,
            "birthDate": fake.date_of_birth(minimum_age=25, maximum_age=65).isoformat(),
            "gender": random.choice(["Male", "Female", "Other"]),
            "primaryLanguage": random.choice(["nl", "de", "et"])
        }
        persons.append(person)

        personnel = {
            "identifier": person["identifier"],  # Link by identifier
            "institution": org["identifier"],
            "department": department["identifier"],  # Link to specific department within their organization
            "jobTitle": job_title,  # Use department-specific job title
            "email": email_address
        }
        healthcare_personnel.append(personnel)

# Apply variations to each list and track duplicates
addresses = introduce_variations(addresses, address_variation, variation_rate=0.2, entity_type='Address')
persons = introduce_variations(persons, person_names_variation, variation_rate=0.2, entity_type='Person')
persons = introduce_variations(persons, person_dob_variation, variation_rate=0.2, entity_type='Person')
healthcare_organization = introduce_variations(healthcare_organization, organization_name_variation, variation_rate=0.2, entity_type='HealthcareOrganization')
healthcare_personnel = introduce_variations(healthcare_personnel, email_variation, variation_rate=0.2, entity_type='HealthcarePersonnel')
service_department = introduce_variations(service_department, department_name_variation, variation_rate=0.2, entity_type='ServiceDepartment')

# Export the duplicate registry for validation
from variation_helpers import export_duplicate_registry
export_duplicate_registry('golden_standard_duplicates.csv')

# store tables
store_table_as_csv(addresses, 'Address.csv')
store_table_as_csv(healthcare_organization, 'HealthcareOrganization.csv')
store_table_as_csv(service_department, 'ServiceDepartment.csv')
store_table_as_csv(healthcare_personnel, 'HealthcarePersonnel.csv')
store_table_as_csv(persons, 'Person.csv')