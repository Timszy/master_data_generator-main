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

## Codebase file descriptions
├─ data_creator.py
│  └─ Main script to synthesize the tabular CSVs (orgs, departments, personnel, people, addresses, contacts). :contentReference[oaicite:4]{index=4}
├─ variation_helpers.py
│  └─ Helper functions for injecting/handling variations (e.g., typos, missing attributes) for dedupe benchmarking. :contentReference[oaicite:5]{index=5}
├─ data_variator.ipynb
│  └─ Notebook for exploring/creating data variations across the synthetic tables. :contentReference[oaicite:6]{index=6}
├─ Turndupeintoset_missing_attributes.ipynb
│  └─ Notebook to transform duplicate outputs into “set” representations focused on missing-attribute scenarios. :contentReference[oaicite:7]{index=7}
├─ Turndupeintoset_relation.ipynb
│  └─ Notebook to convert duplicate/linkage results into relation-level sets for analysis. :contentReference[oaicite:8]{index=8}
├─ Turndupeintoset_syntactic.ipynb
│  └─ Notebook to build sets of duplicates under syntactic-noise (typos/format) conditions. :contentReference[oaicite:9]{index=9}
├─ ground_truths/
│  └─ Folder intended for ground-truth files used to evaluate deduplication; stores labeled duplicate mappings. :contentReference[oaicite:10]{index=10}
└─ src/
   └─ Source code folder (project modules/utilities live here; use for organized imports). :contentReference[oaicite:11]{index=11}

