### Week 6: Networking & Security

**Days 36–42** | _Secure communication & systems_

- **Day 36**: Socket Programming & Network Basics
- **Day 37**: Building Secure APIs
- **Day 38**: Encryption & Cryptography
- **Day 39**: Authentication Protocols
- **Day 40**: Web Security Best Practices
- **Day 41**: Network Scanning & Monitoring
- **Day 42**: Weekly Project – Secure Portfolio Tracker

### **Week 6: Networking & Security**

**Days 36–42** | _Secure communication & systems_

This week bridges the gap between building applications and making them secure, reliable, and production-ready. We'll move from low-level network communication to high-level security principles.

---

### **Day 36: Socket Programming & Network Basics**

- **Objective:** Understand the fundamentals of how computers communicate over a network by building a simple client-server application from scratch.
- **Core Concepts:**
  - The OSI & TCP/IP Models (High-level overview)
  - TCP vs. UDP Protocols
  - IP Addresses, Ports, and DNS
  - Socket API: `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `send()`, `recv()`
  - Building a simple Echo Server and Client.
- **Hands-On Activity:**
  - **Tutorial:** Create a basic TCP chat server in Python/Node.js that can handle multiple clients. Clients can connect via Telnet or a simple script and send messages broadcast to all other connected clients.
  - **Challenge:** Modify the server to log all chat messages to a file.

---

### **Day 37: Building Secure APIs**

- **Objective:** Apply security principles directly to the APIs you've been building, moving from functionality to robustness.
- **Core Concepts:**
  - RESTful API Security Best Practices.
  - Input Validation & Sanitization (Preventing SQL Injection, XSS).
  - HTTPS/SSL/TLS: Why it's non-negotiable.
  - Data Serialization & safe parsing.
  - Security Headers (e.g., `Content-Security-Policy`).
  - Using middleware for security (e.g., `helmet` in Express.js).
- **Hands-On Activity:**
  - **Code Audit:** Review one of your existing Flask/Express APIs.
  - **Implementation:**
    1.  Add input validation for all endpoints (e.g., using `Joi` for Node.js or `Flask-WTF/ Marshmallow` for Python).
    2.  Implement and enforce HTTPS in your development environment.
    3.  Add the `helmet` library (Node.js) or its equivalent to set security headers.

---

### **Day 38: Encryption & Cryptography**

- **Objective:** Learn how to protect data at rest and in transit using cryptographic principles.
- **Core Concepts:**
  - Hashing vs. Encryption (Symmetric vs. Asymmetric).
  - Algorithms: SHA-256, bcrypt/scrypt (for passwords), AES (symmetric), RSA (asymmetric).
  - Digital Signatures and Certificates.
  - Public Key Infrastructure (PKI) - how HTTPS works under the hood.
  - Salting passwords and why it's critical.
- **Hands-On Activity:**
  - **Tutorial:**
    1.  Write a script to hash a password using a library like `bcrypt`.
    2.  Write a script to perform symmetric encryption/decryption of a file or string using a library like `cryptography` (Python) or `crypto` (Node.js).
  - **Challenge:** Use OpenSSL commands to generate a self-signed certificate and key pair.

---

### **Day 39: Authentication Protocols**

- **Objective:** Implement robust, standard-based user authentication, moving beyond basic sessions.
- **Core Concepts:**
  - The shortfalls of Basic Auth and Session-Cookies for APIs.
  - **JWT (JSON Web Tokens):** Structure, signing, and verification.
  - OAuth 2.0 & OpenID Connect Flows (Authorization Code flow).
  - The roles of Client, Resource Server, Authorization Server.
- **Hands-On Activity:**
  - **Tutorial:** Refactor the authentication in your portfolio tracker project.
    1.  Replace session-based login with a JWT-based login system.
    2.  Create a `/login` endpoint that returns a JWT.
    3.  Create middleware to protect API routes by verifying the JWT.
  - **Bonus:** Integrate a "Login with Google" using OAuth 2.0.

---

### **Day 40: Web Security Best Practices**

- **Objective:** Identify and defend against the most common web application vulnerabilities.
- **Core Concepts:**
  - **OWASP Top 10** Deep Dive:
    - Broken Access Control
    - Cryptographic Failures (sensitive data exposure)
    - Injection (SQLi, Command Injection)
    - Insecure Design
    - Security Misconfiguration
    - Vulnerable and Outdated Components
  - Cross-Site Scripting (XSS) - Reflected, Stored, DOM-based.
  - Cross-Site Request Forgery (CSRF).
- **Hands-On Activity:**
  - **Vulnerability Hunt:** Use a deliberately vulnerable app like OWASP Juice Shop or a simple one you create to find and exploit XSS and SQL Injection vulnerabilities.
  - **Defense:** Implement the fixes for these vulnerabilities in your own code (e.g., parameterized queries, output encoding).

---

### **Day 41: Network Scanning & Monitoring**

- **Objective:** Learn the basics of offensive and defensive security to understand your system's attack surface and health.
- **Core Concepts:**
  - Defense in Depth.
  - Network reconnaissance with tools like `nmap` and `ping`.
  - Introduction to Firewalls and Intrusion Detection Systems (IDS).
  - Logging, Monitoring, and Alerting.
  - Using `tcpdump` or Wireshark for basic packet analysis.
- **Hands-On Activity:**
  - **Tutorial:**
    1.  Use `nmap` to scan your own local network and discover devices and open ports.
    2.  Start a simple service on your machine and use `nmap` to find it.
    3.  Use `tcpdump`/Wireshark to capture a few packets from a `ping` command and inspect them.
  - **Challenge:** Set up a basic logging system for your portfolio tracker that logs authentication attempts (success/failure) to a file.

---

### **Day 42: Weekly Project – Secure Portfolio Tracker**

- **Objective:** Integrate all the security concepts from the week into a single, robust application.
- **Project Requirements:**
  1.  **Secure Authentication:** Must use JWT for stateless authentication. Passwords must be hashed with bcrypt/scrypt.
  2.  **Hardened API:** All API endpoints must be protected. Implement input validation and sanitization on all user inputs.
  3.  **Data Encryption:** At least one piece of sensitive user data (e.g., an API key for a stock data service) must be encrypted in the database.
  4.  **Security Headers:** Implement key security headers like `Content-Security-Policy` and `Strict-Transport-Security`.
  5.  **Audit Logging:** Log all user logins (successful and failed) and significant actions (e.g., adding a large trade).
- **Deliverable:**
  - A fully functional, security-hardened Portfolio Tracker web application.
  - A `SECURITY.md` document explaining the security measures you have implemented and why.

---

**Weekly Reflection Prompt:**
_What was the most surprising vulnerability you learned about? How has this week changed the way you think about writing code, even for simple applications?_
