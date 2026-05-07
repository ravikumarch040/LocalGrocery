# GitHub Wiki Page Order (Prepared from Workspace Docs)

This file organizes the repository Markdown documentation into a practical GitHub Wiki publishing order.

## Scope analyzed

- Total Markdown files detected: `151`
- Documentation files after excluding generated/vendor/cache docs (`venv`, `.pytest_cache`, package licenses, iOS launch-image placeholders): `95`
- Reference image files found (`png/jpg/jpeg/gif/webp/svg`): `0`
- Markdown image references found (`![...](...)`): `0`

## Recommended Wiki Structure and Publishing Order

Use this order when creating pages in the GitHub Wiki so readers get context first, then architecture, implementation, operations, and verification.

### 1) Home and Entry Points

1. `README.md` -> **Home**
2. `DOCUMENTATION_INDEX.md` -> **Documentation Index**
3. `QUICK_REFERENCE.md` -> **Quick Reference**
4. `README_IMPLEMENTATION.md` -> **Implementation Status (Overview)**

### 2) Product and Vision

5. `wiki/Product/Vision.md` -> **Product Vision**
6. `wiki/Product/Problem_Statement.md` -> **Problem Statement**
7. `wiki/Product/Business_Model.md` -> **Business Model**
8. `wiki/Product/Requirements.md` -> **Requirements**
9. `wiki/Product/Roadmap.md` -> **Product Roadmap**
10. `wiki/Product/Implementation_Roadmap.md` -> **Implementation Roadmap**

### 3) Architecture

11. `wiki/Architecture/System_Overview.md` -> **System Overview**
12. `wiki/Architecture/Design_and_Architecture.md` -> **Design and Architecture**
13. `wiki/Architecture/Component_Architecture.md` -> **Component Architecture**
14. `wiki/Architecture/Detailed_Component_Diagram.md` -> **Detailed Component Diagram**
15. `wiki/Architecture/Data_Architecture.md` -> **Data Architecture**
16. `wiki/Architecture/Security_Architecture.md` -> **Security Architecture**

### 4) Backend Platform

17. `backend/README.md` -> **Backend Overview**
18. `wiki/Backend/PYTHON_SETUP_GUIDE.md` (or `backend/PYTHON_SETUP_GUIDE.md`) -> **Backend Setup (Python + FastAPI)**
19. `BACKEND_QUICK_START.md` -> **Backend Quick Start**
20. `backend/SERVICES_QUICK_REFERENCE.md` -> **Backend Services Quick Reference**
21. `wiki/Backend/TECH_STACK_ANALYSIS.md` -> **Tech Stack Analysis**
22. `wiki/Backend/API_Overview.md` -> **API Overview**
23. `wiki/Backend/API_Contracts.md` -> **API Contracts**
24. `wiki/Backend/Database_Schema.md` -> **Database Schema**
25. `wiki/Backend/ASYNC_ORM_SERIALIZATION_PATTERN.md` -> **Async ORM Serialization Pattern**
26. `wiki/Backend/Retailer_Onboarding_KYC_Flow.md` -> **Retailer Onboarding and KYC Flow**

### 5) Service-Level Documentation

27. `backend/services/auth_service/README.md` -> **Auth Service**
28. `backend/services/order_service/README.md` -> **Order Service**
29. `backend/services/cart_service/README.md` -> **Cart Service**
30. `backend/services/catalog_service/README.md` -> **Catalog Service**
31. `backend/services/inventory_service/README.md` -> **Inventory Service**
32. `backend/services/delivery_service/README.md` -> **Delivery Service**
33. `backend/services/payment_service/README.md` -> **Payment Service**
34. `backend/services/notification_service/README.md` -> **Notification Service**
35. `INVENTORY_SERVICE_GUIDE.md` -> **Inventory Service Deep Dive**

### 6) Frontend and Mobile

36. `frontend/flutter/README.md` -> **Flutter Apps Overview**
37. `frontend/flutter/QUICK_START.md` -> **Flutter Quick Start**
38. `frontend/flutter/FIREBASE_SETUP.md` -> **Firebase Setup**
39. `frontend/flutter/DEVELOPER_REFERENCE.md` -> **Flutter Developer Reference**
40. `frontend/flutter/DEVELOPMENT_ROADMAP.md` -> **Flutter Development Roadmap**
41. `frontend/flutter/IMPLEMENTATION_STATUS.md` -> **Flutter Implementation Status**
42. `frontend/flutter/IMPLEMENTATION_SUMMARY.md` -> **Flutter Implementation Summary**
43. `frontend/flutter/apps/customer_app/README.md` -> **Customer App**
44. `frontend/flutter/apps/delivery_app/README.md` -> **Delivery App**
45. `frontend/flutter/apps/retailer_app/README.md` -> **Retailer App**
46. `wiki/Mobile/Flutter_App_UI_Flow.md` -> **Flutter App UI Flow**
47. `wiki/Mobile/Customer_App_Flows.md` -> **Customer App Flows**
48. `wiki/Mobile/Delivery_App_Flows.md` -> **Delivery App Flows**
49. `wiki/Mobile/Retailer_App_Flows.md` -> **Retailer App Flows**

### 7) Wireframes and UX Artifacts

50. `wiki/FLUTTER WIREFRAMES/Flutter Navigation Structure.md` -> **Flutter Navigation Structure**
51. `wiki/FLUTTER WIREFRAMES/CUSTOMER APP WIREFRAMES.md` -> **Customer App Wireframes**
52. `wiki/FLUTTER WIREFRAMES/DELIVERY PARTNER APP WIREFRAMES.md` -> **Delivery Partner App Wireframes**
53. `wiki/FLUTTER WIREFRAMES/RETAILER APP WIREFRAMES.md` -> **Retailer App Wireframes**
54. `wiki/FLUTTER WIREFRAMES/ADMIN DASHBOARD WIREFRAMES.md` -> **Admin Dashboard Wireframes**

### 8) Delivery, Release, and Operations

55. `wiki/DevOps/CI_CD_Strategy.md` -> **CI/CD Strategy**
56. `wiki/DevOps/Release_Process.md` -> **Release Process**
57. `wiki/SETUP_COMPLETE.md` -> **Setup Completion**
58. `wiki/MVP_STACK_MIGRATION.md` -> **MVP Stack Migration**

### 9) Validation, Testing, and Reporting

59. `TEST_PLAN.md` -> **Test Plan**
60. `TESTING_GUIDE.md` -> **Integration Testing Guide**
61. `TESTING_INFRASTRUCTURE_SUMMARY.md` -> **Testing Infrastructure Summary**
62. `TESTING_OTP_FLOW.md` -> **OTP Testing Notes**
63. `TEST_REPORT.md` -> **Test Report**
64. `MICROSERVICES_VERIFICATION_COMPLETE.md` -> **Microservices Verification**
65. `TASK_COMPLETION_SUMMARY.md` -> **Task Completion Summary**

### 10) Status, Checklists, and Change History

66. `MICROSERVICES_STATUS.md` -> **Microservices Status**
67. `BACKEND_STATUS_OVERVIEW.md` -> **Backend Status Overview**
68. `BACKEND_DEVELOPMENT_ROADMAP.md` -> **Backend Development Roadmap**
69. `BACKEND_ACTION_CHECKLIST.md` -> **Backend Action Checklist**
70. `IMPLEMENTATION_CHECKLIST.md` -> **Implementation Checklist**
71. `SERVICES_ARCHITECTURE_COMPLETE.md` -> **Services Architecture Complete**
72. `COMPLETE_MICROSERVICES_GUIDE.md` -> **Complete Microservices Guide**
73. `STORE_PRODUCT_API_SUMMARY.md` -> **Store Product API Summary**
74. `STORE_PRODUCT_API_STATUS.md` -> **Store Product API Status**
75. `wiki/Backend/STORE_PRODUCT_API_QUICK_REFERENCE.md` -> **Store Product API Quick Reference**
76. `wiki/Backend/STORE_PRODUCT_API_CHECKLIST.md` -> **Store Product API Checklist**
77. `wiki/Backend/STORE_PRODUCT_API_COMPLETION.md` -> **Store Product API Completion**
78. `wiki/Backend/DEBUGGING_JOURNEY.md` -> **Debugging Journey**
79. `wiki/DOCUMENTATION_REORGANIZATION.md` -> **Documentation Reorganization**
80. `wiki/GITIGNORE_UPDATE.md` -> **.gitignore Update**

### 11) Internal/Utility Docs (Optional in public wiki)

81. `FILE_MANIFEST.md` -> **File Manifest (Internal)**
82. `backend/services/cart_service/FILE_INDEX.md` -> **Cart Service File Index (Internal)**
83. `backend/services/cart_service/QUICK_START.md` -> **Cart Service Quick Start (Detailed/Internal)**
84. `backend/services/cart_service/IMPLEMENTATION_COMPLETE.md` -> **Cart Service Implementation Complete (Detailed/Internal)**
85. `backend/services/cart_service/CART_SERVICE_IMPLEMENTATION_SUMMARY.md` -> **Cart Service Implementation Summary (Detailed/Internal)**
86. `backend/services/cart_service/TESTING_CHECKLIST.md` -> **Cart Service Testing Checklist (Detailed/Internal)**
87. `backend/services/catalog_service/IMPLEMENTATION_SUMMARY.md` -> **Catalog Implementation Summary (Detailed/Internal)**
88. `backend/services/catalog_service/SEEDING_GUIDE.md` -> **Catalog Seeding Guide (Detailed/Internal)**
89. `backend/services/catalog_service/SEEDING_SUCCESS.md` -> **Catalog Seeding Success (Historical/Internal)**
90. `backend/services/delivery_service/SERVICE_STATUS.md` -> **Delivery Service Status (Detailed/Internal)**
91. `backend/services/auth_service/TEST_RESULTS.md` -> **Auth Test Results (Historical/Internal)**
92. `backend/services/auth_service/TEST_RESULTS_FINAL.md` -> **Auth Test Results Final (Historical/Internal)**
93. `frontend/flutter/IMPLEMENTATION_STATUS.md` -> **Flutter Status Snapshot (Historical)**
94. `frontend/flutter/IMPLEMENTATION_SUMMARY.md` -> **Flutter Summary Snapshot (Historical)**
95. `copilot-instructions.md` -> **Agent/Tooling Instructions (Do not publish to product wiki)**

## Duplicate/Overlap Recommendation

- Prefer canonical source under `wiki/` when duplicate content exists in root/backend folders.
- Keep only one setup guide page in wiki navigation (prefer `wiki/Backend/PYTHON_SETUP_GUIDE.md`).
- Keep deep service internals as child pages or an "Engineering Notes" section to avoid cluttering top-level wiki navigation.

## Reference Image Preparation

No standalone image files or markdown image links were found in the workspace scan.

If you want visuals in wiki pages, options are:

- Export diagrams/wireframes to `wiki/assets/` and reference them with relative links.
- Keep existing Mermaid-style textual diagrams directly in markdown pages.

