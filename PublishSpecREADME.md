# Postman OpenAPI Management

This folder contains Makefile targets and helper files for publishing and managing OpenAPI specs in Postman’s **Spec Hub**.

---

## **Targets Overview**

### **1. `make postman-api-full-publish`**
- Deletes **all existing specs** in the configured workspace.
- Publishes `openapi/c2m_openapi_spec_final.yaml` as `index.yaml`.
- Stores the new **Spec ID** in `postman/postman_spec_uid.txt`.

### **2. `make postman-api-update`**
- Updates the existing spec (`index.yaml`) using the saved **Spec ID**.
- Use this target after making changes to your OpenAPI file.

### **3. `make postman-api-list-specs`**
- Lists all specs in the workspace with their **name**, **ID**, **type**, and **last updated timestamp**.

### **4. `make postman-api-delete-old-specs`**
- Deletes all but the **most recent spec** in the workspace.

### **5. `make postman-api-debug`**
- Verifies the **Postman API Key** and **workspace connectivity**.
- Outputs all specs and APIs visible to the workspace.

---

## **Common Workflows**

### **Initial Setup (Clean Slate)**
```bash
make postman-api-full-publish
