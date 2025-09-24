# Python Learning Journey - Day Two 🐍

**Date**: September 23, 2025  
**Instructor**: Mr. Miracle (Orientation on Backend Intro via Zoom)  
**Extra Setup**: Google Classroom created ✅

---

## 📖 Summary

Today, I continued my journey with **backend development** by learning how to set up a **Linux server** on my old laptop for hosting and database management.  
The session also covered hosting **Python apps** and ensuring proper security practices.

---

## 🔑 Key Learnings

1. Linux distributions use different package managers (`apt`, `yum`, `dnf`).
2. Installed and configured **Apache/Nginx** for serving websites.
3. Installed and secured **MySQL/PostgreSQL** for database management.
4. Configured **firewall rules** to allow HTTP, HTTPS, and database connections.
5. Hosted a basic **Flask app** and made it persistent with `systemd`.
6. Learned about SSL setup using **Certbot** and server hardening with **fail2ban**.
7. Understood the importance of **backups and monitoring** (Prometheus, Grafana, htop).

---

## 🛠 Practical Commands I Used

```bash
sudo apt update && sudo apt upgrade
sudo apt install nginx mysql-server python3 python3-pip
sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw allow 22/tcp
```
