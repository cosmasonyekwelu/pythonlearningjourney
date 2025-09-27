**Topic**: Setting up a Linux Server for Hosting & Database Management,

## 📖 Summary

Today, I learned how to set up a **Linux server** for hosting purposes, including web and database services. The focus was on:

- Installing Linux distributions (Ubuntu, Debian, CentOS)
- Updating system packages
- Installing web servers (Apache, Nginx)
- Installing and configuring database servers (MySQL/MariaDB, PostgreSQL)
- Setting up firewall rules
- Hosting static websites and Python apps (Flask)
- Optional: SSL setup, domain configuration, and security considerations

---

## 🔑 Key Learnings

1. Linux distributions have different package managers (`apt`, `yum`, `dnf`).
2. Web servers (Apache/Nginx) require proper starting, enabling, and testing.
3. Database servers need secure setup, user creation, and privilege assignment.
4. Firewall rules are critical to expose only necessary ports.
5. Python apps can be hosted using Flask and made persistent using `systemd`.
6. Security best practices: SSH keys, fail2ban, and system updates.

---

## 🧰 Prerequisites

- A _Linux system_ (Debian/Ubuntu/CentOS/Arch/etc.)
- Basic terminal skills
- Internet connection
- A static IP (optional, but helpful for external access)
- (Optional) Domain name

---

## 🧾 Step-by-Step: Hosting a Server on Linux

### . _Update Your System_

Open the terminal and run:

For Debian/Ubuntu:

bash
sudo apt update && sudo apt upgrade

For RedHat/CentOS:

bash
sudo yum update

---

### . _Install Server Software_

Depends on what type of server you want to run.

#### 🌐 Web Server (Apache or Nginx)

- _Apache:_

bash
sudo apt install apache2

Access it at http://localhost or your machine's IP.

- _Nginx:_

bash
sudo apt install nginx

#### 💾 File Server (Samba or FTP)

- _Samba (for sharing with Windows/macOS):_

bash
sudo apt install samba

- _VSFTPD (FTP server):_

bash
sudo apt install vsftpd

#### 💬 Game Server (e.g. Minecraft, CS\:GO, Valheim)

Check the specific server software and installation steps.

#### App Hosting (Python, Node.js, etc.)

- Python:

bash
sudo apt install python3 python3-pip

You can serve apps using frameworks like Flask, Express, etc.

---

### _Open Firewall Ports_

Use ufw (Uncomplicated Firewall) to allow traffic:

bash
sudo ufw allow 80 # HTTP
sudo ufw allow 443 # HTTPS
sudo ufw allow 22 # SSH
sudo ufw enable

bash
sudo ufw allow 80/tcp # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw allow 3306/tcp # MySQL
sudo ufw allow 5432/tcp # PostgreSQL
sudo ufw enable

---

### _Serve Your Content_

#### Static Website (HTML/CSS)

Place your files in /var/www/html/ (for Apache) or configure a directory in Nginx.

bash
sudo cp index.html /var/www/html/

#### Dynamic App (Flask example)

python
from flask import Flask
app = Flask(**name**)

@app.route('/')
def hello():
return "Hello from Flask!"

app.run(host='0.0.0.0', port=5000)

Run it:

bash
python3 app.py

Then go to http://<your-ip>:5000

---

### _Access from Outside (Remote Hosting)_

If you want to access the server from the internet:

1. _Find your public IP_:

bash
curl ifconfig.me

2. _Port Forwarding_: Configure your router to forward external requests (e.g., port 80) to your Linux machine.

3. (Optional) _Get a Domain Name_:

   - Buy a domain (from Namecheap, GoDaddy, etc.)
   - Point it to your IP using DNS A record

4. (Optional) _Use Dynamic DNS_:

   - Use a service like DuckDNS or No-IP if you don’t have a static IP.

For hosting applications that require databases, you will need to install a database server. The most common databases for Linux servers are MySQL or PostgreSQL.

- _Install MySQL (or MariaDB, a MySQL-compatible fork)_:

  bash
  sudo apt install mysql-server # Ubuntu/Debian
  sudo yum install mariadb-server # CentOS/RedHat
  sudo dnf install mariadb-server # Fedora

- _Install PostgreSQL_:

  bash
  sudo apt install postgresql postgresql-contrib # Ubuntu/Debian
  sudo yum install postgresql-server # CentOS/RedHat
  sudo dnf install postgresql-server # Fedora

- _Start and Enable the Database Service_:

  bash
  sudo systemctl start mysql # MySQL/MariaDB
  sudo systemctl enable mysql # MySQL/MariaDB

  sudo systemctl start postgresql # PostgreSQL
  sudo systemctl enable postgresql # PostgreSQL

After installing the database server, you'll need to configure it.

- _Secure MySQL/MariaDB_ (important to set root password and remove test users):

  bash
  sudo mysql_secure_installation

- _Access MySQL_:

  bash
  sudo mysql -u root -p

- _Create a Database and User_:

  sql
  CREATE DATABASE my_database;
  CREATE USER 'my_user'@'localhost' IDENTIFIED BY 'password';
  GRANT ALL PRIVILEGES ON my_database.\* TO 'my_user'@'localhost';
  FLUSH PRIVILEGES;

- For PostgreSQL, you can do similarly:

  bash
  sudo -u postgres psql
  CREATE DATABASE my_database;
  CREATE USER my_user WITH ENCRYPTED PASSWORD 'password';
  GRANT ALL PRIVILEGES ON DATABASE my_database TO my_user;

- _Start and Enable the Service_:

  bash
  sudo systemctl start apache2 # Apache
  sudo systemctl enable apache2 # Apache (to start on boot)

  sudo systemctl start nginx # Nginx
  sudo systemctl enable nginx # Nginx (to start on boot)

You can test the web server by navigating to the server's IP address in your browser.

If you're hosting a website, you'll probably want to configure a domain name and set up SSL (Secure Socket Layer) encryption to secure traffic.

- _Install Certbot for SSL with Let's Encrypt_:

  bash
  sudo apt install certbot python3-certbot-nginx # For Nginx
  sudo apt install certbot python3-certbot-apache # For Apache

- _Generate SSL Certificate_:

  bash
  sudo certbot --nginx # For Nginx
  sudo certbot --apache # For Apache

This will automatically configure SSL for your website.

### _Test Your Server_

After setting everything up, check that the web server is running by visiting the server's IP address. If it's a web application, ensure your database is correctly connected.

### _Backup and Monitoring_

Regular backups and monitoring are essential for server maintenance.

- _Backup_: Use tools like rsync or automated services to back up the database and important files.
- _Monitoring: Set up monitoring tools like **Prometheus, **Grafana, or simpler tools like \*\*htop_ and _netstat_.

### ✅ _Make it Persistent_

Use _systemd_ to run apps as services:

Create a file: /etc/systemd/system/myapp.service

ini
[Unit]
Description=My App
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/youruser/myapp.py
WorkingDirectory=/home/youruser
Restart=always
User=youruser

[Install]
WantedBy=multi-user.target

Enable it:

bash
sudo systemctl daemon-reexec
sudo systemctl enable myapp
sudo systemctl start myapp

---

## 🔒 Bonus: Security Tips

- Used fail2ban to prevent brute-force attacks:

bash
sudo apt install fail2ban
