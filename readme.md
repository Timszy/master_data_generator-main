# Master Data Generator

## 📖 Overview
This repository provides a framework for generating **synthetic healthcare organizational data** starting from **tabular (CSV)** and converted into **knowledge graph (RDF/Turtle)** formats. 

The synthetic data models a simplified but realistic structure of healthcare organizations, including their service departments, personnel, and associated addresses, with a focus on European countries (Netherlands, Austria, Estonia). Each healthcare organization is linked to service departments, healthcare personnel (who are also represented in the Person table), and addresses. The generator ensures realistic patterns such as region-specific names, addresses, and email formats.

The objective of this data generation is to facilitate **benchmarking of entity deduplication methods**

---

## CSV Tables and Data Description

- **HealthcareOrganization**: Main table representing healthcare organizations.
- **HealthcarePersonnel**: Contains healthcare personnel, linked to organizations.
- **Person**: Inherits from HealthcarePersonnel, adding personal information.
- **ServiceDepartment**: Represents departments within an organization, linked to it.
- **Address**: Contains address details, used by organizations and departments.
- **ContactPoint**: Contains contact point details, used by organizations and departments.

This data is stored in 6 CSV files one for each relationship.

---

## 🌐 Knowledge Graph Convertion
With these 6 CSV files, the repository also includes functionality to convert tabular data into a **Schema.org-compliant knowledge graph**.  

- Uses [`rdflib`](https://rdflib.readthedocs.io/) for RDF generation.  
- Serializes data in **Turtle (`.ttl`) format**.  
- Assigns unique URIs based on fake uuid's to each entity (e.g., `http://example.org/HealthcareOrganization/uuid`).  

This enables graph-based experiments such as embeddings, SPARQL queries, and deduplication tasks.

---

## 📂 Knowledge graph Description

Below is the **authoritative master data format** used by this project, with each attribute mapped to its nearest **Schema.org** property.
PK == Primary Key, FK == Foreign Key

### Address
_Source: [`schema:PostalAddress`](https://schema.org/PostalAddress)_

| Column        | Type   | Constraints | Schema.org Mapping             |
|---------------|--------|-------------|--------------------------------|
| `identifier`  | string | PK          | `schema:identifier`            |
| `text`        | string |             | `schema:streetAddress`         |
| `city`        | string |             | `schema:addressLocality`       |
| `postal_code` | string |             | `schema:postalCode`            |
| `country`     | string |             | `schema:addressCountry`        |

### Contact
_Source: [`schema:ContactPoint`](https://schema.org/ContactPoint)_

| Column              | Type   | Constraints | Schema.org Mapping      |
|---------------------|--------|-------------|-------------------------|
| `identifier`        | string | PK          | `schema:identifier`                    |
| `phone`             | string |             | `schema:telephone`      |
| `email`             | string |             | `schema:email`          |
| `fax`               | string |             | `schema:faxNumber`      |
| `contact_type`      | string |             | `schema:contactType`    |
| `available_language`| string |             | `schema:availableLanguage` |

### HealthCareOrganization
_Source: [`schema:MedicalOrganization`](https://schema.org/MedicalOrganization)_

| Column       | Type   | Constraints | Schema.org Mapping      |
|--------------|--------|-------------|-------------------------|
| `identifier` | string | PK          | `schema:identifier`     |
| `name`       | string | NOT NULL    | `schema:name`           |
| `contact`    | string | FK -> Contact.identifier | `schema:contactPoint` |
| `address`    | string | FK -> Address.identifier | `schema:address`     |

### ServiceDepartment
_Source: Organization **department** pattern (`schema:parentOrganization`)_

| Column        | Type   | Constraints | Schema.org Mapping            |
|---------------|--------|-------------|--------------------------------|
| `identifier`  | string | PK          | `schema:identifier`           |
| `name`        | string | NOT NULL    | `schema:name`                 |
| `is_part_of`  | string | FK -> HealthCareOrganization.identifier | `schema:parentOrganization` |
| `contact`     | string | FK -> Contact.identifier | `schema:contactPoint`        |
| `address`     | string | FK -> Address.identifier | `schema:address`            |

> In the KG, `ServiceDepartment → schema:parentOrganization → HealthCareOrganization`.  


### Person
_Source: [`schema:Person`](https://schema.org/Person)_

| Column         | Type | Constraints | Schema.org Mapping   |
|----------------|------|-------------|----------------------|
| `identifier`   | string | PK        | `schema:identifier`  |
| `name`         | string | NOT NULL  | `schema:name`        |
| `birth_date`   | date   |           | `schema:birthDate`   |
| `gender`       | string |           | `schema:gender`      |
| `knows_language` | string |         | `schema:knowsLanguage` |

### HealthCarePersonnel
_Source: specialization of Person_

| Column       | Type   | Constraints                               | Schema.org Mapping |
|--------------|--------|-------------------------------------------|--------------------|
| `identifier` | string | UNIQUE, FK -> Person.identifier           | `schema:identifier` |
| `job_title`  | string |                                           | `schema:jobTitle`  |
| `institution`| string | FK -> HealthCareOrganization.identifier   | `schema:worksFor`  |
| `department` | string | FK -> ServiceDepartment.identifier        | `schema:memberOf`  |
| `email`      | string |                                           | `schema:email`     |

---

## 🔗 Relationships (FKs → RDF Relations)

- **Organization ↔ Department**
  - `ServiceDepartment.is_part_of` → `schema:parentOrganization`
  - (Optional inverse) `HealthCareOrganization` → `schema:department` → `ServiceDepartment`

- **Addresses & Contacts**
  - `HealthCareOrganization.address` → `schema:address` → `PostalAddress`
  - `ServiceDepartment.address` → `schema:address` → `PostalAddress`
  - `HealthCareOrganization.contact` → `schema:contactPoint` → `ContactPoint`
  - `ServiceDepartment.contact` → `schema:contactPoint` → `ContactPoint`

- **People & Roles**
  - `HealthCarePersonnel.institution` → `schema:worksFor` → `HealthCareOrganization`
  - `HealthCarePersonnel.department` → `schema:memberOf` → `ServiceDepartment`
  - `HealthCarePersonnel.identifier` references `Person.identifier` (inheritance of core person attributes).

---

# Codebase file descriptions

## 📂 CSV Generation Code Overview

The repository includes several scripts and notebooks dedicated to generating and varying the **tabular CSV data**:

- **`data_creator.py`**  
  Main generator script that produces the baseline synthetic dataset.  
  It outputs CSVs for addresses, organizations, service departments, personnel, and persons, using Faker to localize names and addresses for the Netherlands, Austria, and Estonia. 
  Dataset size can be controlled with parameters: NUM_ORGANIZATIONS, MIN_DEPARTMENTS_PER_ORG, MAX_DEPARTMENTS_PER_ORG, MIN_PERSONNEL_PER_ORG, MAX_PERSONNEL_PER_ORG can be specified to change dataset sizes accordingly.

- **`variation_helpers.py`**  
  Module with functions to inject noise (e.g., typos, abbreviations, translations, missing attributes) into entities.  
  It maintains a duplicate registry and can export ground-truth mappings for deduplication benchmarking. This module is used in all the other scripts.

- **`data_variator.ipynb`**  
  Notebook that can apply the different types of noise to the base dataset using functionalities of variation_helpers

- **`Turndupeintoset_missing_attributes.ipynb`**  
  Processes duplicate data related to missing attributes.  
  Ensures that the corresponding golden standard files remain consistent and UUIDs are correctly updated.

- **`Turndupeintoset_relation.ipynb`**  
  Handles duplicates in relation-based data (e.g., organization–department links).  
  Validates that golden standards are accurate and synchronizes UUIDs across related entities.

- **`Turndupeintoset_syntactic.ipynb`**  
  Processes syntactic duplicates such as typos and formatting inconsistencies.  
  Updates UUIDs where needed and makes sure the golden standards match the introduced variations.

Golden standards are saved in ground_truths

➡️ **Execution order:**  
`data_creator.py` → `data_variator.ipynb` → one of the `Turndupeintoset_*` notebooks (depending on which type of duplicates/noise is being validated).

## 🧪 Noise Types applied to the CSV's 

To better simulate real-world integration scenarios, the dataset supports two major categories of noise: **Syntactic Noise** and **Completeness Noise**.

### 🔤 Syntactic Noise
Syntactic noise alters the textual representation of entities without changing their underlying meaning.  
This includes spelling mistakes, formatting differences, abbreviations, or even multilingual variants.  

We distinguish two severities:
- **Simple noise** — surface-level changes usually captured by string similarity or normalization methods.  
  Examples: typos, abbreviated names (`S. Janssen`), swapped name order (`Janssen Eva`), date formatting differences, or email domain changes.
- **Complex noise** — changes requiring semantic reasoning, context, or multilingual knowledge.  
  Examples: translations (`Radiology → Radiologie`), synonyms/aliases (`nl → Dutch`), or organizational abbreviations (`St. John’s Hospital → SJH`).

### 🧩 Completeness Noise
Completeness noise simulates **missing or incomplete information**, which often arises in real-world data entry or system integration.  
Unlike syntactic noise, these errors don’t create conflicting values but instead reduce the available information for deduplication.

Two subcategories are introduced:
- **Attribute completeness** — missing literals/fields within an entity.  
  Example: an `Address` without a postal code, or a `ContactPoint` without a phone number.
- **Structural/relational completeness** — missing edges between entities in the graph.  
  Example: a `ServiceDepartment` missing its link to a `HealthcareOrganization`, or `HealthcarePersonnel` not linked to their department.

Our initial focus is on **structured missingness** (values omitted by design or system constraints), as this is a common pattern in integrated healthcare datasets. The variations do however provide the possibility to change the percentage of data to be removed.

## 📂 Knowledge Graph Conversion

All generated CSVs are stored in **`src/Data_Source/`** and can be transformed into **RDF/Turtle knowledge graphs** using the `ConvertCSVtoKG.py` script which can be found under src.

- **`ConvertCSVtoKG.py`**  
  Loads the CSV files for organizations, departments, personnel, persons, addresses, and contact points.  
  It builds two RDF graphs at the same time, maps each table to its Schema.org class (`MedicalOrganization`, `Department`, `Person`, `PostalAddress`, `ContactPoint`), and writes the output as `.ttl` files in `src/Knowledge Graphs/`.

The eventual Knowledge graphs alongside their respective ground truth are used to compare. To compare one needs at least three files
The original clean knowledge graph, which is healthcare_graph_Main and one of the variated graphs alongside the golden standard file belonging to the variant.

## 🚀 How to Install

1. **Set up the environment**
   ```bash
   python -m venv venv
   # Activate venv (Windows)
   venv\Scripts\Activate

   pip install -r requirements.txt

## 🔮 Possible Extensions

There are several directions in which this project can be extended:

- **Schema fluidity**  
  Support different schema sizes and differ between the number of attributes or relations one entity can have.

- **Noise configuration**  
  Add CLI or config options to control noise directly when generating data.

- **Extend scope**  
  Extend Faker locales beyond NL, AT, and EE to cover other European (or global) healthcare settings, add different variations.

- **Visualization tools**  
  Provide simple scripts or notebooks to visualize entity counts, duplicate rates, or graph structures.

- **SPARQL validation & SHACL**  
  Add integrity checks and competency queries to verify the generated knowledge graphs.

