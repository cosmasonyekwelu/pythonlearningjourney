# Day 02 - Python Learning Journey.

**Date:** September 23, 2025

## Activities

1. Attended orientation on **Backend Introduction** via Zoom (Instructor: Mr. Miracle)
2. Set up a **Linux server (Ubuntu)** on my old laptop
3. Created and joined **Google Classroom** for course activities
4. Installed web servers (Apache/Nginx) and databases (MySQL/PostgreSQL)
5. Hosted a basic Flask app and configured persistence using `systemd`

## Tutorial

- **Title:** Backend Orientation & Linux Server Setup
- **URL:** Zoom Session (Instructor-led)
- **Topics Covered:**
  - Linux package managers (`apt`, `yum`, `dnf`)
  - Web server setup (Apache, Nginx)
  - Database setup and security (MySQL, PostgreSQL)
  - Firewall configuration for HTTP, HTTPS, SSH
  - Hosting Python apps (Flask)
  - SSL setup using Certbot
  - Server monitoring & security (fail2ban, Prometheus, Grafana, htop)

## Key Learnings

- Different Linux distributions use different package managers
- Installed and configured **Nginx/Apache** for serving applications
- Installed and secured **MySQL/PostgreSQL** databases
- Opened firewall ports for secure access (HTTP, HTTPS, SSH)
- Used `systemd` to keep Flask apps running persistently
- Understood importance of **SSL certificates, monitoring, and backups**

## Practical Commands

```bash
sudo apt update && sudo apt upgrade
sudo apt install nginx mysql-server python3 python3-pip
sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw allow 22/tcp.

```

## Reflection

Today was all about setting up infrastructure. I learned how to configure a Linux server for hosting Python applications, securing it with firewalls and SSL, and ensuring persistence with systemd. This gave me a solid foundation for deploying future backend projects.
