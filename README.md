# VulnScan AI - Automated Web Vulnerability Scanning System

[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

## Overview

VulnScan AI is a professional, full-stack web application for automated vulnerability scanning targeting **OWASP Top 10:2025** web vulnerabilities. The system combines automated scanning, AI-powered severity prediction, and comprehensive reporting for academic and professional use.

### Key Features

- **OWASP Top 10:2025 Coverage**: Detects Broken Access Control, Injection, Security Misconfiguration, Cryptographic Failures, Insecure Design, and Authentication Failures
- **AI-Powered Analysis**: Machine learning models (Random Forest, Logistic Regression, Naive Bayes) predict vulnerability severity with confidence scores
- **NVD Integration**: Automatic CVE/CWE mapping with CVSS scores from National Vulnerability Database
- **Professional Reports**: Generate comprehensive PDF reports with remediation guidance
- **Modern UI/UX**: Responsive, dark-themed cybersecurity interface built with Next.js and Tailwind CSS
- **Secure Authentication**: JWT-based authentication with secure session management
- **Production-Ready**: Deployable on Vercel (frontend), Render/Railway/Heroku (backend), and Neon (database)

## Technology Stack

### Frontend
- **Framework**: Next.js 16 with App Router
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui, Radix UI
- **Authentication**: JWT with HTTP-only cookies
- **State Management**: React Context API
- **Icons**: Lucide React

### Backend
- **Framework**: Flask 3.0
- **Database**: PostgreSQL (Neon)
- **ORM**: psycopg2 (raw SQL for optimal performance)
- **ML Models**: scikit-learn (Random Forest, Logistic Regression, Naive Bayes)
- **PDF Generation**: ReportLab
- **API Integration**: NVD REST API

### Infrastructure
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render / Railway / Heroku
- **Database**: Neon PostgreSQL
- **Version Control**: Git / GitHub

## Architecture

\`\`\`
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │  Login   │  │Dashboard │  │  Scan Results Page   │   │
│  │ Register │  │ URL Input│  │  Vuln Details        │   │
│  └──────────┘  └──────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS / REST API
                          ▼
┌─────────────────────────────────────────────────────────┐
│               Backend (Python Flask)                     │
│  ┌────────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ OWASP Scanner  │  │ AI Severity │  │ NVD API     │  │
│  │ SQL, XSS, etc. │  │ Predictor   │  │ Integration │  │
│  └────────────────┘  └─────────────┘  └─────────────┘  │
│  ┌─────────────────────────────────────────────────┐   │
│  │         PDF Report Generator                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ PostgreSQL Protocol
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Database (Neon PostgreSQL)                      │
│  ┌─────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Users  │  │    Scans     │  │ Vulnerabilities │   │
│  └─────────┘  └──────────────┘  └─────────────────┘   │
│  ┌─────────────────┐  ┌────────────────────────────┐   │
│  │  CVE Mappings   │  │   Scan Metadata            │   │
│  └─────────────────┘  └────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
\`\`\`

## Database Schema

### Tables

1. **users_sync** (neon_auth schema)
   - User authentication and profile data
   - Fields: id, email, name, password_hash, created_at, updated_at

2. **scans**
   - Scan requests and status tracking
   - Fields: id, user_id, target_url, scan_status, vulnerability counts, timestamps

3. **vulnerabilities**
   - Detected security vulnerabilities
   - Fields: id, scan_id, vulnerability details, CWE/CVSS data, severity, AI predictions, remediation

4. **cve_mappings**
   - CVE associations for vulnerabilities
   - Fields: id, vulnerability_id, cve_id, description, CVSS score, dates

5. **scan_metadata**
   - Additional scan information and logs

## Installation & Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL database (or Neon account)
- Git

### Local Development

#### 1. Clone Repository

\`\`\`bash
git clone https://github.com/yourusername/vulnscan-ai.git
cd vulnscan-ai
\`\`\`

#### 2. Setup Frontend

\`\`\`bash
npm install
\`\`\`

Create `.env.local`:
\`\`\`
DATABASE_URL=postgresql://user:password@localhost:5432/vulnscan
JWT_SECRET=your-secret-key-minimum-32-characters
BACKEND_URL=http://localhost:5000
\`\`\`

Run development server:
\`\`\`bash
npm run dev
\`\`\`

Frontend will be available at http://localhost:3000

#### 3. Setup Backend

\`\`\`bash
cd backend
pip install -r requirements.txt
\`\`\`

Create `.env`:
\`\`\`
DATABASE_URL=postgresql://user:password@localhost:5432/vulnscan
NVD_API_KEY=your-nvd-api-key  # Optional
\`\`\`

Train AI models:
\`\`\`bash
python ai_model/train_models.py
\`\`\`

Run backend server:
\`\`\`bash
python app.py
\`\`\`

Backend will be available at http://localhost:5000

#### 4. Setup Database

Run the SQL migration scripts in order:
\`\`\`bash
psql $DATABASE_URL < scripts/001_create_schema.sql
psql $DATABASE_URL < scripts/002_seed_sample_data.sql
\`\`\`

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions covering:
- Vercel (Frontend)
- Render / Railway / Heroku (Backend)
- Neon (Database)

## Project Structure

\`\`\`
vulnscan-ai/
├── app/                          # Next.js app directory
│   ├── api/                      # API routes
│   │   ├── auth/                 # Authentication endpoints
│   │   └── scans/                # Scan management endpoints
│   ├── dashboard/                # Dashboard page
│   ├── login/                    # Login page
│   ├── register/                 # Registration page
│   ├── scan/[id]/                # Scan results page
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Landing page
├── backend/                      # Python Flask backend
│   ├── ai_model/                 # ML severity prediction
│   │   ├── severity_predictor.py
│   │   ├── train_models.py
│   │   └── saved_models/         # Trained model files
│   ├── integrations/             # External API integrations
│   │   └── nvd_api.py           # NVD API client
│   ├── pdf_generator/           # PDF report generation
│   │   └── report_generator.py
│   ├── scanners/                 # Vulnerability scanners
│   │   └── owasp_scanner.py     # OWASP Top 10 scanner
│   ├── app.py                    # Flask application
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Container configuration
├── components/                   # React components
│   ├── auth-provider.tsx        # Authentication context
│   └── ui/                       # UI components (shadcn)
├── lib/                          # Utility libraries
│   ├── auth.ts                   # Auth utilities
│   ├── db.ts                     # Database client
│   └── utils.ts                  # Helper functions
├── scripts/                      # Database migrations
│   ├── 001_create_schema.sql
│   └── 002_seed_sample_data.sql
├── DEPLOYMENT.md                 # Deployment guide
└── README.md                     # This file
\`\`\`

## Features Breakdown

### 1. Authentication System
- Secure JWT-based authentication
- Password hashing with SHA-256
- HTTP-only cookie sessions
- Protected routes and API endpoints

### 2. Vulnerability Scanning
Detects the following OWASP Top 10:2025 vulnerabilities:
- **A01:2025 - Broken Access Control**: Unauthorized admin access, IDOR
- **A03:2025 - Injection**: SQL injection, XSS, command injection
- **A05:2025 - Security Misconfiguration**: Missing headers, debug mode
- **A02:2025 - Cryptographic Failures**: Unencrypted transmission, weak crypto
- **A04:2025 - Insecure Design**: Design flaws and logic errors
- **A07:2025 - Authentication Failures**: Weak passwords, session issues

### 3. AI Severity Prediction
- Three ML models: Random Forest, Logistic Regression, Naive Bayes
- TF-IDF vectorization of vulnerability descriptions
- Confidence scores for predictions
- Trained on vulnerability patterns and CVSS scores

### 4. NVD Integration
- Automatic CVE lookup by CWE ID
- CVSS v3 score retrieval
- Vulnerability descriptions and metadata
- 24-hour caching to reduce API calls

### 5. PDF Report Generation
- Professional formatting with ReportLab
- Executive summary with severity breakdown
- Detailed vulnerability listings
- Color-coded severity indicators
- Remediation recommendations
- CVE/CWE references

## API Endpoints

### Frontend API (Next.js)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | User login |
| `/api/auth/logout` | POST | User logout |
| `/api/auth/me` | GET | Get current user |
| `/api/scans` | GET | List user's scans |
| `/api/scans/start` | POST | Start new scan |
| `/api/scans/[id]` | GET | Get scan details |
| `/api/scans/[id]/pdf` | GET | Download PDF report |

### Backend API (Flask)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/scan/start` | POST | Execute vulnerability scan |
| `/api/scan/status/<id>` | GET | Get scan status |
| `/api/generate-pdf` | POST | Generate PDF report |

## Usage Guide

### 1. Register Account
- Navigate to the registration page
- Provide name, email, and password (min 8 characters)
- Submit to create account and auto-login

### 2. Start Scan
- Enter target URL in dashboard (e.g., https://example.com)
- Click "Start Scan"
- System initiates vulnerability detection

### 3. View Results
- Navigate to scan results page
- Review vulnerability details including:
  - Vulnerability name and type
  - CWE classification
  - CVSS score
  - AI-predicted severity with confidence
  - Associated CVEs
  - Evidence and affected locations
  - Remediation recommendations

### 4. Download Report
- Click "Download PDF" button
- Professional PDF report generated with all findings
- Use for documentation and remediation tracking

## Security Best Practices

### Implementation
- JWT tokens with secure HTTP-only cookies
- Password hashing (upgrade to bcrypt for production)
- SQL injection prevention via parameterized queries
- CORS configuration for API security
- Environment variable management
- HTTPS enforcement in production

### Recommendations
- Regular dependency updates
- API rate limiting
- Input validation and sanitization
- Secure session management
- Database connection pooling
- Error logging without sensitive data exposure

## Performance Optimization

- Database indexes on frequently queried columns
- NVD API response caching (24 hours)
- Efficient SQL queries with proper joins
- Async/await patterns for non-blocking operations
- Frontend code splitting and lazy loading
- Image optimization with Next.js Image component

## Testing

### Manual Testing
1. Register new user account
2. Login with credentials
3. Start scan with test URL
4. Verify vulnerability detection
5. Check AI predictions
6. Download and review PDF report

### Unit Testing (Future Enhancement)
- pytest for backend
- Jest for frontend
- Integration tests for API endpoints
- E2E tests with Playwright

## Academic Use & FYP Defense

### Demonstration Points

1. **Problem Statement**: Growing need for automated security testing
2. **Solution**: AI-enhanced vulnerability scanning targeting OWASP Top 10
3. **Technical Implementation**: Full-stack with modern frameworks
4. **ML Integration**: Supervised learning for severity prediction
5. **External APIs**: NVD integration for CVE/CWE data
6. **User Experience**: Professional, intuitive interface
7. **Scalability**: Cloud-native architecture
8. **Security**: Best practices implementation

### Presentation Tips
- Live demo of scan execution
- Show AI prediction accuracy
- Demonstrate PDF report generation
- Explain architecture and design decisions
- Highlight OWASP Top 10 coverage
- Discuss future enhancements

## Future Enhancements

- [ ] Advanced scanning techniques (authenticated scans, dynamic analysis)
- [ ] More ML models (XGBoost, Neural Networks, BERT)
- [ ] Real-time scanning progress updates via WebSockets
- [ ] Scheduled automatic scans
- [ ] Scan comparison and trend analysis
- [ ] Integration with CI/CD pipelines
- [ ] Multi-language support
- [ ] Advanced reporting with charts and graphs
- [ ] Team collaboration features
- [ ] API for third-party integrations

## Troubleshooting

### Common Issues

**Database Connection Errors**
- Verify DATABASE_URL is correct
- Check network connectivity to database
- Ensure database user has proper permissions

**Backend Not Starting**
- Check Python version (3.11+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check port 5000 is not in use

**Frontend Build Errors**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Verify environment variables are set

**Scan Failures**
- Check target URL is accessible
- Verify backend is running and healthy
- Check backend logs for error details

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is created for academic purposes. For commercial use, please contact the author.

## Author

Created as a Final Year Project (FYP) demonstrating:
- Full-stack development
- Machine learning integration
- Security vulnerability analysis
- Professional software engineering practices

## Acknowledgments

- OWASP for vulnerability classifications
- NIST for NVD API
- shadcn/ui for component library
- Vercel for hosting platform

## Contact & Support

For questions, issues, or feedback:
- Create an issue on GitHub
- Email: your-email@example.com

---

**Note**: This system is for educational and authorized testing only. Always obtain proper authorization before scanning any web application.
\`\`\`
