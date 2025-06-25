import random
import copy
import re
from datetime import datetime, timedelta
from faker import Faker
from deep_translator import GoogleTranslator
import pandas as pd
# main file for introducing variations to entities in a dataset
# Variation rate
variation_rate_default = 0.2

# Dictionary to track all introduced duplicates across all entities
duplicate_registry = {}

# In variation_helpers.py, modify the functions to use a deterministic UUID generation

import hashlib
import uuid

# Add this global dictionary at the top with other globals
variation_id_cache = {}

def generate_consistent_uuid(original_id, entity_type):
    """Generate a consistent UUID based on original ID, entity type, and variation type"""
    cache_key = f"{original_id}_{entity_type}"
    
    if cache_key not in variation_id_cache:
        # Use uuid5 for deterministic UUID generation
        namespace = uuid.uuid5(uuid.NAMESPACE_DNS, original_id)
        variation_id_cache[cache_key] = str(uuid.uuid5(namespace, f"{entity_type}"))
    
    return variation_id_cache[cache_key]

def register_duplicate(original_id, duplicate_id, entity_type, variation_type, field_name, original_value, varied_value):
    """Register a duplicate relationship in the global registry"""
    if original_id not in duplicate_registry:
        duplicate_registry[original_id] = []
    
    duplicate_registry[original_id].append({
        'duplicate_id': duplicate_id,
        'entity_type': entity_type,
        'variation_type': variation_type,
        'field_name': field_name,
        'original_value': original_value,
        'varied_value': varied_value
    })

# Modified introduce_variations function
# Modified introduce_variations function to handle inheritance
def introduce_variations(data_list, variation_function, variation_rate=variation_rate_default, entity_type=None):
    """
    Generate variations for a subset of items in data_list using the variation_function
    
    Args:
        data_list: List of entities to potentially create variations for
        variation_function: Function that generates variations
        variation_rate: Percentage of entities to create variations for
        entity_type: Type name of the entity (e.g., "Address", "Person")
    """
    # Determine entity type - use provided entity_type or guess from function name
    
    # Generate variations for only a subset of the items based on the variation_rate
    selected_indices = random.sample(range(len(data_list)), int(len(data_list) * variation_rate))
    variations = []
    
    for index in selected_indices:
        original_item = data_list[index]
        varied_item, variation_info = variation_function(original_item)
        # Generate consistent UUID using parent entity type for inheritance
        if entity_type == "HealthcarePersonnel" or entity_type == "Person":
            consistent_uuid = generate_consistent_uuid(
            original_item["identifier"], 
            "Person",  # Use parent type here
            )
            varied_item["identifier"] = consistent_uuid 
        else:
            varied_item["identifier"] = fake.uuid4()  # Generate a new UUID if no parent type
        
        # Override the UUID generated in the variation function
        
        
        variations.append(varied_item)
        register_duplicate(
            original_id=original_item["identifier"],
            duplicate_id=varied_item["identifier"],
            entity_type=entity_type,  # Keep original entity type for registry
            variation_type=variation_info["variation_type"],
            field_name=variation_info["field_name"],
            original_value=variation_info.get("original_value", ""),
            varied_value=variation_info.get("varied_value", "")
        )
    return data_list + variations

#### Address variations
# Updated address_variation function with balanced variation application
fake = Faker()

def address_variation(address, noise_severity = "low"):
    """Generate variations of an address with balanced distribution"""
    possible_variations = []

    if address.get("text"):
        possible_variations.append("house_number_suffix")
    if address.get("city") and len(address.get("city")) > 3:
        possible_variations.append("city_typo")
    if address.get("country") in ["NL", "AT", "EE"]:
        possible_variations.append("country_expansion")
    if address.get("postalCode"):
        possible_variations.append("postal_format")

    if not possible_variations:
        default_var = copy.deepcopy(address)
        default_var["identifier"] = fake.uuid4()  # Generate a new UUID
        return default_var, {
            "variation_type": "no_change", 
            "field_name": "address",
            "original_value": str(address),
            "varied_value": str(default_var)
        }

    selected_variation = random.choice(possible_variations)

    if selected_variation == "house_number_suffix":
        var = copy.deepcopy(address)
        original_value = var["text"]
        words = var["text"].split()
        for i, word in enumerate(words):
            if word.isdigit() or (word[:-1].isdigit() and not word[-1].isdigit()):
                words[i] = words[i] + random.choice(["A", "B", "C"])
                break
        var["text"] = " ".join(words)
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "house_number_suffix", 
            "field_name": "text",
            "original_value": original_value,
            "varied_value": var["text"]
        }

    if selected_variation == "city_typo":
        var = copy.deepcopy(address)
        original_city = var["city"]
        city = list(var["city"])
        pos = random.randint(1, len(city) - 2)
        typo_type = random.choice(["swap", "duplicate", "missing", "extra"])
        if typo_type == "swap" and pos < len(city) - 1:
            city[pos], city[pos+1] = city[pos+1], city[pos]
        elif typo_type == "duplicate":
            city.insert(pos, city[pos])
        elif typo_type == "missing":
            city.pop(pos)
        elif typo_type == "extra":
            city.insert(pos, random.choice("abcdefghijklmnopqrstuvwxyz"))
        var["city"] = "".join(city)
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "city_typo", 
            "field_name": "city",
            "original_value": original_city,
            "varied_value": var["city"]
        }

    if selected_variation == "country_expansion":
        var = copy.deepcopy(address)
        original_country = var["country"]
        country_map = {"NL": "Netherlands", "AT": "Austria", "EE": "Estonia"}
        var["country"] = country_map[var["country"]]
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "country_expansion", 
            "field_name": "country",
            "original_value": original_country,
            "varied_value": var["country"]
        }

    if selected_variation == "postal_format":
        var = copy.deepcopy(address)
        original_postal = var["postalCode"]
        if " " in var["postalCode"]:
            var["postalCode"] = var["postalCode"].replace(" ", "")
        else:
            var["postalCode"] = var["postalCode"] + " "
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "postal_format", 
            "field_name": "postalCode",
            "original_value": original_postal,
            "varied_value": var["postalCode"]
        }
    

##### Person name variations
def person_variation(person, noise_severity = "low"):
    """Generate variations of a person with balanced distribution"""
    possible_variations = []
    
    # Check what variations are possible based on available fields
    names = person.get("personName", "").split()
    if len(names) > 1:
        possible_variations.append("name_swap")
        possible_variations.append("abbreviated_first_name")
    
    if names and any(len(name) > 2 for name in names):
        possible_variations.append("name_typo")
    
    if "knowsLanguage" in person and person["knowsLanguage"] in ["nl", "de", "et"]:
        possible_variations.append("language_expansion")
    
    if "birthDate" in person and len(person["birthDate"].split('-')) == 3:
        possible_variations.append("date_format_variation")
    
    # If no variations are possible, return with no changes
    if not possible_variations:
        default_var = copy.deepcopy(person)
        default_var["identifier"] = fake.uuid4()  # Generate a new UUID
        return default_var, {
            "variation_type": "no_change", 
            "field_name": "person",
            "original_value": str(person),
            "varied_value": str(default_var)
        }
    
    # Select a variation randomly from the possible ones
    selected_variation = random.choice(possible_variations)
    
    # Name order swap variation
    if selected_variation == "name_swap":
        var = copy.deepcopy(person)
        names = var["personName"].split()
        original_value = var["personName"]
        var["personName"] = ' '.join(names[::-1])
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "name_swap", 
            "field_name": "personName",
            "original_value": original_value,
            "varied_value": var["personName"]
        }
    
    # First name abbreviation
    if selected_variation == "abbreviated_first_name":
        var = copy.deepcopy(person)
        names = var["personName"].split()
        original_value = var["personName"]
        first_initial = names[0][0] + "."
        var["personName"] = f"{first_initial} {' '.join(names[1:])}"
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "abbreviated_first_name", 
            "field_name": "personName",
            "original_value": original_value,
            "varied_value": var["personName"]
        }
    
    # Name typo variation
    if selected_variation == "name_typo":
        var = copy.deepcopy(person)
        names = var["personName"].split()
        original_value = var["personName"]
        name_to_change = random.choice([n for n in names if len(n) > 2])
        name_chars = list(name_to_change)
        pos = random.randint(1, len(name_chars) - 2)
        
        typo_type = random.choice(["swap", "missing", "extra", "wrong_letter"])
        if typo_type == "swap" and pos < len(name_chars) - 1:
            name_chars[pos], name_chars[pos+1] = name_chars[pos+1], name_chars[pos]
        elif typo_type == "missing":
            name_chars.pop(pos)
        elif typo_type == "extra":
            name_chars.insert(pos, random.choice("abcdefghijklmnopqrstuvwxyz"))
        elif typo_type == "wrong_letter":
            name_chars[pos] = random.choice("abcdefghijklmnopqrstuvwxyz")
        
        changed_name = "".join(name_chars)
        var["personName"] = var["personName"].replace(name_to_change, changed_name, 1)
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "name_typo", 
            "field_name": "personName",
            "original_value": original_value,
            "varied_value": var["personName"]
        }
    
    # Language expansion variation
    if selected_variation == "language_expansion":
        var = copy.deepcopy(person)
        original_value = var["knowsLanguage"]
        language_map = {
            "nl": "Dutch",
            "de": "German",
            "et": "Estonian"
        }
        if var["knowsLanguage"] in language_map:
            var["knowsLanguage"] = language_map[var["knowsLanguage"]]
            var["identifier"] = fake.uuid4()  # Generate a new UUID
            return var, {
                "variation_type": "language_expansion", 
                "field_name": "knowsLanguage",
                "original_value": original_value,
                "varied_value": var["knowsLanguage"]
            }
    
    # Birthday format variation (swap day/month)
    if selected_variation == "date_format_variation":
        var = copy.deepcopy(person)
        original_value = var["birthDate"]
        date_parts = var["birthDate"].split('-')
        var["birthDate"] = f"{date_parts[0]}-{date_parts[2]}-{date_parts[1]}"
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "date_format_variation",
            "field_name": "birthDate",
            "original_value": original_value,
            "varied_value": var["birthDate"]
        }

#### Organization name variations
def organization_name_variation(organization, noise_severity = "low"):
    """Generate variations of an organization name with balanced distribution"""
    possible_variations = []
    
    # Check for possible variations
    if "healthcareOrganizationName" in organization:
        org_name = organization["healthcareOrganizationName"]
        
        # Check if name can be abbreviated (has at least 2 capital letters)
        capitals = [c for c in org_name if c.isupper()]
        if len(capitals) >= 2:
            possible_variations.append("name_abbreviation")
        
        # Check if name has words that are long enough for typos
        words = org_name.split()
        if any(len(word) > 3 for word in words):
            possible_variations.append("name_typo")
    
    # If no variations are possible, return with no changes
    if not possible_variations:
        default_var = copy.deepcopy(organization)
        default_var["identifier"] = default_var["identifier"] + "_var_default"
        return default_var, {
            "variation_type": "no_change", 
            "field_name": "organization",
            "original_value": str(organization),
            "varied_value": str(default_var)
        }
    
    # Select a variation randomly from the possible ones
    selected_variation = random.choice(possible_variations)
    
    # Variation 1: Abbreviate the name using capital letters
    if selected_variation == "name_abbreviation":
        var = copy.deepcopy(organization)
        original_name = var["healthcareOrganizationName"]
        
        # Identify the suffix part
        suffixes = [" Zorg", " Gesundheitszentrum", " Tervisekeskus", " Healthcare"]
        suffix = ""
        main_name = original_name
        
        for potential_suffix in suffixes:
            if original_name.endswith(potential_suffix):
                suffix = potential_suffix
                main_name = original_name[:-len(suffix)]
                break
                
        # Create abbreviation from capital letters
        capitals = [c for c in main_name if c.isupper()]
        abbreviation = ''.join(capitals) + suffix
        var["healthcareOrganizationName"] = abbreviation
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "name_abbreviation", 
            "field_name": "healthcareOrganizationName",
            "original_value": original_name,
            "varied_value": abbreviation
        }
        
    # Variation 2: Introduce typos in the name
    if selected_variation == "name_typo":
        var = copy.deepcopy(organization)
        original_name = var["healthcareOrganizationName"]
        
        # Identify the suffix part
        suffixes = [" Zorg", " Gesundheitszentrum", " Tervisekeskus", " Healthcare"]
        suffix = ""
        main_name = original_name
        
        for potential_suffix in suffixes:
            if original_name.endswith(potential_suffix):
                suffix = potential_suffix
                main_name = original_name[:-len(suffix)]
                break
        
        # Apply typos to the main part of the name only
        words = main_name.split()
        if words:
            word_to_change = random.choice([w for w in words if len(w) > 3])
            word_chars = list(word_to_change)
            pos = random.randint(1, len(word_chars) - 2)
            
            # Different types of typos
            typo_type = random.choice(["swap", "missing", "extra", "substitute"])
            
            if typo_type == "swap" and pos < len(word_chars) - 1:
                word_chars[pos], word_chars[pos+1] = word_chars[pos+1], word_chars[pos]
            elif typo_type == "missing":
                word_chars.pop(pos)
            elif typo_type == "extra":
                word_chars.insert(pos, random.choice("abcdefghijklmnopqrstuvwxyz"))
            elif typo_type == "substitute":
                word_chars[pos] = random.choice("abcdefghijklmnopqrstuvwxyz")
            
            changed_word = "".join(word_chars)
            new_name = main_name.replace(word_to_change, changed_word, 1) + suffix
            
            var["healthcareOrganizationName"] = new_name
            var["identifier"] = fake.uuid4()  # Generate a new UUID
            return var, {
                "variation_type": "name_typo", 
                "field_name": "healthcareOrganizationName",
                "original_value": original_name,
                "varied_value": new_name
            }

###3 department name variations
def department_name_variation(department, noise_severity = "low"):
    contact_point_df = pd.read_csv("Data_source/Baseline/ContactPoint.csv")
    """Generate variations of a department name with balanced distribution"""
    possible_variations = []
    
    # Check for possible variations
    if "serviceDepartmentName" in department:
        dept_name = department["serviceDepartmentName"]
        
        abbreviations = {
            "Anesthesia": "Anesth Dept",
            "Cardiovascular": "Cardio",
            "Community Health": "Comm Health",
            "Dentistry": "Dental",
            "Dermatology": "Derm",
            "Diet Nutrition": "Diet & Nutr",
            "Emergency": "ER",
            "Endocrine": "Endo",
            "Gastroenterologic": "GI",
            "Genetic": "Gen Med",
            "Geriatric": "Geri",
            "Gynecologic": "GYN",
            "Hematologic": "Hema",
            "Infectious": "ID",
            "Laboratory Science": "Lab",
            "Midwifery": "Midwife Svc",
            "Musculoskeletal": "MSK",
            "Neurologic": "Neuro",
            "Nursing": "Nurs",
            "Obstetric": "OB",
            "Oncologic": "Onc",
            "Optometric": "Opt",
            "Otolaryngologic": "ENT",
            "Pathology": "Path",
            "Pediatric": "Peds",
            "Pharmacy Specialty": "Pharm",
            "Physiotherapy": "PT",
            "Plastic Surgery": "Plastics",
            "Podiatric": "Foot Care",
            "Primary Care": "PCP",
            "Psychiatric": "Psych",
            "Public Health": "Pub Health",
            "Pulmonary": "Pulm",
            "Radiography": "Rad",
            "Renal": "Kidney",
            "Respiratory Therapy": "Resp",
            "Rheumatologic": "Rheum",
            "Speech Pathology": "Speech",
            "Surgical": "Surg",
            "Toxicologic": "Tox",
            "Urologic": "Uro"
        }
        
        alternatives = {
            "Anesthesia": "Anesthesiology Department",
            "Cardiovascular": "Heart Center",
            "Community Health": "Community Care Services",
            "Dentistry": "Dental Services",
            "Dermatology": "Skin Care Center",
            "Diet Nutrition": "Nutritional Services",
            "Emergency": "Emergency Services",
            "Endocrine": "Hormone & Metabolism Center",
            "Gastroenterologic": "Digestive Health Center",
            "Genetic": "Medical Genetics Department",
            "Geriatric": "Elderly Care Services",
            "Gynecologic": "Women's Health Center",
            "Hematologic": "Blood Disorders Clinic",
            "Infectious": "Infection Control & Prevention",
            "Laboratory Science": "Clinical Laboratory",
            "Midwifery": "Midwifery & Birth Center",
            "Musculoskeletal": "Bone & Joint Center",
            "Neurologic": "Brain & Spine Center",
            "Nursing": "Nursing Services",
            "Obstetric": "Maternity Care",
            "Oncologic": "Cancer Center",
            "Optometric": "Vision Care Center",
            "Otolaryngologic": "Ear, Nose & Throat",
            "Pathology": "Diagnostic Pathology",
            "Pediatric": "Children's Health",
            "Pharmacy Specialty": "Clinical Pharmacy",
            "Physiotherapy": "Physical Rehabilitation",
            "Plastic Surgery": "Reconstructive & Cosmetic Surgery",
            "Podiatric": "Foot & Ankle Center",
            "Primary Care": "Family Medicine",
            "Psychiatric": "Mental Health Services",
            "Public Health": "Population Health Center",
            "Pulmonary": "Lung & Breathing Center",
            "Radiography": "Medical Imaging",
            "Renal": "Kidney Care Center",
            "Respiratory Therapy": "Respiratory Care Services",
            "Rheumatologic": "Arthritis & Rheumatism Center",
            "Speech Pathology": "Speech & Language Therapy",
            "Surgical": "Surgical Services",
            "Toxicologic": "Poison Control Center",
            "Urologic": "Urology & Kidney Health"
        }
        
        # Check if the department name can be abbreviated
        for full, _ in abbreviations.items():
            if full in dept_name:
                possible_variations.append("department_abbreviation")
                break
                
        # Check if name has an alternative
        if dept_name in alternatives:
            possible_variations.append("alternative_naming")
            possible_variations.append("translation")
    
    # If no variations are possible, return with no changes
    if not possible_variations:
        default_var = copy.deepcopy(department)
        default_var["identifier"] = fake.uuid4()  # Generate a new UUID
        return default_var, {
            "variation_type": "no_change", 
            "field_name": "department",
            "original_value": str(department),
            "varied_value": str(default_var)
        }
    
    # Select a variation randomly from the possible ones
    selected_variation = random.choice(possible_variations)
    
    # Abbreviation variation
    if selected_variation == "department_abbreviation":
        var = copy.deepcopy(department)
        original_name = var["serviceDepartmentName"]
        dept_name = var["serviceDepartmentName"]
        abbreviations = {
            "Anesthesia": "Anesth Dept",
            "Cardiovascular": "Cardio",
            "Community Health": "Comm Health",
            "Dentistry": "Dental",
            "Dermatology": "Derm",
            "Diet Nutrition": "Diet & Nutr",
            "Emergency": "ER",
            "Endocrine": "Endo",
            "Gastroenterologic": "GI",
            "Genetic": "Gen Med",
            "Geriatric": "Geri",
            "Gynecologic": "GYN",
            "Hematologic": "Hema",
            "Infectious": "ID",
            "Laboratory Science": "Lab",
            "Midwifery": "Midwife Svc",
            "Musculoskeletal": "MSK",
            "Neurologic": "Neuro",
            "Nursing": "Nurs",
            "Obstetric": "OB",
            "Oncologic": "Onc",
            "Optometric": "Opt",
            "Otolaryngologic": "ENT",
            "Pathology": "Path",
            "Pediatric": "Peds",
            "Pharmacy Specialty": "Pharm",
            "Physiotherapy": "PT",
            "Plastic Surgery": "Plastics",
            "Podiatric": "Foot Care",
            "Primary Care": "PCP",
            "Psychiatric": "Psych",
            "Public Health": "Pub Health",
            "Pulmonary": "Pulm",
            "Radiography": "Rad",
            "Renal": "Kidney",
            "Respiratory Therapy": "Resp",
            "Rheumatologic": "Rheum",
            "Speech Pathology": "Speech",
            "Surgical": "Surg",
            "Toxicologic": "Tox",
            "Urologic": "Uro"
        }
        
        for full, abbr in abbreviations.items():
            if full in dept_name:
                var["serviceDepartmentName"] = dept_name.replace(full, abbr)
                var["identifier"] = fake.uuid4()  # Generate a new UUID
                return var, {
                    "variation_type": "department_abbreviation", 
                    "field_name": "serviceDepartmentName",
                    "original_value": original_name,
                    "varied_value": var["serviceDepartmentName"]
                }
        
    # Alternative naming variation
    if selected_variation == "alternative_naming":
        var = copy.deepcopy(department)
        original_name = var["serviceDepartmentName"]
        dept_name = var["serviceDepartmentName"]
        alternatives = {
            "Anesthesia": "Anesthesiology Department",
            "Cardiovascular": "Heart Center",
            "Community Health": "Community Care Services",
            "Dentistry": "Dental Services",
            "Dermatology": "Skin Care Center",
            "Diet Nutrition": "Nutritional Services",
            "Emergency": "Emergency Services",
            "Endocrine": "Hormone & Metabolism Center",
            "Gastroenterologic": "Digestive Health Center",
            "Genetic": "Medical Genetics Department",
            "Geriatric": "Elderly Care Services",
            "Gynecologic": "Women's Health Center",
            "Hematologic": "Blood Disorders Clinic",
            "Infectious": "Infection Control & Prevention",
            "Laboratory Science": "Clinical Laboratory",
            "Midwifery": "Midwifery & Birth Center",
            "Musculoskeletal": "Bone & Joint Center",
            "Neurologic": "Brain & Spine Center",
            "Nursing": "Nursing Services",
            "Obstetric": "Maternity Care",
            "Oncologic": "Cancer Center",
            "Optometric": "Vision Care Center",
            "Otolaryngologic": "Ear, Nose & Throat",
            "Pathology": "Diagnostic Pathology",
            "Pediatric": "Children's Health",
            "Pharmacy Specialty": "Clinical Pharmacy",
            "Physiotherapy": "Physical Rehabilitation",
            "Plastic Surgery": "Reconstructive & Cosmetic Surgery",
            "Podiatric": "Foot & Ankle Center",
            "Primary Care": "Family Medicine",
            "Psychiatric": "Mental Health Services",
            "Public Health": "Population Health Center",
            "Pulmonary": "Lung & Breathing Center",
            "Radiography": "Medical Imaging",
            "Renal": "Kidney Care Center",
            "Respiratory Therapy": "Respiratory Care Services",
            "Rheumatologic": "Arthritis & Rheumatism Center",
            "Speech Pathology": "Speech & Language Therapy",
            "Surgical": "Surgical Services",
            "Toxicologic": "Poison Control Center",
            "Urologic": "Urology & Kidney Health"
        }
        
        if dept_name in alternatives:
            var["serviceDepartmentName"] = alternatives[dept_name]
            var["identifier"] = fake.uuid4()  # Generate a new UUID
            return var, {
                "variation_type": "alternative_naming", 
                "field_name": "serviceDepartmentName",
                "original_value": original_name,
                "varied_value": var["serviceDepartmentName"]
            }
    # Translation variation
    if selected_variation == "translation":
        var = copy.deepcopy(department)
        original_name = var["serviceDepartmentName"]
        contactidentifier = var["contactPoint"]
        contact_point = contact_point_df[contact_point_df["identifier"] == contactidentifier]
        tranlation_language = contact_point["availableLanguage"]
        language = tranlation_language.str.strip('[]').str.split(',').str[0]
        str_language = language.iloc[0].strip("'")
        language_map = {
                        "nl": "dutch",
                        "de": "german",
                        "et": "estonian",
                        "en": "english"
                    }
        language_code = language_map.get(str_language.lower(), "english")
        translator = GoogleTranslator(source="english", target=language_code)
        translated_name = translator.translate(original_name)
        var["serviceDepartmentName"] = translated_name
        var["identifier"] = fake.uuid4()
        return var, {
            "variation_type": "translation", 
            "field_name": "serviceDepartmentName",
            "original_value": original_name,
            "varied_value": var["serviceDepartmentName"]
        }


def email_variation(entity, noise_severity = "low"):
    """Generate variations of email addresses with balanced distribution"""
    possible_variations = []
    
    # Check for possible variations
    if "email" in entity:
        email = entity["email"]
        parts = email.split('@')
        
        if len(parts) == 2:
            local, domain = parts
            domain_parts = domain.split('.')
            
            # Check if local part is long enough for typo
            if len(local) > 3:
                possible_variations.append("email_typo")
                
            # Check if domain can be changed based on language
            if len(domain_parts) >= 2:
                if "availableLanguage" in entity and entity["availableLanguage"]:
                    if (isinstance(entity["availableLanguage"], list) and 
                        any(lang.lower() in ["nl", "de", "et"] for lang in entity["availableLanguage"])):
                        possible_variations.append("email_domain_change_list")
                    elif (isinstance(entity["availableLanguage"], str) and 
                          entity["availableLanguage"].startswith("[") and
                          any(lang.lower() in ["nl", "de", "et"] for lang in 
                              [l.strip().strip("'\"") for l in entity["availableLanguage"].strip("[]").split(",")])):
                        possible_variations.append("email_domain_change_str")
    
    # If no variations are possible, return with no changes
    if not possible_variations:
        default_var = copy.deepcopy(entity)
        default_var["identifier"] = fake.uuid4()  # Generate a new UUID
        return default_var, {
            "variation_type": "no_change", 
            "field_name": "email",
            "original_value": entity.get("email", ""),
            "varied_value": entity.get("email", "")
        }
    
    # Select a variation randomly from the possible ones
    selected_variation = random.choice(possible_variations)
    
    # Email typo variation (before @)
    if selected_variation == "email_typo":
        var = copy.deepcopy(entity)
        original_email = var["email"]
        parts = original_email.split('@')
        local, domain = parts
        
        # Different types of typos
        typo_type = random.choice(["swap", "missing", "extra", "duplicate"])
        local_chars = list(local)
        pos = random.randint(1, len(local_chars) - 2)
        
        if typo_type == "swap" and pos < len(local_chars) - 1:
            local_chars[pos], local_chars[pos+1] = local_chars[pos+1], local_chars[pos]
        elif typo_type == "missing":
            local_chars.pop(pos)
        elif typo_type == "extra":
            local_chars.insert(pos, random.choice("abcdefghijklmnopqrstuvwxyz"))
        elif typo_type == "duplicate":
            local_chars.insert(pos, local_chars[pos])
        
        var["email"] = f"{''.join(local_chars)}@{domain}"
        var["identifier"] = fake.uuid4()  # Generate a new UUID
        return var, {
            "variation_type": "email_typo", 
            "field_name": "email",
            "original_value": original_email,
            "varied_value": var["email"]
        }
    
    # Domain suffix change based on language list
    if selected_variation == "email_domain_change_list":
        var = copy.deepcopy(entity)
        original_email = var["email"]
        parts = original_email.split('@')
        local, domain = parts
        domain_parts = domain.split('.')
        
        # Get first language code from availableLanguage that matches our target languages
        target_langs = ["nl", "de", "et"]
        available_langs = [lang.lower() for lang in var["availableLanguage"]]
        matching_langs = [lang for lang in available_langs if lang in target_langs]
        
        if matching_langs:
            domain_parts[-1] = matching_langs[0]
            new_domain = '.'.join(domain_parts)
            var["email"] = f"{local}@{new_domain}"
            var["identifier"] = fake.uuid4()  # Generate a new UUID
            return var, {
                "variation_type": "email_domain_change", 
                "field_name": "email",
                "original_value": original_email,
                "varied_value": var["email"]
            }
    
    # Domain suffix change based on language string
    if selected_variation == "email_domain_change_str":
        var = copy.deepcopy(entity)
        original_email = var["email"]
        parts = original_email.split('@')
        local, domain = parts
        domain_parts = domain.split('.')
        
        # Try to extract language from string format
        try:
            lang_list = [l.strip().strip("'\"") for l in var["availableLanguage"].strip("[]").split(",")]
            target_langs = ["nl", "de", "et"]
            matching_langs = [lang.lower() for lang in lang_list if lang.lower() in target_langs]
            
            if matching_langs:
                domain_parts[-1] = matching_langs[0]
                new_domain = '.'.join(domain_parts)
                var["email"] = f"{local}@{new_domain}"
                var["identifier"] = fake.uuid4()  # Generate a new UUID
                return var, {
                    "variation_type": "email_domain_change", 
                    "field_name": "email",
                    "original_value": original_email,
                    "varied_value": var["email"]
                }
        except:
            pass  # If parsing fails, fall through to default

    # Default variation if none of the above apply
    var_default = copy.deepcopy(entity)
    var_default["identifier"] = fake.uuid4()  # Generate a new UUID
    return var_default, {
        "variation_type": "no_change", 
        "field_name": "email",
        "original_value": var_default.get("email", ""),
        "varied_value": var_default.get("email", "")
    }

def export_duplicate_registry(filename='duplicate_registry.csv'):
    """
    Export the duplicate registry to a CSV file for reference
    """
    import csv
    
    with open(filename, 'w', newline='',encoding='utf-8') as csvfile:
        fieldnames = ['original_id', 'duplicate_id', 'entity_type', 'variation_type', 
                     'field_name', 'original_value', 'varied_value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for original_id, duplicates in duplicate_registry.items():
            for dup in duplicates:
                writer.writerow({
                    'original_id': original_id,
                    'duplicate_id': dup['duplicate_id'],
                    'entity_type': dup['entity_type'],
                    'variation_type': dup['variation_type'],
                    'field_name': dup['field_name'],
                    'original_value': dup.get('original_value', ''),
                    'varied_value': dup.get('varied_value', '')
                })