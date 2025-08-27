import stanza
import re
from dateutil import parser
import pandas as pd
import uuid

# Download and initialize Stanza pipeline (first time only)
# Comment this out after first run if you don't want to download each time
stanza.download('en')
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma,ner')

def extract_entities_from_story(text):
    """Extract structured information from a healthcare professional story using Stanza."""
    
    # Process with Stanza
    doc = nlp(text)
    
    # Initialize entity containers
    entities = {
        "person": {},
        "healthcare_personnel": {},
        "organization": {},
        "service_department": {},
        "address": {},
        "contact_point": {}
    }
    
    # Extract person information
    person_name = None
    for sent in doc.sentences:
        for ent in sent.ents:
            if ent.type == 'PERSON':
                person_name = ent.text
                break
        if person_name:
            break
    
    if person_name:
        person_id = f"person_{str(uuid.uuid4())[:8]}"
        entities["person"] = {
            "identifier": person_id,
            "personName": person_name,
            "gender": None  # Would need more analysis to extract
        }
        
        # Extract birth date using regex (same as before)
        birth_date_match = re.search(r"[Bb]orn (?:on|in) ([A-Za-z]+ \d{1,2}, \d{4}|\d{4})", text)
        if birth_date_match:
            try:
                birth_date = parser.parse(birth_date_match.group(1))
                entities["person"]["birthDate"] = birth_date.strftime("%Y-%m-%d")
            except:
                # Handle just the year case
                year_match = re.search(r"[Bb]orn in (\d{4})", text)
                if year_match:
                    entities["person"]["birthDate"] = f"{year_match.group(1)}-01-01"
    
    
    # Adjusted organization extraction using refined regex patterns
    # org_patterns = [
    #     r"(?<=of\s)(?:the\s)?(?P<org>[A-Za-z0-9\-,\s]+?(?:Gesundheitszentrum|Zorg|Tervisekeskus|))\b",
    #     r"(?<=at\s)(?:the\s)?(?P<org>[A-Za-z0-9\-,\s]+?(?:Gesundheitszentrum|Zorg|Tervisekeskus|))\b"
    # ]
    

    # for pattern in org_patterns:
    #     org_match = re.search(pattern, text)
    #     if org_match:
    #         org_name = org_match.group("org").strip()
    #         entities["organization"] = {
    #             "identifier": f"org_{str(uuid.uuid4())[:8]}",
    #             "healthcareOrganizationName": org_name
    #         }
    #         break
    
    
    # Try to extract organization using Stanza as backup if regex fails
    # if "organization" not in entities or not entities["organization"]:
        for sent in doc.sentences:
            for ent in sent.ents:
                if ent.type == 'ORG':
                    org_name = ent.text
                    # Check if it's likely a healthcare organization
                    if any(term in org_name for term in ["Hospital", "Clinic", "Medical", "Health", 
                                                        "Gesundheitszentrum", "Zorg", "Care", "Center"]):
                        entities["organization"] = {
                            "identifier": f"org_{str(uuid.uuid4())[:8]}",
                            "healthcareOrganizationName": org_name
                        }
                        break
            if "organization" in entities and entities["organization"]:
                break
    
    # Extract job title and department (same as before)
    job_titles = [
    "Anesthesiologist", "Anesthesiology Nurse", "Anesthesiology Assistant",
    "Cardiologist", "Cardiovascular Surgeon", "Cardiac Nurse", "EKG Technician",
    "Public Health Nurse", "Community Health Worker", "Health Educator",
    "Dentist", "Dental Hygienist", "Orthodontist", "Dental Assistant",
    "Dermatologist", "Dermatology Nurse", "Skin Care Specialist",
    "Dietitian", "Nutritionist", "Diet Technician", "Nutrition Counselor",
    "Emergency Physician", "ER Nurse", "Trauma Surgeon", "Emergency Medical Technician",
    "Endocrinologist", "Diabetes Educator", "Endocrine Nurse",
    "Gastroenterologist", "GI Nurse", "GI Technician",
    "Geneticist", "Genetic Counselor", "Clinical Genetics Specialist",
    "Geriatrician", "Gerontology Nurse", "Elderly Care Specialist",
    "Gynecologist", "Women's Health Nurse", "Obstetrics Technician",
    "Hematologist", "Blood Bank Technologist", "Hematology Nurse",
    "Infectious Disease Specialist", "Epidemiologist", "Infection Control Nurse",
    "Lab Technician", "Medical Laboratory Scientist", "Pathologist",
    "Midwife", "Obstetric Nurse", "Doula",
    "Orthopedic Surgeon", "Physical Therapist", "Orthopedic Nurse",
    "Neurologist", "Neurosurgeon", "Neurological Nurse", "EEG Technician",
    "Registered Nurse", "Nurse Practitioner", "Licensed Practical Nurse", "Nurse Manager",
    "Obstetrician", "Labor & Delivery Nurse", "Neonatal Nurse",
    "Oncologist", "Radiation Therapist", "Oncology Nurse",
    "Optometrist", "Ophthalmologist", "Optician", "Vision Therapist",
    "Otolaryngologist", "ENT Specialist", "Audiologist",
    "Pathologist", "Histology Technician", "Cytotechnologist", "Morgue Attendant",
    "Pediatrician", "Pediatric Nurse", "Child Life Specialist", "School Nurse",
    "Pharmacist", "Pharmacy Technician", "Clinical Pharmacologist",
    "Physiotherapist", "Physical Therapy Assistant", "Rehabilitation Specialist",
    "Plastic Surgeon", "Cosmetic Surgery Nurse", "Reconstructive Specialist",
    "Podiatrist", "Foot Care Nurse", "Orthotic Specialist",
    "Family Physician", "General Practitioner", "Primary Care Nurse", "Medical Assistant",
    "Psychiatrist", "Psychologist", "Mental Health Nurse", "Therapist",
    "Epidemiologist", "Public Health Officer", "Community Outreach Specialist",
    "Pulmonologist", "Respiratory Therapist", "Lung Function Technician",
    "Radiologist", "X-Ray Technician", "MRI Technologist", "CT Scan Technician",
    "Nephrologist", "Dialysis Nurse", "Renal Dietitian",
    "Respiratory Therapist", "Pulmonary Function Technologist", "Sleep Technician",
    "Rheumatologist", "Arthritis Specialist", "Rheumatology Nurse",
    "Speech Pathologist", "Speech Therapist", "Communication Disorders Specialist",
    "Surgeon", "Surgical Nurse", "Anesthesia Assistant", "Surgical Technologist",
    "Toxicologist", "Poison Control Specialist", "Environmental Health Officer",
    "Urologist", "Urology Nurse", "Urodynamics Technician"
    ]

    Departments = [ "Anesthesia",
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
    "Urologic" ]

    for title in job_titles:
        if title in text:
            if "person" in entities and entities["person"]:
                entities["healthcare_personnel"] = {
                    "identifier": entities["person"]["identifier"],
                    "jobTitle": title
                }
                
                # Try to extract department
                for department in Departments:
                    if department in text:
                        entities["service_department"] = {
                            "identifier": f"dept_{str(uuid.uuid4())[:8]}",
                            "serviceDepartmentName": department
                        }
                        entities["healthcare_personnel"]["department"] = entities["service_department"]["identifier"]
                        break
                    entities["service_department"] = {
                        "identifier": f"dept_{str(uuid.uuid4())[:8]}",
                        "serviceDepartmentName": department
                    }
                    if "healthcare_personnel" in entities:
                        entities["healthcare_personnel"]["department"] = entities["service_department"]["identifier"]
            break
    
    # Extract contact information (same as before)
    email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)
    if email_match:
        email = email_match.group(1)
        if "healthcare_personnel" in entities:
            entities["healthcare_personnel"]["email"] = email
        
        entities["contact_point"] = {
            "identifier": f"contact_{str(uuid.uuid4())[:8]}",
            "contactType": "Customer Service",
            "email": email
        }
        
        # Extract phone
        phone_match = re.search(r"(?:call|phone|reach|contact) (?:at |the |her |him |)([+\d()-x\.]+)", text)
        if phone_match:
            entities["contact_point"]["phone"] = phone_match.group(1)
    
    # Enhanced address extraction with Stanza's location entities
    #address_match = re.search(r"([A-Za-z-]+\. \d+|[A-Za-z]+ \d+), ([A-Za-z ]+), ([A-Za-z]+)", text)
    address_match = False
    if address_match:
        street = address_match.group(1)
        city = address_match.group(2)
        country = address_match.group(3)
        
        entities["address"] = {
            "identifier": f"addr_{str(uuid.uuid4())[:8]}",
            "text": street,
            "city": city,
            "country": country,
            "postalCode": None  # Need separate extraction for postal codes
        }
    else:
        # Try to use Stanza's location entities
        locations = []
        for sent in doc.sentences:
            for ent in sent.ents:
                if ent.type == 'LOC' or ent.type == 'GPE':
                    locations.append(ent.text)
        
        # If we found at least 2 locations (city/country)
        if len(locations) >= 2:
            # Try to find street address with regex
            street_match = re.search(r"(\w+(?:-\w+)?\.? \d+)", text)
            street = street_match.group(1) if street_match else None
            
            entities["address"] = {
                "identifier": f"addr_{str(uuid.uuid4())[:8]}",
                "text": street,
                "city": locations[0],  # Assuming first location is city
                "country": locations[-1],  # Assuming last location is country
                "postalCode": None
            }
    
    # Link address to organization if both exist
    if "address" in entities and entities["address"] and "organization" in entities and entities["organization"]:
        entities["organization"]["address"] = entities["address"]["identifier"]
    
    return entities

# Process a single story as an example
story1 = """Melissa Allen is a skilled Registered Nurse at the Nursing Department of Faulkner-Howard Gesundheitszentrum 
located at Frankstr. 64, Schwechat, Austria. Born on November 25, 1977, Melissa provides exceptional patient care. 
Reach out to her at melissaallen@healthcare.org or call the department at 677-438-9305x55082."""

# Define more stories for testing
story2 = """Ms. Amanda Davis, an expert Nephrologist, leads renal care at West, Miller and Flores Gesundheitszentrum. Working from Lucie-Bräuer-Gasse 143 in Bruck an der Leitha, Austria, Amanda, born December 3, 1966, improves patient lives daily. Contact her at msamandadavis@healthcare.org or phone (460)275-4151x15055."""

story3 = """Cody Crawford, a dedicated Communication Disorders Specialist, assists patients at Bryan, Barnes and Hill Gesundheitszentrum, located at Lea-Kronberger-Weg 71, Eggenburg, Austria. Born on April 16, 1982, Cody excels in patient communication strategies. He can be contacted at codycrawford@healthcare.org or via 001-263-577-8570x7427."""

story4 = """Amy Kaiser is a renowned Sleep Technician working at Robbins Group Zorg, Twanhof 24, Holwierde, Netherlands. Born on November 16, 1960, Amy provides effective therapies for sleep disorders. She's reachable at amykaiser@healthcare.org or +31875-408035."""

story5 = """Danielle Beasley, a respected Neurological Nurse, serves patients at Peterson LLC Zorg. Located at Lisahof 123 in Groesbeek, Netherlands, Danielle, born January 16, 1963, offers outstanding neurological care. Reach Danielle at daniellebeasley@healthcare.org or call (0323) 659927."""

# Example extraction
extracted_data = extract_entities_from_story(story1)
#print("Example extraction:", extracted_data)

def convert_to_dataframes(stories):
    all_entities = []
    
    for story in stories:
        extracted = extract_entities_from_story(story)
        all_entities.append(extracted)
    
    # Create dataframes for each entity type
    persons_df = pd.DataFrame([e["person"] for e in all_entities if "person" in e and e["person"]])
    healthcare_personnel_df = pd.DataFrame([e["healthcare_personnel"] for e in all_entities if "healthcare_personnel" in e and e["healthcare_personnel"]])
    organizations_df = pd.DataFrame([e["organization"] for e in all_entities if "organization" in e and e["organization"]])
    departments_df = pd.DataFrame([e["service_department"] for e in all_entities if "service_department" in e and e["service_department"]])
    addresses_df = pd.DataFrame([e["address"] for e in all_entities if "address" in e and e["address"]])
    contact_points_df = pd.DataFrame([e["contact_point"] for e in all_entities if "contact_point" in e and e["contact_point"]])
    print(all_entities)
    # Return all dataframes
    return {
        "Person": persons_df,
        "HealthcarePersonnel": healthcare_personnel_df,
        "HealthcareOrganization": organizations_df,
        "ServiceDepartment": departments_df,
        "Address": addresses_df,
        "ContactPoint": contact_points_df
    }

# Process all stories
all_stories = [story1, story2, story3, story4, story5]
dfs = convert_to_dataframes(all_stories)



# Print summary of extracted entities
print("\nExtraction summary:")
for entity_type, df in dfs.items():
    print(f"{entity_type}: {len(df)} records")

# Save to CSV files
# output_dir = "src/data/unstructured/"
# import os
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# for entity_name, df in dfs.items():
#     df.to_csv(f"{output_dir}{entity_name}.csv", index=False)
#     print(f"Saved {entity_name}.csv with {len(df)} records")

