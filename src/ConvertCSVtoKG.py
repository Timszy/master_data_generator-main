import pandas as pd
import re
import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD, RDFS

print("===== HEALTHCARE KNOWLEDGE GRAPH GENERATOR =====")

# ============= 1. DATA LOADING =============

print("\n1. Loading CSV data...")
#Load CSV files
healthcare_org_df = pd.read_csv("src/Data_Source/Sample_15_test/sample_relation/HealthcareOrganization.csv")
service_dept_df = pd.read_csv("src/Data_Source/Sample_15_test/sample_relation/ServiceDepartment.csv")
Address_df = pd.read_csv("src/Data_Source/Sample_15_test/sample_relation/Address.csv")
HealthcarePersonnel_df = pd.read_csv("src/Data_Source/Sample_15_test/sample_relation/HealthcarePersonnel.csv")
Person_df = pd.read_csv("src/Data_Source/Sample_15_test/sample_relation/Person.csv")
contact_point_df = pd.read_csv("src/Data_Source/Sample_15_test/sample_relation/ContactPoint.csv")

# sound = "low"

# healthcare_org_df = pd.read_csv(f"src/Data_Source/Sample_35_train/train_struct/HealthcareOrganization_{sound}.csv")
# service_dept_df = pd.read_csv(f"src/Data_Source/Sample_35_train/train_struct/ServiceDepartment_{sound}.csv")
# Address_df = pd.read_csv(f"src/Data_Source/Sample_35_train/train_struct/Address_{sound}.csv")
# HealthcarePersonnel_df = pd.read_csv(f"src/Data_Source/Sample_35_train/train_struct/HealthcarePersonnel_{sound}.csv")
# Person_df = pd.read_csv(f"src/Data_Source/Sample_35_train/train_struct/Person_{sound}.csv")
# contact_point_df = pd.read_csv(f"src/Data_Source/Sample_35_train/train_struct/ContactPoint_{sound}.csv")

# healthcare_org_df = pd.read_csv(f"src/Data_Source/Sample_35_train/traindata_dupe/HealthcareOrganization.csv")
# service_dept_df = pd.read_csv(f"src/Data_Source/Sample_35_train/traindata_dupe/ServiceDepartment.csv")
# Address_df = pd.read_csv(f"src/Data_Source/Sample_35_train/traindata_dupe/Address.csv")
# HealthcarePersonnel_df = pd.read_csv(f"src/Data_Source/Sample_35_train/traindata_dupe/HealthcarePersonnel.csv")
# Person_df = pd.read_csv(f"src/Data_Source/Sample_35_train/traindata_dupe/Person.csv")
# contact_point_df = pd.read_csv(f"src/Data_Source/Sample_35_train/traindata_dupe/ContactPoint.csv")


# noise = 'low'
# # Load variant CSV files
# healthcare_org_df_var = pd.read_csv(f"src/Data_Source/Sample_15_test/sample_struct/HealthcareOrganization_{noise}.csv")
# service_dept_df_var = pd.read_csv(f"src/Data_Source/Sample_15_test/sample_struct/ServiceDepartment_{noise}.csv")
# Address_df_var = pd.read_csv(f"src/Data_Source/Sample_15_test/sample_struct/Address_{noise}.csv")
# HealthcarePersonnel_df_var = pd.read_csv(f"src/Data_Source/Sample_15_test/sample_struct/HealthcarePersonnel_{noise}.csv")
# Person_df_var = pd.read_csv(f"src/Data_Source/Sample_15_test/sample_struct/Person_{noise}.csv")
# contact_point_df_var = pd.read_csv(f"src/Data_Source/Sample_15_test/sample_struct/ContactPoint_{noise}.csv")

#Load variant CSV files
healthcare_org_df_var = pd.read_csv(f"src/Data_Source/Sample_35_train/train_relation/HealthcareOrganization.csv")
service_dept_df_var = pd.read_csv(f"src/Data_Source/Sample_35_train/train_relation/ServiceDepartment.csv")
Address_df_var = pd.read_csv(f"src/Data_Source/Sample_35_train/train_relation/Address.csv")
HealthcarePersonnel_df_var = pd.read_csv(f"src/Data_Source/Sample_35_train/train_relation/HealthcarePersonnel.csv")
Person_df_var = pd.read_csv(f"src/Data_Source/Sample_35_train/train_relation/Person.csv")
contact_point_df_var = pd.read_csv(f"src/Data_Source/Sample_35_train/train_relation/ContactPoint.csv")



# ============= 3. CREATE AND POPULATE KNOWLEDGE GRAPHS =============

print("\n4. Creating knowledge graphs...")
# Initialize RDF graphs
g_original = Graph()
g_var = Graph()

# Define namespaces for both graphs
for g in [g_original, g_var]:
    g.bind("schema", SCHEMA := Namespace("https://schema.org/"))
    g.bind("ex", EX := Namespace("http://example.org/"))
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)

# Helper function to process entity data for both graphs
def process_entity(entity_type, original_df, var_df, process_func):
    """
    Process entities for both original and replacement graphs using the same function
    
    Args:
        entity_type: String name of the entity type (for logging)
        original_df: DataFrame for original graph
        var_df: DataFrame for replacement graph
        process_func: Function to process a single row for a graph
    """
    print(f"  - Adding {entity_type}...")
    
    # Process each dataset with its corresponding graph
    for name, (df, graph) in [("Original", (original_df, g_original)), 
                              ("Variant", (var_df, g_var))]:
        for _, row in df.iterrows():
            process_func(graph, row)

# ---- HEALTHCARE ORGANIZATIONS ----
def process_org(g, row):
    org_uri = URIRef(f"{EX}HealthcareOrganization/{row['identifier']}")
    
    # Use only schema.org class
    g.add((org_uri, RDF.type, SCHEMA.MedicalOrganization))
    
    g.add((org_uri, SCHEMA.identifier, Literal(row['identifier'], datatype=XSD.string)))
    g.add((org_uri, SCHEMA.name, Literal(row['healthcareOrganizationName'], datatype=XSD.string)))
    g.add((org_uri, RDFS.label, Literal(row['healthcareOrganizationName'], datatype=XSD.string)))  # <-- Add this line
    
    # Add address 
    address_uri = URIRef(f"{EX}Address/{row['address']}")
    g.add((org_uri, SCHEMA.address, address_uri))
    
    contact_point_uri = URIRef(f"{EX}ContactPoint/{row['contactPoint']}")
    g.add((org_uri, SCHEMA.contactPoint, contact_point_uri))

process_entity("Healthcare Organizations", healthcare_org_df, healthcare_org_df_var, process_org)

# ---- SERVICE DEPARTMENTS ----
def process_dept(g, row):
    dept_uri = URIRef(f"{EX}ServiceDepartment/{row['identifier']}")
    
    # Use only schema.org class
    g.add((dept_uri, RDF.type, SCHEMA.Department))
    
    g.add((dept_uri, SCHEMA.identifier, Literal(row['identifier'], datatype=XSD.string)))
    g.add((dept_uri, SCHEMA.name, Literal(row['serviceDepartmentName'], datatype=XSD.string)))
    g.add((dept_uri, RDFS.label, Literal(row['serviceDepartmentName'], datatype=XSD.string)))  # <-- Add this line
    
    # Add address
    address_uri = URIRef(f"{EX}Address/{row['address']}")
    g.add((dept_uri, SCHEMA.address, address_uri))
    
    # Link to parent organization if specified
    org_uri = URIRef(f"{EX}HealthcareOrganization/{row['isPartOf']}")
    g.add((dept_uri, SCHEMA.parentOrganization, org_uri))
    
    contact_point_uri = URIRef(f"{EX}ContactPoint/{row['contactPoint']}")
    g.add((dept_uri, SCHEMA.contactPoint, contact_point_uri))

process_entity("Service Departments", service_dept_df, service_dept_df_var, process_dept)

# ---- CONTACT POINTS ----
def process_contact(g, row):
    contact_point_uri = URIRef(f"{EX}ContactPoint/{row['identifier']}")
    
    g.add((contact_point_uri, RDF.type, SCHEMA.ContactPoint))
    
    # Add contact point properties
    g.add((contact_point_uri, SCHEMA.identifier, Literal(row['identifier'], datatype=XSD.string)))
    g.add((contact_point_uri, SCHEMA.contactType, Literal(row['contactType'], datatype=XSD.string)))
    g.add((contact_point_uri, RDFS.label, Literal(row['contactType'], datatype=XSD.string)))

    g.add((contact_point_uri, SCHEMA.telephone, Literal(row['phone'], datatype=XSD.string)))
    g.add((contact_point_uri, SCHEMA.email, Literal(row['email'], datatype=XSD.string)))
    g.add((contact_point_uri, SCHEMA.availableLanguage, Literal(row['availableLanguage'], datatype=XSD.string)))
    g.add((contact_point_uri, SCHEMA.faxNumber, Literal(row['fax'], datatype=XSD.string)))

process_entity("Contact Points", contact_point_df, contact_point_df_var, process_contact)

# ---- PERSONS ----
def process_person(g, row):
    person_uri = URIRef(f"{EX}Person/{row['identifier']}")
    
    # Define this entity as a Person according to schema.org
    g.add((person_uri, RDF.type, SCHEMA.Person))
    
    # Add properties with datatypes
    g.add((person_uri, SCHEMA.identifier, Literal(row['identifier'], datatype=XSD.string)))
    g.add((person_uri, SCHEMA.name, Literal(row['personName'], datatype=XSD.string)))
    g.add((person_uri, RDFS.label, Literal(row['personName'], datatype=XSD.string)))  # <-- Add this line
    
    # Add birthDate if available - use date datatype
    if pd.notnull(row.get('birthDate')):
        g.add((person_uri, SCHEMA.birthDate, Literal(row['birthDate'], datatype=XSD.string)))
    
    # Add gender if available
    if pd.notnull(row.get('gender')):
        g.add((person_uri, SCHEMA.gender, Literal(row['gender'], datatype=XSD.string)))
    
    # Add language if available
    if pd.notnull(row.get('knowsLanguage')):
        g.add((person_uri, SCHEMA.knowsLanguage, Literal(row['knowsLanguage'], datatype=XSD.string)))

process_entity("Persons", Person_df, Person_df_var, process_person)

# ---- HEALTHCARE PERSONNEL ----
def process_personnel(g, row, person_df):
    personnel_id = row['identifier']
    
    # Find matching Person record if it exists
    matching_person = person_df[person_df['identifier'] == personnel_id]
    has_person_data = not matching_person.empty
    
    # Use the person URI directly - no separate personnel_uri variable needed
    person_uri = URIRef(f"{EX}Person/{personnel_id}")
    
    # Only add type and identifier if it doesn't already exist as a Person
    if not has_person_data:
        g.add((person_uri, RDF.type, SCHEMA.Person))
        g.add((person_uri, SCHEMA.identifier, Literal(personnel_id, datatype=XSD.string)))
    
    # Link to institution if available
    if pd.notnull(row.get('institution')):
        org_uri = URIRef(f"{EX}HealthcareOrganization/{row['institution']}")
        g.add((person_uri, SCHEMA.worksFor, org_uri))
    
    # Link to department if available
    if pd.notnull(row.get('department')):
        dept_uri = URIRef(f"{EX}ServiceDepartment/{row['department']}")
        g.add((person_uri, SCHEMA.memberOf, dept_uri))
    
    # Add job title if available
    if pd.notnull(row.get('jobTitle')):
        g.add((person_uri, SCHEMA.jobTitle, Literal(row['jobTitle'], datatype=XSD.string)))
    
    # Add email if available
    if pd.notnull(row.get('email')):
        g.add((person_uri, SCHEMA.email, Literal(row['email'], datatype=XSD.string)))

# Special case for personnel since it needs person dataframe too
print("  - Adding Healthcare Personnel...")
for _, row in HealthcarePersonnel_df.iterrows():
    process_personnel(g_original, row, Person_df)

for _, row in HealthcarePersonnel_df_var.iterrows():
    process_personnel(g_var, row, Person_df_var)

# ---- ADDRESSES ----
def process_address(g, row):
    address_uri = URIRef(f"{EX}Address/{row['identifier']}")
    
    g.add((address_uri, RDF.type, SCHEMA.PostalAddress))
    
    g.add((address_uri, SCHEMA.identifier, Literal(row['identifier'], datatype=XSD.string)))
    
    if pd.notnull(row.get('text')):
        g.add((address_uri, SCHEMA.streetAddress, Literal(row['text'], datatype=XSD.string)))
        g.add((address_uri, RDFS.label, Literal(row['text'], datatype=XSD.string)))  # <-- Add this line
    

    if pd.notnull(row.get('city')):
        g.add((address_uri, SCHEMA.addressLocality, Literal(row['city'], datatype=XSD.string)))
    
    if pd.notnull(row.get('postalCode')):
        g.add((address_uri, SCHEMA.postalCode, Literal(row['postalCode'], datatype=XSD.string)))
    
    if pd.notnull(row.get('country')):
        g.add((address_uri, SCHEMA.addressCountry, Literal(row['country'], datatype=XSD.string)))

process_entity("Addresses", Address_df, Address_df_var, process_address)

# ============= 5. SAVE KNOWLEDGE GRAPHS =============

print("\n5. Saving knowledge graphs...")
# Save the graphs
g_original.serialize(destination=f"src/Knowledge Graphs/test.ttl", format="turtle")
g_var.serialize(destination=f"src/Knowledge Graphs/test.ttl", format="turtle")

print("\nDone! Created:")
print("  - healthcare_graph_original.ttl - Graph using original data")
print("  - healthcare_graph_replaced.ttl - Graph with replaced instances")


