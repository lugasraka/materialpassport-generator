# Product Requirements Document (PRD)
## Material Passport Generator

**Version:** 2.0  
**Date:** January 2025  
**Author:** Raka Adrianto  
**Status:** Web App Development Phase

---

## Executive Summary

The Material Passport Generator is an AI-powered web application that automates the creation of digital material passports for building products. It addresses the urgent need for material transparency in construction to enable circular economy practices and comply with emerging EU regulations.

**Problem:** Creating material passports manually is time-consuming (4-8 hours per product) and requires specialized knowledge.

**Solution:** AI/ML system that extracts material composition from technical documents, predicts recyclability, and generates standardized digital passports in minutes.

**Impact:** Enable 90% time reduction in passport creation, support circular economy transition, and facilitate compliance with EU Digital Product Passport regulations.

---

## Problem Statement

### Market Context
- The EU is mandating Digital Product Passports (DPP) for construction products by 2026
- Construction industry generates 35% of global waste (1.3 billion tons annually)
- Material composition data is scattered across PDFs, lacking standardization
- Manufacturers struggle to comply with new regulations
- Circular economy requires transparent material information

### User Pain Points

**Manufacturers:**
- Manual data entry from multiple sources
- Inconsistent formats across product lines
- High cost of compliance
- Limited sustainability expertise

**Architects/Specifiers:**
- Cannot easily compare material sustainability
- Time-consuming to verify circular economy claims
- Need standardized data for LCA tools

**Recyclers:**
- Unknown material composition of demolition waste
- Cannot assess recyclability without testing
- Miss recovery opportunities

---

## User Personas

### Persona 1: Sustainability Manager (Primary)
**Name:** Maria Schmidt  
**Role:** Sustainability Manager at Building Materials Manufacturer  
**Goals:**
- Comply with EU DPP regulations
- Improve product circularity scores
- Reduce time spent on documentation

**Frustrations:**
- Manual data collection from R&D, production, suppliers
- Different formats for different markets
- No automated way to calculate sustainability metrics

**Quote:** *"I spend 40% of my time just gathering data from different departments. I need a system that does this automatically."*

### Persona 2: Circular Economy Consultant
**Name:** James Chen  
**Role:** Consultant advising manufacturers on circular economy  
**Goals:**
- Identify improvement opportunities in product design
- Benchmark clients against industry standards
- Generate recommendations quickly

**Frustrations:**
- Clients don't have structured material data
- Manual analysis of composition
- Hard to quantify circularity improvements

**Quote:** *"I need to see the material composition instantly to advise on recyclability improvements."*

### Persona 3: Architect/Specifier (Secondary)
**Name:** Sara Andersson  
**Role:** Sustainable Design Architect  
**Goals:**
- Specify sustainable materials
- Meet green building certification requirements
- Support client sustainability targets

**Frustrations:**
- Can't easily compare material sustainability
- EPDs don't all have same information
- Manual LCA calculations

---

## Goals & Success Metrics

### Business Goals
1. **Compliance:** Enable manufacturers to meet EU DPP requirements
2. **Efficiency:** Reduce passport creation time by 90%
3. **Adoption:** 100+ material passports generated in Phase 1
4. **Impact:** Measurable increase in material recycling rates

### User Goals
1. Auto-generate passports from existing documents
2. Understand material recyclability immediately
3. Get actionable recommendations for improvement
4. Export in standardized formats

### Success Metrics

**Phase 2 (Web App Development) Metrics:**

**Technical Performance:**
- API response time <200ms (P50), <500ms (P95)
- Page load time <2 seconds
- PDF generation <5 seconds
- System uptime >99%
- Error rate <1%

**Quality Assurance:**
- Test coverage >80% for backend logic
- All 6 models loading successfully
- 100% of API endpoints functional
- Zero critical security vulnerabilities
- Cross-browser compatibility achieved

**Portfolio Demonstration:**
- Clean, professional UI design
- Working end-to-end passport generation flow
- Deployed application (not just local)
- Comprehensive documentation (API docs, user guide)
- 100+ sample passports generated for demo

**User Experience:**
- Mobile responsive design
- Intuitive user interface (no user guide needed)
- Fast loading (<2 seconds)
- Clear error messages
- PDF export working correctly

**Phase 1 (ML Foundation) Metrics - ACHIEVED:**

**Model Performance:**
- Compressive strength prediction R² >0.90 (ACHIEVED: 0.94 with XGBoost)
- Recyclability prediction accuracy >85% (ACHIEVED: 87% with Multi-task NN)
- Model inference <100ms (ACHIEVED: <50ms for all models)
- All 6 models trained and saved successfully

**Data Quality:**
- Dataset: 1,030 concrete samples processed
- Sustainability metrics calculated for all samples
- Feature engineering completed (recycled content, CO2, circularity)
- Data validation pipeline implemented

**Documentation:**
- Complete project documentation (README, PRD, Implementation Plan)
- Jupyter notebooks for data exploration, baseline models, deep learning
- Model performance analysis completed
- Learning insights documented

**Overall Impact Metrics:**

**User Adoption:**
- Generate 100+ material passports successfully
- 500+ page views in first week of launch
- 10+ unique users testing the system
- PDF download rate >70% of generated passports

**Sustainability Impact:**
- 90% of generated passports achieve A or B grade (good sustainability)
- Average recycled content >30% in generated passports
- CO2 emissions calculated and displayed for all passports
- Clear circularity scores (0-100) provided

**Business Value:**
- Time saved: 90% reduction vs manual process (4-8 hours to <5 minutes)
- Demonstration of AI/ML capability for sustainability
- Portfolio-ready project for job applications
- Real-world application of ML in construction industry

**Portfolio & Learning Metrics:**

**Technical Skills Demonstrated:**
- Python ML ecosystem (pandas, scikit-learn, PyTorch)
- Regression, classification, and deep learning
- Feature engineering and model selection
- MLOps basics (model deployment, API design)
- Full-stack development (FastAPI + Next.js)
- Cloud deployment (Vercel + Render)

**Product Management Skills:**
- User research and persona development
- Metric definition and success criteria
- Feature prioritization (MoSCoW)
- Stakeholder mapping
- End-to-end product delivery

**Domain Expertise:**
- Building materials sustainability
- Circular economy principles
- Regulatory landscape (EU DPP)
- Life cycle assessment (LCA) basics

**Execution Quality:**
- Clear documentation throughout
- Version control with Git
- Incremental progress tracking
- Problem-solving documented
- Adaptability based on feedback

---

## Features & Requirements

### Phase 1: Foundation - Machine Learning (Completed)

#### Completed Features
1. ✅ **Data Acquisition & Exploration**
   - Concrete Compressive Strength dataset from UCI ML Repository
   - 1,030 samples with 8 composition features
   - Exploratory data analysis and visualization

2. ✅ **Baseline ML Models**
   - Linear Regression (R²: 0.82, RMSE: 6.5)
   - Random Forest (R²: 0.91, RMSE: 4.2)
   - XGBoost (R²: 0.94, RMSE: 3.1)

3. ✅ **Deep Learning Models**
   - Simple Neural Network (R²: 0.89, RMSE: 4.8)
   - Deep Neural Network (R²: 0.92, RMSE: 3.5)
   - Multi-task Neural Network (Strength R²: 0.90, Recyclability Accuracy: 87%)

4. ✅ **Feature Engineering**
   - Recycled content calculation
   - CO2 emissions estimation
   - Circularity score (0-100)
   - Sustainability grade assignment (A-F)

### Phase 2: Web Application - MVP (Current)

#### Must Have (P0) - Passport Generation Focus

1. **Passport Generation Form**
   - Material composition input (8 fields for concrete)
   - Model selector (6 trained models available)
   - Real-time input validation
   - Example/template data loader
   - Submit with "Generate Passport" action

2. **Passport Display Page**
   - Professional, document-like layout
   - Material composition breakdown table
   - Predictions section with confidence indicators
   - Sustainability metrics with visual gauges
   - QR code for passport verification
   - Certification stamp/badge
   - Print-optimized styling

3. **Core API Endpoints**
   - `POST /api/v1/passport/generate` - Generate new passport
   - `GET /api/v1/passport/{id}` - Retrieve passport
   - `GET /api/v1/passport/{id}/pdf` - Download PDF
   - `GET /api/v1/passport/{id}/qr` - QR code image
   - `GET /api/v1/models` - List available models

4. **Sustainability Metrics**
   - Recycled content percentage (automatically calculated)
   - CO2 emissions estimate (kg CO2/m³)
   - Circularity score (0-100 scale)
   - Sustainability grade (A-F based on metrics)

5. **Export Functionality**
   - PDF download with professional formatting
   - Shareable passport links
   - QR code generation for verification

#### Should Have (P1)

1. **Batch Passport Generation**
   - Upload CSV with multiple compositions
   - Generate multiple passports at once
   - Download all as ZIP file

2. **Passport Gallery**
   - View all generated passports
   - Filter by sustainability grade
   - Sort by date, circularity score, or CO2
   - Search functionality

3. **Model Comparison**
   - Compare predictions from all 6 models
   - Display confidence intervals
   - Visual chart comparison
   - Highlight best-performing model

4. **Recent History**
   - Store recent passports in localStorage
   - Quick access to previous generations
   - One-click regeneration

#### Could Have (P2)

1. **Additional Export Formats**
   - JSON format for integration
   - CSV format for bulk export
   - XML format (for legacy systems)

2. **Advanced Visualizations**
   - Composition pie chart
   - Sustainability radar chart
   - Time-series for different formulations
   - Interactive gauges

3. **Template Library**
   - Pre-built templates for common materials
   - Industry standard compositions
   - Save custom templates

### Phase 3: Enhanced Features (Future)

#### Must Have (P0)

1. **Document AI Integration**
   - PDF upload (technical data sheets)
   - Automatic text extraction
   - NER for material identification
   - Intelligent form pre-filling

2. **Analytics Dashboard**
   - Usage statistics
   - Portfolio-wide sustainability metrics
   - Trend analysis
   - Performance tracking

3. **Collaboration Features**
   - Share passports with stakeholders
   - Comments and feedback
   - Version control for passports

#### Should Have (P1)

1. **User Authentication**
   - Secure login (JWT tokens)
   - Save passports to account
   - Passport history
   - Rate limiting for free users

2. **Advanced Recommendations**
   - ML-powered optimization suggestions
   - Alternative material suggestions
   - Cost-benefit analysis

3. **Comparison Tool**
   - Compare 2-3 passports side-by-side
   - Highlight differences in composition
   - Visual comparison of metrics

#### Could Have (P2)

1. **Image Recognition**
   - Identify materials from product photos
   - Material type classification

2. **Knowledge Graph**
   - Material relationships
   - Property database
   - Compatibility matrix

3. **Integration APIs**
   - BIM software integration
   - ERP system integration
   - PLM system integration

---

## Architecture & Technology Stack

### System Architecture

The Material Passport Generator web application follows a modern microservices-like architecture with separate backend and frontend services.

**Architecture Overview:**
```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                        │
│                    (Next.js Frontend)                        │
│                     Hosted on Vercel                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS REST API
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Service                       │
│                     (FastAPI)                                 │
│                    Hosted on Render                          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   ML Models │  │    Utils    │  │   Data      │
│  (PyTorch)  │  │ (QR, PDF)   │  │ Validation  │
│             │  │             │  │             │
│ - Linear    │  │ - QR Code   │  │ - Pydantic  │
│ - RF        │  │ - PDF Gen   │  │ - CORS      │
│ - XGBoost   │  │             │  │             │
│ - Simple NN │  │             │  │             │
│ - Deep NN   │  │             │  │             │
│ - Multi NN  │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Implementation Decisions & Rationale

**Decision 1: Separate Backend and Frontend**
- **Approach:** FastAPI (backend) + Next.js (frontend) as separate services
- **Rationale:**
  - Clear separation of concerns
  - Frontend and backend can scale independently
  - Frontend can be easily swapped (e.g., to mobile app)
  - Allows backend to be used by multiple clients
  - Best practices for production applications
- **Alternatives Considered:**
  - Next.js API routes: Simplified but limited Python ML integration
  - Monolithic Flask app: Not modern, harder to scale
  - Server-side rendering only: No API flexibility

**Decision 2: FastAPI for Backend**
- **Approach:** Use FastAPI 0.100.0 with Python 3.9+
- **Rationale:**
  - Modern, async-first framework
  - Automatic API documentation (OpenAPI/Swagger)
  - Built-in data validation with Pydantic
  - Excellent performance (comparable to Go and Node.js)
  - Easy integration with PyTorch and scikit-learn
  - Strong community support and documentation
- **Alternatives Considered:**
  - Flask: Too basic, requires more boilerplate
  - Django REST Framework: Heavy, overkill for MVP
  - Express.js: Would require rewriting ML models in JavaScript

**Decision 3: Next.js for Frontend**
- **Approach:** Use Next.js 14 with App Router and TypeScript
- **Rationale:**
  - Industry-standard React framework
  - Server-side rendering for better SEO
  - Excellent developer experience
  - Built-in API routes for simplicity
  - Optimized deployments with Vercel
  - Great documentation and community
  - TypeScript for type safety
- **Alternatives Considered:**
  - Create React App: No SSR, outdated
  - Vue.js: Smaller community than React
  - Streamlit: Faster to build but less professional UI
  - Plain HTML/JS: No modern framework benefits

**Decision 4: Vercel + Render for Deployment**
- **Approach:** Deploy frontend to Vercel, backend to Render
- **Rationale:**
  - Both offer generous free tiers perfect for portfolio projects
  - Zero-configuration deployment from GitHub
  - Professional-looking URLs (custom domains available)
  - Excellent documentation and support
  - Easy to scale if needed
  - Industry-standard platforms
- **Alternatives Considered:**
  - AWS/GCP/Azure: More expensive, complex setup
  - Heroku: Free tier removed, expensive
  - DigitalOcean: Good value but requires more DevOps work
  - Local development only: Not suitable for portfolio demonstration

**Decision 5: Primary Focus on Passport Generation**
- **Approach:** Prioritize passport generation over other features
- **Rationale:**
  - Aligns with product name and value proposition
  - Delivers core value to users immediately
  - Easier to demonstrate impact
  - Clearer scope for MVP
  - Better story for portfolio (single feature done well vs many features mediocre)
- **Alternatives Considered:**
  - Build all features simultaneously: Too complex, risk of failure
  - Focus on Document AI first: No training data, speculative
  - Focus on batch processing: Less compelling demo

**Decision 6: Tailwind CSS for Styling**
- **Approach:** Use Tailwind CSS for UI styling
- **Rationale:**
  - Rapid UI development
  - Consistent design system
  - Excellent responsiveness out of the box
  - Small bundle size
  - Great developer experience
  - Industry-standard approach
- **Alternatives Considered:**
  - CSS Modules: More verbose, harder to maintain
  - Styled Components: Heavier, more runtime overhead
  - Bootstrap: Outdated design, less customizable
  - Material-UI: Heavy, opinionated design

**Decision 7: Focus on Concrete Materials**
- **Approach:** Start with concrete as primary material type
- **Rationale:**
  - High-quality dataset available (UCI ML Repository)
  - Direct relevance to construction industry
  - Clear sustainability metrics (recycled content: slag, fly ash)
  - Well-understood domain knowledge
  - Demonstrates AI/ML capability clearly
- **Future Plans:**
  - Add steel, wood, glass materials in Phase 2/3
  - Use transfer learning from concrete models
  - Collect training data for other materials

### Backend Technology Stack

**Core Framework:**
- **FastAPI 0.100.0** - Modern, fast web framework for building APIs with Python 3.9+
- **Uvicorn 0.23.1** - ASGI server for running FastAPI
- **Pydantic 2.1.1** - Data validation using Python type annotations

**Machine Learning:**
- **PyTorch 2.0.1** - Deep learning framework for neural networks
- **scikit-learn 1.3.0** - Traditional ML models (Linear, RF, XGBoost)
- **XGBoost 1.7.6** - Gradient boosting implementation
- **LightGBM 4.0.0** - Light gradient boosting

**Data Processing:**
- **pandas 2.0.3** - Data manipulation and analysis
- **numpy 1.24.3** - Numerical computing
- **scipy 1.11.1** - Scientific computing

**Utility Libraries:**
- **qrcode 7.4.2** - QR code generation for passport verification
- **reportlab 4.0.7** - PDF document generation
- **python-multipart 0.0.6** - File upload handling

**Deployment:**
- **Render** - Free cloud hosting for Python web services
- **GitHub** - Version control and CI/CD

### Frontend Technology Stack

**Core Framework:**
- **Next.js 14** (App Router) - React framework with SSR, API routes, and excellent DX
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript

**Styling:**
- **Tailwind CSS** - Utility-first CSS framework
- **PostCSS** - CSS transformation tool

**Data Visualization:**
- **Recharts** - Composable charting library built on React components

**Icons:**
- **Lucide React** - Beautiful icon library for React

**QR Codes & PDF:**
- **react-qr-code** - React QR code component
- **html2canvas** - Convert HTML to canvas
- **jspdf** - Generate PDF in browser

**HTTP Client:**
- **Fetch API** - Native browser API (or axios for advanced features)

**Deployment:**
- **Vercel** - Free cloud hosting optimized for Next.js
- **GitHub** - Automatic deployment on push

### Technology Rationale

**Why FastAPI?**
- Modern Python framework with async support
- Automatic API documentation (OpenAPI/Swagger)
- Built-in data validation with Pydantic
- Excellent performance (comparable to Go and Node.js)
- Easy integration with PyTorch and scikit-learn

**Why Next.js?**
- Industry-standard React framework
- Server-side rendering for better SEO
- Excellent developer experience
- Built-in API routes for simplicity
- Optimized deployments with Vercel
- Great documentation and community support

**Why Vercel + Render?**
- Both offer generous free tiers perfect for portfolio projects
- Zero-configuration deployment from GitHub
- Professional-looking URLs
- Excellent documentation and support
- Easy to scale if needed

**Why Tailwind CSS?**
- Rapid UI development
- Consistent design system
- Excellent responsiveness
- Small bundle size
- Great developer experience

---

## Technical Requirements

### Functional Requirements

**Passport Generation:**
1. System shall accept material composition input through web form (8 fields)
2. System shall validate input values (positive numbers, reasonable ranges)
3. System shall allow model selection from 6 trained models
4. System shall generate unique passport ID (UUID)
5. System shall generate complete passport in <30 seconds

**Prediction & Analysis:**
6. System shall predict compressive strength using selected ML model
7. System shall predict recyclability score (0-100) using multi-task model
8. System shall calculate recycled content percentage
9. System shall estimate CO2 emissions based on composition
10. System shall calculate circularity score (0-100)
11. System shall assign sustainability grade (A-F) based on metrics

**Passport Display:**
12. System shall display material composition in table format
13. System shall show predictions with confidence indicators
14. System shall present sustainability metrics with visual gauges
15. System shall display QR code for passport verification
16. System shall show certification badge/stamp
17. System shall be optimized for print viewing

**Export & Sharing:**
18. System shall generate professional PDF documents
19. System shall provide shareable passport URLs
20. System shall allow passport download in multiple formats (PDF, JSON)
21. System shall generate QR codes linking to passport web page

**Data Management:**
22. System shall store recent passports in client-side storage (localStorage)
23. System shall provide passport retrieval by unique ID
24. System shall validate model availability before prediction
25. System shall handle errors gracefully with user-friendly messages

**API Services:**
26. System shall provide REST API endpoints for all functions
27. System shall include automatic API documentation (OpenAPI/Swagger)
28. System shall implement CORS for frontend-backend communication
29. System shall include health check endpoint for monitoring
30. System shall support concurrent requests (100+ users)

### Non-Functional Requirements

**Performance:**
1. **API Response Time:** <200ms (P50), <500ms (P95) for prediction endpoints
2. **Page Load Time:** <2 seconds for initial page load
3. **PDF Generation:** <5 seconds for complete passport PDF
4. **Model Inference:** <100ms per prediction
5. **Database Query:** <100ms for passport retrieval

**Scalability:**
6. **Concurrent Users:** Support 100+ concurrent users in Phase 1
7. **Throughput:** Handle 1000+ passport generations per day
8. **Growth:** Architecture must scale to 10,000+ users with minimal changes
9. **Storage:** Support storing 10,000+ passports in backend

**Reliability & Availability:**
10. **Uptime:** >99% uptime during business hours
11. **Error Rate:** <1% error rate for all requests
12. **Data Persistence:** No data loss for generated passports
13. **Recovery:** Graceful degradation if services fail

**Security:**
14. **Data Encryption:** All data encrypted in transit (HTTPS)
15. **Input Validation:** All user inputs validated before processing
16. **CORS:** Proper CORS configuration to prevent unauthorized access
17. **Rate Limiting:** Implement rate limiting (100 req/min per IP)
18. **Error Handling:** No sensitive information in error messages
19. **Environment Variables:** All secrets stored securely, never committed

**Usability:**
20. **Accessibility:** WCAG 2.1 AA compliance
21. **Mobile Responsive:** Full functionality on mobile devices
22. **Browser Support:** Chrome, Firefox, Safari, Edge (latest 2 versions)
23. **Cross-Platform:** Works on Windows, Mac, Linux, iOS, Android

**Maintainability:**
24. **Code Quality:** Follow PEP 8 (Python) and ESLint (TypeScript) standards
25. **Documentation:** Inline code comments for complex logic
26. **API Documentation:** Complete OpenAPI/Swagger documentation
27. **Testing:** Unit test coverage >80% for backend logic
28. **Logging:** Comprehensive logging for debugging and monitoring

**Compliance:**
29. **Data Privacy:** No personal data collected without consent
30. **Cookie Policy:** Clear cookie policy and user consent
31. **Terms of Service:** Clear terms of service displayed to users
32. **GDPR:** Compliant with GDPR data protection requirements

### Data Requirements
1. Material composition (percentages must sum to 100%)
2. Product identification (name, SKU, manufacturer)
3. Optional: technical specifications, certifications
4. Privacy: No personally identifiable information

---

## User Stories

### Epic 1: Passport Generation
**As a** sustainability manager  
**I want to** upload my product's material composition  
**So that** I can automatically generate a digital material passport

**Acceptance Criteria:**
- Upload CSV with composition data
- See composition visualization
- View calculated sustainability metrics
- Download passport as PDF

### Epic 2: Sustainability Insights
**As a** consultant  
**I want to** see recyclability score and improvement recommendations  
**So that** I can advise my client on product optimization

**Acceptance Criteria:**
- Recyclability score displayed (0-100)
- Color-coded sustainability grade
- Top 3 improvement recommendations
- Comparison with industry benchmarks

### Epic 3: Compliance
**As a** manufacturer  
**I want to** export passports in EU DPP format  
**So that** I can comply with regulations

**Acceptance Criteria:**
- Export includes all mandatory fields
- Format validates against EU schema
- Batch export for product catalog

---

## Out of Scope (Phase 1 - Web App MVP)

### Explicitly Out of Scope

1. **User Authentication**
   - No login/signup functionality
   - No user accounts or profiles
   - No session management
   - Passports stored client-side only (localStorage)

2. **Document AI Integration**
   - No PDF upload for automatic data extraction
   - No OCR or text extraction from technical sheets
   - No NER for material identification
   - Manual input only

3. **Real-time Collaboration**
   - No multi-user editing
   - No real-time updates
   - No comments or feedback system
   - No version control for passports

4. **Mobile Applications**
   - No native iOS/Android apps
   - Web app will be mobile-responsive but not native

5. **IoT Sensor Integration**
   - No sensor data ingestion
   - No real-time monitoring
   - No IoT device connectivity

6. **Blockchain Verification**
   - No blockchain-based verification
   - No immutable records
   - QR code links to web page only

7. **Multi-language Support**
   - English language only
   - No i18n/l10n
   - No translation features

8. **Enterprise Integrations**
   - No PLM system integration (SAP Teamcenter, etc.)
   - No ERP system integration
   - No BIM software integration
   - API access for enterprise customers (Phase 2)

9. **Full Life Cycle Assessment (LCA)**
   - No comprehensive LCA calculations
   - Simplified CO2 estimation only
   - No full environmental impact assessment

10. **Supply Chain Traceability**
    - No origin tracking
    - No supplier verification
    - No blockchain traceability

11. **Payment Processing**
    - No billing or payments
    - No subscription management
    - No premium tiers

12. **Email Notifications**
    - No email alerts
    - No notifications system
    - No reminders or follow-ups

### Deferred to Phase 2/3

1. **Advanced AI Features**
   - Document AI (PDF extraction) - Phase 2
   - Knowledge graph - Phase 2
   - NLP for material descriptions - Phase 2
   - Image recognition - Phase 2

2. **Business Features**
   - User authentication - Phase 2
   - Paid plans/subscriptions - Phase 3
   - Enterprise API access - Phase 3
   - Analytics dashboard - Phase 2

3. **Integrations**
   - BIM software - Phase 3
   - ERP/PLM systems - Phase 3
   - Government reporting - Phase 3

---

## Stakeholders

### Internal
- **Product Owner:** You (learning AI/ML + Product Management)
- **Developer:** You (building technical skills)
- **Domain Expert:** Siemens sustainability colleagues (validation)

### External (Potential)
- **Early Adopters:** 5-10 building material manufacturers
- **Advisors:** Circular economy consultants
- **Validators:** Sustainability certification bodies

---

## Risks & Mitigation

### Risk 1: Data Quality
**Risk:** Inconsistent or incomplete source data  
**Impact:** High  
**Mitigation:** 
- Implement robust data validation
- Provide clear error messages
- Offer manual override option

### Risk 2: Model Accuracy
**Risk:** ML model doesn't generalize beyond concrete  
**Impact:** Medium  
**Mitigation:**
- Start with concrete (high-quality dataset)
- Collect diverse training data
- Use transfer learning approach

### Risk 3: Regulatory Alignment
**Risk:** EU DPP requirements change  
**Impact:** Medium  
**Mitigation:**
- Monitor regulatory developments
- Flexible data schema
- Version control for formats

### Risk 4: Adoption
**Risk:** Users prefer manual processes  
**Impact:** Medium  
**Mitigation:**
- Focus on time savings
- Demonstrate ROI clearly
- Provide excellent documentation

---

## Dependencies

### Technical Dependencies
- UCI ML Repository (dataset access)
- Cloud hosting (deployment)
- PDF generation libraries
- ML frameworks (PyTorch, scikit-learn)

### Business Dependencies
- Access to real technical data sheets (Phase 2)
- User feedback from sustainability professionals
- Validation from domain experts

---

## Timeline & Milestones

### Completed Phases

**Week 1-2: Foundation**
- ✅ Dataset acquisition and exploration
- ✅ Baseline ML models trained (Linear Regression, Random Forest, XGBoost)
- ✅ Feature engineering for recyclability scoring
- ✅ Sustainability metrics calculation
- ✅ Core project documentation

**Week 3-4: Deep Learning**
- ✅ Neural network models implemented (Simple NN, Deep NN, Multi-task NN)
- ✅ Multi-task learning (strength + recyclability prediction)
- ✅ Model optimization and comparison
- ✅ Model interpretability analysis

### Current Phase: Web App Development

**Week 5: Backend API Development**
- FastAPI project setup and configuration
- Model loading and prediction service
- Sustainability metrics service
- Passport generation service
- QR code and PDF generation utilities
- API endpoint implementation and testing

**Week 6: Frontend Development**
- Next.js application setup with App Router
- UI component library (Tailwind CSS)
- Passport generator form
- Passport display page
- Visualizations for sustainability metrics
- PDF export integration
- Responsive design implementation

**Week 7: Deployment & Polish**
- Backend deployment to Render (free tier)
- Frontend deployment to Vercel (free tier)
- CORS and environment configuration
- End-to-end testing
- Documentation (API docs, user guide)
- Performance optimization
- Bug fixes and polish

### Future Phases (Week 8-12)

**Week 8-9: Enhanced Features**
- Batch passport generation
- Passport gallery and comparison
- Shareable links and QR codes
- Advanced visualizations
- Model comparison view

**Week 10-11: Production Readiness**
- Analytics dashboard
- User authentication (optional)
- Rate limiting and security hardening
- Monitoring and logging
- Comprehensive testing

**Week 12: Launch & Portfolio**
- Beta testing with real users
- Feedback collection and iteration
- Portfolio presentation preparation
- Documentation completion
- Demo video creation

---

## Appendix

### Regulatory Context
- EU Ecodesign for Sustainable Products Regulation (ESPR)
- Digital Product Passport requirements
- Construction Products Regulation (CPR)

### Competitive Landscape
- Manual solutions (consultants, Excel templates)
- Enterprise PLM systems (SAP, Siemens Teamcenter)
- Specialized LCA software (GaBi, SimaPro)
- **Differentiation:** AI-powered, circular economy focus, accessible pricing

### References
- Ellen MacArthur Foundation - Circular Economy Principles
- EU DPP Technical Specifications (Draft)
- Materials Passport Framework (BAMB Project)
- Concrete Compressive Strength Dataset - UCI ML Repository
- Web App Implementation Plan - See `WEB_APP_IMPLEMENTATION_PLAN.md` in project root

---

**Document Status:** Living document, updated to reflect web app implementation decisions
**Version:** 2.0 (Updated January 25, 2025)
**Next Review:** Upon completion of Phase 2 (Web App MVP)
**Feedback:** Open for comments and suggestions
**Related Documents:**
- WEB_APP_IMPLEMENTATION_PLAN.md - Detailed 3-week web app implementation plan
- README.md - Project overview and status
- GETTING_STARTED.md - Setup and installation guide
- START_HERE.md - Quick start guide
