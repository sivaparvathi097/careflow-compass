# CareFlow AI — Frontend Architecture Documentation

## 1. Role-Based Page List

### Triage Staff Routes (`/triage/*`)
| Page | Route | Purpose |
|------|-------|---------|
| Login | `/` | Role selection (Triage / Admin) |
| Main Dashboard | `/triage/dashboard` | Overview: total patients, high risk, dept load |
| Upload Patient | `/triage/upload` | Manual patient entry + file upload |
| Real-Time Data | `/triage/realtime` | Live patient table (auto-refresh every 5s) |
| Analysis | `/triage/analysis` | AI risk assessment, explainable AI panel |
| Department View | `/triage/department` | Dept beds, queue (read-only) |

### Hospital Admin Routes (`/admin/*`)
| Page | Route | Purpose |
|------|-------|---------|
| Admin Overview | `/admin/dashboard` | KPIs, weekly trends, risk pie chart |
| Departments | `/admin/departments` | Ward tables, bed grids per department |
| Disease Trends | `/admin/trends` | Symptom aggregation charts |
| Risk & Alerts | `/admin/alerts` | Dept risk %, alert triggers |

---

## 2. Navigation per Role

### Triage Sidebar
- Main Dashboard → `/triage/dashboard`
- Upload Patient Data → `/triage/upload`
- Real-Time Patient Data → `/triage/realtime`
- Switch Role → `/` (logout)

### Admin Sidebar
- Overview → `/admin/dashboard`
- Departments → `/admin/departments`
- Disease Trends → `/admin/trends`
- Risk & Alerts → `/admin/alerts`
- Switch Role → `/` (logout)

### Cross-Page Navigation
- Upload form submit → `/triage/analysis`
- Real-time table row click → `/triage/analysis`
- Analysis "View Department" → `/triage/department`

---

## 3. Component Breakdown

### Shared Components
| Component | File | Usage |
|-----------|------|-------|
| `AppSidebar` | `components/AppSidebar.tsx` | Role-based sidebar navigation |
| `DashboardLayout` | `components/DashboardLayout.tsx` | Layout wrapper with sidebar + `<Outlet>` |
| `StatCard` | `components/StatCard.tsx` | Reusable KPI card with icon + variant |
| `RiskBadge` | `components/RiskBadge.tsx` | Color-coded risk level badge |

### Triage Pages
- **TriageDashboard**: 3x StatCard + dept load grid
- **UploadPatient**: Form (8 fields) + file upload dropzone
- **RealtimePatients**: Table with live indicator
- **Analysis**: Risk score + progress bar, AI panel, vitals, dept classification
- **DepartmentView**: Bed stats cards + patient queue table

### Admin Pages
- **AdminDashboard**: 4x StatCard + LineChart + BarChart + PieChart
- **AdminDepartments**: Dept selector tabs + ward table + bed grid
- **AdminTrends**: Multi-line symptom chart + bar charts
- **AdminAlerts**: Risk % table + pie chart + alert trigger cards

---

## 4. API Endpoint Contracts (Frontend Expectations)

### Patient APIs

#### `POST /api/patients`
- **Purpose**: Submit manually entered patient
- **Request**: `{ patientId, age, gender, symptoms, bloodPressure, heartRate, temperature, preExistingConditions }`
- **Response**: `{ patient: Patient, riskScore, riskLevel, department, contributingFactors, reasonSummary, confidenceScore }`

#### `GET /api/patients`
- **Purpose**: Fetch all patients
- **Response**: `{ patients: Patient[] }`

#### `GET /api/patients/realtime`
- **Purpose**: SSE or WebSocket for live patient arrivals
- **Response**: Stream of `Patient` objects

#### `GET /api/patients/:id/analysis`
- **Purpose**: AI analysis for specific patient
- **Response**: `{ riskScore, riskLevel, contributingFactors, reasonSummary, confidenceScore, department }`

### Department APIs

#### `GET /api/departments`
- **Purpose**: List all departments with bed info
- **Response**: `{ departments: [{ name, totalBeds, available, occupied, wards: Ward[] }] }`

#### `GET /api/departments/:name/queue`
- **Purpose**: Patient queue for department
- **Response**: `{ patients: Patient[] }`

### Admin APIs

#### `GET /api/admin/overview`
- **Purpose**: Dashboard KPIs
- **Response**: `{ totalPatients, admittedToday, dischargedToday, bedsAvailable }`

#### `GET /api/admin/trends/weekly`
- **Purpose**: Weekly case trend data
- **Response**: `{ data: [{ day, cases }] }`

#### `GET /api/admin/trends/symptoms`
- **Purpose**: Symptom trend aggregation
- **Response**: `{ data: [{ week, symptomCounts: Record<string, number> }] }`

#### `GET /api/admin/alerts`
- **Purpose**: Active alert triggers
- **Response**: `{ alerts: [{ condition, departments, triggered }] }`

#### `GET /api/admin/risk-summary`
- **Purpose**: Risk distribution
- **Response**: `{ low, medium, high }`

### File Upload

#### `POST /api/upload`
- **Purpose**: Upload CSV/JSON/TXT/EHR files
- **Request**: `multipart/form-data` with file
- **Response**: `{ patients: Patient[] }`

---

## 5. Data Flow

### Manual Input Flow
1. Triage enters data in `/triage/upload`
2. Form submits → patient added to global state
3. Patient selected → navigate to `/triage/analysis`
4. Analysis shows AI risk assessment

### Real-Time Simulation Flow
1. `PatientContext` generates synthetic patient every 5s
2. Patient appended to global list
3. `/triage/realtime` table auto-updates
4. Row click → selects patient → `/triage/analysis`

### Admin Data Flow
1. Admin views `/admin/dashboard` → reads from global patient state
2. Charts compute from patient array (dept distribution, risk counts)
3. Departments page uses static mock ward data
4. Alerts page uses static thresholds

---

## 6. State Management

### Global State (PatientContext)
- `patients: Patient[]` — unified list (manual + synthetic)
- `selectedPatient: Patient | null` — currently viewed patient
- `addPatient()` — adds to list
- `selectPatient()` — sets selection

### Page-Specific State
- Upload form: local `useState` for form fields
- Department selector: local `useState` for active department tab
- All chart data: derived from global patient list or static mocks

---

## 7. Notes for Backend Integration

### Real-Time Requirements
- `/api/patients/realtime` should use **WebSocket or SSE** for live updates
- Replace the 5-second interval with server-push when backend available

### Backend-Dependent Pages
- `/triage/upload` → `POST /api/patients` + `POST /api/upload`
- `/triage/analysis` → `GET /api/patients/:id/analysis`
- `/admin/dashboard` → `GET /api/admin/overview`
- `/admin/trends` → `GET /api/admin/trends/*`
- `/admin/alerts` → `GET /api/admin/alerts`

### Analytical Endpoints (Can Be Cached)
- Weekly trends, symptom aggregation, dept comparison
- Risk summary can refresh every 30s

### Authentication Notes
- Current: simulated role via route prefix
- Backend should implement JWT-based auth with role claim
- Sidebar and routes should gate based on `user.role`

---

## 8. Notes for UI Enhancement

### Recommended Improvements
- Add dark mode toggle (theme tokens already configured)
- Mobile responsive sidebar (hamburger menu)
- Add loading skeletons for async data
- Add toast notifications for patient uploads
- Add search/filter on real-time patient table
- Add export functionality (CSV download)
- Add pagination for large patient lists
- Animate chart transitions with framer-motion
